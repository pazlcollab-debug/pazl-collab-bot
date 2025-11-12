from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from colorama import Fore, init
from pyairtable.formulas import match

from states.form_states import FormStates
from services.airtable_api import create_expert_record, get_table
from services.utils import validate_text_input, get_photo_url
from config import DEFAULT_PHOTO_URL
from keyboards.main_menu import get_main_menu, get_status_menu, get_post_approval_menu  # ✅ добавлен новый импорт
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

init(autoreset=True)
router = Router()

# 🧠 Кэш для предотвращения повторной отправки
sent_records_cache = set()

# ==========================
# 🔁 Унификация статусов (RU/EN)
# ==========================
STATUS_ALIASES = {
    "🟢 Одобрено": "Approved",
    "🟢 Approved": "Approved",
    "🟡 На модерации": "Pending",
    "🟡 Pending": "Pending",
    "🔴 Отклонено": "Declined",
    "🔴 Declined": "Declined"
}

# ==========================
# ⚙️ Логирование шагов
# ==========================
def log_step(user_id, state, value):
    print(Fore.YELLOW + f"[{user_id}] → {state}: {value}")

# ==========================
# 📸 Клавиатуры для фото
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
    """Проверяет, есть ли у пользователя анкета, и форматирует дату красиво."""
    table = get_table()
    try:
        records = table.all(formula=match({"TelegramID": str(telegram_id)}))
        if not records:
            return None

        record = records[0]
        raw_date = record["fields"].get("Date", "—")

        # 🔹 Форматируем дату
        formatted_date = raw_date
        try:
            if "T" in raw_date:
                from datetime import datetime
                dt = datetime.fromisoformat(raw_date.replace("Z", "+00:00")).astimezone()
                formatted_date = dt.strftime("%d.%m.%Y в %H:%M")
        except Exception:
            pass

        return {
            "id": record["id"],
            "status": record["fields"].get("Status", "Pending"),
            "date": formatted_date
        }

    except Exception as e:
        print(f"⚠️ Ошибка при проверке анкеты: {e}")
        return None


# ==========================
# 🧩 Финализация анкеты
# ==========================
async def finalize_form(obj, state: FSMContext, lang: str, telegram_id: str, photo_url: str, is_callback: bool = False):
    """Завершает анкету и отправляет данные в Airtable"""
    await state.update_data(photo_url=photo_url)
    full_data = await state.get_data()
    full_data["telegram_id"] = telegram_id
    lang = full_data.get("lang", lang)

    print(Fore.CYAN + f"[{telegram_id}] 📨 Finalizing form ({lang})")
    print(Fore.BLUE + f"[{telegram_id}] 📦 Отправляем данные в Airtable...")

    try:
        await create_expert_record(full_data)
        print(Fore.GREEN + f"[{telegram_id}] ✅ Анкета успешно отправлена в Airtable")

        # ✅ Добавляем пользователя в кэш только после успешной записи
        sent_records_cache.add(str(telegram_id))

        # ✅ Финальное сообщение пользователю
        text = (
            "✅ Спасибо! Ваша анкета успешно отправлена на проверку.\n\n"
            "📊 Теперь вы можете проверить её статус, нажав кнопку ниже 👇"
            if lang == "ru"
            else
            "✅ Thank you! Your form has been submitted for review.\n\n"
            "📊 You can now check its status using the button below 👇"
        )

        await state.clear()
        keyboard = get_status_menu(lang)  # меню «Проверить статус анкеты»

        if is_callback:
            await obj.edit_text(text, reply_markup=keyboard)
        else:
            await obj.answer(text, reply_markup=keyboard)

    except Exception as e:
        print(Fore.RED + f"[{telegram_id}] ❌ Ошибка при отправке анкеты: {e}")
        error_text = (
            "❌ Ошибка при отправке анкеты, попробуйте позже."
            if lang == "ru"
            else
            "❌ Error submitting form, try later."
        )
        if is_callback:
            await obj.edit_text(error_text, reply_markup=get_main_menu(lang))
        else:
            await obj.answer(error_text, reply_markup=get_main_menu(lang))
        await state.clear()
