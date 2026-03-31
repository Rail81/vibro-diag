@echo off
chcp 65001 > nul
:: ===============================================================
:: Vibro-Diagnostics Universal Start Script
:: ===============================================================
echo.
echo ** Vibro-Diagnostics **

:: Step 0: Check for .env file
if not exist .env (
    echo.
    echo  [!] Файл конфигурации .env не найден!
    echo      Пожалуйста, сначала запустите configure.bat для его создания.
    echo.
    pause
    exit /b
)

:: Step 1: Set up the virtual environment
if exist venv (
    echo [1/2] Виртуальное окружение найдено. Активация...
) else (
    echo [1/2] Виртуальное окружение не найдено. Создание...
    python -m venv venv
)
call venv\Scripts\activate

:: Step 2: Install all dependencies
echo [2/2] Установка и проверка зависимостей...
python -m pip install --upgrade pip setuptools > nul
python -m pip install Flask==2.2.2 Werkzeug==2.2.2 SQLAlchemy==2.0.0 Flask-SQLAlchemy==3.0.3 psycopg2-binary==2.9.9 python-dotenv==1.0.1 flask-migrate==4.0.5 pdfkit==1.0.0 > nul

:: Step 3: Run the application
echo.
echo --- Запуск приложения ---
echo URL: http://127.0.0.1:5000
set FLASK_APP=app.py
set FLASK_ENV=development
flask run

pause