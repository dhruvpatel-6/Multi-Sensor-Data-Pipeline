Clear-Host
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "STARTING QUADRUPED REALITY CONVERGENCE SYSTEM PIPELINE" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

Write-Host "[1/3] Launching Edge Sensor HAL Stream (Port 5555)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "python sensor_stream.py"
Start-Sleep -Seconds 2

Write-Host "[2/3] Launching Analytics Worker Engine (Port 5556)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "python analytics_worker.py"
Start-Sleep -Seconds 2

Write-Host "[3/3] Launching Enterprise UI Dashboard Browser Layer..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "streamlit run visualization/view_dashboard.py"

Write-Host ""
Write-Host "Pipeline fully deployed! View running logs in separate shell panels." -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Cyan