# ==========================
# 📊 Проверка статуса анкеты
# ==========================
@router.message(F.text.in_(['📊 Проверить статус анкеты', '📊 Check form status']))
async def check_form_status(message: Message, state: FSMContext):
    lang = (await state.get_data()).get("lang", "ru")
    user_id = str(message.from_user.id)
    result = await check_existing_form(user_id)

    if not result:
        text = (
            "ℹ️ У вас пока нет анкеты.\n\nНажмите «🟡 Заполнить анкету», чтобы отправить первую."
            if lang == "ru"
            else "ℹ️ You don't have a form yet.\n\nPress \"🟡 Fill the form\" to submit your first one."
        )
        await message.answer(text, reply_markup=get_main_menu(lang))
        return

    raw_status = result["status"]
    status = STATUS_ALIASES.get(raw_status, raw_status)
    date = result["date"]

    # 🟢 Приводим статус к виду с эмодзи и переводом
    status_display = {
        "Pending": "🟡 На модерации" if lang == "ru" else "🟡 Pending review",
        "Approved": "🟢 Одобрено" if lang == "ru" else "🟢 Approved",
        "Declined": "🔴 Отклонено" if lang == "ru" else "🔴 Declined"
    }.get(status, status)

    # 💬 Если анкета одобрена — поздравляем и показываем меню после одобрения
    if status == "Approved":
        text = (
            f"🎉 Отличные новости!\n\n✅ Ваша анкета была одобрена {date}.\n\n"
            "Теперь вы можете пользоваться всеми функциями PAZL Collab 🙌"
            if lang == "ru"
            else
            f"🎉 Great news!\n\n✅ Your form was approved on {date}.\n\n"
            "You can now access all PAZL Collab features 🙌"
        )

        await message.answer(text, reply_markup=get_post_approval_menu(lang))  # ✅ сообщение и меню

        # 🟢 Отмечаем в Airtable, что пользователь уведомлён вручную
        try:
            from services.airtable_api import get_table
            from pyairtable.formulas import match
            table = get_table()
            records = table.all(formula=match({"TelegramID": str(message.from_user.id)}))
            if records:
                record_id = records[0]["id"]
                table.update(record_id, {"Notified": True})
                print(f"✅ [Manual Notify] Пользователь {message.from_user.id} отмечен как уведомлён (ручная проверка).")
        except Exception as e:
            print(f"⚠️ Ошибка при обновлении Notified вручную ({message.from_user.id}): {e}")

        return

    # 💬 Иначе — просто показываем статус
    if lang == "ru":
        text = (
            f"✅ Вы отправили анкету {date}.\n"
            f"📋 Текущий статус: *{status_display}*\n\n"
            "Чтобы проверить актуальное состояние — нажмите «📊 Проверить статус анкеты»."
        )
    else:
        text = (
            f"✅ You submitted your form on {date}.\n"
            f"📋 Current status: *{status_display}*\n\n"
            "To check the latest update — press \"📊 Check form status\"."
        )

    await message.answer(text, reply_markup=get_status_menu(lang), parse_mode="Markdown")


# ==========================
# 🟡 Старт анкеты
# ==========================
@router.message(F.text.in_(['🟡 Заполнить анкету', '🟡 Fill the form']))
async def start_form(message: Message, state: FSMContext):
    lang = (await state.get_data()).get("lang", "ru")
    user_id = str(message.from_user.id)

    # 🧹 Сбрасываем возможную старую запись в кэше, если анкеты нет в Airtable
    if user_id in sent_records_cache:
        existing_check = await check_existing_form(user_id)
        if not existing_check:
            sent_records_cache.discard(user_id)
            print(Fore.CYAN + f"[{user_id}] ♻️ Сброшен из кэша — анкеты в Airtable нет")

    print(Fore.BLUE + f"[{user_id}] ▶ start_form ({lang})")

    # 🔍 Проверяем наличие анкеты в Airtable
    existing = await check_existing_form(user_id)

    if existing:
        raw_status = existing["status"]
        status = STATUS_ALIASES.get(raw_status, raw_status)
        date = existing["date"]

        text = (
            f"✅ Вы уже отправляли анкету {date}.\n📋 Текущий статус: *{status}*\n\n"
            f"Чтобы проверить актуальное состояние — нажмите «📊 Проверить статус анкеты»."
            if lang == "ru"
            else
            f"✅ You already submitted your form on {date}.\n📋 Current status: *{status}*\n\n"
            f"To check the latest status — press \"📊 Check form status\"."
        )
        await message.answer(text, reply_markup=get_status_menu(lang), parse_mode="Markdown")
        return

    # 🚀 Начинаем заполнение новой анкеты
    await state.update_data(
        lang=lang,
        main_direction=[], additional_methods=[], work_formats=[], client_requests=[],
        products=[], client_sources=[], collab_formats=[], collab_partners=[],
        collab_offer=[], motivation=[]
    )

    await message.answer(
        "📋 БЛОК 1: ЛИЧНЫЕ ДАННЫЕ И КОНТАКТЫ\n\nВведите ФИО:" if lang == "ru"
        else "📋 BLOCK 1: PERSONAL DATA\n\nEnter full name:"
    )
    await state.set_state(FormStates.waiting_for_name)
