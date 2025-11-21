# 🚀 How to Start Everything - EDEN

## Quick Start (Easiest)

### Option 1: Showcase Mode (Recommended for Demo)
```bash
cd /home/vedantso/ShowcaseSoftware
./start_showcase_mode.sh
```
This starts:
- ✅ Ollama (LLM)
- ✅ Cognitive Layer (Brain) - with test knowledge graph
- ✅ Planning Layer (uses llama3.1)

Then start Electron dashboard:
```bash
cd electron-app
npm start
```

---

## Option 2: Full System (All Services)

```bash
cd /home/vedantso/ShowcaseSoftware
./start_all_services.sh
```

This starts:
- ✅ Ollama
- ✅ Cognitive Layer
- ✅ Input Layer (Camera)
- ✅ Planning Layer

---

## Manual Start (Step by Step)

### Terminal 1: Ollama
```bash
ollama serve
```
Keep this terminal open!

### Terminal 2: Cognitive Layer
```bash
cd /home/vedantso/ShowcaseSoftware
POPULATE_TEST_DATA=true python3 brain_server.py
```
Open: http://localhost:8000

### Terminal 3: Planning Layer
```bash
cd /home/vedantso/ShowcaseSoftware
python3 -m planning_layer.planning_server
```
API: http://localhost:8001

### Terminal 4: Electron Dashboard
```bash
cd /home/vedantso/ShowcaseSoftware/electron-app
npm start
```

---

## Verify Everything is Running

```bash
# Check Ollama
curl http://localhost:11434/api/tags && echo " ✓ Ollama"

# Check Cognitive Layer
curl http://localhost:8000/api/graph/state > /dev/null && echo " ✓ Cognitive Layer"

# Check Planning Layer
curl http://localhost:8001/api/plan/status > /dev/null && echo " ✓ Planning Layer"
```

---

## Stop Everything

```bash
# Kill all services
pkill -f brain_server.py
pkill -f planning_server
pkill ollama

# Or kill by port
lsof -ti :8000 | xargs kill -9
lsof -ti :8001 | xargs kill -9
```

---

## Troubleshooting

**Port already in use?**
```bash
lsof -ti :8000 | xargs kill -9
lsof -ti :8001 | xargs kill -9
```

**Check logs:**
```bash
tail -f /tmp/eden_cognitive.log
tail -f /tmp/eden_planning.log
```

**Ollama not starting?**
```bash
ollama serve
# Check if it's running:
curl http://localhost:11434/api/tags
```

