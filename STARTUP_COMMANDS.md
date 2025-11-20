# Complete Startup Commands for EDEN

## Why the Error Happened

The error `[Errno 98] error while attempting to bind on address ('0.0.0.0', 8000): address already in use` occurred because:

1. **Port 8000 was already occupied** by a previous instance of `brain_server.py` (PID 13638)
2. When you tried to start a new server, it couldn't bind to port 8000 because the old one was still using it
3. **Solution**: Kill the old process first, then start the new one

## Complete Startup Sequence

### Step 1: Check What's Already Running

```bash
# Check if Ollama is running
curl -s http://localhost:11434/api/tags > /dev/null && echo "✓ Ollama running" || echo "✗ Ollama not running"

# Check if EDEN server is running
curl -s http://localhost:8000/api/graph/state > /dev/null && echo "✓ EDEN server running" || echo "✗ EDEN server not running"

# Check processes
ps aux | grep -E "(ollama|brain_server)" | grep -v grep
```

### Step 2: Kill Existing Processes (if needed)

```bash
# Find and kill old EDEN server
ps aux | grep brain_server | grep -v grep | awk '{print $2}' | xargs kill -9

# Or kill by port
lsof -ti :8000 | xargs kill -9

# Kill Ollama (if needed)
pkill ollama
```

### Step 3: Start Ollama

```bash
# Start Ollama in background
ollama serve &

# OR start in foreground (keep terminal open)
ollama serve

# Verify it's running
sleep 2 && curl http://localhost:11434/api/tags
```

**Note**: If you see "address already in use", Ollama is already running - that's fine!

### Step 4: Pull Model (if not already done)

```bash
# Check what models you have
ollama list

# Pull a model (if needed)
ollama pull llama3
# OR
ollama pull mistral
```

### Step 5: Start EDEN Brain Server

```bash
cd /home/vedantso/ShowcaseSoftware
python3 brain_server.py
```

**Keep this terminal open!** The server needs to keep running.

### Step 6: Verify Everything is Working

```bash
# In a NEW terminal, test the server
curl http://localhost:8000/api/graph/state | python3 -m json.tool | head -10

# Check event processing config
curl http://localhost:8000/api/events/config | python3 -m json.tool

# Test event processing
curl -X POST http://localhost:8000/api/events/process \
  -H "Content-Type: application/json" \
  -d '{"description": "Test event", "user_name": "Test"}'
```

## All-in-One Startup Script

Create a file `start_eden.sh`:

```bash
#!/bin/bash

echo "=== Starting EDEN Cognitive Layer ==="

# Check if Ollama is running
if curl -s http://localhost:11434/api/tags > /dev/null; then
    echo "✓ Ollama is already running"
else
    echo "Starting Ollama..."
    ollama serve &
    sleep 3
    if curl -s http://localhost:11434/api/tags > /dev/null; then
        echo "✓ Ollama started successfully"
    else
        echo "✗ Failed to start Ollama"
        exit 1
    fi
fi

# Check if port 8000 is in use
if lsof -ti :8000 > /dev/null; then
    echo "Port 8000 is in use. Killing old process..."
    lsof -ti :8000 | xargs kill -9
    sleep 2
fi

# Start EDEN server
echo "Starting EDEN Brain Server..."
cd /home/vedantso/ShowcaseSoftware
python3 brain_server.py
```

Make it executable and run:
```bash
chmod +x start_eden.sh
./start_eden.sh
```

## Quick Reference Commands

### Start Everything
```bash
# Terminal 1: Ollama
ollama serve

# Terminal 2: EDEN Server
cd /home/vedantso/ShowcaseSoftware && python3 brain_server.py

# Terminal 3: Testing
curl http://localhost:8000/api/graph/state
```

### Check Status
```bash
# Check Ollama
curl http://localhost:11434/api/tags

# Check EDEN server
curl http://localhost:8000/api/graph/state

# Check processes
ps aux | grep -E "(ollama|brain_server)"
```

### Kill Everything
```bash
# Kill EDEN server
pkill -f brain_server.py
# OR
lsof -ti :8000 | xargs kill -9

# Kill Ollama
pkill ollama
```

### Restart Everything
```bash
# Kill old processes
pkill -f brain_server.py
pkill ollama

# Wait a moment
sleep 2

# Start Ollama
ollama serve &

# Start EDEN server
cd /home/vedantso/ShowcaseSoftware && python3 brain_server.py
```

## Troubleshooting

### Port 8000 Already in Use
```bash
# Find what's using it
lsof -i :8000

# Kill it
lsof -ti :8000 | xargs kill -9
```

### Ollama Port 11434 Already in Use
```bash
# This is usually fine - Ollama is already running
# Just verify:
curl http://localhost:11434/api/tags
```

### Import Errors
```bash
# Reinstall dependencies
cd /home/vedantso/ShowcaseSoftware
pip3 install -r requirements.txt --user
```

### Server Won't Start
```bash
# Check Python version (needs 3.10+)
python3 --version

# Check if all dependencies are installed
python3 -c "import fastapi, networkx, chromadb; print('OK')"
```

## Expected Output

When everything starts correctly:

**Ollama:**
```
INFO[0000] Starting server... 
INFO[0000] Using default host: 127.0.0.1:11434
```

**EDEN Server:**
```
INFO:     Started server process [XXXXX]
INFO:     Waiting for application startup.
EDEN Cognitive Layer initialized
Graph nodes: 2
Graph edges: 0
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

## Web Interface

Once both are running, open:
```
http://localhost:8000
```

You should see:
- 3D graph visualization
- God Mode control panel
- Status indicator

