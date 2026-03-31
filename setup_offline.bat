@echo off
echo Configuring the environment for the vibro-diagnostics application (offline)...

:: Check for Python
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Python is not installed! Please install it first.
    pause
    exit /b
)

:: Create and activate virtual environment
echo Creating virtual environment...
if not exist venv (
    python -m venv venv
)
call venv\Scripts\activate

:: Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

:: Install dependencies
echo Installing Python dependencies...
pip install -r requirements.txt

echo.
echo Setup complete!
echo.
echo NEXT STEPS:
_e_cho 1. Create a .env file in the root of the project.
echo 2. Fill in your database connection details.
echo 3. Create and initialize the database (see README.md).
echo 4. Run the application using: run.bat
pause