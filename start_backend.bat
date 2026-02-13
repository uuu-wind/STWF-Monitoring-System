@echo off
setlocal enabledelayedexpansion

echo ========================================
echo Starting Wind Farm Monitoring System
echo ========================================
echo.

set SCRIPT_DIR=%~dp0
set BACKEND_DIR=%SCRIPT_DIR%backend
set FRONTEND_DIR=%SCRIPT_DIR%frontend
set STM32_DIR=%SCRIPT_DIR%STM32_Receiver

set PY_EMBED_DIR=%BACKEND_DIR%\python-embed
set PY_EMBED_EXE=%PY_EMBED_DIR%\python.exe

set VENV_DIR=%BACKEND_DIR%\venv
set VENV_ACTIVATE=%VENV_DIR%\Scripts\activate.bat
set VENV_PY=%VENV_DIR%\Scripts\python.exe
set BACKEND_REQUIREMENTS=%BACKEND_DIR%\requirements.txt

set VENV_PYZ=%BACKEND_DIR%\virtualenv.pyz

REM -------------------------------
REM Step 0: Ensure embeddable Python 3.13.7 exists in backend\python-embed
REM -------------------------------
echo [Step 0] Preparing embeddable Python 3.13.7 in project...
echo.

where powershell >nul 2>&1
if not %errorlevel%==0 (
    echo Error: PowerShell not found. Cannot download/extract embeddable Python automatically.
    pause
    exit /b 1
)

if not exist "%PY_EMBED_EXE%" (
    echo Embeddable Python not found. Downloading and extracting...
    echo.

    if not exist "%PY_EMBED_DIR%" mkdir "%PY_EMBED_DIR%"

    set "PY_VER_NUM=3.13.7"
    set "PY_ZIP=python-%PY_VER_NUM%-embed-amd64.zip"
    set "PY_URL=https://www.python.org/ftp/python/%PY_VER_NUM%/%PY_ZIP%"
    set "PY_TMP=%TEMP%\%PY_ZIP%"

    echo Downloading: %PY_URL%
    powershell -NoProfile -ExecutionPolicy Bypass -Command ^
      "$ErrorActionPreference='Stop'; $ProgressPreference='SilentlyContinue';" ^
      "Invoke-WebRequest -Uri '%PY_URL%' -OutFile '%PY_TMP%' -UseBasicParsing | Out-Null; exit 0"
    if not %errorlevel%==0 (
        echo Error: Failed to download embeddable Python zip.
        echo URL: %PY_URL%
        pause
        exit /b 1
    )

    echo Extracting to: %PY_EMBED_DIR%
    powershell -NoProfile -ExecutionPolicy Bypass -Command ^
      "$ErrorActionPreference='Stop';" ^
      "Expand-Archive -Path '%PY_TMP%' -DestinationPath '%PY_EMBED_DIR%' -Force; exit 0"
    if not %errorlevel%==0 (
        echo Error: Failed to extract embeddable Python zip.
        pause
        exit /b 1
    )

    if not exist "%PY_EMBED_EXE%" (
        echo Error: python.exe not found after extraction: %PY_EMBED_EXE%
        pause
        exit /b 1
    )
)

REM Enable import site (helps embedded Python behave more like normal Python)
if exist "%PY_EMBED_DIR%\python313._pth" (
    powershell -NoProfile -ExecutionPolicy Bypass -Command ^
      "$ErrorActionPreference='Stop';" ^
      "$p='%PY_EMBED_DIR%\python313._pth';" ^
      "$c=Get-Content $p -Raw;" ^
      "if($c -match '#import site'){ $c=$c -replace '#import site','import site'; Set-Content -Path $p -Value $c -NoNewline }" ^
      "exit 0" >nul 2>&1
)

"%PY_EMBED_EXE%" -c "import sys; print(sys.version)" >nul 2>&1
if not %errorlevel%==0 (
    echo Error: Embedded python failed to run. This may be missing VC++ runtime on this machine.
    echo Path: %PY_EMBED_EXE%
    pause
    exit /b 1
)

echo Embeddable Python ready: %PY_EMBED_EXE%
echo.

REM -------------------------------
REM Step 1: Download virtualenv.pyz (zipapp) and create venv (NO venv module needed)
REM -------------------------------
if not exist "%VENV_ACTIVATE%" (
    echo [Step 1] Creating virtual environment via virtualenv.pyz ...
    echo.

    if not exist "%VENV_PYZ%" (
        echo Downloading virtualenv.pyz...
        powershell -NoProfile -ExecutionPolicy Bypass -Command ^
          "$ErrorActionPreference='Stop'; $ProgressPreference='SilentlyContinue';" ^
          "Invoke-WebRequest -Uri 'https://bootstrap.pypa.io/virtualenv.pyz' -OutFile '%VENV_PYZ%' -UseBasicParsing | Out-Null; exit 0"
        if not %errorlevel%==0 (
            echo Error: Failed to download virtualenv.pyz
            pause
            exit /b 1
        )
    )

    pushd "%BACKEND_DIR%"
    "%PY_EMBED_EXE%" "%VENV_PYZ%" "%VENV_DIR%"
    if not %errorlevel%==0 (
        popd
        echo Error: Failed to create virtual environment using virtualenv.pyz
        pause
        exit /b 1
    )
    popd

    if not exist "%VENV_ACTIVATE%" (
        echo Error: Virtual environment creation seems incomplete. activate.bat not found.
        pause
        exit /b 1
    )
)

echo Virtual environment ready.
echo.

REM -------------------------------
REM Original checks
REM -------------------------------
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

cd /d "%BACKEND_DIR%"
call "%VENV_ACTIVATE%"
echo Virtual environment activated.

echo Installing dependencies...
echo.
pip install -r "%BACKEND_REQUIREMENTS%"
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
echo.
echo Press any key to close this window...
pause >nul
