@echo off
:: ===============================================================
:: Vibro-Diagnostics Universal Start Script
::
:: This script handles everything:
:: 1. Creates a virtual environment if it doesn't exist.
:: 2. Installs the correct, tested dependencies.
:: 3. Starts the application.
:: ===============================================================
echo.
echo ** Vibro-Diagnostics **

:: Step 1: Set up the virtual environment
if exist venv (
    echo Virtual environment found. Activating...
) else (
    echo Virtual environment not found. Creating it now...
    python -m venv venv
)
call venv\Scripts\activate
echo.

:: Step 2: Install all dependencies
echo Installing required packages (this may take a moment)...
:: We install packages directly to avoid issues with requirements.txt
python -m pip install --upgrade pip setuptools > nul
python -m pip install Flask==2.2.2 Werkzeug==2.2.2 SQLAlchemy==2.0.0 Flask-SQLAlchemy==3.0.3 psycopg2-binary==2.9.9 python-dotenv==1.0.1 flask-migrate==4.0.5 pdfkit==1.0.0 > nul
echo Dependencies are up to date.
echo.

:: Step 3: Run the application
echo Starting the application...
echo Find it at http://127.0.0.1:5000
set FLASK_APP=app.py
set FLASK_ENV=development
flask run

pause