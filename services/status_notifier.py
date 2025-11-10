import asyncio
from pyairtable import Table
from config import AIRTABLE_API_KEY, AIRTABLE_BASE_ID, BOT_TOKEN
from aiogram import Bot
from keyboards.main_menu import get_post_approval_menu, get_main_menu

bot = Bot(token=BOT_TOKEN)
table = Table(AIRTABLE_API_KEY, AIRTABLE_BASE_ID, "Experts")

# Хранилище статусов, чтобы не спамить одинаковыми уведомлениями
known_statuses = {}


async def check_expert_status():
    """Проверяет статусы экспертов в Airtable и уведомляет при изменении"""
    print("🔍 Запуск проверки статусов в Airtable...")

    while True:
        try:
            records = table.all(fields=["TelegramID", "Status", "Language"])
            for rec in records:
                fields = rec.get("fields", {})
                telegram_id = fields.get("TelegramID")
                status = fields.get("Status")
                lang = fields.get("Language", "ru")

                if not telegram_id or not status:
                    continue

                prev_status = known_statuses.get(telegram_id)
                if prev_status != status:
                    known_statuses[telegram_id] = status

                    if status.lower() == "approved":
                        text = (
                            "🎉 Ваша анкета одобрена! Добро пожаловать в сообщество экспертов 🙌"
                            if lang == "ru"
                            else
                            "🎉 Your form has been approved! Welcome to the expert community 🙌"
                        )
                        await bot.send_message(
                            telegram_id,
                            text,
                            reply_markup=get_post_approval_menu(lang)
                        )

                    elif status.lower() == "declined":
                        text = (
                            "⚠️ Ваша анкета требует доработки. Администратор свяжется с вами для уточнений."
                            if lang == "ru"
                            else
                            "⚠️ Your form requires revision. The admin will contact you soon."
                        )
                        await bot.send_message(
                            telegram_id,
                            text,
                            reply_markup=get_main_menu(lang)
                        )

        except Exception as e:
            print(f"❌ Ошибка проверки статусов: {e}")

        await asyncio.sleep(1800)  # Проверяем каждые 30 секунд
