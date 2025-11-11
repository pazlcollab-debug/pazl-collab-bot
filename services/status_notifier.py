import asyncio
import logging
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyairtable import Table
from config import AIRTABLE_API_KEY, AIRTABLE_BASE_ID
from keyboards.main_menu import get_post_approval_menu, get_main_menu

# --- Таблица Airtable ---
table = Table(AIRTABLE_API_KEY, AIRTABLE_BASE_ID, "Experts")

# --- Канал для уведомлений ---
CHANNEL_ID = -1003351503095  # PAZL Collab — Moderation

# --- Кэш статусов ---
known_statuses = {}


# ==============================
# 📢 Новая анкета → в канал
# ==============================
async def notify_new_expert(bot, expert_name: str, lang: str, record_id: str = None):
    """Отправляет уведомление о новой анкете в канал модерации"""
    lang_tag = "RU" if lang == "ru" else "EN"
    status_text = "🟡 На модерации" if lang == "ru" else "🟡 Pending"

    text = (
        "━━━━━━━━━━━\n"
        f"🆕 Новая анкета ({lang_tag})\n"
        f"👤 Имя: {expert_name}\n"
        f"📋 Статус: {status_text}\n"
        "━━━━━━━━━━━\n"
        "❗️Требуется внимание администратора"
    )

    # --- Кнопка Airtable ---
    reply_markup = None
    if record_id:
        airtable_url = f"https://airtable.com/{AIRTABLE_BASE_ID}/Experts/{record_id}"
        reply_markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📂 Открыть в Airtable", url=airtable_url)]
        ])

    try:
        await bot.send_message(
            chat_id=CHANNEL_ID,
            text=text,
            reply_markup=reply_markup
        )
        logging.info(f"📢 Уведомление о новой анкете отправлено: {expert_name}")
    except Exception as e:
        logging.error(f"⚠️ Ошибка при отправке уведомления в канал: {e}")


# ==============================
# 🔄 Проверка статусов экспертов
# ==============================
async def check_expert_status(bot):
    """Проверяет статусы анкет и уведомляет пользователей при изменении"""
    logging.info("🔍 Фоновый мониторинг статусов экспертов запущен...")

    while True:
        try:
            records = table.all(fields=["TelegramID", "Status", "Language"])
            total = len(records)
            approved_count = 0

            for rec in records:
                fields = rec.get("fields", {})
                telegram_id = fields.get("TelegramID")
                status = fields.get("Status")
                lang = fields.get("Language", "ru")

                if not telegram_id or not status:
                    continue

                prev_status = known_statuses.get(telegram_id)

                # Пропускаем, если статус не изменился
                if prev_status == status:
                    continue

                # Обновляем кэш
                known_statuses[telegram_id] = status

                normalized_status = str(status).strip().lower()

                # --- Approved ---
                if normalized_status in ["approved", "🟢 одобрено"]:
                    approved_count += 1
                    text = (
                        "✅ Ваша анкета одобрена!\n\n"
                        "Теперь вы можете заполнить дополнительные данные и принять участие в каталоге экспертов 👇"
                        if lang == "ru"
                        else
                        "✅ Your form has been approved!\n\n"
                        "Now you can complete your profile and join the expert catalog 👇"
                    )

                    try:
                        await bot.send_message(
                            chat_id=telegram_id,
                            text=text,
                            reply_markup=get_post_approval_menu(lang)
                        )
                        logging.info(f"✅ Пользователь {telegram_id} уведомлён об одобрении анкеты.")
                    except Exception as e:
                        logging.error(f"⚠️ Ошибка при уведомлении Approved ({telegram_id}): {e}")

                # --- Declined ---
                elif normalized_status in ["declined", "🔴 отклонено"]:
                    text = (
                        "⚠️ Ваша анкета требует доработки. Администратор свяжется с вами для уточнений."
                        if lang == "ru"
                        else
                        "⚠️ Your form requires revision. The admin will contact you soon."
                    )
                    try:
                        await bot.send_message(
                            chat_id=telegram_id,
                            text=text,
                            reply_markup=get_main_menu(lang)
                        )
                        logging.info(f"⚠️ Пользователь {telegram_id} уведомлён о необходимости доработки.")
                    except Exception as e:
                        logging.error(f"⚠️ Ошибка при уведомлении Declined ({telegram_id}): {e}")

            logging.info(f"⚙️ Проверено {total} записей, новых Approved: {approved_count}")

        except Exception as e:
            logging.error(f"❌ Ошибка при проверке статусов: {e}")

        # Проверка каждые 30 минут
        await asyncio.sleep(1800)
