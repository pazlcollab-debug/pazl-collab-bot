from fastapi import FastAPI, Query, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from pydantic import BaseModel
from api.airtable_service import get_approved_experts
import requests
import os
import aiohttp
import time
from collections import defaultdict
from datetime import datetime, timedelta
from config import AIRTABLE_API_KEY, AIRTABLE_BASE_ID, BOT_TOKEN

# ==========================
# 🚀 Инициализация приложения
# ==========================
# Настройка логирования
from services.logger_config import setup_logging
from config import ENV
import logging

json_format = ENV == "prod"
setup_logging(level="INFO", json_format=json_format)
logger = logging.getLogger(__name__)

app = FastAPI(title="PAZL Collab API")

# ==========================
# 🛡️ Rate Limiting
# ==========================
# Простой in-memory rate limiter
rate_limit_store = defaultdict(list)
RATE_LIMIT_REQUESTS = 100  # Максимум запросов
RATE_LIMIT_WINDOW = 60  # За окно в секундах

# ==========================
# 📝 Логирование запросов
# ==========================
@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    """
    Логирование всех запросов для отладки
    """
    start_time = time.time()
    
    # Логируем входящий запрос
    logger.info(f"→ {request.method} {request.url.path} | Client: {request.client.host if request.client else 'unknown'}")
    
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        logger.info(f"← {request.method} {request.url.path} | Status: {response.status_code} | Time: {process_time:.3f}s")
        return response
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(f"✗ {request.method} {request.url.path} | Error: {str(e)} | Time: {process_time:.3f}s", exc_info=True)
        raise


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """Rate limiting middleware для защиты от злоупотреблений"""
    # Пропускаем статические файлы
    if request.url.path.startswith("/webapp/assets"):
        return await call_next(request)
    
    # Получаем IP клиента
    client_ip = request.client.host if request.client else "unknown"
    
    # Проверяем rate limit
    now = time.time()
    window_start = now - RATE_LIMIT_WINDOW
    
    # Очищаем старые записи
    rate_limit_store[client_ip] = [
        timestamp for timestamp in rate_limit_store[client_ip]
        if timestamp > window_start
    ]
    
    # Проверяем лимит
    if len(rate_limit_store[client_ip]) >= RATE_LIMIT_REQUESTS:
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "error": "Too many requests",
                "message": f"Rate limit exceeded. Maximum {RATE_LIMIT_REQUESTS} requests per {RATE_LIMIT_WINDOW} seconds."
            }
        )
    
    # Добавляем текущий запрос
    rate_limit_store[client_ip].append(now)
    
    # Продолжаем обработку
    response = await call_next(request)
    return response

# ==========================
# 📱 Подключение Mini App (React build)
# ==========================

BASE_DIR = os.path.dirname(os.path.dirname(__file__))   # pazl-collab-bot/
FRONTEND_DIST = os.path.join(BASE_DIR, "frontend", "dist")

# 1️⃣ Ассеты (CSS/JS) - должен быть ПЕРВЫМ
app.mount(
    "/webapp/assets",
    StaticFiles(directory=os.path.join(FRONTEND_DIST, "assets")),
    name="webapp-assets"
)


# ==========================
# 🌍 CORS
# ==========================
# Разрешаем только домены Telegram для безопасности
TELEGRAM_ORIGINS = [
    "https://web.telegram.org",
    "https://webk.telegram.org",
    "https://webz.telegram.org",
]

# В dev режиме разрешаем localhost
ALLOWED_ORIGINS = TELEGRAM_ORIGINS.copy()
if os.getenv("ENV", "dev") == "dev":
    ALLOWED_ORIGINS.extend([
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ])

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# ==========================
# ⚙️ Airtable
# ==========================
from services.airtable_client import get_airtable_client

