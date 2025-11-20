# EDEN Cognitive Layer

This package contains the core cognitive processing system for the EDEN humanoid robot.

## Structure

```
cognitive_layer/
├── __init__.py           # Package initialization, exports main classes
├── config.py             # Configuration (Ollama, thresholds, personality modulation)
├── ego_core.py           # Core Ego Graph engine with memory and event processing
├── llm_analyzer.py       # LLM-powered cognitive analyzer (Ollama integration)
├── scenario_manager.py   # Demo scenario management (trauma arc, etc.)
└── templates/
    └── index.html        # Frontend 3D visualization
```

## Main Components

### EgoGraph (`ego_core.py`)
- Self-modulating knowledge graph
- Personality-based perception filtering
- Memory management (user-specific and global)
- Event processing pipeline

### CognitiveAnalyzer (`llm_analyzer.py`)
- LLM-powered event importance analysis
- Ollama integration
- Fallback to heuristic analysis

### Configuration (`config.py`)
- Ollama settings
- Importance thresholds
- Personality modulation weights
- Memory parameters

## Usage

```python
from cognitive_layer import EgoGraph

# Initialize
ego_graph = EgoGraph()

# Process an event
event = {
    "description": "Ian just finished building the robot",
    "user_name": "Ian",
    "detected_actions": ["completed"]
}
result = ego_graph.process_event_frame(event)
```

## Import Paths

After reorganization, use:
- `from cognitive_layer import EgoGraph`
- `from cognitive_layer.ego_core import EventFrame, MemoryNode`
- `from cognitive_layer.llm_analyzer import CognitiveAnalyzer`

