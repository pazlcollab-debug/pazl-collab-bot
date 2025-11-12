import os
from dotenv import load_dotenv

# ==============================
# 🔹 Загрузка переменных окружения
# ==============================
load_dotenv()

# --- Основные токены и ключи ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
AIRTABLE_API_KEY = os.getenv("AIRTABLE_API_KEY")
AIRTABLE_BASE_ID = os.getenv("AIRTABLE_BASE_ID")

# --- Админ и фото ---
ADMIN_ID = int(os.getenv("ADMIN_ID")) if os.getenv("ADMIN_ID") else None
DEFAULT_PHOTO_URL = os.getenv("DEFAULT_PHOTO_URL", "https://example.com/default.png")

# --- WebApp URL ---
WEBAPP_URL = os.getenv("WEBAPP_URL", "http://localhost:5173")

# --- Среда (опционально) ---
ENV = os.getenv("ENV", "dev")

# --- Проверка конфигурации ---
if not BOT_TOKEN or not AIRTABLE_API_KEY or not AIRTABLE_BASE_ID:
    print("⚠️ Внимание: отсутствуют обязательные переменные окружения! Проверь .env или Secrets Railway.")
