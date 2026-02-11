@echo off
setlocal enabledelayedexpansion

echo ========================================
echo Starting Wind Farm Monitoring System
echo ========================================
echo.

set SCRIPT_DIR=%~dp0
set VENV_ACTIVATE=%SCRIPT_DIR%backend\venv\Scripts\activate.bat
set BACKEND_DIR=%SCRIPT_DIR%backend
set FRONTEND_DIR=%SCRIPT_DIR%frontend

if not exist "%VENV_ACTIVATE%" (
    echo Error: Virtual environment not found at %VENV_ACTIVATE%
    echo Please create the virtual environment first.
    pause
    exit /b 1
)

if not exist "%BACKEND_DIR%\app.py" (
    echo Error: app.py not found at %BACKEND_DIR%
    pause
    exit /b 1
)

if not exist "%FRONTEND_DIR%\package.json" (
    echo Error: package.json not found at %FRONTEND_DIR%
    pause
    exit /b 1
)

echo Starting Backend Service...
echo.
start "Backend Service" cmd /k "cd /d %BACKEND_DIR% && call %VENV_ACTIVATE% && echo Virtual environment activated. && echo Starting backend service... && echo. && python app.py"

echo Waiting for backend to start...
timeout /t 3 /nobreak >nul

echo Starting Frontend Service...
echo.
start "Frontend Service" cmd /k "cd /d %FRONTEND_DIR% && echo Starting frontend service... && echo. && npm run dev"

echo.
echo ========================================
echo Services are starting...
echo ========================================
echo Backend: Running in separate window
echo Frontend: Running in separate window
echo.
echo Backend API: http://localhost:8000
echo Frontend: http://localhost:5173
echo.
echo Press any key to close this window...
pause >nul
