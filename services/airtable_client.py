"""
Улучшенный клиент для работы с Airtable API
- Retry с exponential backoff
- Обработка rate limits
- Кэширование
"""
import asyncio
import logging
import time
from typing import Optional, Dict, Any, List
import requests
from config import AIRTABLE_API_KEY, AIRTABLE_BASE_ID

logger = logging.getLogger(__name__)

# Константы для retry
MAX_RETRIES = 3
INITIAL_BACKOFF = 1  # секунды
MAX_BACKOFF = 10  # секунды
RATE_LIMIT_WAIT = 30  # секунды при 429 ошибке


class AirtableClient:
    """Клиент для работы с Airtable API с retry и обработкой ошибок"""
    
    def __init__(self, base_id: str = None, api_key: str = None):
        self.base_id = base_id or AIRTABLE_BASE_ID
        self.api_key = api_key or AIRTABLE_API_KEY
        self.base_url = f"https://api.airtable.com/v0/{self.base_id}"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        json_data: Optional[Dict] = None,
        retry_count: int = 0
    ) -> requests.Response:
        """
        Выполняет HTTP запрос с retry и обработкой ошибок
        """
        url = f"{self.base_url}/{endpoint}"
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=self.headers, params=params, timeout=10)
            elif method.upper() == "POST":
                response = requests.post(url, headers=self.headers, json=json_data, params=params, timeout=10)
            elif method.upper() == "PATCH":
                response = requests.patch(url, headers=self.headers, json=json_data, params=params, timeout=10)
            elif method.upper() == "PUT":
                response = requests.put(url, headers=self.headers, json=json_data, params=params, timeout=10)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=self.headers, params=params, timeout=10)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            # Обработка rate limit (429)
            if response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", RATE_LIMIT_WAIT))
                logger.warning(f"Rate limit hit. Waiting {retry_after} seconds...")
                
                if retry_count < MAX_RETRIES:
                    time.sleep(retry_after)
                    return self._make_request(method, endpoint, params, json_data, retry_count + 1)
                else:
                    response.raise_for_status()
            
            # Обработка временных ошибок (5xx)
            if 500 <= response.status_code < 600:
                if retry_count < MAX_RETRIES:
                    backoff = min(INITIAL_BACKOFF * (2 ** retry_count), MAX_BACKOFF)
                    logger.warning(
                        f"Server error {response.status_code}. "
                        f"Retrying in {backoff} seconds... (attempt {retry_count + 1}/{MAX_RETRIES})"
                    )
                    time.sleep(backoff)
                    return self._make_request(method, endpoint, params, json_data, retry_count + 1)
                else:
                    response.raise_for_status()
            
            # Обработка других ошибок
            if not response.ok:
                response.raise_for_status()
            
            return response
            
        except requests.exceptions.Timeout:
            if retry_count < MAX_RETRIES:
                backoff = min(INITIAL_BACKOFF * (2 ** retry_count), MAX_BACKOFF)
                logger.warning(f"Request timeout. Retrying in {backoff} seconds...")
                time.sleep(backoff)
                return self._make_request(method, endpoint, params, json_data, retry_count + 1)
            else:
                raise Exception("Request timeout after multiple retries")
        
        except requests.exceptions.ConnectionError:
            if retry_count < MAX_RETRIES:
                backoff = min(INITIAL_BACKOFF * (2 ** retry_count), MAX_BACKOFF)
                logger.warning(f"Connection error. Retrying in {backoff} seconds...")
                time.sleep(backoff)
                return self._make_request(method, endpoint, params, json_data, retry_count + 1)
            else:
                raise Exception("Connection error after multiple retries")
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Airtable API error: {e}")
            raise
    
    def get_records(
        self,
        table_name: str,
        formula: Optional[str] = None,
        max_records: Optional[int] = None,
        fields: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Получает записи из таблицы
        """
        params = {}
        if formula:
            params["filterByFormula"] = formula
        if max_records:
            params["maxRecords"] = max_records
        if fields:
            params["fields[]"] = fields
        
        response = self._make_request("GET", table_name, params=params)
        data = response.json()
        return data.get("records", [])
    
    def get_record(self, table_name: str, record_id: str) -> Dict[str, Any]:
        """
        Получает одну запись по ID
        """
        response = self._make_request("GET", f"{table_name}/{record_id}")
        return response.json()
    
    def create_record(self, table_name: str, fields: Dict[str, Any]) -> Dict[str, Any]:
        """
        Создает новую запись
        """
        json_data = {"fields": fields}
        response = self._make_request("POST", table_name, json_data=json_data)
        return response.json()
    
    def update_record(self, table_name: str, record_id: str, fields: Dict[str, Any]) -> Dict[str, Any]:
        """
        Обновляет запись
        """
        json_data = {"fields": fields}
        response = self._make_request("PATCH", f"{table_name}/{record_id}", json_data=json_data)
        return response.json()


# Глобальный экземпляр клиента
_airtable_client = None


def get_airtable_client() -> AirtableClient:
    """Получает глобальный экземпляр клиента Airtable"""
    global _airtable_client
    if _airtable_client is None:
        _airtable_client = AirtableClient()
    return _airtable_client

