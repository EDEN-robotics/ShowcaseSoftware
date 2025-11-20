# EDEN Cognitive Layer - The "Ego Engine"

The Self-Modulating Knowledge Graph system for the EDEN humanoid robot, featuring real-time personality adjustment, intelligent event processing, and 3D visualization.

## 🎯 Overview

EDEN is a humanoid robotics project at the Texas A&M TURTLE Lab. This cognitive layer implements a sophisticated "Ego Engine" that processes events through multiple cognitive layers (heuristic, semantic, and LLM-powered analysis) to determine what should be remembered, filtered through the lens of personality and memory context.

## 🏗️ Architecture

- **Backend**: Python FastAPI server with NetworkX graph engine
- **Frontend**: 3D visualization using 3d-force-graph
- **Memory**: ChromaDB for semantic memory storage
- **LLM**: Ollama integration for cognitive event analysis
- **Personality**: Big 5 Personality Traits (OCEAN model)

## 📋 Prerequisites

- Python 3.10+
- Ollama (for LLM-powered analysis) - [Install Ollama](https://ollama.ai)
- 4GB+ RAM (for Ollama models)

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd ShowcaseSoftware
```

### 2. Install Python Dependencies

```bash
pip3 install -r requirements.txt --user
```

### 3. Install and Setup Ollama

```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull a model (choose one)
ollama pull llama3
# OR
ollama pull mistral

# Start Ollama (in a separate terminal)
ollama serve
```

**Note**: The system works without Ollama but will use fallback heuristic analysis. For full cognitive capabilities, Ollama is recommended.

### 4. Start the EDEN Brain Server

```bash
python3 brain_server.py
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
EDEN Cognitive Layer initialized
```

### 5. Open the Web Interface

Open your browser to: `http://localhost:8000`

You'll see:
- 3D graph visualization with the central SELF node
- God Mode control panel with personality sliders
- Real-time graph updates

## 📁 Project Structure

```
ShowcaseSoftware/
├── cognitive_layer/          # Core cognitive processing system
│   ├── __init__.py          # Package exports
│   ├── config.py            # Configuration (Ollama, thresholds)
│   ├── ego_core.py          # Ego Graph engine & event processing
│   ├── llm_analyzer.py      # LLM cognitive analyzer (Ollama)
│   ├── scenario_manager.py  # Demo scenarios
│   ├── templates/
│   │   └── index.html       # 3D visualization frontend
│   └── README.md            # Cognitive layer docs
│
├── brain_server.py          # FastAPI server (main entry point)
├── test_event_processing.py # Test script
├── requirements.txt         # Python dependencies
│
├── README.md               # This file
├── QUICK_START.md          # Quick start guide
├── STARTUP_COMMANDS.md     # Complete startup commands
├── EVENT_PROCESSING_GUIDE.md # Event processing documentation
└── PROJECT_STRUCTURE.md    # Detailed structure overview
```

## ✨ Features

### God Mode Dashboard
- Real-time personality trait adjustment via sliders
- Visual feedback: SELF node color changes based on personality
- Event injection buttons for trauma/kindness scenarios

### Intelligent Event Processing
- **3-Layer Analysis**: Heuristic → Semantic → LLM cognitive reasoning
- **Personality-Aware**: Importance modulated by Big 5 traits
- **Memory Context**: Considers relevant past memories
- **Dynamic Thresholds**: Adjusts based on event type and context

### 3D Graph Visualization
- Central SELF node (the "Ego")
- Memory nodes orbiting around SELF
- Color-coded nodes: Red (threat/trauma), Green (joy), Blue (memory)
- Dynamic edge weights based on personality

## 🔌 API Endpoints

### Core Endpoints

- `GET /` - Web interface
- `GET /api/graph/state` - Get current graph state
- `WS /ws` - WebSocket for real-time updates

### Personality Control

- `POST /api/god_mode/set_personality` - Update personality trait
  ```json
  {"trait": "Agreeableness", "value": 0.9}
  ```

### Interactions

- `POST /api/interact` - Process user interaction
  ```json
  {"user": "Ian", "action": "Waves hello"}
  ```

### Event Processing

- `POST /api/events/process` - Process single event frame
  ```json
  {
    "description": "Ian just finished building the robot",
    "user_name": "Ian",
    "detected_actions": ["completed", "finished"]
  }
  ```

- `POST /api/events/batch` - Process batch of events
  ```json
  {
    "events": [
      {"description": "Event 1", "user_name": "Ian"},
      {"description": "Event 2", "user_name": "Student"}
    ]
  }
  ```

- `GET /api/events/config` - Get configuration
- `POST /api/events/config` - Update configuration

### Demo Events

- `POST /api/event/inject` - Inject trauma/kindness event
  ```json
  {"event_type": "trauma", "description": "John throws can"}
  ```

## 🧪 Testing

### Test Event Processing

```bash
python3 test_event_processing.py
```

### Test with cURL

```bash
# Test single event
curl -X POST http://localhost:8000/api/events/process \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Ian just finished building the robot",
    "user_name": "Ian",
    "detected_actions": ["completed"]
  }'

# Get graph state
curl http://localhost:8000/api/graph/state | python3 -m json.tool
```

## 📖 Documentation

- **[QUICK_START.md](QUICK_START.md)** - Quick setup guide
- **[STARTUP_COMMANDS.md](STARTUP_COMMANDS.md)** - Complete startup commands
- **[EVENT_PROCESSING_GUIDE.md](EVENT_PROCESSING_GUIDE.md)** - Event processing documentation
- **[PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)** - Detailed structure overview
- **[cognitive_layer/README.md](cognitive_layer/README.md)** - Cognitive layer documentation

## 🔧 Configuration

Edit `cognitive_layer/config.py` to customize:

- Ollama URL and model
- Importance thresholds by event type
- Personality modulation weights
- Memory processing parameters

## 🐛 Troubleshooting

### Port 8000 Already in Use

```bash
# Kill existing server
lsof -ti :8000 | xargs kill -9
```

### Ollama Not Found

```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Verify it's running
curl http://localhost:11434/api/tags
```

### Import Errors

```bash
# Reinstall dependencies
pip3 install --upgrade -r requirements.txt --user
```

See [STARTUP_COMMANDS.md](STARTUP_COMMANDS.md) for more troubleshooting.

## 🧠 How It Works

### Event Processing Pipeline

1. **Event Arrives**: JSON event with description, user info, actions
2. **Retrieve Memories**: Semantic search for relevant past memories
3. **3-Layer Analysis**:
   - **Heuristic**: Keyword-based quick scoring
   - **Semantic**: Similarity to important memories
   - **LLM**: Deep cognitive reasoning via Ollama
4. **Personality Modulation**: Adjust importance based on Big 5 traits
5. **Dynamic Threshold**: Determine if event should be remembered
6. **Graph Update**: Add to graph if important, or store as episodic memory

### Personality Traits

- **Openness**: Receptiveness to novel events
- **Conscientiousness**: Values achievements and completions
- **Extroversion**: Amplifies social interactions
- **Agreeableness**: Amplifies positive social events
- **Neuroticism**: Amplifies threats and negative events

## 🤝 Contributing

This is a research project for the Texas A&M TURTLE Lab. For contributions, please follow the project's contribution guidelines.

## 📝 License

[Add your license here]

## 🙏 Acknowledgments

- Texas A&M TURTLE Lab
- Ollama for LLM capabilities
- NetworkX for graph operations
- ChromaDB for semantic memory storage

## 📧 Contact

[Add contact information]

---

**Note**: This system is designed for the EDEN humanoid robot showcase. The cognitive layer processes events intelligently, deciding what's important enough to remember based on personality and memory context - mimicking human cognitive processing.
