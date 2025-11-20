#!/bin/bash

# EDEN Input Layer Startup Script
# Starts both camera server and frame processor

echo "=== Starting EDEN Input Layer ==="

# Check if camera server is already running
if lsof -ti :8765 > /dev/null 2>&1; then
    echo "⚠️  Port 8765 is already in use. Killing existing process..."
    lsof -ti :8765 | xargs kill -9
    sleep 2
fi

# Start camera server in background
echo "📹 Starting Camera Server..."
python3 -m input_layer.camera_server &
CAMERA_PID=$!
echo "   Camera Server PID: $CAMERA_PID"

# Wait a moment for server to start
sleep 3

# Check if camera server started successfully
if ! ps -p $CAMERA_PID > /dev/null; then
    echo "❌ Camera Server failed to start"
    exit 1
fi

echo "✓ Camera Server started"

# Start frame processor in background
echo "🧠 Starting Frame Processor..."
python3 -m input_layer.frame_processor &
PROCESSOR_PID=$!
echo "   Frame Processor PID: $PROCESSOR_PID"

# Wait a moment
sleep 2

# Check if frame processor started successfully
if ! ps -p $PROCESSOR_PID > /dev/null; then
    echo "❌ Frame Processor failed to start"
    kill $CAMERA_PID 2>/dev/null
    exit 1
fi

echo "✓ Frame Processor started"
echo ""
echo "=== Input Layer Running ==="
echo "Camera Server PID: $CAMERA_PID"
echo "Frame Processor PID: $PROCESSOR_PID"
echo ""
echo "Press Ctrl+C to stop both processes"

# Wait for interrupt
trap "echo ''; echo 'Stopping...'; kill $CAMERA_PID $PROCESSOR_PID 2>/dev/null; exit" INT TERM

# Keep script running
wait

