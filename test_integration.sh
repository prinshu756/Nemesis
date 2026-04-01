#!/bin/bash

# Nemesis Backend-Frontend Integration Test Script
# This script verifies that all components are properly connected

echo "================================"
echo "Nemesis Integration Test Suite"
echo "================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counters
TESTS_PASSED=0
TESTS_FAILED=0

# Function to test API endpoint
test_api_endpoint() {
    local method=$1
    local endpoint=$2
    local description=$3
    
    echo -n "Testing $description... "
    
    response=$(curl -s -w "\n%{http_code}" -X "$method" "http://localhost:8000$endpoint" \
        -H "Content-Type: application/json" 2>/dev/null)
    
    http_code=$(echo "$response" | tail -n1)
    
    if [ "$http_code" -lt 300 ] && [ "$http_code" -ge 200 ]; then
        echo -e "${GREEN}✓ PASS${NC} (HTTP $http_code)"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ FAIL${NC} (HTTP $http_code)"
        ((TESTS_FAILED++))
    fi
}

# Check if backend is running
echo -e "${YELLOW}1. Checking Backend Connectivity${NC}"
echo ""

if ! nc -z localhost 8000 2>/dev/null; then
    echo -e "${RED}✗ Backend not running on port 8000${NC}"
    echo "  Start backend with: python -m api.main"
    echo ""
else
    echo -e "${GREEN}✓ Backend is running${NC}"
    echo ""
fi

# Test API endpoints
echo -e "${YELLOW}2. Testing API Endpoints${NC}"
echo ""

test_api_endpoint "GET" "/" "API health check"
test_api_endpoint "GET" "/devices" "Get devices endpoint"
test_api_endpoint "GET" "/alerts" "Get alerts endpoint"
test_api_endpoint "GET" "/status" "Get system status"
test_api_endpoint "GET" "/traffic" "Get traffic logs"
test_api_endpoint "GET" "/honeypots/detection" "Get honeypot detections"
test_api_endpoint "GET" "/anomalies" "Get anomalies"

echo ""

# Database tests
echo -e "${YELLOW}3. Testing Database Configuration${NC}"
echo ""

# Check local SQLite
if [ -f "nemesis.db" ]; then
    echo -e "${GREEN}✓ Local SQLite database found${NC}"
    
    # Try to query it
    sqlite_devices=$(sqlite3 nemesis.db "SELECT COUNT(*) FROM devices 2>/dev/null;" 2>/dev/null)
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ SQLite is accessible ($sqlite_devices devices)${NC}"
        ((TESTS_PASSED++))
    else
        echo -e "${YELLOW}⚠ SQLite not accessible (may need initialization)${NC}"
    fi
else
    echo -e "${YELLOW}⚠ SQLite database not found (will be created on first run)${NC}"
fi
echo ""

# Test database persistence endpoints
echo -e "${YELLOW}4. Testing Database Persistence Endpoints${NC}"
echo ""

test_api_endpoint "GET" "/db/status" "Get database status"
test_api_endpoint "GET" "/db/devices" "Get persisted devices"
test_api_endpoint "GET" "/db/alerts" "Get persisted alerts"
test_api_endpoint "GET" "/db/traffic" "Get persisted traffic logs"
test_api_endpoint "GET" "/db/honeypot-interactions" "Get persisted honeypot interactions"

echo ""

# Frontend environment check
echo -e "${YELLOW}5. Checking Frontend Configuration${NC}"
echo ""

if [ -f "frontend/.env" ]; then
    echo -e "${GREEN}✓ Frontend .env file exists${NC}"
    
    if grep -q "VITE_API_URL=http://localhost:8000" frontend/.env; then
        echo -e "${GREEN}✓ API URL correctly configured${NC}"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ API URL not correctly configured${NC}"
        ((TESTS_FAILED++))
    fi
else
    echo -e "${RED}✗ Frontend .env file not found${NC}"
    ((TESTS_FAILED++))
fi

# Check if API service file exists
if [ -f "frontend/src/services/api.js" ]; then
    echo -e "${GREEN}✓ Frontend API service exists${NC}"
    ((TESTS_PASSED++))
else
    echo -e "${RED}✗ Frontend API service not found${NC}"
    ((TESTS_FAILED++))
fi

# Check if persistence hook exists
if [ -f "frontend/src/hooks/usePersistence.jsx" ]; then
    echo -e "${GREEN}✓ Frontend persistence hook exists${NC}"
    ((TESTS_PASSED++))
else
    echo -e "${RED}✗ Frontend persistence hook not found${NC}"
    ((TESTS_FAILED++))
fi

echo ""

# Python checks
echo -e "${YELLOW}6. Checking Python Dependencies${NC}"
echo ""

if python -c "import fastapi" 2>/dev/null; then
    echo -e "${GREEN}✓ FastAPI installed${NC}"
    ((TESTS_PASSED++))
else
    echo -e "${RED}✗ FastAPI not installed${NC}"
    ((TESTS_FAILED++))
fi

if python -c "import sqlalchemy" 2>/dev/null; then
    echo -e "${GREEN}✓ SQLAlchemy installed${NC}"
    ((TESTS_PASSED++))
else
    echo -e "${RED}✗ SQLAlchemy not installed${NC}"
    ((TESTS_FAILED++))
fi

if python -c "from core.database import DatabaseManager" 2>/dev/null; then
    echo -e "${GREEN}✓ Database models available${NC}"
    ((TESTS_PASSED++))
else
    echo -e "${RED}✗ Database models not available${NC}"
    ((TESTS_FAILED++))
fi

echo ""
echo "================================"
echo "Test Summary"
echo "================================"
echo -e "Passed: ${GREEN}$TESTS_PASSED${NC}"
echo -e "Failed: ${RED}$TESTS_FAILED${NC}"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed! System is ready.${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Start backend: python -m api.main"
    echo "  2. Start frontend: cd frontend && npm run dev"
    echo "  3. Open http://localhost:5173"
    exit 0
else
    echo -e "${RED}✗ Some tests failed. Please check the output above.${NC}"
    exit 1
fi
