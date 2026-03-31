@echo off
echo Initializing the database with test data...

:: Check for virtual environment
if not exist venv (
    echo Virtual environment not found! Please run setup.bat first.
    pause
    exit /b
)

:: Activate virtual environment
call venv\Scripts\activate

:: Run the database initialization script
python init_db.py

echo Database initialization complete!
pause