# ==========================
# 👤 Блок 1: Личные данные
# ==========================
@router.message(FormStates.waiting_for_name)
async def process_name(message: Message, state: FSMContext):
    user_id = str(message.from_user.id)
    lang = (await state.get_data()).get("lang", "ru")
    log_step(user_id, "waiting_for_name", message.text)

    name = validate_text_input(message.text)
    if name:
        await state.update_data(name=name)
        await message.answer("Телефон / WhatsApp:" if lang == "ru" else "Phone / WhatsApp:")
        await state.set_state(FormStates.waiting_for_phone)
    else:
        await message.answer("Введите корректное имя." if lang == "ru" else "Enter valid name.")


@router.message(FormStates.waiting_for_phone)
async def process_phone(message: Message, state: FSMContext):
    user_id = str(message.from_user.id)
    lang = (await state.get_data()).get("lang", "ru")
    log_step(user_id, "waiting_for_phone", message.text)

    phone = validate_text_input(message.text)
    if phone:
        await state.update_data(phone=phone)
        await message.answer("Telegram (@username):")
        await state.set_state(FormStates.waiting_for_telegram)
    else:
        await message.answer("Введите корректный телефон." if lang == "ru" else "Enter valid phone.")


@router.message(FormStates.waiting_for_telegram)
async def process_telegram(message: Message, state: FSMContext):
    user_id = str(message.from_user.id)
    lang = (await state.get_data()).get("lang", "ru")
    log_step(user_id, "waiting_for_telegram", message.text)

    telegram = validate_text_input(message.text)
    if telegram:
        await state.update_data(telegram=telegram)
        await message.answer("Ваш город:" if lang == "ru" else "Your city:")
        await state.set_state(FormStates.waiting_for_city)
    else:
        await message.answer("Введите корректный Telegram." if lang == "ru" else "Enter valid Telegram.")


@router.message(FormStates.waiting_for_city)
async def process_city(message: Message, state: FSMContext):
    user_id = str(message.from_user.id)
    lang = (await state.get_data()).get("lang", "ru")
    log_step(user_id, "waiting_for_city", message.text)

    city = validate_text_input(message.text)
    if city:
        await state.update_data(city=city)
        await message.answer(
            "Instagram / основные социальные сети (укажите ссылки):"
            if lang == "ru" else
            "Instagram / social media (provide links):"
        )
        await state.set_state(FormStates.waiting_for_social)
    else:
        await message.answer("Введите корректный город." if lang == "ru" else "Enter valid city.")
# ==========================
# 🎯 Блок 2: Профессиональная экспертиза
# ==========================
@router.message(FormStates.waiting_for_social)
async def process_social(message: Message, state: FSMContext):
    user_id = str(message.from_user.id)
    lang = (await state.get_data()).get("lang", "ru")
    log_step(user_id, "waiting_for_social", message.text)

    social = validate_text_input(message.text)
    if social:
        await state.update_data(social=social)
        text = (
            "📚 БЛОК 2: ПРОФЕССИОНАЛЬНАЯ ЭКСПЕРТИЗА\n\nВыберите основное направление деятельности (можно несколько):"
            if lang == "ru" else
            "📚 BLOCK 2: PROFESSIONAL EXPERTISE\n\nSelect main direction (multiple choice):"
        )
        keyboard = get_main_direction_keyboard(lang, [])
        await message.answer(text, reply_markup=keyboard)
        await state.set_state(FormStates.waiting_for_main_direction)
    else:
        await message.answer("Введите корректные соцсети." if lang == "ru" else "Enter valid social media.")


