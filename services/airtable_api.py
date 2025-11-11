import asyncio
import requests
import csv
import os
from datetime import datetime
from pyairtable import Table
from aiogram import Bot
from config import AIRTABLE_API_KEY, AIRTABLE_BASE_ID, BOT_TOKEN
from services.status_notifier import notify_new_expert  # 📢 уведомление в канал

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
# 💰 Average check (исправленный, синхронизирован с form_keyboards.py)
# ==========================
AVERAGE_CHECK_MAPPING_RU = {
    "under_10k": "до 10 тыс рублей",
    "10_30k": "10–30 тыс рублей",
    "30_50k": "30–50 тыс рублей",
    "50_100k": "50–100 тыс рублей",
    "over_100k": "от 100 тыс рублей"
}

AVERAGE_CHECK_MAPPING_EN = {
    "under_10k": "up to $100",
    "10_30k": "$100–300",
    "30_50k": "$300–500",
    "50_100k": "$500–1 000",
    "over_100k": "over $1 000"
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
VALID_DIRECTIONS_RU = set(DIRECTION_MAPPING_RU.values())
VALID_DIRECTIONS_EN = set(DIRECTION_MAPPING_EN.values())

# ==========================
# 🎭 Methods
# ==========================
METHODS_MAPPING_RU = {
    "nlp": "НЛП",
    "constellations": "Системные расстановки",
    "art_therapy": "Арт-терапия",
    "mac": "МАК (метафорические ассоциативные карты)",
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
VALID_METHODS_RU = set(METHODS_MAPPING_RU.values())
VALID_METHODS_EN = set(METHODS_MAPPING_EN.values())

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
    "inner_parts": "Работа с внутренними частями личности",
    "spiritual": "Духовное развитие",
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
    "inner_parts": "Working with inner parts of personality",
    "spiritual": "Spiritual development, self-search",
    "other": "Other"
}

# ==========================
# ⚙️ Airtable setup
# ==========================
_cached_fields = None
_sent_notifications = set()

def get_table(table_name='Experts'):
    return Table(AIRTABLE_API_KEY, AIRTABLE_BASE_ID, table_name)

def get_all_table_fields():
    global _cached_fields
    if _cached_fields:
        return _cached_fields
    url = f"https://api.airtable.com/v0/meta/bases/{AIRTABLE_BASE_ID}/tables"
    headers = {"Authorization": f"Bearer {AIRTABLE_API_KEY}"}
    try:
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            data = r.json()
            for t in data.get("tables", []):
                if t["name"] == "Experts":
                    _cached_fields = [f["name"] for f in t["fields"]]
                    return _cached_fields
    except Exception as e:
        print(f"⚠️ Ошибка при получении полей Airtable: {e}")
    return []

# ==========================
# 🧭 Universal mapping
# ==========================
def smart_map(values, mapping_ru, mapping_en, lang):
    mapping = mapping_ru if lang == "ru" else mapping_en
    if isinstance(values, list):
        return [mapping.get(v, v) for v in values if v]
    return mapping.get(values, values)

# ==========================
# 🗂️ CSV Logging
# ==========================
def log_record_to_csv(record_id, name, lang, telegram_id):
    os.makedirs("logs", exist_ok=True)
    csv_path = "logs/airtable_records.csv"
    file_exists = os.path.exists(csv_path)
    with open(csv_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["datetime", "record_id", "name", "lang", "telegram_id"])
        writer.writerow([
            datetime.now().isoformat(timespec="seconds"),
            record_id,
            name,
            lang,
            telegram_id
        ])

# ==========================
# 📤 Create record in Airtable
# ==========================
async def create_expert_record(data: dict):
    table = get_table()
    available = get_all_table_fields()
    lang = data.get("lang", "ru")

    airtable_data = {
        "Name": data.get("name", ""),
        "Phone": data.get("phone", ""),
        "Telegram": data.get("telegram", ""),
        "City": data.get("city", ""),
        "Language": lang,
    }

    if "Social" in available:
        airtable_data["Social"] = data.get("social", "")

    if "Education" in available:
        airtable_data["Education"] = smart_map(data.get("education", ""), EDUCATION_MAPPING_RU, EDUCATION_MAPPING_EN, lang)

    if "Experience" in available:
        airtable_data["Experience"] = smart_map(data.get("experience", ""), EXPERIENCE_MAPPING_RU, EXPERIENCE_MAPPING_EN, lang)

    if "Clients" in available:
        airtable_data["Clients"] = smart_map(data.get("clients_count", ""), CLIENTS_COUNT_MAPPING_RU, CLIENTS_COUNT_MAPPING_EN, lang)

    if "AverageCheck" in available:
        airtable_data["AverageCheck"] = smart_map(data.get("average_check", ""), AVERAGE_CHECK_MAPPING_RU, AVERAGE_CHECK_MAPPING_EN, lang)

    if "Audience" in available:
        airtable_data["Audience"] = data.get("audience", "")

    if "Positioning" in available:
        airtable_data["Positioning"] = data.get("positioning", "")

    if "TelegramID" in available:
        airtable_data["TelegramID"] = str(data.get("telegram_id", ""))

    if "Direction" in available:
        dirs = smart_map(data.get("main_direction", []), DIRECTION_MAPPING_RU, DIRECTION_MAPPING_EN, lang)
        valid = VALID_DIRECTIONS_RU if lang == "ru" else VALID_DIRECTIONS_EN
        airtable_data["Direction"] = [d for d in dirs if d in valid]

    if "Methods" in available:
        m = smart_map(data.get("additional_methods", []), METHODS_MAPPING_RU, METHODS_MAPPING_EN, lang)
        valid = VALID_METHODS_RU if lang == "ru" else VALID_METHODS_EN
        airtable_data["Methods"] = [x for x in m if x in valid]

    if "Format" in available:
        airtable_data["Format"] = smart_map(data.get("work_formats", []), WORK_FORMAT_MAPPING_RU, WORK_FORMAT_MAPPING_EN, lang)

    if "Requests" in available:
        reqs = data.get("client_requests", [])
        if isinstance(reqs, str):
            reqs = [reqs] if reqs else []
        mapped = smart_map(reqs, REQUESTS_MAPPING_RU, REQUESTS_MAPPING_EN, lang)
        known = set(REQUESTS_MAPPING_RU.values()) | set(REQUESTS_MAPPING_EN.values())
        airtable_data["Requests"] = [r for r in mapped if r in known]

    if "Photo" in available and data.get("photo_url"):
        airtable_data["Photo"] = [{"url": data["photo_url"]}]

    if "Status" in available:
        airtable_data["Status"] = "🟡 На модерации" if lang == "ru" else "🟡 Pending"

    airtable_data = {k: v for k, v in airtable_data.items() if v not in ("", None, [], [{}])}

    try:
        record = table.create(airtable_data)
        record_id = record["id"]
        print(f"✅ Новая запись создана в Airtable ({lang}): {record_id}")

        log_record_to_csv(
            record_id,
            data.get("name", "Без имени"),
            lang,
            data.get("telegram_id", "")
        )

        async def notify():
            if record_id in _sent_notifications:
                return
            _sent_notifications.add(record_id)
            await asyncio.sleep(1.5)
            bot = Bot(token=BOT_TOKEN)
            try:
                await notify_new_expert(bot=bot, expert_name=data.get("name", "Без имени"), lang=lang, record_id=record_id)
            finally:
                await bot.session.close()

        asyncio.create_task(notify())
        return record_id

    except Exception as e:
        print(f"❌ Ошибка при создании записи: {e}")
        raise

# ==========================
# 🔄 Update status
# ==========================
async def update_expert_status(expert_id: str, status: str):
    table = get_table()
    try:
        table.update(expert_id, {"Status": status})
        print(f"✅ Статус обновлён: {status}")
        return True
    except Exception as e:
        print(f"❌ Ошибка при обновлении статуса: {e}")
        raise
