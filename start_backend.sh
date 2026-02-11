#!/bin/bash

echo "========================================"
echo "Starting Wind Farm Monitoring System"
echo "========================================"
echo ""

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
VENV_ACTIVATE="$SCRIPT_DIR/backend/venv/bin/activate"
BACKEND_DIR="$SCRIPT_DIR/backend"
FRONTEND_DIR="$SCRIPT_DIR/frontend"

if [ ! -f "$VENV_ACTIVATE" ]; then
    echo "Error: Virtual environment not found at $VENV_ACTIVATE"
    echo "Please create a virtual environment first."
    read -p "Press any key to exit..."
    exit 1
fi

if [ ! -f "$BACKEND_DIR/app.py" ]; then
    echo "Error: app.py not found at $BACKEND_DIR"
    read -p "Press any key to exit..."
    exit 1
fi

if [ ! -f "$FRONTEND_DIR/package.json" ]; then
    echo "Error: package.json not found at $FRONTEND_DIR"
    read -p "Press any key to exit..."
    exit 1
fi

echo "Starting Backend Service..."
echo ""

# 在新的终端窗口中启动后端服务
osascript -e "tell application \"Terminal\" to do script \"cd '$BACKEND_DIR' && source '$VENV_ACTIVATE' && echo 'Virtual environment activated.' && echo 'Starting backend service...' && echo '' && python3 app.py\""

echo "Waiting for backend to start..."
sleep 3

echo "Starting Frontend Service..."
echo ""

# 在新的终端窗口中启动前端服务
osascript -e "tell application \"Terminal\" to do script \"cd '$FRONTEND_DIR' && echo 'Starting frontend service...' && echo '' && npm run dev\""

echo ""
echo "========================================"
echo "Services are starting..."
echo "========================================"
echo "Backend: Running in separate terminal window"
echo "Frontend: Running in separate terminal window"
echo ""
echo "Backend API: http://localhost:8000"
echo "Frontend: http://localhost:5173"
echo ""
echo "Press any key to close this window..."
read -n 1 -s
