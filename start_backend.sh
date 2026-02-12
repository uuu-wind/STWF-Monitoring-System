#!/bin/bash

echo "========================================"
echo "Starting Wind Farm Monitoring System"
echo "========================================"
echo ""

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
VENV_ACTIVATE="$SCRIPT_DIR/backend/venv/bin/activate"
BACKEND_DIR="$SCRIPT_DIR/backend"
FRONTEND_DIR="$SCRIPT_DIR/frontend"
STM32_DIR="$SCRIPT_DIR/STM32_Receiver"
BACKEND_REQUIREMENTS="$BACKEND_DIR/requirements.txt"

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

if [ ! -f "$BACKEND_REQUIREMENTS" ]; then
    echo "Error: requirements.txt not found at $BACKEND_DIR"
    read -p "Press any key to exit..."
    exit 1
fi

if [ ! -f "$FRONTEND_DIR/package.json" ]; then
    echo "Error: package.json not found at $FRONTEND_DIR"
    read -p "Press any key to exit..."
    exit 1
fi

if [ ! -f "$STM32_DIR/main.py" ]; then
    echo "Error: main.py not found at $STM32_DIR"
    read -p "Press any key to exit..."
    exit 1
fi

if [ ! -f "$STM32_DIR/dhcp_server.py" ]; then
    echo "Error: dhcp_server.py not found at $STM32_DIR"
    read -p "Press any key to exit..."
    exit 1
fi



echo "Checking and Installing Dependencies..."
echo ""

cd "$BACKEND_DIR"
source "$VENV_ACTIVATE"
echo "Virtual environment activated."
echo "Installing dependencies..."
echo ""
pip install -r requirements.txt
echo ""
echo "Dependencies installed successfully!"
echo ""

# 在新的终端窗口中启动后端服务
osascript -e "tell application \"Terminal\" to do script \"cd '$BACKEND_DIR' && source '$VENV_ACTIVATE' && echo 'Virtual environment activated.' && echo 'Starting backend service...' && echo '' && python3 app.py\""

echo "Waiting for backend to start..."
sleep 3

echo "Starting Frontend Service..."
echo ""

# 在新的终端窗口中启动前端服务
osascript -e "tell application \"Terminal\" to do script \"cd '$FRONTEND_DIR' && echo 'Starting frontend service...' && echo '' && npm run dev\""

echo "Starting STM32 Receiver Services..."
echo ""

# 在新的终端窗口中启动STM32 main服务
osascript -e "tell application \"Terminal\" to do script \"cd '$STM32_DIR' && source '$VENV_ACTIVATE' && echo 'Virtual environment activated.' && echo 'Starting STM32 main service...' && echo '' && python3 main.py\""

echo "Waiting for STM32 main service to start..."
sleep 2

echo "Starting DHCP Server..."
echo ""

# 在新的终端窗口中启动DHCP服务
osascript -e "tell application \"Terminal\" to do script \"cd '$STM32_DIR' && source '$VENV_ACTIVATE' && echo 'Virtual environment activated.' && echo 'Starting DHCP server...' && echo '' && python3 dhcp_server.py\""

echo ""
echo "========================================"
echo "Services are starting..."
echo "========================================"
echo "Backend: Running in separate terminal window"
echo "Frontend: Running in separate terminal window"
echo "STM32 Main: Running in separate terminal window"
echo "DHCP Server: Running in separate terminal window"
echo ""
echo "Backend API: http://localhost:8000"
echo "Frontend: http://localhost:5173"
echo "STM32 Receiver: Running in separate terminal window"
echo "DHCP Server: Running in separate terminal window"
echo ""
echo "Press any key to close this window..."
read -n 1 -s
