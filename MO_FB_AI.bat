@echo off
chcp 65001 >nul
setlocal
set "BASE=%~dp0"
set "VENV=%BASE%fb_ai_manager\venv"

echo Dang kiem tra Python...
where python >nul 2>nul
if errorlevel 1 (
    echo [LOI] Chua cai Python. Vao python.org/downloads de cai, nho tick "Add Python to PATH".
    pause
    exit /b 1
)

if not exist "%VENV%\Scripts\python.exe" (
    echo Dang tao moi truong ao rieng cho tool (lan dau se hoi lau)...
    python -m venv "%VENV%"
)

echo Dang cai thu vien can thiet (flask, requests) trong moi truong ao...
"%VENV%\Scripts\python.exe" -m pip install -q -r "%BASE%fb_ai_manager\requirements.txt"

echo Dang mo FB AI Manager...
"%VENV%\Scripts\python.exe" "%BASE%fb_ai_manager\run.py"
pause
