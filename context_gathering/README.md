# EDEN Context Gathering Layer

The Context Gathering Layer analyzes frames to determine importance and generate rich context descriptions using Vision-Language Models (VLM).

## Overview

This layer sits between the Input Layer and Cognitive Layer, providing:

1. **Importance Analysis**: Determines which frames are important and why
2. **VLM Analysis**: Uses Ollama llama3.2-vision to analyze what's happening
3. **Structured Extraction**: Extracts objects, actions, emotions, spatial relationships
4. **Cognitive Formatting**: Formats data exactly as the cognitive layer expects

## Components

### ContextAnalyzer (`context_analyzer.py`)
Main class that orchestrates context gathering:
- Analyzes frames with VLM
- Determines importance
- Extracts structured information
- Formats for cognitive layer

### FrameImportanceAnalyzer (`frame_importance.py`)
Analyzes why frames are important:
- Motion-based importance
- Object detection importance
- Novelty detection (scene changes)
- VLM-powered importance reasoning

## How It Works

```
Frame → Importance Analysis → VLM Scene Analysis → Structured Extraction → Cognitive Layer Format
```

### Step 1: Importance Analysis
- Calculates motion importance (0-1 score)
- Calculates detection importance (based on objects)
- Calculates novelty (scene changes)
- Combines into weighted importance score

### Step 2: VLM Scene Analysis
- Sends frame to Ollama llama3.2-vision
- Gets natural language description
- Analyzes: objects, actions, emotions, spatial relationships

### Step 3: Structured Extraction
- Extracts detected objects from YOLO
- Extracts actions from VLM description
- Detects emotional tone
- Identifies spatial relationships

### Step 4: Cognitive Layer Format
- Formats as EventFrame JSON
- Includes all metadata
- Adds importance reasoning
- Ready for cognitive layer processing

## Usage

### Direct Usage

```python
from context_gathering import ContextAnalyzer
import cv2

analyzer = ContextAnalyzer()

# Process a frame
frame = cv2.imread("frame.jpg")
metadata = {
    "frame_id": "frame_001",
    "timestamp": "2024-01-01T12:00:00",
    "motion_score": 45.2,
    "detections": [
        {"class": "person", "confidence": 0.9, "bbox": [100, 100, 200, 300]}
    ]
}

context_data = await analyzer.gather_context(frame, metadata)
```

### Integration with Frame Processor

The frame processor automatically uses the context gathering layer:

```python
from input_layer import FrameProcessor

processor = FrameProcessor()
# Automatically uses ContextAnalyzer internally
```

## Output Format

The context gathering layer outputs data in this format:

```json
{
  "frame_id": "frame_123_1234567890",
  "timestamp": "2024-11-20T01:00:00",
  "description": "A person is waving hello...",
  "detected_objects": ["person", "bottle"],
  "detected_actions": ["waving", "walking"],
  "emotional_tone": "positive",
  "scene_context": "A person is waving...",
  "source": "camera_frame",
  "metadata": {
    "motion_score": 45.2,
    "detection_count": 2,
    "importance_score": 0.75,
    "is_important": true,
    "importance_reasoning": "High motion detected with person present...",
    "yolo_detections": [...],
    "spatial_relationships": ["Person is near the table"]
  }
}
```

## Configuration

Edit `context_gathering/config.py`:

- **VLM Model**: `VLM_MODEL = "llama3.2-vision:11b"`
- **Importance Weights**: Motion, detection, novelty weights
- **Prompts**: Customize VLM prompts
- **Analysis Features**: Enable/disable emotional tone, spatial relationships

## Importance Analysis

The importance score combines:

1. **Motion Importance** (30% weight)
   - Low motion (< 25): 0.2
   - Moderate (25-50): 0.5
   - High (50-100): 0.7
   - Very high (> 100): 0.9

2. **Detection Importance** (40% weight)
   - No objects: 0.2
   - Objects detected: 0.4-0.7
   - Important objects (person/human): 0.5-0.9

3. **Novelty Score** (30% weight)
   - No changes: 0.3
   - Scene changes: 0.5-0.8

**Final Score**: Weighted average of all three

## VLM Analysis

The VLM analyzes:
- Main objects and people
- Actions and movements
- Spatial relationships
- Emotional context
- Notable events
- Context clues

## Integration Points

### With Input Layer
- Receives frames from `CameraServer`
- Gets metadata (motion, detections)

### With Cognitive Layer
- Sends formatted events to `/api/events/process`
- Matches `EventFrame` structure exactly

## Performance

- **VLM Analysis**: ~1-3 seconds per frame (depends on GPU)
- **Importance Analysis**: < 10ms (heuristic-based)
- **Total Processing**: ~1-3 seconds per important frame

## Dependencies

- `requests` - For Ollama API calls
- `numpy` - For numerical operations
- `cv2` - For image encoding (already in input_layer)

## Troubleshooting

### VLM Not Responding
- Check Ollama is running: `curl http://localhost:11434/api/tags`
- Verify model is pulled: `ollama list`
- Pull model: `ollama pull llama3.2-vision:11b`

### Low Importance Scores
- Adjust weights in `config.py`
- Lower `MOTION_THRESHOLD_FOR_ANALYSIS`
- Lower `MIN_CONFIDENCE_FOR_IMPORTANCE`

### Import Errors
- Ensure `context_gathering` is in Python path
- Check `__init__.py` exists

