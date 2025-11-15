import requests
from config import AIRTABLE_API_KEY, AIRTABLE_BASE_ID
from services.cache import get_cache
from services.airtable_client import get_airtable_client
import logging

logger = logging.getLogger(__name__)

TABLE_NAME = "Experts"
CACHE_TTL = 300  # 5 минут кэширования


def get_approved_experts(use_cache: bool = True):
    """
    Возвращает всех экспертов со статусом 'Approved' или 'Одобрено'
    (поддерживает RU/EN форматы и эмодзи перед статусом)
    С кэшированием для уменьшения нагрузки на Airtable API
    """
    cache = get_cache()
    cache_key = "approved_experts"
    
    # Проверяем кэш
    if use_cache:
        cached = cache.get(cache_key)
        if cached is not None:
            logger.debug("Returning cached experts list")
            return cached
    
    try:
        client = get_airtable_client()
        formula = "OR({Status}='🟢 Approved', {Status}='Approved', {Status}='🟢 Одобрено', {Status}='Одобрено')"
        
        records = client.get_records(
            table_name=TABLE_NAME,
            formula=formula,
            max_records=100
        )

        experts = []
        for record in records:
            fields = record.get("fields", {})
            expert = {
                "id": record.get("id"),
                "telegram_id": str(fields.get("TelegramID", "")) if fields.get("TelegramID") is not None else "",
                "name": fields.get("Name"),
                "city": fields.get("City"),
                "language": fields.get("Language", "ru"),  # 🔹 язык по умолчанию
                "direction": (
                    fields["Direction"][0]
                    if isinstance(fields.get("Direction"), list)
                    else fields.get("Direction")
                ),
                "telegram": fields.get("Telegram"),
                "photo_url": (
                    fields["Photo"][0]["url"]
                    if isinstance(fields.get("Photo"), list) and fields["Photo"]
                    else None
                ),
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
            experts.append(expert)

        # Сохраняем в кэш
        if use_cache:
            cache.set(cache_key, experts, ttl=CACHE_TTL)
            logger.info(f"Cached {len(experts)} approved experts for {CACHE_TTL} seconds")

        return experts

    except Exception as e:
        logger.error(f"Error fetching approved experts: {e}", exc_info=True)
        # В случае ошибки пытаемся вернуть кэшированные данные, если есть
        if use_cache:
            cached = cache.get(cache_key)
            if cached is not None:
                logger.warning("Returning stale cache due to error")
                return cached
        return []
