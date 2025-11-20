# EDEN Quick Start - All Services

## One-Command Startup

```bash
cd /home/vedantso/ShowcaseSoftware
./start_all_services.sh
```

This starts:
- ✅ Ollama (VLM/LLM)
- ✅ Cognitive Layer (port 8000)
- ✅ Input Layer (Camera + Frame Processor)
- ✅ Planning Layer (port 8001)

## Manual Startup (4 Terminals)

### Terminal 1: Ollama
```bash
ollama serve
```

### Terminal 2: Cognitive Layer
```bash
cd /home/vedantso/ShowcaseSoftware
python3 brain_server.py
```
**Open:** http://localhost:8000

### Terminal 3: Input Layer
```bash
cd /home/vedantso/ShowcaseSoftware
./start_input_layer.sh
```

### Terminal 4: Planning Layer
```bash
cd /home/vedantso/ShowcaseSoftware
python3 -m planning_layer.planning_server
```

## Verify Everything is Running

```bash
# Check all services
curl http://localhost:11434/api/tags && echo " ✓ Ollama"
curl http://localhost:8000/api/graph/state > /dev/null && echo " ✓ Cognitive Layer"
curl http://localhost:8001/api/plan/status > /dev/null && echo " ✓ Planning Layer"
```

## Test the Full Pipeline

### 1. Test Cognitive Layer
```bash
curl -X POST http://localhost:8000/api/events/process \
  -H "Content-Type: application/json" \
  -d '{"description": "Test event", "user_name": "Test"}'
```

### 2. Test Planning Layer
```bash
curl -X POST http://localhost:8001/api/plan/generate \
  -H "Content-Type: application/json" \
  -d '{"goal": "Pick up cup", "scene_description": "Cup on table"}'
```

### 3. View Cognitive Layer Dashboard
Open: http://localhost:8000

## Stop All Services

```bash
pkill -f brain_server.py
pkill -f camera_server
pkill -f frame_processor
pkill -f planning_server
pkill ollama
```

Or press Ctrl+C in the startup script terminal.

