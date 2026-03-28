#!/bin/bash
# Start Nemesis Frontend Dashboard
# This script starts the React frontend on port 5173

set -e

echo "🎨 Starting Nemesis Frontend Dashboard..."
echo ""

# Check if we're in the right directory
if [ ! -f "frontend/package.json" ]; then
    echo "❌ Error: frontend/package.json not found"
    echo "Please run this script from the Nemesis root directory"
    exit 1
fi

cd frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
    echo "✓ Dependencies installed"
else
    echo "✓ Dependencies already installed"
fi

echo ""
echo "🎨 Starting frontend dev server..."
echo "🌐 Access Dashboard: http://localhost:5173"
echo "📡 Connecting to API: http://localhost:8000"
echo ""
echo "Press CTRL+C to stop the server"
echo ""

# Start development server
npm run dev
