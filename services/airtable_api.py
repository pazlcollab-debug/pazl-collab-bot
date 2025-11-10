from pyairtable import Table
from config import AIRTABLE_API_KEY, AIRTABLE_BASE_ID
import requests

# ==========================
# 🎓 Education
# ==========================
EDUCATION_MAPPING_RU = {
    "psych_higher": "Высшее психологическое",
    "medical_higher": "Высшее медицинское",
    "pedagogical_higher": "Высшее педагогическое",
    "other_higher": "Высшее другое",
    "secondary": "Среднее специальное",
    "none": "Нет профильного образования"
}
EDUCATION_MAPPING_EN = {
    "psych_higher": "Higher psychological",
    "medical_higher": "Higher medical",
    "pedagogical_higher": "Higher pedagogical",
    "other_higher": "Higher other",
    "secondary": "Secondary specialized",
    "none": "No specialized education"
}

# ==========================
# 🧭 Experience
# ==========================
EXPERIENCE_MAPPING_RU = {
    "less_1": "Менее 1 года",
    "1_2": "1-2 года",
    "2_3": "2-3 года",
    "3_5": "3-5 лет",
    "5_7": "5-7 лет",
    "7_10": "7-10 лет",
    "more_10": "Более 10 лет"
}
EXPERIENCE_MAPPING_EN = {
    "less_1": "Less than 1 year",
    "1_2": "1-2 years",
    "2_3": "2-3 years",
    "3_5": "3-5 years",
    "5_7": "5-7 years",
    "7_10": "7-10 years",
    "more_10": "More than 10 years"
}

# ==========================
# 👥 Clients count
# ==========================
CLIENTS_COUNT_MAPPING_RU = {
    "1_5": "1-5 клиентов",
    "5_10": "5-10 клиентов",
    "10_15": "10-15 клиентов",
    "15_20": "15-20 клиентов",
    "20_30": "20-30 клиентов",
    "more_30": "Более 30 клиентов"
}
CLIENTS_COUNT_MAPPING_EN = {
    "1_5": "1-5 clients",
    "5_10": "5-10 clients",
    "10_15": "10-15 clients",
    "15_20": "15-20 clients",
    "20_30": "20-30 clients",
    "more_30": "More than 30 clients"
}

# ==========================
# 💰 Average check
# ==========================
AVERAGE_CHECK_MAPPING_RU = {
    "under_10k": "до 10 тыс рублей",
    "10_30k": "10-30 тыс",
    "30_50k": "30-50 тыс",
    "50_100k": "50-100 тыс",
    "over_100k": "от 100 тыс"
}
AVERAGE_CHECK_MAPPING_EN = {
    "under_10k": "up to 10k rubles",
    "10_30k": "10-30k rubles",
    "30_50k": "30-50k rubles",
    "50_100k": "50-100k rubles",
    "over_100k": "over 100k rubles"
}

# ==========================
# 🧩 Work formats
# ==========================
WORK_FORMAT_MAPPING_RU = {
    "individual_online": "Индивидуальные сессии (онлайн)",
    "individual_offline": "Индивидуальные сессии (оффлайн)",
    "group_online": "Групповые программы (онлайн)",
    "group_offline": "Групповые программы (оффлайн)",
    "marathons": "Марафоны / челленджи",
    "intensives": "Интенсивы / ретриты",
    "courses": "Обучающие курсы",
    "webinars": "Вебинары / мастер-классы"
}
WORK_FORMAT_MAPPING_EN = {
    "individual_online": "Individual sessions (online)",
    "individual_offline": "Individual sessions (offline)",
    "group_online": "Group programs (online)",
    "group_offline": "Group programs (offline)",
    "marathons": "Marathons/challenges",
    "intensives": "Intensives/retreats",
    "courses": "Training courses",
    "webinars": "Webinars/master classes"
}

