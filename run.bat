@echo off
:: ===============================================================
:: Vibro-Diagnostics Quick Run Script
:: ===============================================================

if not exist venv\Scripts\activate (
    echo [!] Виртуальное окружение не найдено. Сначала запустите setup.bat
    pause
    exit /b
)

:: Activate virtual environment and run
call venv\Scripts\activate
set FLASK_APP=app.py
set FLASK_ENV=development

echo Starting application...
flask run