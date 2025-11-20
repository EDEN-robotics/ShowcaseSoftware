#!/bin/bash
# Quick status check for EDEN services

echo "=========================================="
echo "  EDEN Service Status"
echo "=========================================="
echo ""

# Cognitive Layer
echo "Cognitive Layer (Port 8000):"
if curl -s http://localhost:8000/api/graph/state > /dev/null 2>&1; then
    NODES=$(curl -s http://localhost:8000/api/graph/state 2>/dev/null | python3 -c "import sys, json; d=json.load(sys.stdin); print(len(d.get('nodes', [])))" 2>/dev/null || echo "?")
    EDGES=$(curl -s http://localhost:8000/api/graph/state 2>/dev/null | python3 -c "import sys, json; d=json.load(sys.stdin); print(len(d.get('links', [])))" 2>/dev/null || echo "?")
    echo "  ✓ Running - $NODES nodes, $EDGES edges"
    echo "  → http://localhost:8000"
else
    echo "  ✗ Not running"
fi

echo ""

# Planning Layer
echo "Planning Layer (Port 8001):"
if curl -s http://localhost:8001/api/plan/status > /dev/null 2>&1; then
    PLANNER=$(curl -s http://localhost:8001/api/plan/status 2>/dev/null | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('active_planner', 'unknown'))" 2>/dev/null || echo "?")
    echo "  ✓ Running - $PLANNER planner active"
    echo "  → http://localhost:8001"
else
    echo "  ✗ Not running"
fi

echo ""

# Ollama
echo "Ollama (Port 11434):"
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "  ✓ Running"
else
    echo "  ✗ Not running"
fi

echo ""
echo "=========================================="

