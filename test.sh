#!/bin/bash
# Quick Test Suite for Nemesis API
# Run this after the backend is running to verify everything is working

echo "🧪 Running Nemesis API Tests..."
echo ""

# Check if venv exists and activate
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run start_backend.sh first"
    exit 1
fi

source venv/bin/activate

# Check if API is running
echo "1️⃣  Checking if API is running..."
if ! curl -s http://localhost:8000/status > /dev/null 2>&1; then
    echo "❌ API is not running on port 8000"
    echo "   Please start the backend first with: sudo ./start_backend.sh"
    exit 1
fi
echo "✓ API is running"
echo ""

# Run the test script
echo "2️⃣  Running endpoint tests..."
python test_api.py

echo ""
echo "✅ Test suite complete!"
echo ""
echo "Next steps:"
echo "  1. Start frontend:  ./start_frontend.sh"
echo "  2. Open dashboard: http://localhost:5173"
echo "  3. Monitor in browser and API logs"