# ==========================
# 🧠 Directions
# ==========================
DIRECTION_MAPPING_RU = {
    "coaching_life": "Коучинг (лайф-коучинг)",
    "coaching_business": "Коучинг (бизнес-коучинг)",
    "coaching_career": "Коучинг (карьерный)",
    "psych_clinical": "Психология (клиническая практика)",
    "psych_consulting": "Психология (консультирование)",
    "therapy_cbt": "Психотерапия (КПТ)",
    "therapy_gestalt": "Психотерапия (гештальт-терапия)",
    "therapy_psychoanalysis": "Психотерапия (психоанализ)",
    "therapy_schema": "Психотерапия (схема-терапия)",
    "body_therapy": "Телесно-ориентированная терапия",
    "hypnotherapy": "Работа с подсознанием (гипнотерапия)",
    "regression_therapy": "Работа с подсознанием (регрессивная терапия)",
    "astrology": "Астрология",
    "energy_practices": "Энергетические практики",
    "nutrition": "Нутрициология",
    "yoga_therapy": "Йога-терапия",
    "other": "Другое"
}
DIRECTION_MAPPING_EN = {
    "coaching_life": "Coaching (life coaching)",
    "coaching_business": "Coaching (business coaching)",
    "coaching_career": "Coaching (career)",
    "psych_clinical": "Psychology (clinical practice)",
    "psych_consulting": "Psychology (consulting)",
    "therapy_cbt": "Psychotherapy (CBT)",
    "therapy_gestalt": "Psychotherapy (gestalt therapy)",
    "therapy_psychoanalysis": "Psychotherapy (psychoanalysis)",
    "therapy_schema": "Psychotherapy (schema therapy)",
    "body_therapy": "Body-oriented therapy",
    "hypnotherapy": "Subconscious work (hypnotherapy)",
    "regression_therapy": "Subconscious work (regression therapy)",
    "astrology": "Astrology",
    "energy_practices": "Energy practices",
    "nutrition": "Nutrition",
    "yoga_therapy": "Yoga therapy",
    "other": "Other"
}

# ==========================
# 🎭 Methods
# ==========================
METHODS_MAPPING_RU = {
    "nlp": "НЛП",
    "constellations": "Системные расстановки",
    "art_therapy": "Арт-терапия",
    "mac": "МАК",
    "meditation": "Медитативные практики",
    "breathing": "Дыхательные практики",
    "ancestral_work": "Работа с родовыми сценариями",
    "human_design": "Human Design",
    "other": "Другое"
}
METHODS_MAPPING_EN = {
    "nlp": "NLP",
    "constellations": "Systemic constellations",
    "art_therapy": "Art therapy",
    "mac": "MAC (Metaphorical Associative Cards)",
    "meditation": "Meditative practices",
    "breathing": "Breathing practices",
    "ancestral_work": "Ancestral scenario work",
    "human_design": "Human Design",
    "other": "Other"
}

# ==========================
# 💬 Requests
# ==========================
REQUESTS_MAPPING_RU = {
    "anxiety": "Тревожность, панические атаки",
    "depression": "Депрессия, апатия",
    "selfesteem": "Самооценка и уверенность",
    "relationship_partner": "Отношения с партнером",
    "find_partner": "Поиск партнера, одиночество",
    "breakup": "Расставание, развод",
    "parent_child": "Детско-родительские отношения",
    "parents": "Отношения с родителями",
    "burnout": "Профессиональное выгорание",
    "purpose": "Поиск предназначения",
    "career": "Карьерные вопросы",
    "financial": "Финансовые блоки",
    "goal_setting": "Целеполагание",
    "procrastination": "Прокрастинация, мотивация",
    "women_topics": "Женские темы",
    "men_topics": "Мужские темы",
    "psychosomatics": "Психосоматика",
    "trauma": "Работа с травмой (ПТСР)",
    # 🩵 FIX — два варианта безопасно
    "inner_parts": "Работа с внутренними частями",
    "internal_parts": "Работа с внутренними частями",
    "spiritual": "Духовное развитие",
    "spiritual_development": "Духовное развитие",
    "other": "Другое"
}

REQUESTS_MAPPING_EN = {
    "anxiety": "Anxiety, panic attacks, fears",
    "depression": "Depression, apathy, loss of meaning",
    "selfesteem": "Self-esteem and confidence",
    "relationship_partner": "Relationships with partner",
    "find_partner": "Finding a partner, loneliness",
    "breakup": "Breakup, divorce, loss",
    "parent_child": "Parent-child relationships",
    "parents": "Relationships with parents",
    "burnout": "Professional burnout",
    "purpose": "Purpose search, life path",
    "career": "Career issues, professional change",
    "financial": "Financial blocks, money relationships",
    "goal_setting": "Goal setting, achieving goals",
    "procrastination": "Procrastination, motivation",
    "women_topics": "Women's topics",
    "men_topics": "Men's topics",
    "psychosomatics": "Psychosomatics",
    "trauma": "Trauma work (PTSD)",
    # 🩵 FIX — два ключа на один вариант
    "inner_parts": "Working with inner parts of personality",
    "internal_parts": "Working with inner parts of personality",
    "spiritual": "Spiritual development, self-search",
    "spiritual_development": "Spiritual development, self-search",
    "other": "Other"
}

# ==========================
# ⚙️ Подключение к Airtable
# ==========================
def get_table(table_name='Experts'):
    return Table(AIRTABLE_API_KEY, AIRTABLE_BASE_ID, table_name)


