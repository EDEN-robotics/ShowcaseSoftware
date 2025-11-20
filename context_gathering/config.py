"""
Context Gathering Layer Configuration
"""

# Ollama VLM Settings
VLM_MODEL = "llama3.2-vision:11b"
VLM_BASE_URL = "http://localhost:11434"
VLM_TIMEOUT = 30  # seconds
VLM_MAX_RETRIES = 3

# Importance Analysis
IMPORTANCE_ANALYSIS_ENABLED = True
MOTION_WEIGHT = 0.3  # Weight for motion-based importance
DETECTION_WEIGHT = 0.4  # Weight for object detection importance
NOVELTY_WEIGHT = 0.3  # Weight for novelty/change detection

# VLM Prompt Templates
SCENE_ANALYSIS_PROMPT = """You are analyzing a frame from a humanoid robot's camera feed. 

Describe what is happening in this frame with focus on:
1. **Main Objects & People**: What objects and people are visible? Where are they positioned?
2. **Actions & Movements**: What actions are occurring? Are people moving, gesturing, or interacting?
3. **Spatial Relationships**: How are objects/people positioned relative to each other?
4. **Emotional Context**: What is the emotional tone? Are people happy, serious, engaged?
5. **Notable Events**: Any significant events, changes, or interactions happening?
6. **Context Clues**: What might this scene indicate about the situation?

Be detailed but concise. This is part of a continuous video feed, so consider temporal context."""

IMPORTANCE_REASONING_PROMPT = """You are determining why a frame from a robot's camera feed is important.

Given:
- Motion Score: {motion_score}
- Detected Objects: {detected_objects}
- Scene Description: {scene_description}

Analyze:
1. **Why is this frame important?** (or not important)
2. **What makes it stand out?** (motion, objects, interactions, novelty)
3. **What should the robot remember?** (key details, people, events)
4. **Emotional significance**: Any emotional or social importance?

Respond with a brief analysis explaining the importance."""

# Frame Analysis Settings
MIN_CONFIDENCE_FOR_IMPORTANCE = 0.5
MOTION_THRESHOLD_FOR_ANALYSIS = 25.0
MAX_FRAMES_PER_BATCH = 10

# Output Formatting
INCLUDE_DETAILED_DESCRIPTION = True
INCLUDE_EMOTIONAL_TONE = True
INCLUDE_SPATIAL_RELATIONSHIPS = True
INCLUDE_ACTION_ANALYSIS = True

