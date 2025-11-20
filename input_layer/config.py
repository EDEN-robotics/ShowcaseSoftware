"""
Input Layer Configuration
"""

# Camera Settings
CAMERA_INDEX = 0  # Default camera (0 for built-in, 1 for external, etc.)
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
FPS = 30

# YOLO Model Settings
# Path relative to project root, or absolute path
YOLO_MODEL_PATH = "input_layer/YOLOv11obj_model.pt"  # Will check Input-Layer-main/ if not found
YOLO_CONFIDENCE_THRESHOLD = 0.4
YOLO_DEVICE = "cuda"  # "cuda" or "cpu" (auto-detected if "cuda")

# Motion Detection
MOTION_THRESHOLD = 30  # Minimum motion score to consider frame important
MOTION_MEMORY_SIZE = 4  # Number of frames to keep for motion comparison

# Frame Sending
SEND_INTERVAL = 0.4  # Minimum seconds between sending frames (throttling)
FRAME_QUALITY = 85  # JPEG quality (1-100)

# WebSocket Server
WS_HOST = "127.0.0.1"
WS_PORT = 8765

# VLM Settings (Ollama)
VLM_MODEL = "llama3.2-vision:11b"  # Vision Language Model
VLM_TIMEOUT = 30  # seconds

# Cognitive Layer Integration
COGNITIVE_LAYER_URL = "http://localhost:8000"
COGNITIVE_LAYER_ENDPOINT = "/api/events/process"
ENABLE_COGNITIVE_PROCESSING = True  # Send events to cognitive layer

# VLM Prompt Template
VLM_PROMPT = """You are a visual analysis model watching a live feed from a humanoid robot's camera. 
Describe what is happening in this frame. Focus on:
- Main objects and people present
- Actions or movements
- Spatial relationships
- Emotional context or interactions
- Any notable events or changes

Be concise but descriptive. This is part of a video feed, so consider context from previous frames."""

