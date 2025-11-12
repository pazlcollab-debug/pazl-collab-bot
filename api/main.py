from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from api.airtable_service import get_approved_experts
import requests
from config import AIRTABLE_API_KEY, AIRTABLE_BASE_ID

app = FastAPI(title="PAZL Collab API")

# ==========================
# 🌍 Настройка CORS
# ==========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ⚠️ в продакшене сюда вписать домен фронта (например https://pazl.app)
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================
# ⚙️ Константы Airtable
# ==========================
AIRTABLE_URL = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/Experts"
HEADERS = {"Authorization": f"Bearer {AIRTABLE_API_KEY}"}


# ==========================
# 📋 Список экспертов (с фильтрами)
# ==========================
@app.get("/api/experts")
def get_experts(
    lang: str | None = Query(None, description="Фильтр по языку анкеты (ru/en)"),
    city: str | None = Query(None, description="Фильтр по городу"),
    direction: str | None = Query(None, description="Фильтр по направлению (например: yoga, coaching, etc.)"),
    page: int = Query(1, ge=1, description="Номер страницы"),
    limit: int = Query(10, ge=1, le=50, description="Количество карточек на странице"),
):
    """
    Получить всех экспертов со статусом Approved.
    Фильтры:
      - язык анкеты (lang)
      - город (city)
      - направление (direction)
      - постраничная навигация (page, limit)
    """
    experts = get_approved_experts()

    # --- Фильтрация ---
    if lang:
        experts = [e for e in experts if e.get("language", "").lower() == lang.lower().strip()]
    if city:
        experts = [e for e in experts if city.lower().strip() in (e.get("city", "") or "").lower()]
    if direction:
        experts = [e for e in experts if direction.lower().strip() in (e.get("direction", "") or "").lower()]

    # --- Пагинация ---
    total = len(experts)
    start = (page - 1) * limit
    end = start + limit
    paginated = experts[start:end]

    return {
        "page": page,
        "limit": limit,
        "total": total,
        "pages": (total + limit - 1) // limit,
        "experts": paginated,
    }


# ==========================
# 👤 Профиль по Telegram ID
# ==========================
@app.get("/api/profile/{telegram_id}")
def get_profile(telegram_id: str):
    """Получить профиль эксперта по Telegram ID"""
    # ⚠️ Название поля в Airtable должно быть точным — например "Telegram ID"
    params = {"filterByFormula": f"{{Telegram ID}}='{telegram_id}'"}

    try:
        response = requests.get(AIRTABLE_URL, headers=HEADERS, params=params, timeout=10)
        response.raise_for_status()
        records = response.json().get("records", [])
        if not records:
            return {"error": "Profile not found"}
        return format_expert_record(records[0])
    except requests.RequestException as e:
        return {"error": f"Airtable request failed: {e}"}
    except Exception as e:
        return {"error": str(e)}


# ==========================
# 🔎 Эксперт по record_id
# ==========================
@app.get("/api/expert/{record_id}")
def get_expert_by_id(record_id: str):
    """Получить конкретного эксперта по record_id из Airtable"""
    try:
        response = requests.get(f"{AIRTABLE_URL}/{record_id}", headers=HEADERS, timeout=10)
        response.raise_for_status()
        record = response.json()
        return format_expert_record(record)
    except requests.RequestException as e:
        return {"error": f"Airtable request failed: {e}"}
    except Exception as e:
        return {"error": str(e)}


# ==========================
# 🧩 Форматирование записи
# ==========================
def format_expert_record(record: dict):
    """Преобразует запись Airtable в стандартный JSON"""
    fields = record.get("fields", {})

    # Безопасное извлечение направлений и фото
    direction = (
        fields["Direction"][0] if isinstance(fields.get("Direction"), list) and fields["Direction"] else fields.get("Direction")
    )
    photo_url = (
        fields["Photo"][0]["url"] if isinstance(fields.get("Photo"), list) and fields["Photo"] else None
    )

    return {
        "id": record.get("id"),
        "name": fields.get("Name"),
        "city": fields.get("City"),
        "language": fields.get("Language", "ru"),
        "direction": direction,
        "telegram": fields.get("Telegram"),
        "photo_url": photo_url,
        "status": fields.get("Status"),
        "education": fields.get("Education"),
        "experience": fields.get("Experience"),
        "clients": fields.get("Clients"),
        "average_check": fields.get("AverageCheck"),
        "audience": fields.get("Audience"),
        "positioning": fields.get("Positioning"),
        "methods": fields.get("Methods", []),
        "formats": fields.get("Format", []),
        "requests": fields.get("Requests", []),
        "description": fields.get("Description"),
    }


# ==========================
# 🏁 Root (проверка)
# ==========================
@app.get("/")
def root():
    return {"message": "✅ PAZL Collab API is running"}
