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
# 💰 Average check
# ==========================
AVERAGE_CHECK_MAPPING_RU = {
    "under_10k": "до 10 тыс рублей",
    "10_30k": "10-30 тыс рублей",   # исправлено дефисы
    "30_50k": "30-50 тыс рублей",   # исправлено дефисы
    "50_100k": "50-100 тыс рублей", # исправлено дефисы
    "over_100k": "от 100 тыс рублей"
}
AVERAGE_CHECK_MAPPING_EN = {
    "under_10k": "up to $100",
    "10_30k": "$100-300",
    "30_50k": "$300-500",
    "50_100k": "$500-1 000",
    "over_100k": "over $1 000"
}

# ==========================
# 🧩 Work formats
# ==========================
WORK_FORMAT_MAPPING_RU = {
    "individual_online": "Индивидуальные сессии (онлайн)",
    "individual_offline": "Индивидуальные сессии (офлайн)",
    "group_online": "Групповые программы (онлайн)",
    "group_offline": "Групповые программы (офлайн)",
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
    "anxiety": "Тревожность, панические атаки, страхи",
    "depression": "Депрессия, апатия, потеря смысла",
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


def get_table(table_name="Experts"):
    return Table(AIRTABLE_API_KEY, AIRTABLE_BASE_ID, table_name)


def get_all_table_fields(force_refresh=False):
    global _cached_fields
    if _cached_fields and not force_refresh:
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
        mapped = [mapping.get(v, v) for v in values if v]
    else:
        mapped = [mapping.get(values, values)] if values else []
    return [v for v in mapped if v]
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

    if not available:
        available = get_all_table_fields(force_refresh=True)

    airtable_data = {
        "Name": data.get("name", ""),
        "Phone": data.get("phone", ""),
        "Telegram": data.get("telegram", ""),
        "City": data.get("city", ""),
        "Language": lang,
    }

    if "Social" in available:
        airtable_data["Social"] = data.get("social", "")

    # 🎓 Education
    if "Education" in available:
        edu = smart_map(data.get("education", ""), EDUCATION_MAPPING_RU, EDUCATION_MAPPING_EN, lang)
        if edu:
            airtable_data["Education"] = edu[0]

    # 🧭 Experience
    if "Experience" in available:
        exp = smart_map(data.get("experience", ""), EXPERIENCE_MAPPING_RU, EXPERIENCE_MAPPING_EN, lang)
        if exp:
            airtable_data["Experience"] = exp[0]

    # 👥 Clients
    if "Clients" in available:
        clients = smart_map(data.get("clients_count", ""), CLIENTS_COUNT_MAPPING_RU, CLIENTS_COUNT_MAPPING_EN, lang)
        if clients:
            airtable_data["Clients"] = clients[0]

    # 💰 Average Check
    if "AverageCheck" in available:
        avg = smart_map(data.get("average_check", ""), AVERAGE_CHECK_MAPPING_RU, AVERAGE_CHECK_MAPPING_EN, lang)
        if avg:
            airtable_data["AverageCheck"] = avg[0]

    # 🧠 Direction (MULTIPLE SELECT)
    if "Direction" in available:
        dirs = data.get("main_direction", [])
        if isinstance(dirs, str):
            dirs = [dirs]
        mapped = smart_map(dirs, DIRECTION_MAPPING_RU, DIRECTION_MAPPING_EN, lang)
        valid = VALID_DIRECTIONS_RU if lang == "ru" else VALID_DIRECTIONS_EN
        valid_dirs = [d for d in mapped if d in valid]
        if valid_dirs:
            airtable_data["Direction"] = valid_dirs

    # 🎭 Methods (MULTIPLE SELECT)
    if "Methods" in available:
        methods = data.get("additional_methods", [])
        if isinstance(methods, str):
            methods = [methods]
        mapped = smart_map(methods, METHODS_MAPPING_RU, METHODS_MAPPING_EN, lang)
        valid = VALID_METHODS_RU if lang == "ru" else VALID_METHODS_EN
        valid_methods = [m for m in mapped if m in valid]
        if valid_methods:
            airtable_data["Methods"] = valid_methods

    # 💼 Format (MULTIPLE SELECT)
    if "Format" in available:
        formats = data.get("work_formats", [])
        if isinstance(formats, str):
            formats = [formats]
        mapped = smart_map(formats, WORK_FORMAT_MAPPING_RU, WORK_FORMAT_MAPPING_EN, lang)
        valid = set(WORK_FORMAT_MAPPING_RU.values()) if lang == "ru" else set(WORK_FORMAT_MAPPING_EN.values())
        valid_formats = [f for f in mapped if f in valid]
        if valid_formats:
            airtable_data["Format"] = valid_formats

    # 📋 Requests (MULTIPLE SELECT)
    if "Requests" in available:
        reqs = data.get("client_requests", [])
        if isinstance(reqs, str):
            reqs = [reqs]
        mapped = smart_map(reqs, REQUESTS_MAPPING_RU, REQUESTS_MAPPING_EN, lang)
        valid = set(REQUESTS_MAPPING_RU.values()) if lang == "ru" else set(REQUESTS_MAPPING_EN.values())
        valid_reqs = [r for r in mapped if r in valid]
        if valid_reqs:
            airtable_data["Requests"] = valid_reqs

    # 🧍‍♀️ Audience (text)
    if "Audience" in available:
        airtable_data["Audience"] = data.get("audience", "")

    # 🧭 Positioning (text)
    if "Positioning" in available:
        airtable_data["Positioning"] = data.get("positioning", "")

    # 🆔 Telegram ID (в Airtable это Number, передаем как число)
    if "TelegramID" in available:
        telegram_id = data.get("telegram_id", "")
        if telegram_id:
            try:
                # Преобразуем в число, так как в Airtable поле Number
                airtable_data["TelegramID"] = int(telegram_id)
            except (ValueError, TypeError):
                # Если не число, пытаемся преобразовать строку
                airtable_data["TelegramID"] = str(telegram_id)

    # 📸 Photo
    if "Photo" in available and data.get("photo_url"):
        airtable_data["Photo"] = [{"url": data["photo_url"]}]

    # 🟡 Status
    if "Status" in available:
        airtable_data["Status"] = "🟡 На модерации" if lang == "ru" else "🟡 Pending"

    # 🧹 Очистка пустых полей
    airtable_data = {k: v for k, v in airtable_data.items() if v not in ("", None, [], [{}])}

    # 🧾 Лог перед отправкой
    print("📤 Отправляем в Airtable:", airtable_data)

    try:
        record = await asyncio.to_thread(table.create, airtable_data)
        record_id = record["id"]
        print(f"✅ Новая запись создана в Airtable ({lang}): {record_id}")

        log_record_to_csv(
            record_id,
            data.get("name", "Без имени"),
            lang,
            data.get("telegram_id", "")
        )

        # 📢 Уведомление в канал
        async def notify():
            if record_id in _sent_notifications:
                return
            _sent_notifications.add(record_id)
            await asyncio.sleep(1.5)
            bot = Bot(token=BOT_TOKEN)
            try:
                await notify_new_expert(
                    bot=bot,
                    expert_name=data.get("name", "Без имени"),
                    lang=lang,
                    record_id=record_id
                )
            finally:
                await bot.session.close()

        asyncio.create_task(notify())
        return record_id

    except Exception as e:
        error_text = str(e)
        print(f"❌ Ошибка при создании записи: {error_text}")
        if any(x in error_text for x in ["422", "INVALID_MULTIPLE_CHOICE_OPTIONS", "INVALID_VALUE_FOR_COLUMN"]):
            raise Exception(
                "Ошибка при сохранении анкеты в Airtable: "
                "некоторые значения не совпадают с вариантами выбора в таблице. "
                "Проверьте настройки полей (например, 'Format', 'Methods', 'Direction', 'Requests')."
            )
        else:
            raise Exception(f"Ошибка при создании записи: {error_text}")


# ==========================
# 🔄 Update status
# ==========================
STATUS_MAPPING = {
    "🟢 Одобрено": "Approved",
    "🟡 На модерации": "Pending",
    "🔴 Отклонено": "Declined",
    "🟢 Approved": "Approved",
    "🟡 Pending": "Pending",
    "🔴 Declined": "Declined"
}


async def update_expert_status(expert_id: str, status: str):
    table = get_table()
    try:
        normalized_status = STATUS_MAPPING.get(status, status)
        table.update(expert_id, {"Status": normalized_status})
        print(f"✅ Статус обновлён: {normalized_status}")
        return True
    except Exception as e:
        print(f"❌ Ошибка при обновлении статуса: {e}")
        raise
