@echo off
REM Quick start script for Motion Capture to Blender (Windows)

echo ================================================
echo Motion Capture to Blender - Quick Start
echo ================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed
    echo Please install Python 3.9 or higher
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo Error: Node.js is not installed
    echo Please install Node.js 16 or higher
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
for /f "tokens=*" %%i in ('node --version') do set NODE_VERSION=%%i

echo ✓ %PYTHON_VERSION% found
echo ✓ Node.js %NODE_VERSION% found
echo.

REM Backend setup
echo Setting up backend...
cd backend

if not exist "venv" (
    echo Creating Python virtual environment...
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing Python dependencies...
pip install -q --upgrade pip
pip install -q -r requirements.txt

echo ✓ Backend dependencies installed
echo.

REM Frontend setup
echo Setting up frontend...
cd ..\frontend

if not exist "node_modules" (
    echo Installing Node.js dependencies...
    call npm install --silent
    echo ✓ Frontend dependencies installed
) else (
    echo ✓ Frontend dependencies already installed
)

echo.
echo ================================================
echo Setup complete!
echo ================================================
echo.
echo To start the application:
echo.
echo Terminal 1 (Backend):
echo   cd backend
echo   venv\Scripts\activate.bat
echo   python app.py
echo.
echo Terminal 2 (Frontend):
echo   cd frontend
echo   npm run dev
echo.
echo Then open http://localhost:3000 in your browser
echo.
echo ================================================
echo.

pause
