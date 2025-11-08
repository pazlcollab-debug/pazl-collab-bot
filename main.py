import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage  # Для FSM в тесте

from config import BOT_TOKEN
from handlers import start, form  # Импорт роутеров
from services.airtable_api import get_table  # Тест подключения

async def main():
    logging.basicConfig(level=logging.INFO)
    bot = Bot(token=BOT_TOKEN)
    storage = MemoryStorage()  # Для FSM
    dp = Dispatcher(storage=storage)
    
    # Регистрируем роутеры
    dp.include_router(start.router)
    dp.include_router(form.router)
    
    # Тест Airtable (если ключи dummy — warning ок)
    try:
        table = get_table()
        records = table.list_records()  # Проверка соединения
        logging.info("Airtable подключён! Записей: %d", len(records['records']))
    except Exception as e:
        logging.warning(f"Airtable: {e} (заглушки — нормально для теста)")
    
    # Polling для теста (webhook для Railway позже)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
