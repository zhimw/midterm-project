#!/bin/bash

# Family Office AI Agent - Combined Startup Script
# This script starts both backend and frontend in separate processes

echo "🚀 Family Office AI Agent - Startup Script"
echo "=========================================="

trap 'kill $(jobs -p) 2>/dev/null' EXIT

echo ""
echo "📋 Pre-flight checks..."

if [ ! -f "backend/.env" ]; then
    echo "⚠️  backend/.env not found. Creating from template..."
    cp backend/.env.example backend/.env
    echo "❗ Please edit backend/.env with your API keys, then run this script again."
    exit 1
fi

if [ ! -d "backend/venv" ]; then
    echo "📦 Creating Python virtual environment..."
    cd backend
    python3 -m venv venv
    cd ..
fi

if [ ! -d "frontend/node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    cd frontend
    npm install
    cd ..
fi

echo "✅ Pre-flight checks complete"
echo ""

echo "🔧 Starting Backend (port 8000)..."
cd backend
source venv/bin/activate
pip install -q -r requirements.txt
uvicorn app.main:app --reload --port 8000 &
BACKEND_PID=$!
cd ..

sleep 3

echo "🎨 Starting Frontend (port 5173)..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

sleep 2

echo ""
echo "✅ Both services started!"
echo "=========================================="
echo "Backend:  http://localhost:8000"
echo "Frontend: http://localhost:5173"
echo "=========================================="
echo ""
echo "Press Ctrl+C to stop both services"
echo ""

wait
