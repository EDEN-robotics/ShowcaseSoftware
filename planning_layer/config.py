"""
Planning Layer Configuration
"""

import os

# Model Configuration
COSMOS_MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models", "cosmos-reason1-7b")
COSMOS_MODEL_HF_ID = "nvidia/Cosmos-Reason1-7B"

# Quantization Settings
QUANTIZATION_METHOD = "fp8"  # Options: "fp8", "awq", "fp16"
GPU_MEMORY_UTILIZATION = 0.7  # Use 70% of GPU memory
ENFORCE_EAGER = True  # Save memory on consumer cards
TRUST_REMOTE_CODE = True

# Inference Settings
TEMPERATURE = 0.1  # Low temperature for deterministic physics reasoning
MAX_TOKENS = 256  # Maximum tokens in response (reduced for faster inference)
TOP_P = 0.9
TOP_K = 50

# Context Management
MAX_CONTEXT_LENGTH = 2048  # Limit input context to prevent memory issues
MAX_SCENE_DESCRIPTION_LENGTH = 1000  # Truncate scene descriptions if too long
MAX_PLANNING_HISTORY = 10  # Keep last N planning requests in memory

# Ollama Fallback Settings
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = "llama3"  # Fallback model (llama3 or mistral)
OLLAMA_TIMEOUT = 60  # seconds (increased for slower systems)
USE_OLLAMA_FALLBACK = True  # Enable Ollama fallback

# Performance Settings
INFERENCE_TIMEOUT = 30  # seconds - if Cosmos takes longer, use Ollama
SLOW_INFERENCE_THRESHOLD = 10  # seconds - if slower than this, consider Ollama

# GPU Requirements
MIN_GPU_MEMORY_GB = 8  # Minimum GPU memory required (for quantized model)
CUDA_VERSION_REQUIRED = "12.1"  # or "12.4"

# Planning Output Settings
INCLUDE_CONFIDENCE = True
INCLUDE_REASONING = True
DETAILED_ACTIONS = True  # Generate detailed text steps with context

# ROS MCP Integration (Future)
ROS_MCP_ENABLED = False
ROS_MCP_ENDPOINT = "http://localhost:8080"

