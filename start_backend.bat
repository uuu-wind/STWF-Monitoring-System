@echo off
setlocal enabledelayedexpansion

echo ========================================
echo Starting Backend Service
echo ========================================
echo.

set SCRIPT_DIR=%~dp0
set VENV_ACTIVATE=%SCRIPT_DIR%backend\venv\Scripts\activate.bat
set BACKEND_DIR=%SCRIPT_DIR%backend

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

call "%VENV_ACTIVATE%"
echo Virtual environment activated.
echo.

cd /d "%BACKEND_DIR%"
echo Starting backend service...
echo.
python app.py

pause
