#!/bin/bash

# Nemesis SOC Startup Script

echo "🚀 Starting Nemesis Security Operations Center..."

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Check if Node.js is available
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required but not installed."
    exit 1
fi

# Install Python dependencies if requirements.txt exists
if [ -f "requirement.txt" ]; then
    echo "📦 Installing Python dependencies..."
    pip install -r requirement.txt
fi

# Install frontend dependencies
if [ -d "frontend" ]; then
    echo "📦 Installing frontend dependencies..."
    cd frontend
    npm install
    cd ..
fi

echo "🔧 Starting backend API server on port 8001..."
python -m uvicorn api.main:app --host 0.0.0.0 --port 8001 &
BACKEND_PID=$!

echo "🎨 Starting frontend development server..."
cd frontend
npm run dev &
FRONTEND_PID=$!

echo ""
echo "✅ Nemesis SOC is running!"
echo "   📊 Backend API: http://localhost:8001"
echo "   🖥️  Frontend Dashboard: http://localhost:5174"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for interrupt
trap "echo '🛑 Stopping services...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT
wait