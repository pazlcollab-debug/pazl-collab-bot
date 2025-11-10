from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
import logging  # Стандартный logging, не из aiogram

from config import ADMIN_ID
from keyboards.main_menu import get_main_menu, get_lang_keyboard
from states.form_states import FormStates

router = Router()

@router.message(Command('start'))
async def cmd_start(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if user_id == ADMIN_ID:
        await message.answer("👋 Админ, привет! Бот готов к тестам. /broadcast для рассылки.")
    else:
        await message.answer(
            "👋 Добро пожаловать в PAZL Collab Bot!\n\nВыберите язык:",
            reply_markup=get_lang_keyboard()
        )
    logging.info(f"User {user_id} started bot")

@router.callback_query(F.data.startswith('lang_'))
async def choose_lang(callback: CallbackQuery, state: FSMContext):
    lang = callback.data.split('_')[1]
    await state.update_data(lang=lang)
    text = "Язык выбран!" if lang == 'ru' else "Language selected!"
    keyboard = get_main_menu(lang)
    welcome = (
        "PAZL — это сообщество экспертов, которые ищут партнёров для эфиров, подкастов и проектов.\n"
        "Заполните анкету, и после модерации вы сможете найти коллегу для коллаборации."
    ) if lang == 'ru' else (
        "PAZL is a community of experts looking for partners for streams, podcasts, and projects.\n"
        "Fill out the form, and after moderation, you can find a colleague for collaboration."
    )
    await callback.message.answer(text + "\n\n" + welcome, reply_markup=keyboard)
    await callback.answer()
    logging.info(f"Language {lang} selected by user {callback.from_user.id}")

@router.message(F.text.in_(['ℹ️ Как это работает', 'ℹ️ How does it work']))
async def how_it_works(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get('lang', 'ru')
    text = (
        "PAZL помогает экспертам находить коллаборации: заполните анкету → модерация → поиск партнёров в Mini App (свайпы как в Tinder)."
    ) if lang == 'ru' else (
        "PAZL helps experts find collaborations: fill out the form → moderation → partner search in Mini App (swipes like Tinder)."
    )
    await message.answer(text)
    logging.info(f"How it works shown to user {message.from_user.id}, lang {lang}")
