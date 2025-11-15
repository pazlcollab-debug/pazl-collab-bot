# Скрипт для запуска всех компонентов проекта PAZL Collab Bot

Write-Host "🚀 Запуск PAZL Collab Bot..." -ForegroundColor Green
Write-Host ""

# Проверка виртуального окружения
if (-not (Test-Path "venv\Scripts\Activate.ps1")) {
    Write-Host "❌ Виртуальное окружение не найдено!" -ForegroundColor Red
    Write-Host "Создайте его командой: python -m venv venv" -ForegroundColor Yellow
    exit 1
}

# Активация виртуального окружения
Write-Host "📦 Активация виртуального окружения..." -ForegroundColor Cyan
& .\venv\Scripts\Activate.ps1

Write-Host ""
Write-Host "🔧 Запуск компонентов в отдельных окнах:" -ForegroundColor Yellow
Write-Host ""

# Запуск FastAPI сервера
Write-Host "1️⃣ Запуск FastAPI сервера (порт 8000)..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; .\venv\Scripts\Activate.ps1; Write-Host '🚀 FastAPI Server' -ForegroundColor Green; uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload" -WindowStyle Normal

Start-Sleep -Seconds 2

# Запуск Telegram бота
Write-Host "2️⃣ Запуск Telegram бота..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; .\venv\Scripts\Activate.ps1; Write-Host '🤖 Telegram Bot' -ForegroundColor Green; python main.py" -WindowStyle Normal

Start-Sleep -Seconds 2

# Запуск Frontend dev сервера
Write-Host "3️⃣ Запуск Frontend dev сервера (порт 5173)..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\frontend'; Write-Host '🌐 Frontend Dev Server' -ForegroundColor Green; npm run dev" -WindowStyle Normal

Write-Host ""
Write-Host "✅ Все компоненты запущены!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Доступные сервисы:" -ForegroundColor Yellow
Write-Host "  • FastAPI: http://localhost:8000" -ForegroundColor White
Write-Host "  • Frontend: http://localhost:5173" -ForegroundColor White
Write-Host "  • API Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "💡 Для остановки закройте окна PowerShell или нажмите Ctrl+C в каждом окне" -ForegroundColor Cyan
Write-Host ""

