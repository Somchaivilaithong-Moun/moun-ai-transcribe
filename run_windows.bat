@echo off
chcp 65001 > nul
cd /d "%~dp0"
echo =============================================
echo        MOUN AI TRANSCRIBE - LOCAL RUN
echo =============================================
echo.
echo Dang cai/kiem tra thu vien...
py -m pip install -r requirements.txt
if errorlevel 1 (
  echo.
  echo Cai thu vien that bai. Hay kiem tra Python va Internet.
  pause
  exit /b 1
)
echo.
echo Dang mo website local...
py -m streamlit run app.py
pause
