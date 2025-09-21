#!/bin/bash
# Stop all simulator services

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_FILE="${SCRIPT_DIR}/.simulator_pids"

echo "Stopping Simulator Services..."
echo "==============================="

if [ -f "$PID_FILE" ]; then
    PIDS=$(cat "$PID_FILE")
    
    for PID in $PIDS; do
        if kill -0 $PID 2>/dev/null; then
            echo "🛑 Stopping process $PID..."
            kill $PID
            
            # Wait for graceful shutdown
            sleep 2
            
            # Force kill if still running
            if kill -0 $PID 2>/dev/null; then
                echo "   Force killing process $PID..."
                kill -9 $PID
            fi
            
            echo "   ✅ Process $PID stopped"
        else
            echo "   ℹ️  Process $PID already stopped"
        fi
    done
    
    # Clean up PID file
    rm "$PID_FILE"
    
    echo ""
    echo "🎉 All simulator services stopped successfully!"
else
    echo "ℹ️  No running simulator services found"
    
    # Try to kill any remaining processes by port
    echo ""
    echo "🔍 Checking for processes on simulator ports..."
    
    for port in 5002 5003 5004; do
        PID=$(lsof -ti:$port 2>/dev/null)
        if [ -n "$PID" ]; then
            echo "🛑 Found process $PID on port $port, stopping..."
            kill $PID
            sleep 1
            if kill -0 $PID 2>/dev/null; then
                kill -9 $PID
            fi
            echo "   ✅ Process on port $port stopped"
        fi
    done
fi

echo ""
echo "✨ Cleanup complete!"