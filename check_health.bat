@echo off
setlocal enabledelayedexpansion

echo ==========================================
echo AI Code Orchestrator - Integrity Check
echo ==========================================

:: Detect Python
set PYTHON_EXE=python
if exist ".venv\Scripts\python.exe" (
    set PYTHON_EXE=.venv\Scripts\python.exe
)

echo Checking Backend syntax...
%PYTHON_EXE% -m py_compile api\app.py api\admin_routes.py api\config_routes.py api\knowledge_routes.py
if %ERRORLEVEL% EQU 0 (
    echo [OK] Backend
) else (
    echo [FAIL] Backend
)

echo Checking UI types...
cd ui && call npx tsc --noEmit && cd ..
if %ERRORLEVEL% EQU 0 (
    echo [OK] UI
) else (
    echo [FAIL] UI
)

echo Checking Extension compilation...
cd vscode-extension && call npm run compile && cd ..
if %ERRORLEVEL% EQU 0 (
    echo [OK] Extension
) else (
    echo [FAIL] Extension
)

echo ==========================================
pause
