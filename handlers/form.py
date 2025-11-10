from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext

from states.form_states import FormStates
from services.airtable_api import create_expert_record, get_table
from services.utils import validate_text_input, get_photo_url
from config import DEFAULT_PHOTO_URL
from keyboards.main_menu import get_main_menu, get_status_menu
from keyboards.form_keyboards import (
    get_main_direction_keyboard,
    get_methods_keyboard,
    get_education_keyboard,
    get_experience_keyboard,
    get_work_format_keyboard,
    get_clients_count_keyboard,
    get_average_check_keyboard,
    get_client_requests_keyboard
)

router = Router()


# ==========================
# ⚙️ Вспомогательные клавиатуры
# ==========================
def get_photo_keyboard(lang="ru"):
    send_text = "📸 Отправить фото" if lang == "ru" else "📸 Send photo"
    skip_text = "⏭️ Пропустить" if lang == "ru" else "⏭️ Skip"
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=send_text, callback_data="send_photo")],
        [InlineKeyboardButton(text=skip_text, callback_data="skip_photo")]
    ])


def get_skip_keyboard(lang="ru"):
    skip_text = "⏭️ Пропустить" if lang == "ru" else "⏭️ Skip"
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=skip_text, callback_data="skip_photo")]
    ])


# ==========================
# 🔍 Проверка анкеты в Airtable
# ==========================
async def check_existing_form(telegram_id: int):
    """Проверяет, есть ли анкета пользователя по TelegramID"""
    table = get_table()
    try:
        records = table.all(formula=f"{{TelegramID}} = '{telegram_id}'")
        if not records:
            return None
        record = records[0]
        return {
            "id": record["id"],
            "status": record["fields"].get("Status", "Pending"),
            "date": record["fields"].get("Date", "—")
        }
    except Exception as e:
        print(f"⚠️ Ошибка при проверке анкеты: {e}")
        return None


# ==========================
# 🟡 Старт анкеты
# ==========================
@router.message(F.text.in_(['🟡 Заполнить анкету', '🟡 Fill the form']))
async def start_form(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "ru")
    await state.update_data(lang=lang)
    print(f"🚀 Старт анкеты. Язык: {lang}")

    existing = await check_existing_form(message.from_user.id)
    if existing:
        status, date = existing["status"], existing["date"]
        if lang == 'ru':
            text = (
                f"✅ Вы уже отправляли анкету {date}.\n"
                f"📋 Текущий статус: *{status}*\n\n"
                f"Чтобы проверить актуальное состояние — нажмите «📊 Проверить статус анкеты»."
            )
        else:
            text = (
                f"✅ You already submitted your form on {date}.\n"
                f"📋 Current status: *{status}*\n\n"
                f"To check the latest status — press “📊 Check form status”."
            )
        await message.answer(text, reply_markup=get_status_menu(lang), parse_mode="Markdown")
        return

    await state.update_data(
        main_direction=[], additional_methods=[], work_formats=[], client_requests=[],
        products=[], client_sources=[], collab_formats=[], collab_partners=[],
        collab_offer=[], motivation=[]
    )

    text = (
        "📋 БЛОК 1: ЛИЧНЫЕ ДАННЫЕ И КОНТАКТЫ\n\nВведите ФИО:"
        if lang == 'ru' else
        "📋 BLOCK 1: PERSONAL DATA\n\nEnter full name:"
    )
    await message.answer(text)
    await state.set_state(FormStates.waiting_for_name)


