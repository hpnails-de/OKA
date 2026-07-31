@echo off
chcp 65001 >nul
title OKA - Thay Thuoc Cho Code

echo.
echo ============================================
echo   OKA - Cong cu chan doan du an cho AI
echo ============================================
echo.

where python >nul 2>nul
if errorlevel 1 (
    echo [LOI] May nay chua co Python.
    echo.
    echo Cai mien phi tai: https://www.python.org/downloads/
    echo Khi cai, nho TICK vao o "Add Python to PATH" o man hinh dau tien.
    echo Cai xong thi mo lai file nay.
    echo.
    pause
    exit /b 1
)

echo Dang mo OKA...
python "%~dp0oka_don_gian.py"

if errorlevel 1 (
    echo.
    echo [LOI] OKA dong bat thuong. Chup man hinh loi tren va bao cho tac gia qua Issues tren GitHub.
    pause
)
