# 🚀 Инструкция по запуску проекта

## Быстрый запуск

### Windows PowerShell:
```powershell
.\start.ps1
```

### Windows CMD:
```cmd
start.bat
```

### Ручной запуск:

#### 1. FastAPI сервер (порт 8000)
```powershell
.\venv\Scripts\Activate.ps1
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

#### 2. Telegram бот
```powershell
.\venv\Scripts\Activate.ps1
python main.py
```

#### 3. Frontend dev сервер (порт 5173)
```powershell
cd frontend
npm run dev
```

## 📋 Доступные сервисы

После запуска будут доступны:

- **FastAPI API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Frontend Dev Server**: http://localhost:5173
- **WebApp (через API)**: http://localhost:8000/webapp

## ⚙️ Требования

1. Python 3.12+ с виртуальным окружением
2. Node.js и npm
3. Переменные окружения в `.env` файле:
   - `BOT_TOKEN` - токен Telegram бота
   - `AIRTABLE_API_KEY` - API ключ Airtable
   - `AIRTABLE_BASE_ID` - ID базы Airtable
   - `WEBAPP_URL` - URL веб-приложения (опционально)
   - `ENV` - окружение (dev/prod, по умолчанию dev)

## 🛑 Остановка

Для остановки всех сервисов:
- Закройте окна PowerShell/CMD
- Или нажмите `Ctrl+C` в каждом окне

## 📝 Примечания

- Скрипты `start.ps1` и `start.bat` запускают все компоненты в отдельных окнах
- В dev режиме CORS разрешает localhost для разработки
- Логи сохраняются в папке `logs/`