# ==========================
# 📊 Проверка статуса анкеты
# ==========================
@router.message(F.text.in_(['📊 Проверить статус анкеты', '📊 Check form status']))
async def check_form_status(message: Message, state: FSMContext):
    lang = (await state.get_data()).get('lang', 'ru')
    result = await check_existing_form(message.from_user.id)

    if not result:
        text = (
            "ℹ️ У вас пока нет анкеты.\n\nНажмите «🟡 Заполнить анкету», чтобы отправить первую."
            if lang == 'ru'
            else
            "ℹ️ You don’t have a form yet.\n\nPress “🟡 Fill the form” to submit your first one."
        )
        await message.answer(text, reply_markup=get_main_menu(lang))
        return

    status = result["status"]
    date = result["date"]

    if lang == 'ru':
        if status == "Pending":
            text = f"🟡 Ваша анкета от {date} находится на проверке.\n⏳ Статус: *{status}*"
        elif status == "Approved":
            text = f"✅ Ваша анкета от {date} одобрена и добавлена в каталог экспертов."
        elif status == "Declined":
            text = f"⚠️ Ваша анкета от {date} отклонена. Администратор свяжется с вами для доработки."
        else:
            text = f"ℹ️ Ваша анкета от {date}. Статус: {status}"
    else:
        if status == "Pending":
            text = f"🟡 Your form submitted on {date} is under review.\n⏳ Status: *{status}*"
        elif status == "Approved":
            text = f"✅ Your form submitted on {date} has been approved and added to the experts catalog."
        elif status == "Declined":
            text = f"⚠️ Your form submitted on {date} was declined. The admin will contact you soon."
        else:
            text = f"ℹ️ Your form from {date}. Status: {status}"

    await message.answer(text, reply_markup=get_status_menu(lang), parse_mode="Markdown")


# ==========================
# 🧠 Блок 1: Личные данные
# ==========================
@router.message(FormStates.waiting_for_name)
async def process_name(message: Message, state: FSMContext):
    lang = (await state.get_data()).get('lang', 'ru')
    name = validate_text_input(message.text)
    if name:
        await state.update_data(name=name)
        await message.answer("Телефон/WhatsApp:" if lang == 'ru' else "Phone/WhatsApp:")
        await state.set_state(FormStates.waiting_for_phone)
    else:
        await message.answer("Пожалуйста, введите корректное ФИО." if lang == 'ru' else "Please enter valid full name.")


@router.message(FormStates.waiting_for_phone)
async def process_phone(message: Message, state: FSMContext):
    lang = (await state.get_data()).get('lang', 'ru')
    phone = validate_text_input(message.text)
    if phone:
        await state.update_data(phone=phone)
        await message.answer("Telegram (@username):")
        await state.set_state(FormStates.waiting_for_telegram)
    else:
        await message.answer("Введите корректный телефон." if lang == 'ru' else "Enter valid phone.")


@router.message(FormStates.waiting_for_telegram)
async def process_telegram(message: Message, state: FSMContext):
    lang = (await state.get_data()).get('lang', 'ru')
    telegram = validate_text_input(message.text)
    if telegram:
        await state.update_data(telegram=telegram)
        await message.answer("Ваш город:" if lang == 'ru' else "Your city:")
        await state.set_state(FormStates.waiting_for_city)
    else:
        await message.answer("Введите корректный Telegram." if lang == 'ru' else "Enter valid Telegram.")


@router.message(FormStates.waiting_for_city)
async def process_city(message: Message, state: FSMContext):
    lang = (await state.get_data()).get('lang', 'ru')
    city = validate_text_input(message.text)
    if city:
        await state.update_data(city=city)
        await message.answer(
            "Instagram / основные социальные сети (укажите ссылки):"
            if lang == 'ru' else
            "Instagram / social media (provide links):"
        )
        await state.set_state(FormStates.waiting_for_social)
    else:
        await message.answer("Введите корректный город." if lang == 'ru' else "Enter valid city.")


# ==========================
# 🧩 Блок 2: Профессиональная экспертиза
# ==========================
@router.message(FormStates.waiting_for_social)
async def process_social(message: Message, state: FSMContext):
    lang = (await state.get_data()).get('lang', 'ru')
    social = validate_text_input(message.text)
    if social:
        await state.update_data(social=social)
        text = (
            "📚 БЛОК 2: ПРОФЕССИОНАЛЬНАЯ ЭКСПЕРТИЗА\n\nВыберите основное направление деятельности (можно несколько):"
            if lang == 'ru' else
            "📚 BLOCK 2: PROFESSIONAL EXPERTISE\n\nSelect main direction (multiple choice):"
        )
        keyboard = get_main_direction_keyboard(lang, [])
        await message.answer(text, reply_markup=keyboard)
        await state.set_state(FormStates.waiting_for_main_direction)
    else:
        await message.answer("Введите Instagram или соцсети." if lang == 'ru' else "Enter Instagram or social media.")


