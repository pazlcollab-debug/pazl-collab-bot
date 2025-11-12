from aiogram.fsm.state import State, StatesGroup

class FormStates(StatesGroup):
    # Блок 1: Личные данные
    waiting_for_name = State()
    waiting_for_phone = State()
    waiting_for_telegram = State()
    waiting_for_city = State()
    waiting_for_social = State()
    
    # Блок 2: Профессиональная экспертиза
    waiting_for_expertise = State()
    waiting_for_main_direction = State()
    waiting_for_main_direction_other = State()     
    waiting_for_additional_methods = State()
    waiting_for_additional_methods_other = State() 
    waiting_for_education = State()
    waiting_for_education_other = State()          
    waiting_for_experience = State()

    # Блок 3: Формат и объем практики
    waiting_for_format = State()
    waiting_for_clients = State()
    waiting_for_price = State()
    waiting_for_requests = State()
    waiting_for_requests_other = State()           
    
    # Блок 4: Целевая аудитория
    waiting_for_audience = State()
    waiting_for_gender = State()
    waiting_for_age = State()
    waiting_for_status = State()
    waiting_for_income = State()
    waiting_for_geography = State()
    waiting_for_positioning = State()
    
    # Блок 5: Бизнес-модель
    waiting_for_products = State()
    waiting_for_client_sources = State()
    waiting_for_audience_size = State()
    waiting_for_audience_activity = State()
    
    # Блок 6: Опыт коллабораций
    waiting_for_collab_formats = State()
    waiting_for_collab_partners = State()
    waiting_for_collab_offer = State()
    
    # Блок 7: Мотивация
    waiting_for_motivation = State()
    waiting_for_result = State()
    waiting_for_investment = State()
    waiting_for_agreement = State()
    
    # Фото
    waiting_for_photo = State()
