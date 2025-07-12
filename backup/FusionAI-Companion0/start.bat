@echo off
echo FusionAI Companion - Windows Startup Script
echo ==========================================

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

REM Check if we're in the right directory
if not exist "docker-compose.yml" (
    echo Error: Please run this script from the FusionAI-Companion root directory
    pause
    exit /b 1
)

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating Python virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install/upgrade dependencies
echo Installing Python dependencies...
pip install -r requirements.txt

REM Check if .env file exists
if not exist ".env" (
    echo Creating .env file from template...
    copy .env.example .env
    echo.
    echo IMPORTANT: Please edit .env file with your API keys before continuing
    echo Press any key to open .env file in notepad...
    pause
    notepad .env
)

REM Start Docker services
echo Starting Docker services...
docker-compose up -d

REM Wait for services to start
echo Waiting for services to initialize...
timeout /t 30 /nobreak

REM Start the main application
echo Starting FusionAI Companion...
python main.py

pause