@router.callback_query(FormStates.waiting_for_main_direction, F.data.startswith("main_direction:"))
async def process_main_direction_callback(callback: CallbackQuery, state: FSMContext):
    lang = (await state.get_data()).get('lang', 'ru')
    value = callback.data.split(":")[1]
    data = await state.get_data()
    selected = data.get('main_direction', [])

    if value == "done":
        if not selected:
            await callback.answer("Выберите хотя бы один вариант!" if lang == 'ru' else "Select at least one option!", show_alert=True)
            return
        if "other" in selected:
            await callback.message.edit_text("Укажите другое направление:" if lang == 'ru' else "Specify other direction:")
            await state.set_state(FormStates.waiting_for_main_direction_other)
        else:
            text = "Дополнительные методы и инструменты в работе (можно несколько):" if lang == 'ru' else "Additional methods and tools (multiple choice):"
            keyboard = get_methods_keyboard(lang, [])
            await callback.message.edit_text(text, reply_markup=keyboard)
            await state.set_state(FormStates.waiting_for_additional_methods)
    else:
        if value in selected:
            selected.remove(value)
        else:
            selected.append(value)
        await state.update_data(main_direction=selected)
        keyboard = get_main_direction_keyboard(lang, selected)
        await callback.message.edit_reply_markup(reply_markup=keyboard)
    await callback.answer()


@router.message(FormStates.waiting_for_main_direction_other)
async def process_main_direction_other(message: Message, state: FSMContext):
    lang = (await state.get_data()).get('lang', 'ru')
    text_value = validate_text_input(message.text)
    data = await state.get_data()
    selected = data.get("main_direction", [])
    if text_value:
        selected.append(text_value)
    await state.update_data(main_direction=selected)
    text = "Дополнительные методы и инструменты в работе (можно несколько):" if lang == 'ru' else "Additional methods and tools (multiple choice):"
    keyboard = get_methods_keyboard(lang, [])
    await message.answer(text, reply_markup=keyboard)
    await state.set_state(FormStates.waiting_for_additional_methods)


@router.callback_query(FormStates.waiting_for_additional_methods, F.data.startswith("additional_methods:"))
async def process_additional_methods_callback(callback: CallbackQuery, state: FSMContext):
    lang = (await state.get_data()).get('lang', 'ru')
    value = callback.data.split(":")[1]
    data = await state.get_data()
    selected = data.get('additional_methods', [])

    if value == "done":
        text = "Базовое образование:" if lang == 'ru' else "Basic education:"
        keyboard = get_education_keyboard(lang)
        await callback.message.edit_text(text, reply_markup=keyboard)
        await state.set_state(FormStates.waiting_for_education)
    else:
        if value in selected:
            selected.remove(value)
        else:
            selected.append(value)
        await state.update_data(additional_methods=selected)
        keyboard = get_methods_keyboard(lang, selected)
        await callback.message.edit_reply_markup(reply_markup=keyboard)
    await callback.answer()


# ==========================
# 🎓 Блок 3: Формат и практика
# ==========================
@router.callback_query(FormStates.waiting_for_education, F.data.startswith("education:"))
async def process_education_callback(callback: CallbackQuery, state: FSMContext):
    lang = (await state.get_data()).get('lang', 'ru')
    value = callback.data.split(":")[1]
    await state.update_data(education=value)
    text = "Стаж работы в профессии:" if lang == 'ru' else "Work experience:"
    keyboard = get_experience_keyboard(lang)
    await callback.message.edit_text(text, reply_markup=keyboard)
    await state.set_state(FormStates.waiting_for_experience)
    await callback.answer()


@router.callback_query(FormStates.waiting_for_experience, F.data.startswith("experience:"))
async def process_experience_callback(callback: CallbackQuery, state: FSMContext):
    lang = (await state.get_data()).get('lang', 'ru')
    value = callback.data.split(":")[1]
    await state.update_data(experience=value)
    text = "💼 БЛОК 3: ФОРМАТ И ОБЪЕМ ПРАКТИКИ\n\nФормат работы (можно несколько):" if lang == 'ru' else "💼 BLOCK 3: WORK FORMAT\n\nWork format (multiple choice):"
    keyboard = get_work_format_keyboard(lang, [])
    await callback.message.edit_text(text, reply_markup=keyboard)
    await state.set_state(FormStates.waiting_for_format)
    await callback.answer()


