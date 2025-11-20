# EDEN Input Layer

The Input Layer handles camera capture, object detection (YOLOv11), and Vision-Language Model (VLM) processing to generate frame descriptions that feed into the cognitive layer.

## Architecture

```
Camera → YOLO Detection → Motion/Importance Filter → WebSocket → VLM Analysis → Cognitive Layer
```

## Components

### CameraServer (`camera_server.py`)
- Captures frames from camera (OpenCV)
- Runs YOLOv11 object detection
- Detects motion and filters important frames
- Sends frames + metadata via WebSocket (port 8765)

### FrameProcessor (`frame_processor.py`)
- Receives frames from CameraServer
- Uses Ollama VLM (llama3.2-vision) to generate descriptions
- Extracts detected objects and actions
- Sends processed events to cognitive layer API

## Installation

### Dependencies

```bash
pip install ultralytics opencv-python websockets ollama requests numpy
```

### YOLO Model

Place `YOLOv11obj_model.pt` in one of these locations:
- `input_layer/YOLOv11obj_model.pt`
- `input_layer/Input-Layer-main/YOLOv11obj_model.pt`

The system will automatically search for it.

### Ollama VLM Model

```bash
ollama pull llama3.2-vision:11b
```

## Usage

### Start Camera Server

```bash
python3 -m input_layer.camera_server
```

Or:
```bash
cd input_layer
python3 camera_server.py
```

### Start Frame Processor

```bash
python3 -m input_layer.frame_processor
```

Or:
```bash
cd input_layer
python3 frame_processor.py
```

### Run Both Together

**Terminal 1: Camera Server**
```bash
python3 -m input_layer.camera_server
```

**Terminal 2: Frame Processor**
```bash
python3 -m input_layer.frame_processor
```

**Terminal 3: Cognitive Layer Server**
```bash
python3 brain_server.py
```

## Configuration

Edit `input_layer/config.py` to customize:

- Camera settings (index, resolution, FPS)
- YOLO model path and confidence threshold
- Motion detection threshold
- WebSocket host/port
- VLM model name
- Cognitive layer URL

## Flow

1. **Camera Server** captures frames continuously
2. **YOLO** detects objects in each frame
3. **Motion Detection** filters important frames (motion > threshold OR high-confidence detections)
4. **WebSocket** sends important frames to Frame Processor
5. **VLM** generates natural language description
6. **Frame Processor** extracts objects/actions and sends to Cognitive Layer
7. **Cognitive Layer** processes event and decides if it should be remembered

## Integration with Cognitive Layer

The Frame Processor automatically sends events to:
```
POST http://localhost:8000/api/events/process
```

With event data:
```json
{
  "frame_id": "frame_123",
  "timestamp": "2024-01-01T12:00:00",
  "description": "VLM-generated description",
  "detected_objects": ["person", "bottle"],
  "detected_actions": ["waving", "walking"],
  "source": "camera_frame"
}
```

## Troubleshooting

### Camera Not Found
- Check camera index in `config.py` (try 0, 1, 2...)
- Verify camera permissions
- Test with: `python3 -c "import cv2; cap = cv2.VideoCapture(0); print(cap.isOpened())"`

### YOLO Model Not Found
- Check model file exists in expected locations
- Update `YOLO_MODEL_PATH` in config.py

### VLM Errors
- Verify Ollama is running: `curl http://localhost:11434/api/tags`
- Check model is pulled: `ollama list`
- Pull model: `ollama pull llama3.2-vision:11b`

### WebSocket Connection Failed
- Ensure Camera Server is running first
- Check port 8765 is not in use: `lsof -i :8765`
- Verify firewall settings

### Cognitive Layer Not Receiving Events
- Ensure cognitive layer server is running: `python3 brain_server.py`
- Check URL in config: `COGNITIVE_LAYER_URL = "http://localhost:8000"`
- Verify endpoint: `curl http://localhost:8000/api/graph/state`

## Performance

- **Frame Rate**: Typically 5-10 important frames per second (throttled by SEND_INTERVAL)
- **VLM Processing**: ~1-3 seconds per frame (depends on GPU)
- **YOLO Detection**: ~50-100ms per frame (GPU) or ~200-500ms (CPU)

## Improvements Over Original

1. **Better Error Handling**: Graceful fallbacks and reconnection
2. **Configuration File**: Centralized settings
3. **Cognitive Integration**: Direct API integration
4. **Code Organization**: Proper package structure
5. **Type Hints**: Better code documentation
6. **Flexible Model Paths**: Auto-detection of model file
7. **Action Extraction**: Heuristic-based action detection from VLM descriptions

