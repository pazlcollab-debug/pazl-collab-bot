import asyncio
import logging
import os
from datetime import datetime, timedelta
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyairtable import Table
from config import AIRTABLE_API_KEY, AIRTABLE_BASE_ID
from keyboards.main_menu import get_main_menu, get_post_approval_menu  

# ==============================
# ⚙️ Настройка логов
# ==============================
os.makedirs("logs", exist_ok=True)
status_log_path = os.path.join("logs", "status.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | [%(levelname)s] | %(message)s",
    handlers=[
        logging.FileHandler(status_log_path, encoding="utf-8"),
        logging.StreamHandler()
    ]
)

# --- Таблица Airtable ---
table = Table(AIRTABLE_API_KEY, AIRTABLE_BASE_ID, "Experts")

# --- Канал для уведомлений ---
CHANNEL_ID = -1003351503095  # PAZL Collab — Moderation

# --- Кэш статусов и время последней очистки ---
known_statuses = {}
last_cache_reset = datetime.now()

# --- Отображение статусов ---
STATUS_DISPLAY = {
    "approved": {"ru": "🟢 Одобрено", "en": "🟢 Approved"},
    "pending": {"ru": "🟡 На модерации", "en": "🟡 Pending"},
    "declined": {"ru": "🔴 Отклонено", "en": "🔴 Declined"},
}

# ==============================
# 📢 Новая анкета → в канал модерации
# ==============================
async def notify_new_expert(bot, expert_name: str, lang: str, record_id: str = None):
    """Отправляет уведомление о новой анкете в канал модерации"""
    lang_tag = "RU" if lang == "ru" else "EN"
    status_text = STATUS_DISPLAY["pending"][lang]

    text = (
        "✅ Новая анкета\n"
        f"🌍 ({lang_tag})\n"
        f"👤 Имя: {expert_name}\n"
        f"📋 Статус: {status_text}\n"
        "━━━━━━━━━━━\n"
        "❗️Требуется внимание администратора"
    )

    reply_markup = None
    if record_id:
        # 🔗 Ссылка на таблицу Experts с фильтром по конкретной анкете
        airtable_url = (
            f"https://airtable.com/appFX4ZAKQZAjeubq/"
            f"tblQOISTaIlSUCII7/viwGELorZR43zBe7X"
            f"?filterByFormula=RECORD_ID()='{record_id}'"
        )

        reply_markup = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="📂 Открыть в Airtable", url=airtable_url)]
            ]
        )

    try:
        await bot.send_message(chat_id=CHANNEL_ID, text=text, reply_markup=reply_markup)
        logging.info(f"📢 Уведомление о новой анкете отправлено: {expert_name}")
    except Exception as e:
        logging.error(f"⚠️ Ошибка при отправке уведомления в канал: {e}")