@router.callback_query(FormStates.waiting_for_format, F.data.startswith("work_format:"))
async def process_work_format_callback(callback: CallbackQuery, state: FSMContext):
    lang = (await state.get_data()).get('lang', 'ru')
    value = callback.data.split(":")[1]
    data = await state.get_data()
    selected = data.get('work_formats', [])

    if value == "done":
        if not selected:
            await callback.answer("Выберите хотя бы один вариант!" if lang == 'ru' else "Select at least one option!", show_alert=True)
            return
        text = "Среднее количество клиентов в месяц:" if lang == 'ru' else "Average number of clients per month:"
        keyboard = get_clients_count_keyboard(lang)
        await callback.message.edit_text(text, reply_markup=keyboard)
        await state.set_state(FormStates.waiting_for_clients)
    else:
        if value in selected:
            selected.remove(value)
        else:
            selected.append(value)
        await state.update_data(work_formats=selected)
        keyboard = get_work_format_keyboard(lang, selected)
        await callback.message.edit_reply_markup(reply_markup=keyboard)
    await callback.answer()


@router.callback_query(FormStates.waiting_for_clients, F.data.startswith("clients_count:"))
async def process_clients_count_callback(callback: CallbackQuery, state: FSMContext):
    lang = (await state.get_data()).get('lang', 'ru')
    value = callback.data.split(":")[1]
    await state.update_data(clients_count=value)
    text = "Ваш средний чек:" if lang == 'ru' else "Your average check:"
    keyboard = get_average_check_keyboard(lang)
    await callback.message.edit_text(text, reply_markup=keyboard)
    await state.set_state(FormStates.waiting_for_price)
    await callback.answer()


@router.callback_query(FormStates.waiting_for_price, F.data.startswith("avg_check:"))
async def process_average_check_callback(callback: CallbackQuery, state: FSMContext):
    lang = (await state.get_data()).get('lang', 'ru')
    value = callback.data.split(":")[1]
    await state.update_data(average_check=value)
    text = "Какие задачи/запросы вы решаете для клиентов? (до 7 вариантов):" if lang == 'ru' else "What tasks/requests do you solve for clients? (up to 7):"
    keyboard = get_client_requests_keyboard(lang)
    await callback.message.edit_text(text, reply_markup=keyboard)
    await state.set_state(FormStates.waiting_for_requests)
    await callback.answer()


