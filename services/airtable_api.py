from pyairtable import Table, Base
from config import AIRTABLE_API_KEY, AIRTABLE_BASE_ID

def get_table(table_name='Experts'):
    return Table(AIRTABLE_API_KEY, AIRTABLE_BASE_ID, table_name)

async def create_expert_record(data: dict):
    """Создаёт запись эксперта в Airtable (Status=Pending по умолчанию)"""
    table = get_table()
    data['Status'] = 'Pending'  # По ТЗ Шаг 5
    data['Language'] = data.get('lang', 'ru')  # Из Шага 1
    print(f"Создаём запись в Airtable: {data}")  # Тест; раскомментируйте ниже для реального сохранения
    # record = table.create(data)
    # return record['id']
    return {'id': 'test_record_id', 'success': True}  # Заглушка для теста

async def update_expert_status(expert_id: str, status: str):
    """Обновляет статус (Approved для Шага 5)"""
    table = get_table()
    print(f"Обновляем статус {expert_id} на {status}")
    # table.update(expert_id, {'Status': status})
    return True  # Заглушка
