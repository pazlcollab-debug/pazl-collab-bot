@echo off
echo 🚀 Запуск PAZL Collab Bot...
echo.

REM Проверка виртуального окружения
if not exist "venv\Scripts\activate.bat" (
    echo ❌ Виртуальное окружение не найдено!
    echo Создайте его командой: python -m venv venv
    pause
    exit /b 1
)

echo 🔧 Запуск компонентов в отдельных окнах...
echo.

REM Запуск FastAPI сервера
echo 1️⃣ Запуск FastAPI сервера (порт 8000)...
start "FastAPI Server" cmd /k "venv\Scripts\activate.bat && uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload"

timeout /t 2 /nobreak >nul

REM Запуск Telegram бота
echo 2️⃣ Запуск Telegram бота...
start "Telegram Bot" cmd /k "venv\Scripts\activate.bat && python main.py"

timeout /t 2 /nobreak >nul

REM Запуск Frontend dev сервера
echo 3️⃣ Запуск Frontend dev сервера (порт 5173)...
start "Frontend Dev Server" cmd /k "cd frontend && npm run dev"

echo.
echo ✅ Все компоненты запущены!
echo.
echo 📋 Доступные сервисы:
echo   • FastAPI: http://localhost:8000
echo   • Frontend: http://localhost:5173
echo   • API Docs: http://localhost:8000/docs
echo.
echo 💡 Для остановки закройте окна командной строки или нажмите Ctrl+C в каждом окне
echo.
pause

