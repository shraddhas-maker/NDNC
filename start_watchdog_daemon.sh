#!/bin/bash

# NDNC Watchdog Daemon Script
# This script runs the watchdog in the background and automatically restarts it if it crashes

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LOG_FILE="$SCRIPT_DIR/watchdog_daemon.log"
PID_FILE="$SCRIPT_DIR/watchdog_daemon.pid"

# Function to log messages
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Function to check if watchdog is running
is_running() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            return 0
        fi
    fi
    return 1
}

# Function to stop watchdog
stop_watchdog() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            log_message "Stopping watchdog (PID: $PID)..."
            kill "$PID"
            sleep 2
            if ps -p "$PID" > /dev/null 2>&1; then
                log_message "Force killing watchdog..."
                kill -9 "$PID"
            fi
        fi
        rm -f "$PID_FILE"
    fi
}

# Function to start watchdog
start_watchdog() {
    log_message "Starting NDNC Watchdog..."
    
    cd "$SCRIPT_DIR"
    
    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        log_message "ERROR: Virtual environment not found. Run ./setup.sh first"
        exit 1
    fi
    
    # Start watchdog in background
    nohup ./start_watchdog.sh >> "$LOG_FILE" 2>&1 &
    echo $! > "$PID_FILE"
    
    log_message "Watchdog started with PID: $(cat $PID_FILE)"
}

# Function to run daemon (infinite restart loop)
run_daemon() {
    log_message "========================================"
    log_message "NDNC Watchdog Daemon Starting"
    log_message "========================================"
    log_message "Log file: $LOG_FILE"
    log_message "PID file: $PID_FILE"
    log_message "Press Ctrl+C to stop the daemon"
    log_message "========================================"
    
    # Handle Ctrl+C gracefully
    trap 'log_message "Daemon stopping..."; stop_watchdog; exit 0' INT TERM
    
    while true; do
        if ! is_running; then
            log_message "Watchdog is not running. Starting..."
            start_watchdog
        fi
        
        # Check every 10 seconds
        sleep 10
    done
}

# Function to show status
show_status() {
    if is_running; then
        PID=$(cat "$PID_FILE")
        echo "✓ Watchdog daemon is running (PID: $PID)"
        echo "  Log file: $LOG_FILE"
        echo "  To stop: ./stop_watchdog_daemon.sh"
    else
        echo "✗ Watchdog daemon is not running"
        echo "  To start: ./start_watchdog_daemon.sh"
    fi
}

# Main script logic
case "${1:-start}" in
    start)
        if is_running; then
            echo "✗ Watchdog daemon is already running (PID: $(cat $PID_FILE))"
            echo "  Use './start_watchdog_daemon.sh stop' to stop it first"
            exit 1
        fi
        run_daemon
        ;;
    stop)
        log_message "Stopping daemon..."
        stop_watchdog
        log_message "Daemon stopped"
        ;;
    restart)
        log_message "Restarting daemon..."
        stop_watchdog
        sleep 2
        run_daemon
        ;;
    status)
        show_status
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status}"
        exit 1
        ;;
esac

