@echo off

:: Check for virtual environment
if not exist venv (
    echo Virtual environment not found! Please run setup.bat first.
    pause
    exit /b
)

:: Activate virtual environment
call venv\Scripts\activate

:: Set Flask environment variables
set FLASK_APP=app.py
set FLASK_ENV=development

:: Run the application
echo Starting vibro-diagnostics application...
flask run

pause