from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def create_multiselect_keyboard(options: list, callback_prefix: str, selected: list = None, show_done: bool = True):
    if selected is None:
        selected = []
    keyboard = []
    for text, value in options:
        display_text = f"✅ {text}" if value in selected else text
        callback_data = f"{callback_prefix}:{value}"
        keyboard.append([InlineKeyboardButton(text=display_text, callback_data=callback_data)])
    if show_done:
        keyboard.append([InlineKeyboardButton(text="✅ Готово", callback_data=f"{callback_prefix}:done")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# Основное направление, RU/EN
MAIN_DIRECTION_OPTIONS_RU = [
    ("Коучинг (лайф-коучинг)", "coaching_life"),
    ("Коучинг (бизнес-коучинг)", "coaching_business"),
    ("Коучинг (карьерный)", "coaching_career"),
    ("Психология (клиническая практика)", "psych_clinical"),
    ("Психология (консультирование)", "psych_consulting"),
    ("Психотерапия (КПТ)", "therapy_cbt"),
    ("Психотерапия (гештальт-терапия)", "therapy_gestalt"),
    ("Психотерапия (психоанализ)", "therapy_psychoanalysis"),
    ("Психотерапия (схема-терапия)", "therapy_schema"),
    ("Телесно-ориентированная терапия", "body_therapy"),
    ("Работа с подсознанием (гипнотерапия)", "hypnotherapy"),
    ("Работа с подсознанием (регрессивная терапия)", "regression_therapy"),
    ("Астрология", "astrology"),
    ("Энергетические практики", "energy_practices"),
    ("Нутрициология", "nutrition"),
    ("Йога-терапия", "yoga_therapy"),
    ("Другое", "other"),
]
MAIN_DIRECTION_OPTIONS_EN = [
    ("Coaching (life coaching)", "coaching_life"),
    ("Coaching (business coaching)", "coaching_business"),
    ("Coaching (career)", "coaching_career"),
    ("Psychology (clinical practice)", "psych_clinical"),
    ("Psychology (consulting)", "psych_consulting"),
    ("Psychotherapy (CBT)", "therapy_cbt"),
    ("Psychotherapy (gestalt therapy)", "therapy_gestalt"),
    ("Psychotherapy (psychoanalysis)", "therapy_psychoanalysis"),
    ("Psychotherapy (schema therapy)", "therapy_schema"),
    ("Body-oriented therapy", "body_therapy"),
    ("Subconscious work (hypnotherapy)", "hypnotherapy"),
    ("Subconscious work (regression therapy)", "regression_therapy"),
    ("Astrology", "astrology"),
    ("Energy practices", "energy_practices"),
    ("Nutrition", "nutrition"),
    ("Yoga therapy", "yoga_therapy"),
    ("Other", "other"),
]

ADDITIONAL_METHODS_OPTIONS_RU = [
    ("НЛП", "nlp"),
    ("Системные расстановки", "constellations"),
    ("Арт-терапия", "art_therapy"),
    ("МАК", "mac"),
    ("Медитативные практики", "meditation"),
    ("Дыхательные практики", "breathing"),
    ("Работа с родовыми сценариями", "ancestral_work"),
    ("Human Design", "human_design"),
    ("Другое", "other"),
]
ADDITIONAL_METHODS_OPTIONS_EN = [
    ("NLP", "nlp"),
    ("Systemic constellations", "constellations"),
    ("Art therapy", "art_therapy"),
    ("MAC (Metaphorical Associative Cards)", "mac"),
    ("Meditative practices", "meditation"),
    ("Breathing practices", "breathing"),
    ("Ancestral scenario work", "ancestral_work"),
    ("Human Design", "human_design"),
    ("Other", "other"),
]

EDUCATION_OPTIONS_RU = [
    ("Высшее психологическое", "psych_higher"),
    ("Высшее медицинское", "medical_higher"),
    ("Высшее педагогическое", "pedagogical_higher"),
    ("Высшее другое", "other_higher"),
    ("Среднее специальное", "secondary"),
    ("Нет профильного образования", "none"),
]
EDUCATION_OPTIONS_EN = [
    ("Higher psychological", "psych_higher"),
    ("Higher medical", "medical_higher"),
    ("Higher pedagogical", "pedagogical_higher"),
    ("Higher other", "other_higher"),
    ("Secondary specialized", "secondary"),
    ("No specialized education", "none"),
]

EXPERIENCE_OPTIONS_RU = [
    ("Менее 1 года", "less_1"),
    ("1-2 года", "1_2"),
    ("2-3 года", "2_3"),
    ("3-5 лет", "3_5"),
    ("5-7 лет", "5_7"),
    ("7-10 лет", "7_10"),
    ("Более 10 лет", "more_10"),
]
EXPERIENCE_OPTIONS_EN = [
    ("Less than 1 year", "less_1"),
    ("1-2 years", "1_2"),
    ("2-3 years", "2_3"),
    ("3-5 years", "3_5"),
    ("5-7 years", "5_7"),
    ("7-10 years", "7_10"),
    ("More than 10 years", "more_10"),
]

WORK_FORMAT_OPTIONS_RU = [
    ("Индивидуальные сессии (онлайн)", "individual_online"),
    ("Индивидуальные сессии (офлайн)", "individual_offline"),
    ("Групповые программы (онлайн)", "group_online"),
    ("Групповые программы (офлайн)", "group_offline"),
    ("Марафоны/челленджи", "marathons"),
    ("Интенсивы/ретриты", "intensives"),
    ("Обучающие курсы", "courses"),
    ("Вебинары/мастер-классы", "webinars"),
]
WORK_FORMAT_OPTIONS_EN = [
    ("Individual sessions (online)", "individual_online"),
    ("Individual sessions (offline)", "individual_offline"),
    ("Group programs (online)", "group_online"),
    ("Group programs (offline)", "group_offline"),
    ("Marathons/challenges", "marathons"),
    ("Intensives/retreats", "intensives"),
    ("Training courses", "courses"),
    ("Webinars/master classes", "webinars"),
]

CLIENTS_COUNT_OPTIONS_RU = [
    ("1-5 клиентов", "1_5"),
    ("5-10 клиентов", "5_10"),
    ("10-15 клиентов", "10_15"),
    ("15-20 клиентов", "15_20"),
    ("20-30 клиентов", "20_30"),
    ("Более 30 клиентов", "more_30"),
]
CLIENTS_COUNT_OPTIONS_EN = [
    ("1-5 clients", "1_5"),
    ("5-10 clients", "5_10"),
    ("10-15 clients", "10_15"),
    ("15-20 clients", "15_20"),
    ("20-30 clients", "20_30"),
    ("More than 30 clients", "more_30"),
]

AVERAGE_CHECK_OPTIONS_RU = [
    ("до 10 тыс рублей", "under_10k"),
    ("10-30 тыс", "10_30k"),
    ("30-50 тыс", "30_50k"),
    ("50-100 тыс", "50_100k"),
    ("от 100 тыс", "over_100k"),
]
AVERAGE_CHECK_OPTIONS_EN = [
    ("up to 10k rubles", "under_10k"),
    ("10-30k rubles", "10_30k"),
    ("30-50k rubles", "30_50k"),
    ("50-100k rubles", "50_100k"),
    ("over 100k rubles", "over_100k"),
]

CLIENT_REQUESTS_OPTIONS_RU = [
    ("Тревожность, панические атаки, страхи", "anxiety"),
    ("Депрессия, апатия, потеря смысла", "depression"),
    ("Самооценка и уверенность", "self_esteem"),
    ("Отношения с партнером", "partner_relations"),
    ("Поиск партнера, одиночество", "partner_search"),
    ("Расставание, развод", "breakup"),
    ("Детско-родительские отношения", "parent_child"),
    ("Отношения с родителями", "parent_relations"),
    ("Профессиональное выгорание", "burnout"),
    ("Поиск предназначения", "purpose_search"),
    ("Карьерные вопросы", "career"),
    ("Финансовые блоки", "financial_blocks"),
    ("Целеполагание", "goal_setting"),
    ("Прокрастинация, мотивация", "procrastination"),
    ("Женские темы", "women_topics"),
    ("Мужские темы", "men_topics"),
    ("Психосоматика", "psychosomatics"),
    ("Работа с травмой (ПТСР)", "trauma"),
    ("Работа с внутренними частями", "internal_parts"),
    ("Духовное развитие", "spiritual_development"),
    ("Другое", "other"),
]
CLIENT_REQUESTS_OPTIONS_EN = [
    ("Anxiety, panic attacks, fears", "anxiety"),
    ("Depression, apathy, loss of meaning", "depression"),
    ("Self-esteem and confidence", "self_esteem"),
    ("Relationships with partner", "partner_relations"),
    ("Finding a partner, loneliness", "partner_search"),
    ("Breakup, divorce, loss", "breakup"),
    ("Parent-child relationships", "parent_child"),
    ("Relationships with parents", "parent_relations"),
    ("Professional burnout", "burnout"),
    ("Purpose search, life path", "purpose_search"),
    ("Career issues, professional change", "career"),
    ("Financial blocks, money relationships", "financial_blocks"),
    ("Goal setting, achieving goals", "goal_setting"),
    ("Procrastination, motivation", "procrastination"),
    ("Women's topics", "women_topics"),
    ("Men's topics", "men_topics"),
    ("Psychosomatics", "psychosomatics"),
    ("Trauma work (PTSD)", "trauma"),
    ("Working with inner parts of personality", "internal_parts"),
    ("Spiritual development, self-search", "spiritual_development"),
    ("Other", "other"),
]

def get_main_direction_keyboard(lang, selected=None):
    return create_multiselect_keyboard(
        MAIN_DIRECTION_OPTIONS_EN if lang == 'en' else MAIN_DIRECTION_OPTIONS_RU, "main_direction", selected or [])

def get_methods_keyboard(lang, selected=None):
    return create_multiselect_keyboard(
        ADDITIONAL_METHODS_OPTIONS_EN if lang == 'en' else ADDITIONAL_METHODS_OPTIONS_RU, "additional_methods", selected or [])

def get_education_keyboard(lang, selected=None):
    return create_multiselect_keyboard(
        EDUCATION_OPTIONS_EN if lang == 'en' else EDUCATION_OPTIONS_RU, "education", selected or [], show_done=False)

def get_experience_keyboard(lang, selected=None):
    return create_multiselect_keyboard(
        EXPERIENCE_OPTIONS_EN if lang == 'en' else EXPERIENCE_OPTIONS_RU, "experience", selected or [], show_done=False)

def get_work_format_keyboard(lang, selected=None):
    return create_multiselect_keyboard(
        WORK_FORMAT_OPTIONS_EN if lang == 'en' else WORK_FORMAT_OPTIONS_RU, "work_format", selected or [])

def get_clients_count_keyboard(lang, selected=None):
    return create_multiselect_keyboard(
        CLIENTS_COUNT_OPTIONS_EN if lang == 'en' else CLIENTS_COUNT_OPTIONS_RU, "clients_count", selected or [], show_done=False)

def get_average_check_keyboard(lang, selected=None):
    return create_multiselect_keyboard(
        AVERAGE_CHECK_OPTIONS_EN if lang == 'en' else AVERAGE_CHECK_OPTIONS_RU, "avg_check", selected or [], show_done=False)

def get_client_requests_keyboard(lang, selected=None):
    return create_multiselect_keyboard(
        CLIENT_REQUESTS_OPTIONS_EN if lang == 'en' else CLIENT_REQUESTS_OPTIONS_RU, "client_requests", selected or [])