TABLE_NAME = "Experts"


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
    try:
        client = get_airtable_client()
        formula = f"{{TelegramID}}={telegram_id}"
        records = client.get_records(table_name=TABLE_NAME, formula=formula, max_records=1)
        
        if not records:
            raise HTTPException(status_code=404, detail="Profile not found")
        
        return format_expert_record(records[0])

    except HTTPException:
        raise
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error fetching profile for {telegram_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


# ==========================
# 🔎 Эксперт по record_id
# ==========================
@app.get("/api/expert/{record_id}")
def get_expert(record_id: str):
    try:
        client = get_airtable_client()
        record = client.get_record(table_name=TABLE_NAME, record_id=record_id)
        return format_expert_record(record)
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error fetching expert {record_id}: {e}", exc_info=True)
        raise HTTPException(status_code=404, detail="Expert not found")


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
        "telegram_id": str(fields.get("TelegramID", "")) if fields.get("TelegramID") is not None else "",
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
# 🤝 Предложение партнерства
# ==========================
class PartnershipRequest(BaseModel):
    from_user_id: str
    to_user_id: str

@app.post("/api/partnership/request")
async def request_partnership(request: PartnershipRequest):
    """
    Отправляет предложение партнерства от одного пользователя другому
    """
    import logging
    from services.partnership_storage import get_partnership_storage, PartnershipStatus
    
    logger = logging.getLogger(__name__)
    
    logger.info(f"📥 Received partnership request: from={request.from_user_id}, to={request.to_user_id}")
    
    try:
        # Проверяем, нет ли уже pending предложения
        storage = get_partnership_storage()
        if storage.has_pending_partnership(request.from_user_id, request.to_user_id):
            raise HTTPException(
                status_code=400,
                detail="Partnership request already sent and pending"
            )
        
        # Получаем информацию о пользователях из Airtable
        client = get_airtable_client()
        
        logger.info(f"Looking for users: from={request.from_user_id}, to={request.to_user_id}")
        
        # Проверяем, что это не debug-user
        if request.from_user_id == "debug-user" or request.to_user_id == "debug-user":
            logger.error(f"Invalid user ID: from={request.from_user_id}, to={request.to_user_id}")
            raise HTTPException(
                status_code=400, 
                detail="Cannot send partnership request from debug mode. Please open the app through Telegram."
            )
        
        from_formula = f"{{TelegramID}}={request.from_user_id}"
        to_formula = f"{{TelegramID}}={request.to_user_id}"
        
        from_records = client.get_records(table_name=TABLE_NAME, formula=from_formula, max_records=1)
        to_records = client.get_records(table_name=TABLE_NAME, formula=to_formula, max_records=1)
        
        logger.info(f"Found records: from={len(from_records) if from_records else 0}, to={len(to_records) if to_records else 0}")
        
        if not from_records:
            logger.error(f"User not found in Airtable: from_user_id={request.from_user_id}")
            raise HTTPException(status_code=404, detail=f"From user not found: {request.from_user_id}")
        
        if not to_records:
            logger.error(f"User not found in Airtable: to_user_id={request.to_user_id}")
            raise HTTPException(status_code=404, detail=f"To user not found: {request.to_user_id}")
        
        from_user = format_expert_record(from_records[0])
        to_user = format_expert_record(to_records[0])
        
        # Создаем запись о партнерстве
        partnership_id = storage.create_partnership(
            from_user_id=request.from_user_id,
            to_user_id=request.to_user_id,
            metadata={
                "from_user_name": from_user.get("name"),
                "to_user_name": to_user.get("name")
            }
        )
        
        # Отправляем сообщение через Telegram Bot API
        bot_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        
        # Сообщение для получателя
        message_text = (
            f"🤝 *Предложение партнерства*\n\n"
            f"Пользователь *{from_user.get('name', 'Неизвестно')}* хочет стать вашим партнером!\n\n"
            f"📋 *Информация о партнере:*\n"
            f"• Направление: {from_user.get('direction', '—')}\n"
            f"• Город: {from_user.get('city', '—')}\n"
            f"• Язык: {from_user.get('language', '—')}\n\n"
            f"Выберите действие:"
        )
        
        # Создаем клавиатуру с кнопками
        keyboard = {
            "inline_keyboard": [
                [
                    {"text": "✅ Согласиться", "callback_data": f"partnership_accept_{request.from_user_id}_{request.to_user_id}"},
                    {"text": "❌ Отказать", "callback_data": f"partnership_decline_{request.from_user_id}_{request.to_user_id}"}
                ]
            ]
        }
        
        logger.info(f"Sending partnership message to user {request.to_user_id} from {request.from_user_id}")
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    bot_url,
                    json={
                        "chat_id": int(request.to_user_id),
                        "text": message_text,
                        "parse_mode": "Markdown",
                        "reply_markup": keyboard
                    },
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    response_text = await response.text()
                    logger.info(f"Telegram API response: status={response.status}, body={response_text[:200]}")
                    
                    if response.status != 200:
                        # Парсим ответ от Telegram API для более детальной ошибки
                        try:
                            import json
                            error_data = json.loads(response_text)
                            error_description = error_data.get("description", response_text)
                        except:
                            error_description = response_text
                        
                        logger.error(f"Failed to send Telegram message. Status: {response.status}, Error: {error_description}")
                        # Обновляем статус на cancelled при ошибке отправки
                        storage.update_status(partnership_id, PartnershipStatus.CANCELLED)
                        raise HTTPException(
                            status_code=500, 
                            detail=f"Failed to send message to user: {error_description}"
                        )
                    
                    logger.info(f"Telegram message sent successfully to user {request.to_user_id}")
        except aiohttp.ClientError as e:
            logger.error(f"Network error sending Telegram message: {e}")
            storage.update_status(partnership_id, PartnershipStatus.CANCELLED)
            raise HTTPException(
                status_code=500,
                detail=f"Network error sending message: {str(e)}"
            )
        
        logger.info(f"Partnership request created: {partnership_id} from {request.from_user_id} to {request.to_user_id}")
        
        return {
            "success": True,
            "message": "Partnership request sent successfully",
            "partnership_id": partnership_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating partnership request: {e}", exc_info=True)
        import traceback
        error_details = traceback.format_exc()
        logger.error(f"Full traceback: {error_details}")
        raise HTTPException(
            status_code=500, 
            detail=f"Internal server error: {str(e)}"
        )


# ==========================
# 🏁 Root
# ==========================
@app.get("/")
def root():
    return {"message": "✅ PAZL Collab API is running"}


# ==========================
# 📱 SPA Fallback (должен быть ПОСЛЕДНИМ)
# Любые /webapp/... → index.html для React Router
# ==========================
@app.get("/webapp")
@app.get("/webapp/{path:path}")
async def serve_webapp(path: str = ""):
    """
    SPA fallback: отдает index.html для всех маршрутов /webapp/*
    React Router обработает маршрутизацию на клиенте
    Важно для Telegram Mini App: отдаем index.html для всех путей
    """
    index_path = os.path.join(FRONTEND_DIST, "index.html")
    if not os.path.exists(index_path):
        return {
            "error": "Frontend not built. Run 'npm run build' in frontend directory.",
            "path": index_path
        }
    # Важно для Telegram Mini App: правильные заголовки
    return FileResponse(
        index_path,
        media_type="text/html",
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0",
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "SAMEORIGIN",
            # Разрешаем загрузку в iframe Telegram
            "Content-Security-Policy": "frame-ancestors 'self' https://web.telegram.org https://webk.telegram.org https://webz.telegram.org;"
        }
    )
