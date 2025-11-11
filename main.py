import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from handlers import start, form
from services.airtable_api import get_table
from services.status_notifier import check_expert_status


async def main():
    # ============================================================
    # 🔹 ЛОГИРОВАНИЕ
    # ============================================================
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | [%(levelname)s] | %(message)s"
    )
    logging.info("🚀 PAZL Collab Bot v1.0 запущен")

    # ============================================================
    # 🤖 ИНИЦИАЛИЗАЦИЯ
    # ============================================================
    bot = Bot(token=BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    dp.include_router(start.router)
    dp.include_router(form.router)

    # ============================================================
    # 🔗 Проверка подключения к Airtable
    # ============================================================
    try:
        table = get_table()
        records = table.all(max_records=1)  # health-check без загрузки всей базы
        logging.info("✅ Airtable подключён успешно")
    except Exception as e:
        logging.warning(f"⚠️ Ошибка подключения к Airtable: {e} — используется тестовый режим")

    # ============================================================
    # 🟢 Фоновая проверка статусов
    # ============================================================
    try:
        asyncio.create_task(check_expert_status(bot))
        logging.info("🟢 Мониторинг статусов экспертов запущен (каждые 30 мин)")
    except Exception as e:
        logging.error(f"❌ Ошибка при запуске фоновой проверки статусов: {e}")

    # ============================================================
    # 🔁 ЗАПУСК ОСНОВНОГО ЦИКЛА
    # ============================================================
    logging.info("🤖 Подключение к Telegram API...")
    await dp.start_polling(bot)

# ============================================================
# 🛑 ЗАВЕРШЕНИЕ
# ============================================================

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("🛑 Бот остановлен пользователем")
    finally:
        logging.info("🧹 Завершение фоновых задач...")
