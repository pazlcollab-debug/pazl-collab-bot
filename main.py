import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from pyairtable import Table

from config import BOT_TOKEN, AIRTABLE_API_KEY, AIRTABLE_BASE_ID
from handlers import start, form, menu_handlers
from services.airtable_api import get_table
from services.status_notifier import check_expert_status
from keyboards.main_menu import get_expert_menu


# ============================================================
# 📬 Проверка Approved без уведомления и автоуведомление при старте
# ============================================================
async def notify_pending_approved(bot: Bot):
    """
    Проверяет в Airtable анкеты со статусом Approved и Notified=False
    и отправляет им уведомление при старте.
    """
    try:
        table = Table(AIRTABLE_API_KEY, AIRTABLE_BASE_ID, "Experts")
        records = table.all(formula="AND({Status}='Approved', NOT({Notified}))")
        count = len(records)

        if count == 0:
            logging.info("📭 Все одобренные анкеты уже уведомлены.")
            return

        logging.info(f"📬 Найдено {count} одобренных анкет без уведомления. Отправляем уведомления...")

        for rec in records:
            fields = rec.get("fields", {})
            record_id = rec.get("id")
            telegram_id = fields.get("TelegramID")
            lang = fields.get("Language", "ru")

            if not telegram_id:
                continue

            text = (
                "🎉 Отличные новости!\n\n✅ Ваша анкета одобрена!\nТеперь вы можете заполнить дополнительные данные и участвовать в проектах PAZL Collab 👇"
                if lang == "ru"
                else
                "🎉 Great news!\n\n✅ Your form has been approved!\nNow you can complete your profile and join PAZL Collab projects 👇"
            )

            try:
                await bot.send_message(
                    chat_id=int(telegram_id),
                    text=text,
                    reply_markup=get_expert_menu(lang)
                )
                table.update(record_id, {"Notified": True})
                logging.info(f"✅ Пользователь {telegram_id} уведомлён при старте.")
            except Exception as e:
                logging.error(f"⚠️ Ошибка при уведомлении {telegram_id} при старте: {e}")

        logging.info("📨 Все неуведомлённые Approved-пользователи получили сообщение.")

    except Exception as e:
        logging.error(f"❌ Ошибка при авто-уведомлении Approved при старте: {e}")


# ============================================================
# 🚀 Основная функция запуска бота
# ============================================================
async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | [%(levelname)s] | %(message)s"
    )
    logging.info("🚀 PAZL Collab Bot v1.0 запущен")

    bot = Bot(token=BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    # ✅ Подключаем все роутеры
    dp.include_router(start.router)
    dp.include_router(form.router)
    dp.include_router(menu_handlers.router)

    # ============================================================
    # 🔗 Проверка подключения к Airtable
    # ============================================================
    try:
        table = get_table()
        table.all(max_records=1)
        logging.info("✅ Airtable подключён успешно")
    except Exception as e:
        logging.warning(f"⚠️ Ошибка подключения к Airtable: {e} — используется тестовый режим")

    # ============================================================
    # 📬 Проверка Approved без уведомления и отправка при старте
    # ============================================================
    await notify_pending_approved(bot)

    # ============================================================
    # 🟢 Фоновая проверка статусов экспертов
    # ============================================================
    try:
        asyncio.create_task(check_expert_status(bot))
        logging.info("🟢 Мониторинг статусов экспертов запущен (каждые 30 мин)")
    except Exception as e:
        logging.error(f"❌ Ошибка при запуске фоновой проверки статусов: {e}")

    # ============================================================
    # 🔁 Запуск Telegram polling
    # ============================================================
    logging.info("🤖 Подключение к Telegram API...")
    await dp.start_polling(bot)


# ============================================================
# 🛑 Завершение
# ============================================================
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("🛑 Бот остановлен пользователем")
    finally:
        logging.info("🧹 Завершение фоновых задач...")
