from aiogram.fsm.state import State, StatesGroup

class FormStates(StatesGroup):
    waiting_for_name = State()  # ФИО
    waiting_for_phone = State()  # Телефон / WhatsApp
    waiting_for_telegram = State()  # Telegram
    waiting_for_city = State()  # Город
    waiting_for_social = State()  # Instagram / соцсети
    waiting_for_expertise = State()  # Основное направление
    waiting_for_education = State()  # Базовое образование
    waiting_for_experience = State()  # Стаж работы
    waiting_for_format = State()  # Форматы работы
    waiting_for_clients = State()  # Количество клиентов
    waiting_for_price = State()  # Средний чек
    waiting_for_requests = State()  # Основные запросы
    waiting_for_audience = State()  # Пол/возраст/статус/доход/география
    waiting_for_positioning = State()  # Уникальность (1–3 предложения)
    waiting_for_photo = State()  # Фото (Шаг 3 ТЗ)
