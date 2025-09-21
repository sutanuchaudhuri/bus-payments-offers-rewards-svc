#!/bin/bash
# Start all simulator services

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_PATH="${SCRIPT_DIR}/../.venv/bin/python"

echo "Starting Simulator Services..."
echo "================================"

# Check if virtual environment exists
if [ ! -f "$PYTHON_PATH" ]; then
    echo "❌ Virtual environment not found at $PYTHON_PATH"
    echo "Please ensure the virtual environment is set up correctly"
    exit 1
fi

# Start Travel Booking Service (Port 5002)
echo "🛫 Starting Travel Booking Service on port 5002..."
cd "${SCRIPT_DIR}/services"
$PYTHON_PATH travel_booking.py &
TRAVEL_PID=$!
echo "   PID: $TRAVEL_PID"

# Start Hotel Booking Service (Port 5003) 
echo "🏨 Starting Hotel Booking Service on port 5003..."
$PYTHON_PATH hotel_booking.py &
HOTEL_PID=$!
echo "   PID: $HOTEL_PID"

# Start Shopping Service (Port 5004)
echo "🛒 Starting Shopping Service on port 5004..."
$PYTHON_PATH shopping.py &
SHOPPING_PID=$!
echo "   PID: $SHOPPING_PID"

# Wait for services to start
echo ""
echo "⏳ Waiting for services to start..."
sleep 5

# Check service health
echo ""
echo "🔍 Checking service health..."

check_service() {
    local name=$1
    local url=$2
    local pid=$3
    
    if kill -0 $pid 2>/dev/null; then
        if curl -s "$url/health" > /dev/null 2>&1; then
            echo "✅ $name is healthy"
            return 0
        else
            echo "⚠️  $name is running but not responding"
            return 1
        fi
    else
        echo "❌ $name failed to start"
        return 1
    fi
}

SUCCESS_COUNT=0

check_service "Travel Booking Service" "http://localhost:5002" $TRAVEL_PID && ((SUCCESS_COUNT++))
check_service "Hotel Booking Service" "http://localhost:5003" $HOTEL_PID && ((SUCCESS_COUNT++))
check_service "Shopping Service" "http://localhost:5004" $SHOPPING_PID && ((SUCCESS_COUNT++))

echo ""
echo "================================"
echo "✨ Started $SUCCESS_COUNT/3 simulator services"

if [ $SUCCESS_COUNT -eq 3 ]; then
    echo ""
    echo "🎉 All services are running successfully!"
    echo ""
    echo "Service URLs:"
    echo "  Travel:   http://localhost:5002"
    echo "  Hotel:    http://localhost:5003" 
    echo "  Shopping: http://localhost:5004"
    echo ""
    echo "Integration endpoints available at:"
    echo "  Main App: http://localhost:5001/api/integration/*"
    echo ""
    echo "To stop services, run: ./stop_simulators.sh"
else
    echo ""
    echo "⚠️  Some services failed to start. Check the logs above."
fi

# Save PIDs for cleanup
echo "$TRAVEL_PID $HOTEL_PID $SHOPPING_PID" > "${SCRIPT_DIR}/.simulator_pids"