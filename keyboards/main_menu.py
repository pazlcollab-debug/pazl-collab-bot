from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

# ============================================================
# 🟡  Главное меню — ДО отправки анкеты
# ============================================================

def get_main_menu(lang: str = 'ru') -> ReplyKeyboardMarkup:
    """Меню до того, как пользователь отправил анкету."""
    if lang == 'ru':
        buttons = [
            [KeyboardButton(text='🟡 Заполнить анкету')],
            [KeyboardButton(text='ℹ️ Как это работает')]
        ]
    else:
        buttons = [
            [KeyboardButton(text='🟡 Fill the form')],
            [KeyboardButton(text='ℹ️ How it works')]
        ]
    return ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        one_time_keyboard=False
    )


# ============================================================
# 📊  Меню — ПОСЛЕ отправки анкеты (в ожидании проверки)
# ============================================================

def get_status_menu(lang: str = 'ru') -> ReplyKeyboardMarkup:
    """Меню после того, как анкета уже отправлена (Pending)."""
    if lang == 'ru':
        buttons = [
            [KeyboardButton(text='📊 Проверить статус анкеты')],
            [KeyboardButton(text='ℹ️ Как это работает')]
        ]
    else:
        buttons = [
            [KeyboardButton(text='📊 Check form status')],
            [KeyboardButton(text='ℹ️ How it works')]
        ]
    return ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        one_time_keyboard=False
    )


# ============================================================
# ✅  Меню — ПОСЛЕ одобрения анкеты (Approved)
# ============================================================

def get_post_approval_menu(lang: str = 'ru') -> ReplyKeyboardMarkup:
    """Меню после модерации анкеты (Approved)."""
    if lang == 'ru':
        buttons = [
            [KeyboardButton(text='🔍 Найти партнёра для эфира')],
            [KeyboardButton(text='🎙 Найти партнёра для подкаста')],
            [KeyboardButton(text='📘 Инструкции')],
            [KeyboardButton(text='⚙️ Мой профиль')]
        ]
    else:
        buttons = [
            [KeyboardButton(text='🔍 Find partner for stream')],
            [KeyboardButton(text='🎙 Find partner for podcast')],
            [KeyboardButton(text='📘 Instructions')],
            [KeyboardButton(text='⚙️ My profile')]
        ]
    return ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        one_time_keyboard=False
    )


# ============================================================
# 🌐  Клавиатура выбора языка при первом запуске
# ============================================================

def get_lang_keyboard() -> InlineKeyboardMarkup:
    """Инлайн-клавиатура для выбора языка при первом запуске."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='🇷🇺 Русский', callback_data='lang_ru')],
            [InlineKeyboardButton(text='🇬🇧 English', callback_data='lang_en')]
        ]
    )
