from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def get_main_menu(lang='ru'):
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
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True, one_time_keyboard=False)

def get_post_approval_menu(lang='ru'):
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
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True, one_time_keyboard=False)

def get_lang_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='🇷🇺 Русский', callback_data='lang_ru')],
        [InlineKeyboardButton(text='🇬🇧 English', callback_data='lang_en')]
    ])
