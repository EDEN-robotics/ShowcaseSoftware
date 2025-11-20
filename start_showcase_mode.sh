#!/bin/bash

# EDEN Showcase Mode
# Starts Cognitive Layer + Planning Layer with test data
# Input Layer and Context Gathering are DISABLED

echo "=========================================="
echo "  EDEN Showcase Mode"
echo "  (Cognitive + Planning Only)"
echo "=========================================="
echo ""

cd /home/vedantso/ShowcaseSoftware

# Kill existing services
echo "Clearing ports..."
lsof -ti :8000 | xargs kill -9 2>/dev/null || true
lsof -ti :8001 | xargs kill -9 2>/dev/null || true
sleep 2

# Check Ollama
echo "Checking Ollama..."
if curl -s http://localhost:11434/api/tags > /dev/null; then
    echo "✓ Ollama running"
else
    echo "Starting Ollama..."
    ollama serve > /dev/null 2>&1 &
    sleep 3
fi

# Start Cognitive Layer with test data
echo ""
echo "Starting Cognitive Layer (with test knowledge graph)..."
POPULATE_TEST_DATA=true python3 brain_server.py > /tmp/eden_cognitive.log 2>&1 &
COGNITIVE_PID=$!

# Wait for server to start (check multiple times)
echo "Waiting for Cognitive Layer to start..."
for i in {1..10}; do
    sleep 2
    if curl -s http://localhost:8000/api/graph/state > /dev/null 2>&1; then
        NODES=$(curl -s http://localhost:8000/api/graph/state 2>/dev/null | python3 -c "import sys, json; data=json.load(sys.stdin); print(len(data.get('nodes', [])))" 2>/dev/null || echo "?")
        EDGES=$(curl -s http://localhost:8000/api/graph/state 2>/dev/null | python3 -c "import sys, json; data=json.load(sys.stdin); print(len(data.get('links', [])))" 2>/dev/null || echo "?")
        echo "✓ Cognitive Layer started (PID: $COGNITIVE_PID)"
        echo "  Nodes in graph: $NODES"
        echo "  Edges in graph: $EDGES"
        echo "  Web Interface: http://localhost:8000"
        break
    fi
    if [ $i -eq 10 ]; then
        echo "✗ Cognitive Layer failed to start after 20 seconds"
        echo "Check logs: /tmp/eden_cognitive.log"
        echo "Last 30 lines:"
        tail -30 /tmp/eden_cognitive.log
        exit 1
    fi
done

# Start Planning Layer
echo ""
echo "Starting Planning Layer..."
python3 -m planning_layer.planning_server > /tmp/eden_planning.log 2>&1 &
PLANNING_PID=$!
sleep 4

if curl -s http://localhost:8001/api/plan/status > /dev/null; then
    echo "✓ Planning Layer started (PID: $PLANNING_PID)"
    echo "  API: http://localhost:8001"
else
    echo "⚠ Planning Layer may still be starting..."
fi

echo ""
echo "=========================================="
echo "  Showcase Mode Ready!"
echo "=========================================="
echo ""
echo "Services:"
echo "  Cognitive Layer: http://localhost:8000"
echo "  Planning Layer:  http://localhost:8001"
echo ""
echo "Test Planning:"
echo '  curl -X POST http://localhost:8001/api/plan/generate \\'
echo '    -H "Content-Type: application/json" \\'
echo '    -d '"'"'{"goal": "Pick up the red cup", "scene_description": "Red cup is on kitchen counter, 40cm away"}'"'"
echo ""
echo "Press Ctrl+C to stop"

# Cleanup on exit
cleanup() {
    echo ""
    echo "Stopping services..."
    kill $COGNITIVE_PID $PLANNING_PID 2>/dev/null || true
    exit 0
}

trap cleanup INT TERM
wait

