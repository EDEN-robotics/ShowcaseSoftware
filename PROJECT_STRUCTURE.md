# EDEN Project Structure

## Reorganized Structure

All cognitive layer components have been moved into the `cognitive_layer/` folder.

```
ShowcaseSoftware/
├── cognitive_layer/          # Core cognitive processing system
│   ├── __init__.py          # Package exports
│   ├── config.py            # Configuration settings
│   ├── ego_core.py          # Ego Graph engine
│   ├── llm_analyzer.py      # LLM cognitive analyzer
│   ├── scenario_manager.py  # Demo scenarios
│   ├── templates/
│   │   └── index.html       # 3D visualization frontend
│   └── README.md            # Cognitive layer documentation
│
├── brain_server.py          # FastAPI server (main entry point)
├── test_event_processing.py # Test script
├── requirements.txt         # Python dependencies
│
├── README.md               # Main project README
├── QUICK_START.md          # Quick start guide
├── STARTUP_COMMANDS.md     # Complete startup commands
├── EVENT_PROCESSING_GUIDE.md # Event processing documentation
└── PROJECT_STRUCTURE.md    # This file
```

## Import Changes

### Before:
```python
from ego_core import EgoGraph
from llm_analyzer import CognitiveAnalyzer
import config
```

### After:
```python
from cognitive_layer import EgoGraph
from cognitive_layer.llm_analyzer import CognitiveAnalyzer
from cognitive_layer import config
```

## Running the System

The main entry point remains the same:

```bash
python3 brain_server.py
```

The server automatically imports from `cognitive_layer/` package.

## Files Moved

- `ego_core.py` → `cognitive_layer/ego_core.py`
- `llm_analyzer.py` → `cognitive_layer/llm_analyzer.py`
- `config.py` → `cognitive_layer/config.py`
- `scenario_manager.py` → `cognitive_layer/scenario_manager.py`
- `templates/index.html` → `cognitive_layer/templates/index.html`

## Files Updated

- `brain_server.py` - Updated imports and template path
- `test_event_processing.py` - Updated imports
- All files in `cognitive_layer/` - Updated relative imports

## Benefits

1. **Better Organization**: All cognitive layer code in one place
2. **Cleaner Root**: Main directory less cluttered
3. **Package Structure**: Proper Python package with `__init__.py`
4. **Easier Maintenance**: Related files grouped together
5. **Clear Separation**: Cognitive layer separate from server/scripts

