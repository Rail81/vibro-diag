@echo off
echo Настройка окружения для приложения вибродиагностики...

:: Проверка наличия Python
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Python не установлен! Пожалуйста, установите Python 3.7 или выше.
    pause
    exit /b
)

:: Установка Visual C++ Redistributable
echo Установка Visual C++ Redistributable...
powershell -Command "& { Invoke-WebRequest -Uri 'https://aka.ms/vs/17/release/vc_redist.x64.exe' -OutFile 'vc_redist.x64.exe' }"
start /wait vc_redist.x64.exe /quiet /norestart
del vc_redist.x64.exe

:: Создание и активация виртуального окружения
echo Создание виртуального окружения...
if exist venv (
    echo Виртуальное окружение уже существует, пропускаем создание...
) else (
    python -m venv venv
)
call venv\Scripts\activate

:: Обновление pip
echo Обновление pip...
python -m pip install --upgrade pip

:: Установка зависимостей
echo Установка зависимостей...
pip install wheel

:: Установка psycopg2-binary отдельно
echo Установка psycopg2-binary...
pip install --only-binary :all: psycopg2-binary==2.9.9

:: Установка остальных зависимостей
pip install Flask==2.0.1
pip install SQLAlchemy==1.4.23
pip install Flask-SQLAlchemy==2.5.1
pip install python-dotenv==0.19.0
pip install Werkzeug==2.0.1
pip install flask-migrate==3.1.0
pip install pdfkit

:: Создание базы данных
echo Создание базы данных...
set PGPASSWORD=159950707
set PATH=%PATH%;C:\Program Files\PostgreSQL\15\bin
"C:\Program Files\PostgreSQL\15\bin\psql.exe" -U postgres -c "DROP DATABASE IF EXISTS vibro_diagnostics" -h localhost
"C:\Program Files\PostgreSQL\15\bin\psql.exe" -U postgres -c "CREATE DATABASE vibro_diagnostics" -h localhost

:: Инициализация базы данных
echo Инициализация базы данных...
set FLASK_APP=app.py
python app.py

echo Установка завершена!
echo Для запуска приложения используйте run.bat
pause 