@router.callback_query(FormStates.waiting_for_main_direction, F.data.startswith("main_direction:"))
async def process_main_direction_callback(callback: CallbackQuery, state: FSMContext):
    user_id = str(callback.from_user.id)
    lang = (await state.get_data()).get("lang", "ru")
    value = callback.data.split(":")[1]
    log_step(user_id, "waiting_for_main_direction", value)

    data = await state.get_data()
    selected = data.get("main_direction", [])

    if value == "done":
        if not selected:
            await callback.answer("Выберите хотя бы один вариант!" if lang == "ru" else "Select at least one option!", show_alert=True)
            return
        if "other" in selected:
            await callback.message.edit_text("Укажите другое направление:" if lang == "ru" else "Specify other direction:")
            await state.set_state(FormStates.waiting_for_main_direction_other)
            return
        else:
            text = (
                "Дополнительные методы и инструменты в работе (можно несколько):"
                if lang == "ru" else
                "Additional methods and tools (multiple choice):"
            )
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
    user_id = str(message.from_user.id)
    lang = (await state.get_data()).get("lang", "ru")
    log_step(user_id, "waiting_for_main_direction_other", message.text)

    other_value = validate_text_input(message.text)
    if other_value:
        data = await state.get_data()
        selected = data.get("main_direction", [])
        if "other" in selected:
            selected.remove("other")
        selected.append(other_value)
        await state.update_data(main_direction=selected)

        text = (
            "Дополнительные методы и инструменты в работе (можно несколько):"
            if lang == "ru" else
            "Additional methods and tools (multiple choice):"
        )
        keyboard = get_methods_keyboard(lang, [])
        await message.answer(text, reply_markup=keyboard)
        await state.set_state(FormStates.waiting_for_additional_methods)
    else:
        await message.answer("Введите корректное значение." if lang == "ru" else "Enter valid text.")


# ==========================
# 🧩 Методы, образование, опыт
# ==========================
@router.callback_query(FormStates.waiting_for_additional_methods, F.data.startswith("additional_methods:"))
async def process_additional_methods_callback(callback: CallbackQuery, state: FSMContext):
    user_id = str(callback.from_user.id)
    lang = (await state.get_data()).get("lang", "ru")
    value = callback.data.split(":")[1]
    log_step(user_id, "waiting_for_additional_methods", value)

    data = await state.get_data()
    selected = data.get("additional_methods", [])

    if value == "done":
        text = "Базовое образование:" if lang == "ru" else "Basic education:"
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
# 💼 Блок 3: Формат и практика
# ==========================
@router.callback_query(FormStates.waiting_for_education, F.data.startswith("education:"))
async def process_education_callback(callback: CallbackQuery, state: FSMContext):
    user_id = str(callback.from_user.id)
    lang = (await state.get_data()).get("lang", "ru")
    value = callback.data.split(":")[1]
    log_step(user_id, "waiting_for_education", value)

    await state.update_data(education=value)
    text = "Стаж работы в профессии:" if lang == "ru" else "Work experience:"
    keyboard = get_experience_keyboard(lang)
    await callback.message.edit_text(text, reply_markup=keyboard)
    await state.set_state(FormStates.waiting_for_experience)
    await callback.answer()


@router.callback_query(FormStates.waiting_for_experience, F.data.startswith("experience:"))
async def process_experience_callback(callback: CallbackQuery, state: FSMContext):
    user_id = str(callback.from_user.id)
    lang = (await state.get_data()).get("lang", "ru")
    value = callback.data.split(":")[1]
    log_step(user_id, "waiting_for_experience", value)

    await state.update_data(experience=value)
    text = (
        "💼 БЛОК 3: ФОРМАТ И ОБЪЕМ ПРАКТИКИ\n\nФормат работы (можно несколько):"
        if lang == "ru" else
        "💼 BLOCK 3: WORK FORMAT\n\nWork format (multiple choice):"
    )
    keyboard = get_work_format_keyboard(lang, [])
    await callback.message.edit_text(text, reply_markup=keyboard)
    await state.set_state(FormStates.waiting_for_format)
    await callback.answer()


