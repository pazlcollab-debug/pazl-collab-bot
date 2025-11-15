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
def validate_config():
    """Проверяет наличие всех обязательных переменных окружения"""
    missing = []
    
    if not BOT_TOKEN:
        missing.append("BOT_TOKEN")
    if not AIRTABLE_API_KEY:
        missing.append("AIRTABLE_API_KEY")
    if not AIRTABLE_BASE_ID:
        missing.append("AIRTABLE_BASE_ID")
    
    if missing:
        error_msg = (
            f"❌ Ошибка конфигурации: отсутствуют обязательные переменные окружения: {', '.join(missing)}\n"
            "Проверьте .env файл или переменные окружения."
        )
        raise ValueError(error_msg)
    
    return True


# Автоматическая проверка при импорте (можно отключить для тестов)
if __name__ != "__main__":
    try:
        validate_config()
    except ValueError:
        # В dev режиме только предупреждаем, не падаем
        if ENV == "dev":
            print("⚠️ Внимание: отсутствуют обязательные переменные окружения! Проверь .env или Secrets Railway.")
        else:
            raise
