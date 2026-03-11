#!/bin/bash

# Family Office AI Agent - Backend Startup Script

echo "🚀 Starting Family Office AI Agent Backend..."

if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Copying from .env.example..."
    cp .env.example .env
    echo "⚠️  Please edit .env and add your API keys before continuing."
    exit 1
fi

if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

echo "📦 Activating virtual environment..."
source venv/bin/activate

echo "📦 Installing dependencies..."
pip install -q -r requirements.txt

echo "✅ Starting FastAPI server..."
uvicorn app.main:app --reload --port 8000
