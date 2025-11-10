from aiogram import Bot
from aiogram.types import PhotoSize
from config import DEFAULT_PHOTO_URL, BOT_TOKEN

bot = Bot(token=BOT_TOKEN)

async def get_photo_url(photo_sizes: list[PhotoSize], fallback_avatar: bool = False) -> str:
    """Возвращает URL фото из Telegram или fallback при ошибке."""
    if not photo_sizes:
        return DEFAULT_PHOTO_URL

    try:
        # Берём самое большое фото
        largest_photo = max(photo_sizes, key=lambda p: p.file_size or 0)
        # Запрашиваем у Telegram API путь к файлу
        file = await bot.get_file(largest_photo.file_id)
        photo_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file.file_path}"
        return photo_url
    except Exception as e:
        print(f"⚠️ Ошибка получения фото: {e}")
        return DEFAULT_PHOTO_URL if fallback_avatar else DEFAULT_PHOTO_URL


def validate_text_input(text: str, max_len: int = 500) -> str | None:
    """Простая валидация текста — убирает пробелы и ограничивает длину."""
    text = text.strip()
    if text:
        return text[:max_len]
    return None
