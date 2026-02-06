#!/bin/bash

# Quick start script for Motion Capture to Blender
# This script helps set up and run both backend and frontend

set -e

echo "================================================"
echo "Motion Capture to Blender - Quick Start"
echo "================================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed"
    echo "Please install Python 3.9 or higher"
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Error: Node.js is not installed"
    echo "Please install Node.js 16 or higher"
    exit 1
fi

echo "✓ Python $(python3 --version) found"
echo "✓ Node.js $(node --version) found"
echo ""

# Backend setup
echo "Setting up backend..."
cd backend

if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing Python dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

echo "✓ Backend dependencies installed"
echo ""

# Frontend setup
echo "Setting up frontend..."
cd ../frontend

if [ ! -d "node_modules" ]; then
    echo "Installing Node.js dependencies..."
    npm install --silent
    echo "✓ Frontend dependencies installed"
else
    echo "✓ Frontend dependencies already installed"
fi

echo ""
echo "================================================"
echo "Setup complete!"
echo "================================================"
echo ""
echo "To start the application:"
echo ""
echo "Terminal 1 (Backend):"
echo "  cd backend"
echo "  source venv/bin/activate"
echo "  python app.py"
echo ""
echo "Terminal 2 (Frontend):"
echo "  cd frontend"
echo "  npm run dev"
echo ""
echo "Then open http://localhost:3000 in your browser"
echo ""
echo "================================================"
echo ""

# Ask if user wants to start servers now
read -p "Start servers now? (y/N) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "Starting backend server..."
    cd ../backend
    source venv/bin/activate
    
    # Start backend in background
    python app.py &
    BACKEND_PID=$!
    
    echo "Backend started (PID: $BACKEND_PID)"
    echo "Waiting for backend to initialize..."
    sleep 3
    
    echo ""
    echo "Starting frontend server..."
    cd ../frontend
    npm run dev &
    FRONTEND_PID=$!
    
    echo "Frontend started (PID: $FRONTEND_PID)"
    echo ""
    echo "================================================"
    echo "Servers are running!"
    echo "================================================"
    echo ""
    echo "Backend:  http://localhost:8000"
    echo "Frontend: http://localhost:3000"
    echo ""
    echo "Press Ctrl+C to stop both servers"
    echo ""
    
    # Wait for Ctrl+C
    trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT
    wait
else
    echo "Setup complete! Follow the instructions above to start manually."
fi
