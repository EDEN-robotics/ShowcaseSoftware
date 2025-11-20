#!/bin/bash

# Quick test script to verify all services can start

echo "Testing EDEN service startup..."
echo ""

cd /home/vedantso/ShowcaseSoftware

# Test imports
echo "1. Testing imports..."
python3 -c "from cognitive_layer import EgoGraph; print('  ✓ Cognitive layer')" 2>&1 | grep -v "Warning"
python3 -c "from input_layer import CameraServer; print('  ✓ Input layer')" 2>&1 | grep -v "Warning"
python3 -c "from planning_layer import CosmosLite; print('  ✓ Planning layer')" 2>&1 | grep -v "Warning"
python3 -c "from brain_server import app; print('  ✓ Brain server')" 2>&1 | grep -v "Warning"

echo ""
echo "2. Checking ports..."
lsof -i :8000 > /dev/null && echo "  ⚠ Port 8000 in use" || echo "  ✓ Port 8000 free"
lsof -i :8001 > /dev/null && echo "  ⚠ Port 8001 in use" || echo "  ✓ Port 8001 free"
lsof -i :8765 > /dev/null && echo "  ⚠ Port 8765 in use" || echo "  ✓ Port 8765 free"

echo ""
echo "3. Checking services..."
curl -s http://localhost:11434/api/tags > /dev/null && echo "  ✓ Ollama running" || echo "  ✗ Ollama not running"
curl -s http://localhost:8000/api/graph/state > /dev/null && echo "  ✓ Cognitive Layer running" || echo "  ✗ Cognitive Layer not running"
curl -s http://localhost:8001/api/plan/status > /dev/null && echo "  ✓ Planning Layer running" || echo "  ✗ Planning Layer not running"

echo ""
echo "Test complete!"

