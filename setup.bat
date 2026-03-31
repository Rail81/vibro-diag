@echo off
echo Configuring the environment for the vibro-diagnostics application...

:: Check for Python
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Python is not installed! Please install Python 3.9 or higher.
    pause
    exit /b
)

:: Create and activate virtual environment
echo Creating virtual environment...
if not exist venv (
    python -m venv venv
)
call venv\Scripts\activate

:: Upgrade pip & setuptools
echo Upgrading pip & setuptools...
python -m pip install --upgrade pip setuptools

:: Install dependencies
echo Installing Python dependencies...
pip install -r requirements.txt

echo.
echo Setup complete!
echo.
echo NEXT STEPS:
_e_cho 1. Create a .env file in the root of the project (you can copy .env.example).
echo 2. Fill in your database connection details in the .env file.
echo 3. Create the database in PostgreSQL.
echo 4. Initialize the database by running: python init_db.py
echo 5. Run the application using: run.bat or flask run
pause