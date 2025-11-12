from aiogram import Bot
from aiogram.types import PhotoSize
from config import DEFAULT_PHOTO_URL, BOT_TOKEN
import asyncio

# ==============================
# 🤖 Инициализация бота (глобально, но безопасно)
# ==============================
bot = Bot(token=BOT_TOKEN)

# ==============================
# 📸 Получение URL фотографии
# ==============================
async def get_photo_url(photo_sizes: list[PhotoSize], fallback_avatar: bool = False) -> str:
    """
    Возвращает URL фото из Telegram API.
    Добавлен таймаут 5 сек, чтобы бот не зависал, если Telegram долго отвечает.
    """
    if not photo_sizes:
        return DEFAULT_PHOTO_URL

    try:
        # Берём самое большое фото (лучшее качество)
        largest_photo = max(photo_sizes, key=lambda p: p.file_size or 0)

        # ⏱️ Безопасное ожидание с таймаутом
        file = await asyncio.wait_for(bot.get_file(largest_photo.file_id), timeout=5.0)

        photo_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file.file_path}"
        return photo_url

    except asyncio.TimeoutError:
        print("⚠️ Таймаут: Telegram не ответил вовремя при получении фото. Используем fallback.")
        return DEFAULT_PHOTO_URL

    except Exception as e:
        print(f"⚠️ Ошибка получения фото из Telegram: {e}")
        return DEFAULT_PHOTO_URL if fallback_avatar else DEFAULT_PHOTO_URL


# ==============================
# 🧹 Валидация текстовых вводов
# ==============================
def validate_text_input(text: str, max_len: int = 500) -> str | None:
    """
    Простая валидация текста:
    - убирает пробелы по краям;
    - ограничивает длину;
    - возвращает None, если строка пустая.
    """
    if not text:
        return None
    text = text.strip()
    return text[:max_len] if text else None
