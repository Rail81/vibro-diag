@echo off
echo Установка приложения вибродиагностики...
echo.

:: Проверка прав администратора
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo Требуются права администратора! Запустите от имени администратора.
    pause
    exit /b
)

:: Создание рабочей директории
set INSTALL_DIR=C:\vibro_diagnostics
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"
cd /d "%INSTALL_DIR%"

:: Установка Python
if not exist "C:\Python39\python.exe" (
    echo Установка Python 3.9...
    if not exist "installers\python-3.9.7-amd64.exe" (
        echo Ошибка: Не найден установщик Python!
        echo Скопируйте python-3.9.7-amd64.exe в папку installers
        pause
        exit /b
    )
    start /wait installers\python-3.9.7-amd64.exe /quiet InstallAllUsers=1 PrependPath=1
)

:: Установка PostgreSQL
if not exist "C:\Program Files\PostgreSQL\15\bin\psql.exe" (
    echo Установка PostgreSQL...
    if not exist "installers\postgresql-15.5-windows-x64.exe" (
        echo Ошибка: Не найден установщик PostgreSQL!
        echo Скопируйте postgresql-15.5-windows-x64.exe в папку installers
        pause
        exit /b
    )
    start /wait installers\postgresql-15.5-windows-x64.exe --unattendedmodeui minimal --mode unattended --superpassword 159950707
)

:: Установка wkhtmltopdf
if not exist "C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe" (
    echo Установка wkhtmltopdf...
    if not exist "installers\wkhtmltopdf-64bit.exe" (
        echo Ошибка: Не найден установщик wkhtmltopdf!
        echo Скопируйте wkhtmltopdf-64bit.exe в папку installers
        pause
        exit /b
    )
    start /wait installers\wkhtmltopdf-64bit.exe /S
)

:: Установка Visual C++ Redistributable
echo Установка Visual C++ Redistributable...
if not exist "installers\vc_redist.x64.exe" (
    echo Скачивание Visual C++ Redistributable...
    powershell -Command "& { Invoke-WebRequest -Uri 'https://aka.ms/vs/17/release/vc_redist.x64.exe' -OutFile 'installers\vc_redist.x64.exe' }"
)
start /wait installers\vc_redist.x64.exe /quiet /norestart

:: Создание и активация виртуального окружения
echo Создание виртуального окружения Python...
if exist venv (
    echo Удаление старого виртуального окружения...
    rmdir /s /q venv
)
C:\Python39\python.exe -m venv venv
call venv\Scripts\activate

:: Установка зависимостей Python
echo Установка зависимостей Python...
python -m pip install --upgrade pip
pip install --no-index --find-links=wheels -r requirements.txt

:: Настройка переменных окружения
echo Настройка переменных окружения...
setx FLASK_APP "app.py" /M
setx FLASK_ENV "production" /M
setx DATABASE_URL "postgresql://postgres:159950707@localhost:5432/vibro_diagnostics" /M

:: Создание и инициализация базы данных
echo Создание базы данных...
set PGPASSWORD=159950707
set PATH=%PATH%;C:\Program Files\PostgreSQL\15\bin
psql -U postgres -c "DROP DATABASE IF EXISTS vibro_diagnostics"
psql -U postgres -c "CREATE DATABASE vibro_diagnostics"

:: Инициализация базы данных
echo Инициализация базы данных...
python init_db.py

:: Создание ярлыков на рабочем столе
echo Создание ярлыков...
powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\Desktop\Вибродиагностика.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\run.bat'; $Shortcut.Save()"

echo.
echo Установка завершена!
echo Приложение установлено в %INSTALL_DIR%
echo Ярлык для запуска создан на рабочем столе
echo.
echo Для запуска приложения используйте:
echo 1. Ярлык "Вибродиагностика" на рабочем столе
echo 2. Файл run.bat в папке %INSTALL_DIR%
echo.
pause 