@router.callback_query(FormStates.waiting_for_format, F.data.startswith("work_format:"))
async def process_work_format_callback(callback: CallbackQuery, state: FSMContext):
    user_id = str(callback.from_user.id)
    lang = (await state.get_data()).get("lang", "ru")
    value = callback.data.split(":")[1]
    log_step(user_id, "waiting_for_format", value)

    data = await state.get_data()
    selected = data.get("work_formats", [])

    if value == "done":
        if not selected:
            await callback.answer("Выберите хотя бы один вариант!" if lang == "ru" else "Select at least one option!", show_alert=True)
            return
        text = "Среднее количество клиентов в месяц:" if lang == "ru" else "Average number of clients per month:"
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
    user_id = str(callback.from_user.id)
    lang = (await state.get_data()).get("lang", "ru")
    value = callback.data.split(":")[1]
    log_step(user_id, "waiting_for_clients", value)

    await state.update_data(clients_count=value)
    text = "Ваш средний чек:" if lang == "ru" else "Your average check:"
    keyboard = get_average_check_keyboard(lang)
    await callback.message.edit_text(text, reply_markup=keyboard)
    await state.set_state(FormStates.waiting_for_price)
    await callback.answer()


@router.callback_query(FormStates.waiting_for_price, F.data.startswith("avg_check:"))
async def process_average_check_callback(callback: CallbackQuery, state: FSMContext):
    user_id = str(callback.from_user.id)
    lang = (await state.get_data()).get("lang", "ru")
    value = callback.data.split(":")[1]
    log_step(user_id, "waiting_for_price", value)

    await state.update_data(average_check=value)
    text = (
        "Какие задачи/запросы вы решаете для клиентов? (до 7 вариантов):"
        if lang == "ru" else
        "What tasks/requests do you solve for clients? (up to 7):"
    )
    keyboard = get_client_requests_keyboard(lang)
    await callback.message.edit_text(text, reply_markup=keyboard)
    await state.set_state(FormStates.waiting_for_requests)
    await callback.answer()
# ==========================
# 👥 Блок 4: Аудитория и позиционирование
# ==========================
@router.callback_query(FormStates.waiting_for_requests, F.data.startswith("client_requests:"))
async def process_client_requests_callback(callback: CallbackQuery, state: FSMContext):
    user_id = str(callback.from_user.id)
    lang = (await state.get_data()).get("lang", "ru")
    value = callback.data.split(":")[1]
    log_step(user_id, "waiting_for_requests", value)

    data = await state.get_data()
    selected = data.get("client_requests", [])

    if value == "done":
        if not selected:
            await callback.answer("Выберите хотя бы один вариант!" if lang == "ru" else "Select at least one option!", show_alert=True)
            return
        if len(selected) > 7:
            await callback.answer("Максимум 7 вариантов!" if lang == "ru" else "Maximum 7 options!", show_alert=True)
            return

        text = (
            "👥 БЛОК 4: ЦЕЛЕВАЯ АУДИТОРИЯ\n\nОпишите вашу целевую аудиторию: пол, возраст, социальный статус, доход, география (1–2 предложения):"
            if lang == "ru"
            else "👥 BLOCK 4: TARGET AUDIENCE\n\nDescribe your target audience: gender, age, status, income, geography (1–2 sentences):"
        )
        await callback.message.edit_text(text)
        await state.set_state(FormStates.waiting_for_audience)
    else:
        if value in selected:
            selected.remove(value)
        else:
            if len(selected) >= 7:
                await callback.answer("Максимум 7 вариантов!" if lang == "ru" else "Maximum 7 options!", show_alert=True)
                return
            selected.append(value)
        await state.update_data(client_requests=selected)
        keyboard = get_client_requests_keyboard(lang, selected)
        await callback.message.edit_reply_markup(reply_markup=keyboard)
    await callback.answer()


@router.message(FormStates.waiting_for_audience)
async def process_audience_description(message: Message, state: FSMContext):
    user_id = str(message.from_user.id)
    lang = (await state.get_data()).get("lang", "ru")
    log_step(user_id, "waiting_for_audience", message.text)

    audience = validate_text_input(message.text)
    if audience:
        await state.update_data(audience=audience)
        text = (
            "Как вы себя позиционируете? В чем ваша уникальность? (1–3 предложения):"
            if lang == "ru"
            else "How do you position yourself? What makes you unique? (1–3 sentences):"
        )
        await message.answer(text)
        await state.set_state(FormStates.waiting_for_positioning)
    else:
        await message.answer("Введите описание аудитории." if lang == "ru" else "Enter audience description.")


