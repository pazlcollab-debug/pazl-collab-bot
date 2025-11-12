from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

# ============================================================
# 🟡 Главное меню — ДО отправки анкеты
# ============================================================

def get_main_menu(lang: str = 'ru') -> ReplyKeyboardMarkup:
    """
    Главное меню до того, как пользователь отправил анкету.
    Показывается при первом запуске после выбора языка.
    """
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
        input_field_placeholder=(
            "Выберите действие..." if lang == 'ru' else "Choose an action..."
        )
    )


# ============================================================
# 📊 Меню — ПОСЛЕ отправки анкеты (🟡 Pending)
# ============================================================

def get_status_menu(lang: str = 'ru') -> ReplyKeyboardMarkup:
    """
    Меню, которое показывается после того,
    как пользователь уже заполнил анкету, но она ещё на модерации.
    """
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
        input_field_placeholder=(
            "Анкета на модерации..." if lang == 'ru' else "Form under review..."
        )
    )


# ============================================================
# 🟢 Меню — ПОСЛЕ одобрения анкеты (Approved)
# ============================================================

def get_post_approval_menu(lang: str = 'ru') -> ReplyKeyboardMarkup:
    """
    Меню, которое показывается после модерации анкеты,
    если анкета одобрена модератором (статус Approved).
    """
    if lang == 'ru':
        buttons = [
            [KeyboardButton(text='🔍 Найти партнёра для эфира')],
            [KeyboardButton(text='🎙 Найти партнёра для подкаста')],
            [KeyboardButton(text='📘 Инструкции')],
            [KeyboardButton(text='⚙️ Мой профиль')]
        ]
    else:
        buttons = [
            [KeyboardButton(text='🔍 Find a partner for stream')],
            [KeyboardButton(text='🎙 Find a partner for podcast')],
            [KeyboardButton(text='📘 Instructions')],
            [KeyboardButton(text='⚙️ My profile')]
        ]

    return ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        input_field_placeholder=(
            "Выберите действие..." if lang == 'ru' else "Choose an action..."
        )
    )


# ============================================================
# 🔴 Меню — ЕСЛИ анкета отклонена (Declined)
# ============================================================

def get_declined_menu(lang: str = 'ru') -> ReplyKeyboardMarkup:
    """
    Меню, которое показывается, если анкета была отклонена.
    Предлагает пользователю отправить анкету заново.
    """
    if lang == 'ru':
        buttons = [
            [KeyboardButton(text='🟡 Отправить анкету заново')],
            [KeyboardButton(text='ℹ️ Как это работает')]
        ]
    else:
        buttons = [
            [KeyboardButton(text='🟡 Re-submit form')],
            [KeyboardButton(text='ℹ️ How it works')]
        ]

    return ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        input_field_placeholder=(
            "Анкета отклонена, можно отправить заново." if lang == 'ru'
            else "Form declined, you can re-submit."
        )
    )


# ============================================================
# 🌐 Клавиатура выбора языка при первом запуске
# ============================================================

def get_lang_keyboard() -> InlineKeyboardMarkup:
    """
    Инлайн-клавиатура для выбора языка при первом запуске.
    Показывается при /start перед основным меню.
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='🇷🇺 Русский', callback_data='lang_ru')],
            [InlineKeyboardButton(text='🇬🇧 English', callback_data='lang_en')]
        ]
    )


# ============================================================
# 💬 Вспомогательная клавиатура (опционально)
# ============================================================

def get_back_to_main_menu(lang: str = 'ru') -> InlineKeyboardMarkup:
    """
    Инлайн-клавиатура с кнопкой 'Назад в меню',
    которую можно использовать в любых сообщениях бота.
    """
    if lang == 'ru':
        button_text = '⬅️ Вернуться в меню'
    else:
        button_text = '⬅️ Back to menu'

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=button_text, callback_data='back_to_main')]
        ]
    )
# ============================================================
# 🧩 Старый метод — для обратной совместимости
# ============================================================

def get_expert_menu(lang: str = 'ru'):
    """
    ⚠️ Временная совместимость: возвращает меню для эксперта.
    Используется в старых версиях main.py.
    """
    from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

    if lang == 'ru':
        buttons = [
            [KeyboardButton(text='🔍 Найти партнёра для эфира')],
            [KeyboardButton(text='🎙 Найти партнёра для подкаста')],
            [KeyboardButton(text='📘 Инструкции')],
            [KeyboardButton(text='⚙️ Мой профиль')]
        ]
    else:
        buttons = [
            [KeyboardButton(text='🔍 Find a partner for stream')],
            [KeyboardButton(text='🎙 Find a partner for podcast')],
            [KeyboardButton(text='📘 Instructions')],
            [KeyboardButton(text='⚙️ My profile')]
        ]

    return ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        input_field_placeholder=(
            "Выберите действие..." if lang == 'ru' else "Choose an action..."
        )
    )
