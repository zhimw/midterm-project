#!/bin/bash

# Family Office AI Agent - Frontend Startup Script

echo "🚀 Starting Family Office AI Agent Frontend..."

if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Copying from .env.example..."
    cp .env.example .env
fi

if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

echo "✅ Starting Vite dev server..."
npm run dev
