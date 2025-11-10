import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from handlers import start, form
from services.airtable_api import get_table
from services.status_notifier import check_expert_status  # ✅ добавляем импорт фоновой проверки

async def main():
    logging.basicConfig(level=logging.INFO)
    bot = Bot(token=BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    dp.include_router(start.router)
    dp.include_router(form.router)
    
    try:
        table = get_table()
        records = table.all()
        logging.info("Airtable подключён! Записей: %d", len(records))
    except Exception as e:
        logging.warning(f"Airtable: {e} (заглушки — нормально для теста)")
    
    # ✅ запускаем фоновую задачу проверки статусов (раз в 30 минут)
    asyncio.create_task(check_expert_status())

    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
