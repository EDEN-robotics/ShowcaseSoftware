# EDEN Showcase Mode

## Overview
Showcase Mode runs **Cognitive Layer + Planning Layer** with pre-populated test data. Input Layer and Context Gathering are disabled for demo purposes.

## Quick Start

```bash
cd /home/vedantso/ShowcaseSoftware
./start_showcase_mode.sh
```

This will:
1. ✅ Start Cognitive Layer with **artificial knowledge graph** (house environment)
2. ✅ Start Planning Layer (Cosmos or Ollama fallback)
3. ❌ Skip Input Layer
4. ❌ Skip Context Gathering

## What You'll See

### Cognitive Layer Dashboard
Open: **http://localhost:8000**

You'll see:
- **3D Knowledge Graph** with many nodes (rooms, objects, users, interactions)
- **GOD MODE** sliders for personality adjustment
- **EDEN Status** panel showing node/edge counts

### Test Planning

**Via API:**
```bash
curl -X POST http://localhost:8000/api/plan/request \
  -H "Content-Type: application/json" \
  -d '{"goal": "Pick up the red cup from the kitchen counter", "user_context": "Ian"}'
```

**Via Python:**
```python
import requests

response = requests.post(
    "http://localhost:8000/api/plan/request",
    json={
        "goal": "Move the blue book from the office desk to the living room bookshelf",
        "user_context": "Student"
    }
)

print(response.json())
```

## Test Knowledge Graph Contents

The artificial knowledge graph includes:

- **6 Rooms**: Living Room, Kitchen, Bedroom, Bathroom, Office, Garage
- **40+ Objects**: Furniture, appliances, tools, etc.
- **4 Users**: Ian, Student, Judge, Dr. Smith
- **Multiple Interactions**: Past interactions with users
- **Spatial Relationships**: Objects linked to rooms, spatial connections

## Planning Layer Integration

The cognitive layer automatically:
1. Retrieves relevant memories based on goal
2. Builds scene description from memories
3. Calls planning layer with context
4. Stores planning result as new memory
5. Updates graph visualization

## Manual Population

If you want to manually populate test data:

```bash
python3 populate_test_data.py
```

Then restart the cognitive layer:
```bash
POPULATE_TEST_DATA=true python3 brain_server.py
```

## Troubleshooting

**Graph shows only 2 nodes?**
- The test data wasn't loaded. Check startup logs for "Populating cognitive layer..."
- Restart with: `POPULATE_TEST_DATA=true python3 brain_server.py`

**Planning layer not responding?**
- Check: `curl http://localhost:8001/api/plan/status`
- Check logs: `tail -f /tmp/eden_planning.log`

**Ollama not running?**
- Start: `ollama serve`
- Or let the script start it automatically