# ==========================
# 🎯 Блок 4: Целевая аудитория
# ==========================
@router.callback_query(FormStates.waiting_for_requests, F.data.startswith("client_requests:"))
async def process_client_requests_callback(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang = data.get('lang', 'ru')
    value = callback.data.split(":")[1]
    selected = data.get('client_requests', [])

    if value == "done":
        if not selected:
            await callback.answer("Выберите хотя бы один вариант!" if lang == 'ru' else "Select at least one option!", show_alert=True)
            return
        if len(selected) > 7:
            await callback.answer("Максимум 7 вариантов!" if lang == 'ru' else "Maximum 7 options!", show_alert=True)
            return
        text = (
            "👥 БЛОК 4: ЦЕЛЕВАЯ АУДИТОРИЯ И ПОЗИЦИОНИРОВАНИЕ\n\n"
            "Опишите вашу целевую аудиторию: пол, возраст, социальный статус, уровень дохода, география (1–2 предложения):"
            if lang == 'ru'
            else
            "👥 BLOCK 4: TARGET AUDIENCE\n\nDescribe your target audience: gender, age, social status, income, geography (1–2 sentences):"
        )
        await callback.message.edit_text(text)
        await state.set_state(FormStates.waiting_for_audience)
    else:
        if value in selected:
            selected.remove(value)
        else:
            if len(selected) >= 7:
                await callback.answer("Максимум 7 вариантов!" if lang == 'ru' else "Maximum 7 options!", show_alert=True)
                return
            selected.append(value)
        await state.update_data(client_requests=selected)
        keyboard = get_client_requests_keyboard(lang, selected)
        await callback.message.edit_reply_markup(reply_markup=keyboard)
    await callback.answer()


@router.message(FormStates.waiting_for_audience)
async def process_audience_description(message: Message, state: FSMContext):
    lang = (await state.get_data()).get('lang', 'ru')
    audience = validate_text_input(message.text)
    if audience:
        await state.update_data(audience=audience)
        text = (
            "Как вы себя позиционируете? В чем ваша уникальность? (1–3 предложения):"
            if lang == 'ru'
            else
            "How do you position yourself? What makes you unique? (1–3 sentences):"
        )
        await message.answer(text)
        await state.set_state(FormStates.waiting_for_positioning)
    else:
        await message.answer("Введите описание целевой аудитории." if lang == 'ru' else "Enter target audience description.")


# ==========================
# 📸 Фото и завершение анкеты
# ==========================
@router.message(FormStates.waiting_for_positioning)
async def process_positioning(message: Message, state: FSMContext):
    lang = (await state.get_data()).get('lang', 'ru')
    positioning = validate_text_input(message.text)
    if positioning:
        await state.update_data(positioning=positioning)
        text = (
            "📸 Отправьте фото профиля (или нажмите 'Пропустить' для резервного):"
            if lang == 'ru'
            else
            "📸 Send a profile photo (or press 'Skip' for default):"
        )
        await message.answer(text, reply_markup=get_photo_keyboard(lang))
        await state.set_state(FormStates.waiting_for_photo)
    else:
        await message.answer("Введите уникальность." if lang == 'ru' else "Enter uniqueness.")


@router.callback_query(F.data == 'send_photo')
async def send_photo_callback(callback: CallbackQuery, state: FSMContext):
    lang = (await state.get_data()).get('lang', 'ru')
    text = "📸 Отправьте фото профиля:" if lang == 'ru' else "📸 Send a profile photo:"
    await callback.message.edit_text(text, reply_markup=get_skip_keyboard(lang))
    await state.set_state(FormStates.waiting_for_photo)
    await callback.answer()


@router.callback_query(F.data == 'skip_photo')
async def skip_photo_callback(callback: CallbackQuery, state: FSMContext):
    lang = (await state.get_data()).get('lang', 'ru')
    await callback.message.edit_text("⌛ Отправляем анкету..." if lang == 'ru' else "⌛ Sending your form...")
    await state.update_data(photo_url=DEFAULT_PHOTO_URL)
    full_data = await state.get_data()
    full_data['telegram_id'] = callback.from_user.id
    print(f"🌍 Язык анкеты при отправке: {full_data.get('lang')}")
    await create_expert_record(full_data)
    await state.clear()
    keyboard = get_status_menu(lang)
    success_text = (
        "✅ Спасибо! Ваша анкета отправлена на проверку."
        if lang == 'ru' else
        "✅ Thank you! Your form has been submitted for review."
    )
    await callback.message.edit_text(success_text, reply_markup=keyboard)
    await callback.answer()


@router.message(FormStates.waiting_for_photo)
async def process_photo(message: Message, state: FSMContext):
    lang = (await state.get_data()).get('lang', 'ru')
    await message.answer("⌛ Отправляем анкету..." if lang == 'ru' else "⌛ Sending your form...")
    if message.photo:
        photo_url = await get_photo_url(message.photo, fallback_avatar=True)
        await state.update_data(photo_url=photo_url)
    else:
        await state.update_data(photo_url=DEFAULT_PHOTO_URL)
    full_data = await state.get_data()
    full_data['telegram_id'] = message.from_user.id
    print(f"🌍 Язык анкеты при отправке: {full_data.get('lang')}")
    await create_expert_record(full_data)
    await state.clear()
    keyboard = get_status_menu(lang)
    success_text = (
        "✅ Спасибо! Ваша анкета отправлена на проверку."
        if lang == 'ru' else
        "✅ Thank you! Your form has been submitted for review."
    )
    await message.answer(success_text, reply_markup=keyboard)


# ==========================
# 🚫 Отмена анкеты
# ==========================
@router.message(F.text == '/отмена')
async def cancel_form(message: Message, state: FSMContext):
    lang = (await state.get_data()).get('lang', 'ru')
    await state.clear()
    keyboard = get_main_menu(lang)
    await message.answer("Анкета отменена." if lang == 'ru' else "Form canceled.", reply_markup=keyboard)
