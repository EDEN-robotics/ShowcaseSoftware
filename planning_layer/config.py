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
TEMPERATURE = 0.2  # Slightly higher for better reasoning (still deterministic)
MAX_TOKENS = 512  # Increased for more detailed plans with better models
TOP_P = 0.9
TOP_K = 50

# Context Management
MAX_CONTEXT_LENGTH = 2048  # Limit input context to prevent memory issues
MAX_SCENE_DESCRIPTION_LENGTH = 1000  # Truncate scene descriptions if too long
MAX_PLANNING_HISTORY = 10  # Keep last N planning requests in memory

# Ollama Fallback Settings
OLLAMA_BASE_URL = "http://localhost:11434"
# Better models for planning (in order of preference):
# - llama3.1:8b (better reasoning than llama3)
# - qwen2.5:7b (excellent reasoning, smaller)
# - mistral:7b (good balance)
# - deepseek-r1:7b (best reasoning, if available)
OLLAMA_MODEL = "llama3.1"  # Upgraded to better reasoning model (or "qwen2.5", "mistral")
OLLAMA_TIMEOUT = 90  # seconds (increased for better models)
USE_OLLAMA_FALLBACK = True  # Enable Ollama fallback (primary now)

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