# ==============================
# 🔄 Проверка статусов экспертов
# ==============================
async def check_expert_status(bot):
    """Проверяет статусы анкет и уведомляет пользователей при изменении"""
    global last_cache_reset

    logging.info("🔍 Фоновый мониторинг статусов экспертов запущен...")

    while True:
        try:
            # Очистка кэша каждые 24 часа
            if datetime.now() - last_cache_reset >= timedelta(hours=24):
                known_statuses.clear()
                last_cache_reset = datetime.now()
                logging.info("♻️ Кэш статусов сброшен (24 часа прошло).")

            # Получаем все записи
            records = table.all(fields=["TelegramID", "Status", "Language", "Notified"])
            total = len(records)
            approved_count = 0

            # --- Проверка существующих ID ---
            existing_ids = {
                str(rec.get("fields", {}).get("TelegramID"))
                for rec in records
                if rec.get("fields", {}).get("TelegramID")
            }

            # --- Удалённые анкеты ---
            for telegram_id in list(known_statuses.keys()):
                if telegram_id not in existing_ids:
                    try:
                        await bot.send_message(
                            chat_id=int(telegram_id),
                            text="♻️ Обновляем интерфейс...",
                            reply_markup=None
                        )
                        await bot.send_message(
                            chat_id=int(telegram_id),
                            text=(
                                "📋 Ваша анкета больше не найдена в базе.\n"
                                "Пожалуйста, заполните новую, чтобы участвовать в проектах PAZL Collab 🙌"
                            ),
                            reply_markup=get_main_menu("ru")
                        )
                        logging.info(f"🗑 Анкета {telegram_id} удалена — показано стартовое меню.")
                    except Exception as e:
                        logging.error(f"⚠️ Ошибка при уведомлении об удалённой анкете ({telegram_id}): {e}")
                    finally:
                        known_statuses.pop(telegram_id, None)

            # --- Проверка и уведомления ---
            for rec in records:
                fields = rec.get("fields", {})
                record_id = rec.get("id")
                telegram_id = str(fields.get("TelegramID"))
                raw_status = str(fields.get("Status", "")).strip().lower()

                # --- Определяем язык анкеты ---
                lang = fields.get("Language")
                if not lang or not isinstance(lang, str) or lang.strip() == "":
                    try:
                        user = await bot.get_chat(int(telegram_id))
                        lang_code = getattr(user, "language_code", "en").lower()
                        if lang_code.startswith(("ru", "uk", "be")):
                            lang = "ru"
                        else:
                            lang = "en"
                    except Exception:
                        lang = "en"

                notified = bool(fields.get("Notified", False))

                if not telegram_id or not raw_status:
                    continue

                # Очистка статуса от эмодзи
                cleaned_status = (
                    raw_status.replace("🟢", "")
                    .replace("🟡", "")
                    .replace("🔴", "")
                    .replace(":", "")
                    .replace(" ", "")
                    .strip()
                )

                # Унификация статусов
                if cleaned_status in ["approved", "одобрено"]:
                    normalized_status = "approved"
                elif cleaned_status in ["pending", "намодерации"]:
                    normalized_status = "pending"
                elif cleaned_status in ["declined", "отклонено"]:
                    normalized_status = "declined"
                else:
                    normalized_status = "unknown"

                prev_status = known_statuses.get(telegram_id)
                if normalized_status == prev_status:
                    continue

                # --- 🟢 Одобрено ---
                if normalized_status == "approved" and not notified:
                    approved_count += 1
                    approved_time = datetime.now().strftime("%d.%m.%Y в %H:%M")

                    text = (
                        f"🎉 Отличные новости!\n\n"
                        f"✅ Ваша анкета была одобрена {approved_time}.\n\n"
                        f"Теперь вы можете пользоваться всеми функциями PAZL Collab 🙌"
                        if lang == "ru"
                        else
                        f"🎉 Great news!\n\n"
                        f"✅ Your application was approved on {approved_time}.\n\n"
                        f"You can now enjoy all PAZL Collab features 🙌"
                    )

                    try:
                        await bot.send_message(
                            chat_id=int(telegram_id),
                            text=text,
                            reply_markup=get_post_approval_menu(lang)
                        )
                        table.update(record_id, {"Notified": True})
                        logging.info(f"✅ Пользователь {telegram_id} уведомлён об одобрении анкеты.")
                    except Exception as e:
                        logging.error(f"⚠️ Ошибка при уведомлении Approved ({telegram_id}): {e}")

                # --- 🔴 Отклонено ---
                elif normalized_status == "declined" and not notified:
                    text = (
                        "⚠️ Ваша анкета требует доработки. "
                        "Администратор свяжется с вами для уточнений."
                        if lang == "ru"
                        else
                        "⚠️ Your form requires revision. The admin will contact you soon."
                    )
                    try:
                        await bot.send_message(
                            chat_id=int(telegram_id),
                            text=text,
                            reply_markup=get_main_menu(lang)
                        )
                        table.update(record_id, {"Notified": True})
                        logging.info(f"⚠️ Пользователь {telegram_id} уведомлён об отказе.")
                    except Exception as e:
                        logging.error(f"⚠️ Ошибка при уведомлении Declined ({telegram_id}): {e}")

                # Обновляем кэш
                known_statuses[telegram_id] = normalized_status

            if approved_count == 0:
                logging.info("📭 Все одобренные анкеты уже уведомлены.")
            else:
                logging.info(f"⚙️ Проверено {total} записей, новых Approved: {approved_count}")

        except Exception as e:
            logging.error(f"❌ Ошибка при проверке статусов: {e}")

        await asyncio.sleep(1800)  # Проверка каждые 30 минут
