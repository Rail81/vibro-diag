@echo off
chcp 65001 > nul
:: ===============================================================
:: Interactive Environment Configuration
:: ===============================================================
echo.
echo ** Настройка файла конфигурации (.env) **

echo Пожалуйста, введите данные для подключения к базе данных PostgreSQL.

set /p DB_HOST="Хост базы данных (нажмите Enter для localhost): "
if "%DB_HOST%"=="" set DB_HOST=localhost

set /p DB_PORT="Порт базы данных (нажмите Enter для 5432): "
if "%DB_PORT%"=="" set DB_PORT=5432

set /p DB_USER="Имя пользователя (нажмите Enter для postgres): "
if "%DB_USER%"=="" set DB_USER=postgres

set /p DB_PASS="Пароль пользователя: "

set /p DB_NAME="Имя базы данных (нажмите Enter для vibro_diagnostics): "
if "%DB_NAME%"=="" set DB_NAME=vibro_diagnostics

:: Generate a simple secret key
set "SECRET_KEY=%RANDOM%%RANDOM%-%RANDOM%-%RANDOM%"

:: Create the .env file
(echo SECRET_KEY='%SECRET_KEY%'
 echo DATABASE_URL='postgresql://%DB_USER%:%DB_PASS%@%DB_HOST%:%DB_PORT%/%DB_NAME%'
 echo WKHTMLTOPDF_PATH='C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
) > .env

echo.
echo Файл .env успешно создан!
echo.
echo ** Следующие шаги: **
_e_cho 1. Убедитесь, что база данных '%DB_NAME%' существует на сервере PostgreSQL.
_e_cho 2. Запустите 'python init_db.py' для создания таблиц.
_e_cho 3. Запустите 'start.bat' для запуска приложения.
echo.
pause