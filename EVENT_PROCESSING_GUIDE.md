# EDEN Event Processing System Guide

## Overview

The EDEN Cognitive Layer now includes a sophisticated event processing system that analyzes incoming frame descriptions and other events using a hybrid approach combining heuristics, semantic analysis, and LLM-powered cognitive reasoning.

## Architecture

### Three-Layer Analysis System

1. **Heuristic Layer**: Quick keyword-based filtering
   - High-importance keywords: "finished", "completed", "achievement", "significant"
   - Low-importance keywords: "cool", "nice", "casual", "routine"
   - Action-based scoring

2. **Semantic Layer**: Embedding similarity to important memories
   - Compares event to existing high-importance memories
   - Boosts importance if similar to significant past events

3. **LLM Layer**: Deep cognitive analysis via Ollama
   - Considers personality traits
   - Evaluates memory context
   - Provides reasoning and classification

### Personality Modulation

Events are modulated based on current personality state:
- **High Openness**: More receptive to novel events
- **High Neuroticism**: Amplifies threat/negative events
- **High Agreeableness**: Amplifies positive social events
- **High Conscientiousness**: Values completion/achievement events

## Event JSON Schema

```json
{
  "frame_id": "unique_identifier",
  "timestamp": "2024-01-01T12:00:00",
  "description": "VLM-generated frame description",
  "user_id": "optional_user_id",
  "user_name": "optional_user_name",
  "detected_objects": ["object1", "object2"],
  "detected_actions": ["action1", "action2"],
  "emotional_tone": "positive/negative/neutral",
  "scene_context": "high-level scene description",
  "metadata": {
    "camera_angle": "front",
    "confidence": 0.95
  },
  "source": "camera_frame"
}
```

## API Endpoints

### Process Single Event

```bash
POST /api/events/process
Content-Type: application/json

{
  "description": "Ian just finished building the robot",
  "user_name": "Ian",
  "detected_actions": ["completed", "finished"],
  "source": "camera_frame"
}
```

**Response:**
```json
{
  "status": "processed",
  "event_id": "frame_001",
  "importance": 0.75,
  "threshold": 0.5,
  "added_to_graph": true,
  "memory_id": "uuid",
  "reasoning_trace": {
    "heuristic_score": 0.7,
    "semantic_score": 0.6,
    "llm_score": 0.8,
    "llm_reasoning": "This event represents a significant achievement...",
    "final_importance": 0.75,
    "node_type": "achievement"
  },
  "llm_analysis": {
    "reasoning": "...",
    "node_type": "achievement",
    "confidence": 0.85,
    "emotional_impact": "positive",
    "key_insights": ["Major milestone", "User achievement"]
  }
}
```

### Process Batch of Events

```bash
POST /api/events/batch
Content-Type: application/json

{
  "events": [
    {
      "description": "Event 1",
      "user_name": "Ian"
    },
    {
      "description": "Event 2",
      "user_name": "Student"
    }
  ]
}
```

**Response:**
```json
{
  "status": "batch_processed",
  "total_events": 2,
  "added_to_graph": 1,
  "episodic_memories": 1,
  "errors": 0,
  "results": [...]
}
```

### Get Configuration

```bash
GET /api/events/config
```

### Update Configuration

```bash
POST /api/events/config
Content-Type: application/json

{
  "ollama_url": "http://localhost:11434",
  "model": "llama3"
}
```

## Ollama Setup

1. Install Ollama: https://ollama.ai
2. Pull a model:
   ```bash
   ollama pull llama3
   # or
   ollama pull mistral
   ```
3. Ensure Ollama is running (default: `http://localhost:11434`)

The system will automatically fall back to heuristic+semantic analysis if Ollama is unavailable.

## Configuration

Edit `config.py` to customize:

- **OLLAMA_BASE_URL**: Ollama server URL
- **DEFAULT_MODEL**: Model name (llama3, mistral, etc.)
- **THRESHOLDS**: Importance thresholds by event type
- **PERSONALITY_MODULATION**: How personality affects importance
- **MEMORY_SIMILARITY_BOOST**: Boost for events similar to important memories

## Example Usage

### Python

```python
from ego_core import EgoGraph

ego_graph = EgoGraph()

event = {
    "frame_id": "frame_001",
    "description": "Ian just finished building the robot. This is a significant achievement.",
    "user_name": "Ian",
    "detected_actions": ["completed", "finished"],
    "source": "camera_frame"
}

result = ego_graph.process_event_frame(event)
print(f"Importance: {result['importance']}")
print(f"Added to graph: {result['added_to_graph']}")
print(f"Reasoning: {result['reasoning_trace']['llm_reasoning']}")
```

### cURL

```bash
curl -X POST http://localhost:8000/api/events/process \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Student gives friendly high-five",
    "user_name": "Student",
    "detected_actions": ["wave", "high-five"],
    "source": "camera_frame"
  }'
```

## WebSocket Events

The system broadcasts event processing results via WebSocket:

- `event_processed`: Single event processed
- `batch_processed`: Batch of events processed

Both include the full processing result with reasoning traces and graph updates.

## Importance Thresholds

Events are added to the graph if `importance >= threshold`:

- **trauma/threat**: 0.3 (lower threshold, more sensitive)
- **joy/achievement**: 0.6 (moderate threshold)
- **routine/casual**: 0.7 (higher threshold, filters out routine events)
- **default**: 0.5

Thresholds are dynamically adjusted based on:
- Event type
- Personality state (e.g., high neuroticism lowers threshold for threats)
- Memory density (more memories = higher threshold)

## Episodic Memory

Events below the threshold are stored as "episodic memories" - low-priority memories that may decay over time. They don't appear in the main graph but can be retrieved via semantic search.

## Error Handling

- **Ollama unavailable**: Falls back to heuristic+semantic analysis
- **Invalid JSON**: Logged and skipped
- **LLM parsing errors**: Uses default values, logs error
- **Rate limiting**: Events are queued for batch processing

## Testing

Run the test script:

```bash
python3 test_event_processing.py
```

This tests:
1. Important event processing
2. Low-importance event filtering
3. Batch processing
4. Graph state updates

