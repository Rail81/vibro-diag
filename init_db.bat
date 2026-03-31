@echo off
echo Инициализация базы данных...

:: Проверка наличия виртуального окружения
if not exist venv (
    echo Виртуальное окружение не найдено! Сначала запустите setup_offline.bat
    pause
    exit /b
)

:: Активация виртуального окружения
call venv\Scripts\activate

:: Проверка наличия PostgreSQL
if not exist "C:\Program Files\PostgreSQL\15\bin\psql.exe" (
    echo PostgreSQL не установлен!
    pause
    exit /b
)

:: Пересоздание базы данных
echo Пересоздание базы данных...
set PGPASSWORD=159950707
set PATH=%PATH%;C:\Program Files\PostgreSQL\15\bin
"C:\Program Files\PostgreSQL\15\bin\psql.exe" -U postgres -c "DROP DATABASE IF EXISTS vibro_diagnostics" -h localhost
"C:\Program Files\PostgreSQL\15\bin\psql.exe" -U postgres -c "CREATE DATABASE vibro_diagnostics" -h localhost

:: Инициализация базы данных тестовыми данными
echo Инициализация тестовых данных...
python init_db.py

echo Инициализация базы данных завершена!
pause 