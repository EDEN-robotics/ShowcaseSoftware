# EDEN Cognitive Layer - Quick Start Guide

## Step 1: Install Python Dependencies

```bash
cd /home/vedantso/ShowcaseSoftware
pip3 install -r requirements.txt --user
```

## Step 2: Install and Setup Ollama

### Install Ollama

**Linux:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

**Or download from:** https://ollama.ai/download

### Start Ollama Service

```bash
# Start Ollama (runs in background)
ollama serve

# Or if you want to run it in foreground to see logs:
ollama serve
```

**Note:** Ollama runs on `http://localhost:11434` by default.

### Pull a Model

Choose one of these models (llama3 is recommended):

```bash
# Option 1: Llama 3 (recommended, ~4.7GB)
ollama pull llama3

# Option 2: Mistral (smaller, ~4.1GB)
ollama pull mistral

# Option 3: Llama 2 (older, ~3.8GB)
ollama pull llama2
```

### Verify Ollama is Running

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Test a quick generation
ollama run llama3 "Hello, test"
```

## Step 3: Start EDEN Brain Server

```bash
cd /home/vedantso/ShowcaseSoftware
python3 brain_server.py
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
EDEN Cognitive Layer initialized
```

**Keep this terminal open!** The server needs to keep running.

## Step 4: Open the Web Interface

Open your browser and go to:
```
http://localhost:8000
```

You should see:
- 3D graph visualization
- God Mode control panel with personality sliders
- Status indicator

## Step 5: Test Event Processing

### Test with cURL (Terminal)

Open a **new terminal** (keep server running):

```bash
# Test single event processing
curl -X POST http://localhost:8000/api/events/process \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Ian just finished building the robot. This is a significant achievement.",
    "user_name": "Ian",
    "detected_actions": ["completed", "finished"],
    "source": "camera_frame"
  }'
```

### Test Batch Processing

```bash
curl -X POST http://localhost:8000/api/events/batch \
  -H "Content-Type: application/json" \
  -d '{
    "events": [
      {
        "description": "Student gives friendly high-five",
        "user_name": "Student",
        "detected_actions": ["wave", "high-five"]
      },
      {
        "description": "Routine check of robot status",
        "detected_actions": ["check"],
        "source": "system"
      }
    ]
  }'
```

### Test with Python Script

```bash
python3 test_event_processing.py
```

## Step 6: Check Configuration

```bash
# Get current config
curl http://localhost:8000/api/events/config

# Check if Ollama is detected
curl http://localhost:8000/api/events/config | python3 -m json.tool
```

## Troubleshooting

### Ollama Not Found?

```bash
# Check if Ollama is installed
which ollama

# If not found, install it:
curl -fsSL https://ollama.ai/install.sh | sh

# Add to PATH if needed (add to ~/.bashrc):
export PATH=$PATH:$HOME/.local/bin
```

### Ollama Not Running?

```bash
# Start Ollama
ollama serve

# Check if it's running
ps aux | grep ollama
```

### Port 8000 Already in Use?

```bash
# Find what's using port 8000
lsof -i :8000

# Kill the process or use a different port
# Edit brain_server.py and change port=8000 to port=8001
```

### Import Errors?

```bash
# Reinstall dependencies
pip3 install --upgrade -r requirements.txt --user

# Check Python version (needs 3.10+)
python3 --version
```

## Running Everything Together

### Terminal 1: Ollama (if not running as service)

```bash
ollama serve
```

### Terminal 2: EDEN Brain Server

```bash
cd /home/vedantso/ShowcaseSoftware
python3 brain_server.py
```

### Terminal 3: Testing/API Calls

```bash
# Test endpoints here
curl http://localhost:8000/api/graph/state
```

## Quick Commands Reference

```bash
# Start Ollama
ollama serve

# Pull model
ollama pull llama3

# Start server
python3 brain_server.py

# Test event
curl -X POST http://localhost:8000/api/events/process -H "Content-Type: application/json" -d '{"description": "test event"}'

# Get graph state
curl http://localhost:8000/api/graph/state

# Check config
curl http://localhost:8000/api/events/config
```

## What Each Component Does

- **Ollama**: Provides LLM for intelligent event analysis
- **brain_server.py**: FastAPI server that handles all API requests
- **ego_core.py**: Core cognitive engine with graph and memory
- **llm_analyzer.py**: Connects to Ollama for cognitive analysis
- **Web Interface**: 3D visualization at http://localhost:8000

## Next Steps

1. Send events from your vision system to `/api/events/process`
2. Adjust personality traits via God Mode sliders
3. Watch the graph update in real-time via WebSocket
4. Check reasoning traces in API responses

