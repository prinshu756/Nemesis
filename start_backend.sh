#!/bin/bash
# Start Nemesis Backend API Server
# This script starts the FastAPI server on port 8000

set -e

echo "🚀 Starting Nemesis Backend API Server..."
echo ""

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Creating it..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies if needed
echo "📦 Checking dependencies..."
pip install -q -r requirement.txt 2>/dev/null || true

# Start the API server
echo "✓ Dependencies ready"
echo ""
echo "🌐 Starting API on http://0.0.0.0:8000"
echo "📊 Access API: http://localhost:8000"
echo "📡 WebSocket: ws://localhost:8000/ws"
echo ""
echo "Press CTRL+C to stop the server"
echo ""

# Run the server with root if available (for network capture)
if [ "$EUID" -eq 0 ]; then
    echo "✓ Running with root privileges (full network capture enabled)"
else
    echo "⚠️  Running without root (limited network capture)"
    echo "   Use 'sudo ./start_backend.sh' for full network capture"
fi

python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
