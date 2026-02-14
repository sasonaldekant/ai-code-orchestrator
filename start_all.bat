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

:: 1. Syntax & Build Check
echo [Step 1/4] Verifying integrity...

echo Checking Backend syntax...
%PYTHON_EXE% -m py_compile api\app.py api\admin_routes.py api\config_routes.py api\knowledge_routes.py
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Backend syntax check failed! Fix errors before starting.
    pause
    exit /b %ERRORLEVEL%
)

echo Checking UI types...
cd ui && call npx tsc --noEmit && cd ..
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] UI TypeScript check failed!
    pause
    exit /b %ERRORLEVEL%
)

echo Checking Extension compilation...
cd vscode-extension && call npm run compile && cd ..
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] VS Code Extension compilation failed!
    pause
    exit /b %ERRORLEVEL%
)

echo [SUCCESS] All components passed integrity check.
echo.

:: Start Services
echo [Step 2/4] Starting Backend API...
start "AIO - Backend API" cmd /k "%PYTHON_EXE% -m uvicorn api.app:app --reload --port 8000"

timeout /t 2 /nobreak > nul

echo [Step 3/4] Starting Web UI...
start "AIO - Web UI" cmd /k "cd ui && npm run dev"

echo [Step 4/4] Starting Extension Watcher...
start "AIO - Ext Watcher" cmd /k "cd vscode-extension && npm run watch"

echo.
echo ==========================================
echo All services launched successfully.
echo - Backend: http://localhost:8000
echo - Web UI:  Check Vite output
echo ==========================================
pause
