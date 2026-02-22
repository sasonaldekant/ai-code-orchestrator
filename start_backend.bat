@echo off
setlocal enabledelayedexpansion

echo ==========================================
echo AI Code Orchestrator - Startup ^& Health Check
echo ==========================================

:: Detect Python
set PYTHON_EXE=python
if exist ".venv\Scripts\python.exe" (
    set PYTHON_EXE=.venv\Scripts\python.exe
    echo [INFO] Using virtual environment: .venv
) else (
    echo [WARN] .venv not found, using global python.
)

:: Start Services
echo [Step 2/5] Starting Backend API...
start "AIO - Backend API" cmd /k "%PYTHON_EXE% -m uvicorn api.app:app --reload --port 8000"

timeout /t 2 /nobreak > nul


echo ==========================================
echo All services launched successfully.
echo - Backend:    http://localhost:8000
echo ==========================================
pause
