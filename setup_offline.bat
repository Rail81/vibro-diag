@echo off
echo Настройка окружения для приложения вибродиагностики...

:: Проверка наличия Python
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Python не установлен! Установите Python из папки installers\python-3.9.7-amd64.exe
    pause
    exit /b
)

:: Проверка наличия PostgreSQL
if not exist "C:\Program Files\PostgreSQL\15\bin\psql.exe" (
    echo PostgreSQL не установлен! Установите PostgreSQL из папки installers\postgresql-15.5-windows-x64.exe
    pause
    exit /b
)

:: Проверка наличия wkhtmltopdf
if not exist "C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe" (
    echo wkhtmltopdf не установлен! Установите wkhtmltopdf из папки installers\wkhtmltopdf-64bit.exe
    pause
    exit /b
)

:: Создание и активация виртуального окружения
echo Создание виртуального окружения...
if exist venv (
    echo Удаление старого виртуального окружения...
    rmdir /s /q venv
)
python -m venv venv
call venv\Scripts\activate

:: Установка зависимостей из локальных файлов
echo Установка зависимостей...
pip install --no-index --find-links=./wheels wheel
pip install --no-index --find-links=./wheels -r requirements.txt

:: Создание базы данных
echo Создание базы данных...
set PGPASSWORD=159950707
set PATH=%PATH%;C:\Program Files\PostgreSQL\15\bin
"C:\Program Files\PostgreSQL\15\bin\psql.exe" -U postgres -c "DROP DATABASE IF EXISTS vibro_diagnostics" -h localhost
"C:\Program Files\PostgreSQL\15\bin\psql.exe" -U postgres -c "CREATE DATABASE vibro_diagnostics" -h localhost

:: Инициализация базы данных
echo Инициализация базы данных...
python init_db.py

echo Установка завершена!
echo Для запуска приложения используйте run.bat
pause 