@echo off

:: Проверка наличия виртуального окружения
if not exist venv (
    echo Виртуальное окружение не найдено! Сначала запустите setup_offline.bat
    pause
    exit /b
)

:: Активация виртуального окружения
call venv\Scripts\activate

:: Установка переменных окружения
set FLASK_APP=app.py
set FLASK_ENV=development

:: Запуск приложения
echo Запуск приложения вибродиагностики...
python app.py

pause 