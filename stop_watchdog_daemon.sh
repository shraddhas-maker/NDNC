#!/bin/bash

# Stop the NDNC Watchdog Daemon

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PID_FILE="$SCRIPT_DIR/watchdog_daemon.pid"

echo "Stopping NDNC Watchdog Daemon..."

if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    
    if ps -p "$PID" > /dev/null 2>&1; then
        echo "→ Killing daemon process (PID: $PID)..."
        kill "$PID"
        sleep 2
        
        # Force kill if still running
        if ps -p "$PID" > /dev/null 2>&1; then
            echo "→ Force killing..."
            kill -9 "$PID"
        fi
        
        echo "✓ Daemon stopped"
    else
        echo "✗ Daemon is not running (PID file exists but process not found)"
    fi
    
    rm -f "$PID_FILE"
else
    echo "✗ Daemon is not running (no PID file found)"
fi

# Also stop the watchdog itself
WATCHDOG_PID=$(pgrep -f "python.*watch_and_run.py")
if [ -n "$WATCHDOG_PID" ]; then
    echo "→ Stopping watchdog process (PID: $WATCHDOG_PID)..."
    kill "$WATCHDOG_PID" 2>/dev/null
    echo "✓ Watchdog stopped"
fi

echo ""
echo "All processes stopped."

