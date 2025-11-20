# How to Start EDEN - Complete Guide

## 🚀 Easiest Way: One Command

```bash
cd /home/vedantso/ShowcaseSoftware
./start_all_services.sh
```

This starts **everything** automatically!

## 📋 What Gets Started

```
┌─────────────────────────────────────────┐
│  Ollama (VLM/LLM)                       │
│  Port: 11434                            │
└─────────────────────────────────────────┘
           ↓
┌─────────────────────────────────────────┐
│  Cognitive Layer (Brain)                 │
│  Port: 8000                             │
│  Web: http://localhost:8000             │
└─────────────────────────────────────────┘
           ↓
┌─────────────────────────────────────────┐
│  Input Layer                            │
│  ├─ Camera Server (8765)                │
│  └─ Frame Processor                     │
└─────────────────────────────────────────┘
           ↓
┌─────────────────────────────────────────┐
│  Planning Layer                         │
│  Port: 8001                             │
└─────────────────────────────────────────┘
```

## 🔍 Step-by-Step Manual Start

### 1. Start Ollama
```bash
ollama serve
```
**Keep this terminal open!**

### 2. Start Cognitive Layer
**New Terminal:**
```bash
cd /home/vedantso/ShowcaseSoftware
python3 brain_server.py
```
**Keep this terminal open!**
**Open browser:** http://localhost:8000

### 3. Start Input Layer
**New Terminal:**
```bash
cd /home/vedantso/ShowcaseSoftware
./start_input_layer.sh
```
**Keep this terminal open!**

### 4. Start Planning Layer
**New Terminal:**
```bash
cd /home/vedantso/ShowcaseSoftware
python3 -m planning_layer.planning_server
```
**Keep this terminal open!**

## ✅ Verify Everything Works

Run this in a new terminal:

```bash
echo "Checking services..."
curl -s http://localhost:11434/api/tags > /dev/null && echo "✓ Ollama" || echo "✗ Ollama"
curl -s http://localhost:8000/api/graph/state > /dev/null && echo "✓ Cognitive Layer" || echo "✗ Cognitive Layer"
curl -s http://localhost:8001/api/plan/status > /dev/null && echo "✓ Planning Layer" || echo "✗ Planning Layer"
```

## 🧪 Quick Tests

### Test Cognitive Layer
```bash
curl -X POST http://localhost:8000/api/events/process \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Ian just finished building the robot",
    "user_name": "Ian",
    "detected_actions": ["completed"]
  }'
```

### Test Planning Layer
```bash
curl -X POST http://localhost:8001/api/plan/generate \
  -H "Content-Type: application/json" \
  -d '{
    "goal": "Pick up the red cup",
    "scene_description": "Red cup is on kitchen counter, 40cm away"
  }'
```

## 🛑 Stop Everything

```bash
# Kill all services
pkill -f brain_server.py
pkill -f camera_server
pkill -f frame_processor
pkill -f planning_server
pkill ollama
```

Or press **Ctrl+C** in each terminal.

## 📊 Service Status URLs

- **Ollama**: http://localhost:11434/api/tags
- **Cognitive Layer**: http://localhost:8000/api/graph/state
- **Planning Layer**: http://localhost:8001/api/plan/status
- **Web Dashboard**: http://localhost:8000

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Kill processes on ports
lsof -ti :8000 | xargs kill -9
lsof -ti :8001 | xargs kill -9
lsof -ti :8765 | xargs kill -9
```

### Check Logs
```bash
# If using startup script, logs are in:
cat /tmp/eden_cognitive.log
cat /tmp/eden_planning.log
cat /tmp/eden_camera.log
cat /tmp/eden_frame_processor.log
```

### GPU Not Available
Planning layer will automatically use Ollama fallback. Check:
```bash
python3 -c "import torch; print(torch.cuda.is_available())"
```

## 🎯 What Happens When Running

1. **Camera** captures frames → **YOLO** detects objects
2. **Important frames** sent to **Frame Processor**
3. **VLM** (Ollama) analyzes frames → generates descriptions
4. **Context Gathering** determines importance
5. **Cognitive Layer** processes events → stores in memory graph
6. **Planning Layer** generates action plans when needed
7. **Web Dashboard** shows real-time graph visualization

Everything works together automatically!

