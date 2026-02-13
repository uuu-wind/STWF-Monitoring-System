#!/usr/bin/env bash
set -euo pipefail

echo "========================================"
echo "Starting Wind Farm Monitoring System (macOS)"
echo "========================================"
echo

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/backend"
FRONTEND_DIR="$SCRIPT_DIR/frontend"
STM32_DIR="$SCRIPT_DIR/STM32_Receiver"

VENV_DIR="$BACKEND_DIR/venv"
VENV_ACTIVATE="$VENV_DIR/bin/activate"
REQ_FILE="$BACKEND_DIR/requirements.txt"

PY_VER="3.13.7"
PY_MAJOR_MINOR="3.13"

# python.org macOS universal2 installer package filename pattern
# (Python 3.13.7 macOS 64-bit universal2 installer)
PY_PKG="python-${PY_VER}-macos11.pkg"
PY_URL="https://www.python.org/ftp/python/${PY_VER}/${PY_PKG}"
PY_PKG_TMP="/tmp/${PY_PKG}"

# Where python.org installer usually places python
PY_BIN_CANDIDATE="/Library/Frameworks/Python.framework/Versions/${PY_MAJOR_MINOR}/bin/python3.13"

# -------------------------------
# Helper: check python version exactly
# -------------------------------
check_python_3137() {
  local pybin="$1"
  "$pybin" -c 'import sys; raise SystemExit(0 if sys.version_info[:3]==(3,13,7) else 1)' >/dev/null 2>&1
}

# -------------------------------
# Step 0: Ensure Python 3.13.7 exists (install from python.org if missing)
# -------------------------------
echo "[Step 0] Ensuring Python ${PY_VER}..."

PY_BIN=""

# 0.1 Try common python.org install path first
if [[ -x "$PY_BIN_CANDIDATE" ]] && check_python_3137 "$PY_BIN_CANDIDATE"; then
  PY_BIN="$PY_BIN_CANDIDATE"
fi

# 0.2 Try python3.13 on PATH
if [[ -z "$PY_BIN" ]] && command -v python3.13 >/dev/null 2>&1; then
  if check_python_3137 "$(command -v python3.13)"; then
    PY_BIN="$(command -v python3.13)"
  fi
fi

# 0.3 If not found, download & install pkg (requires sudo)
if [[ -z "$PY_BIN" ]]; then
  echo "Python ${PY_VER} not found. Downloading from python.org and installing (requires sudo)..."
  echo "Downloading: $PY_URL"
  curl -L --fail "$PY_URL" -o "$PY_PKG_TMP"

  echo "Installing package with sudo..."
  sudo installer -pkg "$PY_PKG_TMP" -target /

  # Re-check after install
  if [[ -x "$PY_BIN_CANDIDATE" ]] && check_python_3137 "$PY_BIN_CANDIDATE"; then
    PY_BIN="$PY_BIN_CANDIDATE"
  fi

  if [[ -z "$PY_BIN" ]]; then
    echo "ERROR: Python ${PY_VER} installed but still not detected at:"
    echo "  $PY_BIN_CANDIDATE"
    echo "Try running: $PY_BIN_CANDIDATE -V"
    exit 1
  fi
fi

echo "Using Python: $PY_BIN"
echo

# -------------------------------
# Step 1: Create venv if missing
# -------------------------------
echo "[Step 1] Creating/using virtual environment: $VENV_DIR"
if [[ ! -f "$VENV_ACTIVATE" ]]; then
  "$PY_BIN" -m venv "$VENV_DIR"
fi
echo

# -------------------------------
# Checks (same as Windows)
# -------------------------------
[[ -f "$BACKEND_DIR/app.py" ]] || { echo "Error: app.py not found at $BACKEND_DIR"; exit 1; }
[[ -f "$REQ_FILE" ]] || { echo "Error: requirements.txt not found at $REQ_FILE"; exit 1; }
[[ -f "$FRONTEND_DIR/package.json" ]] || { echo "Error: package.json not found at $FRONTEND_DIR"; exit 1; }
[[ -f "$STM32_DIR/main.py" ]] || { echo "Error: main.py not found at $STM32_DIR"; exit 1; }
[[ -f "$STM32_DIR/dhcp_server.py" ]] || { echo "Error: dhcp_server.py not found at $STM32_DIR"; exit 1; }

# -------------------------------
# Step 2: Install backend deps in venv
# -------------------------------
echo "[Step 2] Installing backend dependencies..."
# shellcheck disable=SC1090
source "$VENV_ACTIVATE"
python -m pip install --upgrade pip >/dev/null
pip install -r "$REQ_FILE"
echo "Dependencies installed."
echo

# -------------------------------
# Helper: open a new Terminal window and run a command
# -------------------------------
open_terminal_run() {
  local title="$1"
  local cmd="$2"

  # Uses AppleScript to open a new Terminal window and run cmd
  osascript >/dev/null <<OSA
tell application "Terminal"
  activate
  set w to do script "printf '\\\\033]0;%s\\\\007' '${title}'; ${cmd}"
end tell
OSA
}

# -------------------------------
# Step 3: Start services (separate Terminal windows)
# -------------------------------
echo "[Step 3] Starting services in separate Terminal windows..."
echo

BACKEND_CMD="cd \"${BACKEND_DIR}\" && source \"${VENV_ACTIVATE}\" && echo \"Virtual environment activated.\" && echo \"Starting backend service...\" && python app.py"
FRONTEND_CMD="cd \"${FRONTEND_DIR}\" && echo \"Starting frontend service...\" && npm run dev"
STM32_MAIN_CMD="cd \"${STM32_DIR}\" && source \"${VENV_ACTIVATE}\" && echo \"Virtual environment activated.\" && echo \"Starting STM32 main service...\" && python main.py"
DHCP_CMD="cd \"${STM32_DIR}\" && source \"${VENV_ACTIVATE}\" && echo \"Virtual environment activated.\" && echo \"Starting DHCP server...\" && python dhcp_server.py"

open_terminal_run "Backend Service"   "$BACKEND_CMD"
sleep 2
open_terminal_run "Frontend Service"  "$FRONTEND_CMD"
sleep 1
open_terminal_run "STM32 Main Service" "$STM32_MAIN_CMD"
sleep 1
open_terminal_run "DHCP Server Service" "$DHCP_CMD"

echo "========================================"
echo "Services are starting..."
echo "========================================"
echo "Backend API: http://localhost:8000"
echo "Frontend:    http://localhost:5173"
echo
echo "This window can be closed. Services run in Terminal windows."