def get_all_table_fields():
    url = f"https://api.airtable.com/v0/meta/bases/{AIRTABLE_BASE_ID}/tables"
    headers = {"Authorization": f"Bearer {AIRTABLE_API_KEY}"}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            for table in data.get('tables', []):
                if table['name'] == 'Experts':
                    return [field['name'] for field in table.get('fields', [])]
    except Exception as e:
        print(f"Ошибка: {e}")
    return []

# ==========================
# 🧭 Универсальное сопоставление значений
# ==========================
def smart_map(values, mapping_ru, mapping_en, lang):
    mapping = mapping_ru if lang == "ru" else mapping_en
    print(f"🌐 SMART_MAP → язык: {lang}")

    if isinstance(values, list):
        mapped = [mapping.get(val, val) for val in values if val]
        print(f"➡️ Список сопоставлен: {mapped}")
        return mapped

    mapped_value = mapping.get(values, values)
    print(f"➡️ Одно значение: {mapped_value}")
    return mapped_value

# ==========================
# 📤 Создание записи в Airtable
# ==========================
async def create_expert_record(data: dict):
    table = get_table()
    available_fields = get_all_table_fields()
    lang = data.get('lang', 'ru')

    airtable_data = {
        'Name': data.get('name', ''),
        'Phone': data.get('phone', ''),
        'Telegram': data.get('telegram', ''),
        'City': data.get('city', ''),
        'Language': lang,
    }

    if 'Social' in available_fields:
        airtable_data['Social'] = data.get('social', '')

    if 'Education' in available_fields:
        airtable_data['Education'] = smart_map(data.get('education', ''), EDUCATION_MAPPING_RU, EDUCATION_MAPPING_EN, lang)

    if 'Experience' in available_fields:
        airtable_data['Experience'] = smart_map(data.get('experience', ''), EXPERIENCE_MAPPING_RU, EXPERIENCE_MAPPING_EN, lang)

    if 'Clients' in available_fields:
        airtable_data['Clients'] = smart_map(data.get('clients_count', ''), CLIENTS_COUNT_MAPPING_RU, CLIENTS_COUNT_MAPPING_EN, lang)

    if 'AverageCheck' in available_fields:
        airtable_data['AverageCheck'] = smart_map(data.get('average_check', ''), AVERAGE_CHECK_MAPPING_RU, AVERAGE_CHECK_MAPPING_EN, lang)

    if 'Audience' in available_fields:
        airtable_data['Audience'] = data.get('audience', '')

    if 'Positioning' in available_fields:
        airtable_data['Positioning'] = data.get('positioning', '')

    if 'TelegramID' in available_fields:
        airtable_data['TelegramID'] = str(data.get('telegram_id', ''))

    if 'Direction' in available_fields:
        airtable_data['Direction'] = smart_map(data.get('main_direction', []), DIRECTION_MAPPING_RU, DIRECTION_MAPPING_EN, lang)

    if 'Methods' in available_fields:
        airtable_data['Methods'] = smart_map(data.get('additional_methods', []), METHODS_MAPPING_RU, METHODS_MAPPING_EN, lang)

    if 'Format' in available_fields:
        airtable_data['Format'] = smart_map(data.get('work_formats', []), WORK_FORMAT_MAPPING_RU, WORK_FORMAT_MAPPING_EN, lang)

    if 'Requests' in available_fields:
        raw_requests = data.get('client_requests', [])
        if isinstance(raw_requests, str):
            raw_requests = [raw_requests] if raw_requests else []
        mapped = smart_map(raw_requests, REQUESTS_MAPPING_RU, REQUESTS_MAPPING_EN, lang)

        # 🛡️ Фильтрация неизвестных ключей
        known = set(REQUESTS_MAPPING_RU.values()) | set(REQUESTS_MAPPING_EN.values())
        filtered = [r for r in mapped if r in known]
        airtable_data['Requests'] = filtered

    if 'Photo' in available_fields and data.get('photo_url'):
        airtable_data['Photo'] = [{'url': data['photo_url']}]

    print(f"\n📤 SENDING TO AIRTABLE ({lang}):\n{airtable_data}\n")

    try:
        record = table.create(airtable_data)
        print(f"✅ Запись создана в Airtable с ID: {record['id']}")
        return record['id']
    except Exception as e:
        print(f"❌ Ошибка создания записи: {e}")
        raise

# ==========================
# 🔄 Обновление статуса
# ==========================
async def update_expert_status(expert_id: str, status: str):
    table = get_table()
    print(f"🔄 Обновляем статус {expert_id} → {status}")
    try:
        table.update(expert_id, {'Status': status})
        print("✅ Статус успешно обновлён")
        return True
    except Exception as e:
        print(f"❌ Ошибка при обновлении статуса: {e}")
        raise
