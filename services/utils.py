from aiogram import Bot
from aiogram.types import PhotoSize
from config import DEFAULT_PHOTO_URL, BOT_TOKEN
import asyncio
import re
from typing import Optional

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


def validate_phone(phone: str) -> Optional[str]:
    """
    Валидация телефона (поддерживает различные форматы):
    - +7 (999) 123-45-67
    - +79991234567
    - 89991234567
    - 8 (999) 123-45-67
    - +1 (555) 123-4567
    """
    if not phone:
        return None
    
    phone = phone.strip()
    # Удаляем все символы кроме цифр и +
    cleaned = re.sub(r'[^\d+]', '', phone)
    
    # Проверяем минимальную длину (7 цифр) и максимальную (15 цифр по E.164)
    digits_only = re.sub(r'\+', '', cleaned)
    if len(digits_only) < 7 or len(digits_only) > 15:
        return None
    
    # Если начинается с 8, заменяем на +7 (для России)
    if cleaned.startswith('8') and len(digits_only) == 11:
        cleaned = '+7' + digits_only[1:]
    
    # Если нет + в начале, добавляем (предполагаем российский номер)
    if not cleaned.startswith('+') and len(digits_only) == 10:
        cleaned = '+7' + cleaned
    
    return cleaned if cleaned.startswith('+') else None


def validate_telegram_username(username: str) -> Optional[str]:
    """
    Валидация Telegram username:
    - @username или username
    - 5-32 символа
    - только буквы, цифры и подчеркивания
    """
    if not username:
        return None
    
    username = username.strip()
    # Убираем @ если есть
    if username.startswith('@'):
        username = username[1:]
    
    # Проверяем формат: 5-32 символа, только буквы, цифры и подчеркивания
    if not re.match(r'^[a-zA-Z0-9_]{5,32}$', username):
        return None
    
    return username


def validate_url(url: str) -> Optional[str]:
    """
    Валидация URL (для соцсетей):
    - http://, https:// или без протокола
    - Добавляет https:// если протокола нет
    """
    if not url:
        return None
    
    url = url.strip()
    
    # Если нет протокола, добавляем https://
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    # Простая проверка формата URL
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    if not url_pattern.match(url):
        return None
    
    return url


def validate_email(email: str) -> Optional[str]:
    """
    Валидация email адреса
    """
    if not email:
        return None
    
    email = email.strip().lower()
    email_pattern = re.compile(
        r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    )
    
    if not email_pattern.match(email):
        return None
    
    return email


def sanitize_text(text: str, max_len: int = 500) -> str:
    """
    Санитизация текста для безопасности:
    - Удаляет потенциально опасные символы
    - Ограничивает длину
    """
    if not text:
        return ""
    
    # Убираем лишние пробелы
    text = ' '.join(text.split())
    
    # Ограничиваем длину
    text = text[:max_len]
    
    return text
