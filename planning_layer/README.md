# EDEN Planning Layer

The Planning Layer generates detailed action plans using NVIDIA Cosmos Reason1-7B (text-only mode) with physics reasoning, or falls back to Ollama for planning when GPU unavailable.

## Overview

The Planning Layer receives goals and scene descriptions from the Cognitive Layer and generates detailed, physics-aware action plans. It runs as a separate FastAPI service.

## Architecture

```
Cognitive Layer (Decision)
    ↓
Planning Layer (Cosmos/Ollama)
    ↓
Action Layer (ROS MCP) - Future
```

## Components

### CosmosLite (`cosmos_planner.py`)
- Uses NVIDIA Cosmos Reason1-7B via vLLM
- Text-only mode (no vision encoder)
- Quantized (fp8 or 4-bit) for consumer GPUs
- Physics reasoning for action planning

### OllamaPlanner (`ollama_planner.py`)
- Fallback planner using Ollama (llama3/mistral)
- Prompt-engineered for physics reasoning
- Used when GPU unavailable or Cosmos slow

### PlanningServer (`planning_server.py`)
- FastAPI service on port 8001
- Endpoint: `POST /api/plan/generate`
- Automatic fallback between Cosmos and Ollama

## Installation

### 1. Setup Environment

```bash
cd planning_layer
chmod +x setup_linux.sh
./setup_linux.sh
```

This installs:
- vllm==0.9.2 (pinned version)
- autoawq (quantization support)
- PyTorch with CUDA 12.1
- HuggingFace Hub

### 2. Download Model (CRITICAL - Do Before Showcase!)

```bash
# Download Cosmos model (~15GB)
huggingface-cli download nvidia/Cosmos-Reason1-7B --local-dir ../models/cosmos-reason1-7b
```

**Important**: Download before the showcase! Venue Wi-Fi is slow.

### 3. Verify GPU

```bash
python3 -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
nvidia-smi  # Check GPU memory
```

## Usage

### Start Planning Server

```bash
python3 -m planning_layer.planning_server
```

Or:

```bash
cd planning_layer
python3 planning_server.py
```

Server runs on `http://localhost:8001`

### Generate Plan via API

```bash
curl -X POST http://localhost:8001/api/plan/generate \
  -H "Content-Type: application/json" \
  -d '{
    "goal": "Pick up the red cup",
    "scene_description": "Red cup is on kitchen counter, 40cm away. No obstacles."
  }'
```

### Response Format

```json
{
  "plan_id": "plan_abc123",
  "actions": [
    "Move forward 0.4 meters at reduced speed",
    "Open gripper to maximum width (8cm)",
    "Lower arm 15cm while maintaining horizontal orientation",
    "Close gripper with 60% force",
    "Lift object vertically 20cm"
  ],
  "reasoning": "Object is 40cm away. Need to approach carefully...",
  "confidence": 0.95,
  "model_used": "cosmos",
  "inference_time": 2.3,
  "timestamp": "2024-11-20T01:00:00"
}
```

## Configuration

Edit `planning_layer/config.py`:

- **Model Path**: `COSMOS_MODEL_PATH` (local path to downloaded model)
- **Quantization**: `QUANTIZATION_METHOD` ("fp8", "awq", or "fp16")
- **GPU Memory**: `GPU_MEMORY_UTILIZATION` (0.7 = 70%)
- **Ollama Model**: `OLLAMA_MODEL` ("llama3" or "mistral")
- **Temperature**: `TEMPERATURE` (0.1 for deterministic physics)

## Integration with Cognitive Layer

The cognitive layer can call the planning service:

```python
from planning_layer.integration import PlanningLayerClient

client = PlanningLayerClient("http://localhost:8001")

result = client.generate_plan(
    goal="Pick up the red cup",
    scene_description="Red cup on counter, 40cm away",
    context={"importance_score": 0.8}
)

print(result["actions"])
```

## GPU Requirements

- **Minimum**: 8GB GPU memory (for quantized model)
- **Recommended**: 12GB+ GPU memory
- **CUDA**: 12.1 or 12.4

### GPU Troubleshooting

**Problem**: GPU not detected
```bash
# Check NVIDIA drivers
nvidia-smi

# Check CUDA
nvcc --version

# Reinstall PyTorch with CUDA
pip install torch --index-url https://download.pytorch.org/whl/cu121
```

**Problem**: Out of memory
- Reduce `GPU_MEMORY_UTILIZATION` in config (try 0.5)
- Use fp8 quantization
- Use Ollama fallback instead

**Problem**: Model not found
- Download model: `huggingface-cli download nvidia/Cosmos-Reason1-7B --local-dir ./models/cosmos-reason1-7b`
- Check path in `config.py`

## Fallback Behavior

1. **Cosmos Available**: Uses Cosmos for planning
2. **Cosmos Slow**: Still uses Cosmos but warns
3. **Cosmos Fails**: Automatically falls back to Ollama
4. **GPU Unavailable**: Uses Ollama only

## Testing

### Test Knowledge Graph

Generate test environment:

```bash
python3 -m planning_layer.test_knowledge_graph
```

This creates:
- 6 rooms with objects
- Spatial relationships
- Navigation paths
- Object properties
- Interaction memories

### Test Planning

```python
from planning_layer.cosmos_planner import CosmosLite
from planning_layer.ollama_planner import OllamaPlanner

# Test Cosmos
cosmos = CosmosLite()
if cosmos.is_available():
    result = cosmos.plan(
        goal="Pick up red cup",
        scene_description="Red cup on counter, 40cm away"
    )
    print(result["actions"])

# Test Ollama
ollama = OllamaPlanner()
if ollama.is_available():
    result = ollama.plan(
        goal="Move to kitchen",
        scene_description="Kitchen is 3 meters ahead"
    )
    print(result["actions"])
```

## Performance

- **Cosmos Inference**: ~2-5 seconds per plan (GPU)
- **Ollama Inference**: ~3-8 seconds per plan (CPU/GPU)
- **Memory Usage**: ~8-12GB GPU (quantized)

## Output Format

Plans include:
- **Actions**: List of detailed action steps with context
- **Reasoning**: Physics-based reasoning explanation
- **Confidence**: Score (0.0-1.0) indicating plan quality
- **Model Used**: Which planner generated the plan

## Next Steps

1. **ROS MCP Integration**: Connect planning output to ROS MCP
2. **Action Validation**: Validate plans before execution
3. **Simulation**: Test plans in NVIDIA Cosmos/Isaac Sim
4. **Optimization**: Fine-tune prompts and parameters

## Troubleshooting

### vLLM Installation Issues
- Use pinned version: `vllm==0.9.2`
- Check CUDA compatibility
- Install from specific wheel if needed

### Model Loading Issues
- Verify model path exists
- Check disk space (model is ~15GB)
- Verify quantization support

### Slow Inference
- Check GPU utilization: `nvidia-smi`
- Reduce `MAX_TOKENS` in config
- Use Ollama fallback if consistently slow

### Planning Service Not Responding
- Check if server is running: `curl http://localhost:8001/`
- Check logs for errors
- Verify GPU/Ollama availability

