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
set STM32_DIR=%SCRIPT_DIR%STM32_Receiver
set BACKEND_REQUIREMENTS=%BACKEND_DIR%\requirements.txt

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

if not exist "%BACKEND_REQUIREMENTS%" (
    echo Error: requirements.txt not found at %BACKEND_DIR%
    pause
    exit /b 1
)

if not exist "%FRONTEND_DIR%\package.json" (
    echo Error: package.json not found at %FRONTEND_DIR%
    pause
    exit /b 1
)

if not exist "%STM32_DIR%\main.py" (
    echo Error: main.py not found at %STM32_DIR%
    pause
    exit /b 1
)

if not exist "%STM32_DIR%\dhcp_server.py" (
    echo Error: dhcp_server.py not found at %STM32_DIR%
    pause
    exit /b 1
)



echo Checking and Installing Dependencies...
echo.

cd /d %BACKEND_DIR%
call %VENV_ACTIVATE%
echo Virtual environment activated.
echo Installing dependencies...
echo.
pip install -r requirements.txt
echo.
echo Dependencies installed successfully!
echo.

start "Backend Service" cmd /k "cd /d %BACKEND_DIR% && call %SCRIPT_DIR%backend\venv\Scripts\activate.bat && echo Virtual environment activated. && echo Starting backend service... && echo. && python app.py"

echo Waiting for backend to start...
timeout /t 3 /nobreak >nul

echo Starting Frontend Service...
echo.

start "Frontend Service" cmd /k "cd /d %FRONTEND_DIR% && echo Starting frontend service... && echo. && npm run dev"

echo Starting STM32 Receiver Services...
echo.

start "STM32 Main Service" cmd /k "cd /d %STM32_DIR% && call %SCRIPT_DIR%backend\venv\Scripts\activate.bat && echo Virtual environment activated. && echo Starting STM32 main service... && echo. && python main.py"

echo Waiting for STM32 main service to start...
timeout /t 2 /nobreak >nul

echo Starting DHCP Server...
echo.

start "DHCP Server Service" cmd /k "cd /d %STM32_DIR% && call %SCRIPT_DIR%backend\venv\Scripts\activate.bat && echo Virtual environment activated. && echo Starting DHCP server... && echo. && python dhcp_server.py"

echo.
echo ========================================
echo Services are starting...
echo ========================================
echo Backend: Running in separate window
echo Frontend: Running in separate window
echo STM32 Main: Running in separate window
echo DHCP Server: Running in separate window
echo.
echo Backend API: http://localhost:8000
echo Frontend: http://localhost:5173
echo STM32 Receiver: Running in separate window
echo DHCP Server: Running in separate window
echo.
echo Press any key to close this window...
pause >nul
