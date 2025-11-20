#!/bin/bash

# EDEN Master Startup Script
# Starts all EDEN services together

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=========================================="
echo "  EDEN Complete System Startup"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to check if service is running
check_service() {
    local url=$1
    local name=$2
    if curl -s "$url" > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} $name is running"
        return 0
    else
        echo -e "${RED}✗${NC} $name is not running"
        return 1
    fi
}

# Function to kill process on port
kill_port() {
    local port=$1
    if lsof -ti :$port > /dev/null 2>&1; then
        echo "Killing process on port $port..."
        lsof -ti :$port | xargs kill -9 2>/dev/null || true
        sleep 1
    fi
}

# Clean up ports
echo "Checking ports..."
kill_port 8000
kill_port 8001
kill_port 8765
sleep 2  # Wait for ports to be released
echo ""

# Check Ollama
echo "Step 1: Checking Ollama..."
if check_service "http://localhost:11434/api/tags" "Ollama"; then
    OLLAMA_RUNNING=true
else
    echo "Starting Ollama..."
    ollama serve > /dev/null 2>&1 &
    OLLAMA_PID=$!
    sleep 3
    if check_service "http://localhost:11434/api/tags" "Ollama"; then
        OLLAMA_RUNNING=true
        echo "Ollama started (PID: $OLLAMA_PID)"
    else
        echo -e "${RED}Failed to start Ollama${NC}"
        exit 1
    fi
fi
echo ""

# Start Cognitive Layer
echo "Step 2: Starting Cognitive Layer..."
# Ensure port is free
kill_port 8000
sleep 2

python3 brain_server.py > /tmp/eden_cognitive.log 2>&1 &
COGNITIVE_PID=$!
sleep 5  # Give it more time to start

# Check multiple times
for i in {1..5}; do
    if check_service "http://localhost:8000/api/graph/state" "Cognitive Layer"; then
        echo "Cognitive Layer started (PID: $COGNITIVE_PID)"
        echo "  Web Interface: http://localhost:8000"
        break
    else
        if [ $i -eq 5 ]; then
            echo -e "${RED}Failed to start Cognitive Layer${NC}"
            echo "Check logs: /tmp/eden_cognitive.log"
            echo "Last 20 lines of log:"
            tail -20 /tmp/eden_cognitive.log
            exit 1
        fi
        sleep 2
    fi
done
echo ""

# Start Input Layer
echo "Step 3: Starting Input Layer..."
# Start camera server
python3 -m input_layer.camera_server > /tmp/eden_camera.log 2>&1 &
CAMERA_PID=$!
sleep 2

# Start frame processor
python3 -m input_layer.frame_processor > /tmp/eden_frame_processor.log 2>&1 &
FRAME_PID=$!
sleep 2

echo "Input Layer started"
echo "  Camera Server PID: $CAMERA_PID"
echo "  Frame Processor PID: $FRAME_PID"
echo ""

# Start Planning Layer
echo "Step 4: Starting Planning Layer..."
python3 -m planning_layer.planning_server > /tmp/eden_planning.log 2>&1 &
PLANNING_PID=$!
sleep 4
if check_service "http://localhost:8001/api/plan/status" "Planning Layer"; then
    echo "Planning Layer started (PID: $PLANNING_PID)"
    echo "  API: http://localhost:8001"
else
    echo -e "${YELLOW}Planning Layer may have started but not responding yet${NC}"
    echo "Check logs: /tmp/eden_planning.log"
fi
echo ""

# Final status
echo "=========================================="
echo "  EDEN System Status"
echo "=========================================="
echo ""
check_service "http://localhost:11434/api/tags" "Ollama"
check_service "http://localhost:8000/api/graph/state" "Cognitive Layer"
check_service "http://localhost:8001/api/plan/status" "Planning Layer"
echo ""

echo "=========================================="
echo "  Service Information"
echo "=========================================="
echo "Cognitive Layer: http://localhost:8000 (PID: $COGNITIVE_PID)"
echo "Planning Layer:  http://localhost:8001 (PID: $PLANNING_PID)"
echo "Camera Server:    ws://localhost:8765 (PID: $CAMERA_PID)"
echo "Frame Processor:  (PID: $FRAME_PID)"
if [ ! -z "$OLLAMA_PID" ]; then
    echo "Ollama:           http://localhost:11434 (PID: $OLLAMA_PID)"
fi
echo ""
echo "Log Files:"
echo "  Cognitive: /tmp/eden_cognitive.log"
echo "  Camera:    /tmp/eden_camera.log"
echo "  Frame:     /tmp/eden_frame_processor.log"
echo "  Planning:  /tmp/eden_planning.log"
echo ""
echo "=========================================="
echo "  Press Ctrl+C to stop all services"
echo "=========================================="

# Trap to cleanup on exit
cleanup() {
    echo ""
    echo "Stopping all services..."
    kill $COGNITIVE_PID $CAMERA_PID $FRAME_PID $PLANNING_PID 2>/dev/null || true
    if [ ! -z "$OLLAMA_PID" ]; then
        kill $OLLAMA_PID 2>/dev/null || true
    fi
    echo "All services stopped"
    exit 0
}

trap cleanup INT TERM

# Keep script running
wait

