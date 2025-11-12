import requests
from config import AIRTABLE_API_KEY, AIRTABLE_BASE_ID

TABLE_NAME = "Experts"
AIRTABLE_URL = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{TABLE_NAME}"
HEADERS = {"Authorization": f"Bearer {AIRTABLE_API_KEY}"}


def get_approved_experts():
    """
    Возвращает всех экспертов со статусом 'Approved' или 'Одобрено'
    (поддерживает RU/EN форматы и эмодзи перед статусом)
    """
    formula = "OR({Status}='🟢 Approved', {Status}='Approved', {Status}='🟢 Одобрено', {Status}='Одобрено')"
    params = {"filterByFormula": formula, "maxRecords": 100, "view": "Grid view"}

    try:
        response = requests.get(AIRTABLE_URL, headers=HEADERS, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if "records" not in data:
            print("⚠️ Ответ Airtable не содержит ключ 'records':", data)
            return []

        experts = []
        for record in data["records"]:
            fields = record.get("fields", {})
            expert = {
                "id": record.get("id"),
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

        return experts

    except requests.Timeout:
        print("⏳ Ошибка: превышено время ожидания ответа Airtable")
        return []

    except requests.RequestException as e:
        print(f"🚨 Ошибка запроса к Airtable: {e}")
        return []

    except Exception as e:
        print(f"⚠️ Неизвестная ошибка при получении экспертов: {e}")
        return []
