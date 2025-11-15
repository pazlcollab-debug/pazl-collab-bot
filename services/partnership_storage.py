"""
Хранилище для предложений партнерства
В будущем можно мигрировать на Airtable таблицу "Partnerships"
"""
from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum
import json
import os


class PartnershipStatus(Enum):
    """Статусы предложения партнерства"""
    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    CANCELLED = "cancelled"


class PartnershipStorage:
    """Простое хранилище партнерств (in-memory, можно заменить на Airtable)"""
    
    def __init__(self, storage_file: str = "logs/partnerships.json"):
        self.storage_file = storage_file
        self._partnerships: Dict[str, Dict] = {}
        self._load_from_file()
    
    def _load_from_file(self):
        """Загружает данные из файла"""
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self._partnerships = data
            except Exception as e:
                print(f"Warning: Could not load partnerships from file: {e}")
    
    def _save_to_file(self):
        """Сохраняет данные в файл"""
        try:
            os.makedirs(os.path.dirname(self.storage_file), exist_ok=True)
            with open(self.storage_file, "w", encoding="utf-8") as f:
                json.dump(self._partnerships, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Warning: Could not save partnerships to file: {e}")
    
    def create_partnership(
        self,
        from_user_id: str,
        to_user_id: str,
        metadata: Optional[Dict] = None
    ) -> str:
        """
        Создает новое предложение партнерства
        
        Returns:
            ID предложения
        """
        partnership_id = f"{from_user_id}_{to_user_id}_{int(datetime.now().timestamp())}"
        
        partnership = {
            "id": partnership_id,
            "from_user_id": from_user_id,
            "to_user_id": to_user_id,
            "status": PartnershipStatus.PENDING.value,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        self._partnerships[partnership_id] = partnership
        self._save_to_file()
        
        return partnership_id
    
    def get_partnership(self, partnership_id: str) -> Optional[Dict]:
        """Получает предложение по ID"""
        return self._partnerships.get(partnership_id)
    
    def get_partnerships_by_user(self, user_id: str) -> List[Dict]:
        """Получает все предложения, связанные с пользователем"""
        return [
            p for p in self._partnerships.values()
            if p["from_user_id"] == user_id or p["to_user_id"] == user_id
        ]
    
    def update_status(
        self,
        partnership_id: str,
        status: PartnershipStatus,
        metadata: Optional[Dict] = None
    ) -> bool:
        """Обновляет статус предложения"""
        if partnership_id not in self._partnerships:
            return False
        
        self._partnerships[partnership_id]["status"] = status.value
        self._partnerships[partnership_id]["updated_at"] = datetime.now().isoformat()
        
        if metadata:
            self._partnerships[partnership_id]["metadata"].update(metadata)
        
        self._save_to_file()
        return True
    
    def has_pending_partnership(self, from_user_id: str, to_user_id: str) -> bool:
        """Проверяет, есть ли уже pending предложение между пользователями"""
        for p in self._partnerships.values():
            if (p["from_user_id"] == from_user_id and 
                p["to_user_id"] == to_user_id and 
                p["status"] == PartnershipStatus.PENDING.value):
                return True
        return False


# Глобальный экземпляр хранилища
_partnership_storage = None


def get_partnership_storage() -> PartnershipStorage:
    """Получает глобальный экземпляр хранилища партнерств"""
    global _partnership_storage
    if _partnership_storage is None:
        _partnership_storage = PartnershipStorage()
    return _partnership_storage