@router.message(FormStates.waiting_for_positioning)
async def process_positioning(message: Message, state: FSMContext):
    user_id = str(message.from_user.id)
    lang = (await state.get_data()).get("lang", "ru")
    log_step(user_id, "waiting_for_positioning", message.text)

    positioning = validate_text_input(message.text)
    if positioning:
        await state.update_data(positioning=positioning)
        text = (
            "📸 Отправьте фото профиля (или нажмите 'Пропустить' для резервного изображения):"
            if lang == "ru"
            else "📸 Send a profile photo (or press 'Skip' for default image):"
        )
        await message.answer(text, reply_markup=get_photo_keyboard(lang))
        await state.set_state(FormStates.waiting_for_photo)
    else:
        await message.answer("Введите корректное описание уникальности." if lang == "ru" else "Enter valid uniqueness.")


# ==========================
# 📸 Фото и завершение анкеты
# ==========================
@router.callback_query(F.data == "send_photo")
async def send_photo_callback(callback: CallbackQuery, state: FSMContext):
    lang = (await state.get_data()).get("lang", "ru")
    await callback.message.edit_text(
        "📸 Отправьте фото профиля:" if lang == "ru" else "📸 Send a profile photo:",
        reply_markup=get_skip_keyboard(lang)
    )
    await state.set_state(FormStates.waiting_for_photo)
    await callback.answer()


@router.callback_query(F.data == "skip_photo")
async def skip_photo_callback(callback: CallbackQuery, state: FSMContext):
    lang = (await state.get_data()).get("lang", "ru")
    telegram_id = str(callback.from_user.id)

    existing = await check_existing_form(telegram_id)
    if existing:
        print(Fore.YELLOW + f"[{telegram_id}] ⚠️ Повторная отправка анкеты предотвращена (есть в Airtable)")
        await callback.message.answer(
            "⚠️ Извините, в базе данных ваша анкета уже зафиксирована.\n✅ Ожидайте модерации."
            if lang == "ru"
            else "⚠️ Your form has already been recorded.\n✅ Please wait for moderation."
        )
        await state.clear()
        return

    print(Fore.CYAN + f"[{telegram_id}] 📸 skip_photo (default image)")
    await callback.message.edit_text(
        "⌛ Отправляем анкету..." if lang == "ru" else "⌛ Sending your form..."
    )

    await finalize_form(callback.message, state, lang, telegram_id, DEFAULT_PHOTO_URL, is_callback=True)
    await callback.answer()


@router.message(FormStates.waiting_for_photo)
async def process_photo(message: Message, state: FSMContext):
    lang = (await state.get_data()).get("lang", "ru")
    telegram_id = str(message.from_user.id)
    print(Fore.CYAN + f"[{telegram_id}] 📷 Получено фото от пользователя")

    existing = await check_existing_form(telegram_id)
    if existing:
        print(Fore.YELLOW + f"[{telegram_id}] ⚠️ Повторная отправка анкеты предотвращена (есть в Airtable)")
        await message.answer(
            "⚠️ Извините, в базе данных ваша анкета уже зафиксирована.\n✅ Ожидайте модерации."
            if lang == "ru"
            else "⚠️ Your form has already been recorded.\n✅ Please wait for moderation."
        )
        await state.clear()
        return

    await message.answer("⌛ Отправляем анкету..." if lang == "ru" else "⌛ Sending your form...")

    if message.photo:
        photo_url = await get_photo_url(message.photo, fallback_avatar=True)
    else:
        photo_url = DEFAULT_PHOTO_URL

    await finalize_form(message, state, lang, telegram_id, photo_url)
    print(Fore.MAGENTA + f"[{telegram_id}] ✅ finalize_form успешно вызван")


# ==========================
# 🚫 Отмена анкеты
# ==========================
@router.message(F.text == "/отмена")
async def cancel_form(message: Message, state: FSMContext):
    user_id = str(message.from_user.id)
    lang = (await state.get_data()).get("lang", "ru")
    print(Fore.MAGENTA + f"[{user_id}] ❎ Отмена анкеты пользователем")

    await state.clear()
    keyboard = get_main_menu(lang)
    await message.answer("Анкета отменена." if lang == "ru" else "Form canceled.", reply_markup=keyboard)
