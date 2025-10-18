@echo off
REM Voxel Web Interface Startup Script for Windows

echo Starting Voxel Web Interface...
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo Virtual environment not found. Creating...
    python -m venv venv
    echo Virtual environment created
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if dependencies are installed
python -c "import flask" 2>nul
if errorlevel 1 (
    echo Installing dependencies...
    pip install -e .
    echo Dependencies installed
)

REM Check for .env file
if not exist ".env" (
    echo .env file not found!
    echo Please create a .env file copy from .env.example and configure it.
    echo.
    echo Required settings:
    echo - AI_PROVIDER and AI_MODEL
    echo - ANTHROPIC_API_KEY or OPENAI_API_KEY
    echo - BLENDER_PATH
    echo.
    pause
    exit /b 1
)

REM Create necessary directories
if not exist "uploads" mkdir uploads
if not exist "output" mkdir output
if not exist "logs" mkdir logs

echo.
echo Starting web server...
echo Access the interface at: http://localhost:5000
echo Press Ctrl+C to stop
echo.

REM Start the web server
voxel-web
