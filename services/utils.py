from aiogram.types import PhotoSize
from config import DEFAULT_PHOTO_URL

async def get_photo_url(photo_sizes: list[PhotoSize], fallback_avatar=False):
    """Возвращает URL фото или fallback (Шаг 3 ТЗ)"""
    if photo_sizes:
        # Берём самое большое фото
        largest_photo = max(photo_sizes, key=lambda p: p.file_size or 0)
        return f"https://api.telegram.org/file/bot{BOT_TOKEN}/{largest_photo.file_path}"  # Замените BOT_TOKEN на импорт
    elif fallback_avatar:
        # Если нет фото — аватар пользователя (реализовать getUserProfilePhotos)
        return DEFAULT_PHOTO_URL  # Резервное
    else:
        return DEFAULT_PHOTO_URL

def validate_text_input(text: str, max_len: int = 500):
    """Валидация текста (для анкеты)"""
    return text.strip()[:max_len] if len(text.strip()) > 0 else None

# Другие утилиты (для Шага 6: разбор позиционирования) позже
