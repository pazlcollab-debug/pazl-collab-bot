from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from api.airtable_service import get_approved_experts
import requests
import os
from config import AIRTABLE_API_KEY, AIRTABLE_BASE_ID

# ==========================
# 🚀 Инициализация приложения
# ==========================
app = FastAPI(title="PAZL Collab API")

# ==========================
# 📱 Подключение Mini App (React build)
# ==========================

BASE_DIR = os.path.dirname(os.path.dirname(__file__))   # pazl-collab-bot/
FRONTEND_DIST = os.path.join(BASE_DIR, "frontend", "dist")

# 1️⃣ Ассеты (CSS/JS)
app.mount(
    "/webapp/assets",
    StaticFiles(directory=os.path.join(FRONTEND_DIST, "assets")),
    name="webapp-assets"
)

# 2️⃣ SPA fallback: любые /webapp/... → index.html
@app.get("/webapp")
@app.get("/webapp/{path:path}")
async def serve_webapp(path: str = ""):
    index_path = os.path.join(FRONTEND_DIST, "index.html")
    return FileResponse(index_path)


# ==========================
# 🌍 CORS
# ==========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================
# ⚙️ Airtable
# ==========================
AIRTABLE_URL = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/Experts"
HEADERS = {"Authorization": f"Bearer {AIRTABLE_API_KEY}"}


# ==========================
# 📋 Список экспертов
# ==========================
@app.get("/api/experts")
def get_experts(
    lang: str | None = Query(None),
    city: str | None = Query(None),
    direction: str | None = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=50),
):
    experts = get_approved_experts()

    if lang:
        experts = [e for e in experts if e.get("language", "").lower() == lang.lower().strip()]

    if city:
        experts = [e for e in experts if city.lower().strip() in (e.get("city") or "").lower()]

    if direction:
        experts = [e for e in experts if direction.lower().strip() in (e.get("direction") or "").lower()]

    total = len(experts)
    start = (page - 1) * limit
    end = start + limit

    return {
        "page": page,
        "limit": limit,
        "total": total,
        "pages": (total + limit - 1) // limit,
        "experts": experts[start:end],
    }


# ==========================
# 👤 Профиль по Telegram ID
# ==========================
@app.get("/api/profile/{telegram_id}")
def get_profile(telegram_id: str):
    """Фикс: TelegramID в Airtable — ЧИСЛО → без кавычек"""
    params = {"filterByFormula": f"{{TelegramID}}={telegram_id}"}

    try:
        r = requests.get(AIRTABLE_URL, headers=HEADERS, params=params, timeout=10)
        r.raise_for_status()
        records = r.json().get("records", [])
        if not records:
            return {"error": "Profile not found"}
        return format_expert_record(records[0])

    except Exception as e:
        return {"error": str(e)}


# ==========================
# 🔎 Эксперт по record_id
# ==========================
@app.get("/api/expert/{record_id}")
def get_expert(record_id: str):
    try:
        r = requests.get(f"{AIRTABLE_URL}/{record_id}", headers=HEADERS, timeout=10)
        r.raise_for_status()
        return format_expert_record(r.json())
    except Exception as e:
        return {"error": str(e)}


# ==========================
# 🧩 Форматирование записи
# ==========================
def format_expert_record(record: dict):
    fields = record.get("fields", {})

    direction = (
        fields["Direction"][0]
        if isinstance(fields.get("Direction"), list) and fields["Direction"]
        else fields.get("Direction")
    )

    photo_url = (
        fields["Photo"][0]["url"]
        if isinstance(fields.get("Photo"), list) and fields["Photo"]
        else None
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
# 🏁 Root
# ==========================
@app.get("/")
def root():
    return {"message": "✅ PAZL Collab API is running"}
