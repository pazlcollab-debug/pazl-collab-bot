from aiogram import Router, F
from aiogram.types import Message, FSInputFile
from aiogram.fsm.context import FSMContext

from states.form_states import FormStates
from services.airtable_api import create_expert_record
from services.utils import validate_text_input, get_photo_url
from config import DEFAULT_PHOTO_URL
from keyboards.main_menu import get_main_menu

router = Router()

@router.message(F.text == '🟡 Заполнить анкету')  # Триггер из меню
async def start_form(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get('lang', 'ru')
    text = "Введите ФИО:" if lang == 'ru' else "Enter full name:"
    await message.answer(text)
    await state.set_state(FormStates.waiting_for_name)

@router.message(FormStates.waiting_for_name)
async def process_name(message: Message, state: FSMContext):
    name = validate_text_input(message.text)
    if name:
        await state.update_data(name=name)
        text = "Теперь телефон/WhatsApp:" if lang == 'ru' else "Now phone/WhatsApp:"
        await message.answer(text)
        await state.set_state(FormStates.waiting_for_phone)
    else:
        await message.answer("Пожалуйста, введите корректное ФИО.")

# ... Аналогично для других состояний (waiting_for_phone → waiting_for_telegram → ... → waiting_for_positioning)
# Пример для фото (Шаг 3 ТЗ)
@router.message(FormStates.waiting_for_photo)
async def process_photo(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get('lang', 'ru')
    if message.photo:
        photo_sizes = message.photo
        photo_url = await get_photo_url(photo_sizes, fallback_avatar=True)
        await state.update_data(photo_url=photo_url)
        text = "Фото сохранено! Анкета завершена." if lang == 'ru' else "Photo saved! Form completed."
        await message.answer(text)
        # Сохраняем всю анкету
        full_data = await state.get_data()
        full_data['telegram_id'] = message.from_user.id
        await create_expert_record(full_data)
        await state.clear()
        keyboard = get_main_menu(lang)
        await message.answer("✅ Спасибо! Ваша анкета отправлена на проверку.", reply_markup=keyboard)
    else:
        # Fallback
        photo_url = DEFAULT_PHOTO_URL
        await state.update_data(photo_url=photo_url)
        await message.answer("Фото не получено — использовано резервное. Анкета завершена.")
        # Сохраняем
        full_data = await state.get_data()
        full_data['telegram_id'] = message.from_user.id
        await create_expert_record(full_data)
        await state.clear()
        keyboard = get_main_menu(lang)
        await message.answer("✅ Спасибо! Ваша анкета отправлена на проверку.", reply_markup=keyboard)

# Добавьте обработчики для остальных состояний (waiting_for_phone, waiting_for_city и т.д.) аналогично process_name
# Для множественного выбора (экспертиза) используйте InlineKeyboard
