# EDEN Complete System Startup Guide

## Overview

EDEN consists of multiple services that need to run together:
1. **Ollama** - VLM and LLM services
2. **Cognitive Layer** - Brain server (port 8000)
3. **Input Layer** - Camera server (port 8765) + Frame processor
4. **Planning Layer** - Planning server (port 8001)

## Quick Start (All Services)

### Option 1: Manual Startup (4 Terminals)

**Terminal 1: Ollama**
```bash
ollama serve
```

**Terminal 2: Cognitive Layer**
```bash
cd /home/vedantso/ShowcaseSoftware
python3 brain_server.py
```

**Terminal 3: Input Layer**
```bash
cd /home/vedantso/ShowcaseSoftware
./start_input_layer.sh
```

**Terminal 4: Planning Layer**
```bash
cd /home/vedantso/ShowcaseSoftware
python3 -m planning_layer.planning_server
```

### Option 2: Use Master Startup Script

```bash
cd /home/vedantso/ShowcaseSoftware
./start_all_services.sh
```

## Complete Startup Sequence

### Step 1: Check Prerequisites

```bash
# Check Ollama
curl http://localhost:11434/api/tags > /dev/null && echo "✓ Ollama running" || echo "✗ Start Ollama"

# Check GPU (for Cosmos)
python3 -c "import torch; print(f'GPU: {torch.cuda.is_available()}')"

# Check ports
lsof -i :8000 && echo "Port 8000 in use" || echo "Port 8000 free"
lsof -i :8001 && echo "Port 8001 in use" || echo "Port 8001 free"
lsof -i :8765 && echo "Port 8765 in use" || echo "Port 8765 free"
```

### Step 2: Start Ollama

```bash
ollama serve
```

**Verify:**
```bash
curl http://localhost:11434/api/tags
```

### Step 3: Start Cognitive Layer

```bash
cd /home/vedantso/ShowcaseSoftware
python3 brain_server.py
```

**Verify:**
```bash
curl http://localhost:8000/api/graph/state
```

**Open browser:** `http://localhost:8000`

### Step 4: Start Input Layer

```bash
cd /home/vedantso/ShowcaseSoftware
./start_input_layer.sh
```

Or separately:
```bash
# Terminal 1: Camera Server
python3 -m input_layer.camera_server

# Terminal 2: Frame Processor
python3 -m input_layer.frame_processor
```

**Verify:**
- Camera server: Check WebSocket on port 8765
- Frame processor: Should connect and start processing

### Step 5: Start Planning Layer

```bash
cd /home/vedantso/ShowcaseSoftware
python3 -m planning_layer.planning_server
```

**Verify:**
```bash
curl http://localhost:8001/api/plan/status
```

## Master Startup Script

Create `start_all_services.sh`:

```bash
#!/bin/bash
# Starts all EDEN services

echo "=== Starting EDEN Complete System ==="

# Check Ollama
if curl -s http://localhost:11434/api/tags > /dev/null; then
    echo "✓ Ollama already running"
else
    echo "Starting Ollama..."
    ollama serve &
    sleep 3
fi

# Start Cognitive Layer
echo "Starting Cognitive Layer..."
cd /home/vedantso/ShowcaseSoftware
python3 brain_server.py &
COGNITIVE_PID=$!
sleep 3

# Start Input Layer
echo "Starting Input Layer..."
./start_input_layer.sh &
INPUT_PID=$!
sleep 3

# Start Planning Layer
echo "Starting Planning Layer..."
python3 -m planning_layer.planning_server &
PLANNING_PID=$!
sleep 3

echo ""
echo "=== All Services Started ==="
echo "Cognitive Layer PID: $COGNITIVE_PID (http://localhost:8000)"
echo "Input Layer PID: $INPUT_PID"
echo "Planning Layer PID: $PLANNING_PID (http://localhost:8001)"
echo ""
echo "Press Ctrl+C to stop all services"
wait
```

## Service URLs

- **Cognitive Layer**: http://localhost:8000
- **Planning Layer**: http://localhost:8001
- **Camera Server**: ws://localhost:8765
- **Ollama**: http://localhost:11434

## Verification Checklist

- [ ] Ollama running: `curl http://localhost:11434/api/tags`
- [ ] Cognitive Layer: `curl http://localhost:8000/api/graph/state`
- [ ] Planning Layer: `curl http://localhost:8001/api/plan/status`
- [ ] Camera Server: Check WebSocket connection
- [ ] Frame Processor: Check logs for processing

## Testing the Full Pipeline

### Test 1: Send Event to Cognitive Layer

```bash
curl -X POST http://localhost:8000/api/events/process \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Ian just finished building the robot",
    "user_name": "Ian",
    "detected_actions": ["completed"]
  }'
```

### Test 2: Generate Plan

```bash
curl -X POST http://localhost:8001/api/plan/generate \
  -H "Content-Type: application/json" \
  -d '{
    "goal": "Pick up the red cup",
    "scene_description": "Red cup is on kitchen counter, 40cm away. No obstacles."
  }'
```

### Test 3: Check Integration

The frame processor should automatically:
1. Receive frames from camera server
2. Analyze with VLM
3. Send to cognitive layer
4. Cognitive layer processes and stores

## Troubleshooting

### Port Already in Use

```bash
# Kill services on ports
lsof -ti :8000 | xargs kill -9
lsof -ti :8001 | xargs kill -9
lsof -ti :8765 | xargs kill -9
```

### Services Not Starting

Check logs for each service:
- Cognitive Layer: Check terminal output
- Input Layer: Check camera_server.py and frame_processor.py logs
- Planning Layer: Check planning_server.py logs

### GPU Issues

```bash
# Check GPU
nvidia-smi
python3 -c "import torch; print(torch.cuda.is_available())"

# Planning layer will use Ollama fallback if GPU unavailable
```

## Stopping All Services

```bash
# Kill all Python processes
pkill -f brain_server.py
pkill -f camera_server
pkill -f frame_processor
pkill -f planning_server

# Kill Ollama
pkill ollama
```

