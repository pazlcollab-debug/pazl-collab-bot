# Полный перезапуск проекта
Write-Host "🔄 Полный перезапуск проекта..." -ForegroundColor Cyan

# Останавливаем все процессы Python и Node
Write-Host "`n⏹️  Остановка всех процессов..." -ForegroundColor Yellow
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Get-Process node -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Get-Process npm -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue

Start-Sleep -Seconds 2

Write-Host "✅ Все процессы остановлены" -ForegroundColor Green
Write-Host "`n🚀 Запуск проекта..." -ForegroundColor Cyan
Write-Host "`nОткройте 3 отдельных окна PowerShell и выполните:" -ForegroundColor Yellow
Write-Host "`n1️⃣  FastAPI (окно 1):" -ForegroundColor Cyan
Write-Host "   .\venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host "   uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload" -ForegroundColor White
Write-Host "`n2️⃣  Telegram Bot (окно 2):" -ForegroundColor Cyan
Write-Host "   .\venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host "   python main.py" -ForegroundColor White
Write-Host "`n3️⃣  Frontend (окно 3):" -ForegroundColor Cyan
Write-Host "   cd frontend" -ForegroundColor White
Write-Host "   npm run dev" -ForegroundColor White
Write-Host "`nИли используйте: .\start.ps1" -ForegroundColor Green

