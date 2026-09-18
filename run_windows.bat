@echo off
chcp 65001 >nul
title Moun AI Transcribe

echo ==========================================
echo       MOUN AI TRANSCRIBE - WINDOWS
echo ==========================================
echo.

echo [1/2] Dang cai/cap nhat thu vien...
py -m pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo Khong cai duoc thu vien. Hay kiem tra Python va Internet.
    pause
    exit /b 1
)

echo.
echo [2/2] Dang mo website local...
py -m streamlit run app.py

pause
