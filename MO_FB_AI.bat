@echo off
chcp 65001 >nul
echo Dang kiem tra Python...
where python >nul 2>nul
if errorlevel 1 (
    echo [LOI] Chua cai Python. Vao python.org/downloads de cai, nho tick "Add Python to PATH".
    pause
    exit /b 1
)

echo Dang cai thu vien can thiet (flask, requests)...
python -m pip install -r "%~dp0fb_ai_manager\requirements.txt" >nul

echo Dang mo FB AI Manager...
python "%~dp0fb_ai_manager\run.py"
pause
