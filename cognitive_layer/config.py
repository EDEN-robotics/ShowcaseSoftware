"""
EDEN Cognitive Layer Configuration
"""

# Ollama Configuration
OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_MODEL = "llama3"  # Alternatives: "mistral", "llama2", "codellama"

# Importance Thresholds by Event Type
THRESHOLDS = {
    "trauma": 0.3,
    "threat": 0.3,
    "joy": 0.6,
    "achievement": 0.5,
    "interaction": 0.5,
    "memory": 0.5,
    "routine": 0.7,
    "casual": 0.8,
    "default": 0.5
}

# Personality Modulation Weights
PERSONALITY_MODULATION = {
    "Openness": {
        "novel_events": 0.3,  # Boost novel events
        "routine_events": -0.2  # Reduce routine events
    },
    "Conscientiousness": {
        "achievement_events": 0.4,  # Boost completion/achievement
        "casual_events": -0.2
    },
    "Extroversion": {
        "social_events": 0.3,
        "solitary_events": -0.1
    },
    "Agreeableness": {
        "positive_social": 0.4,
        "negative_social": -0.2
    },
    "Neuroticism": {
        "threat_events": 0.5,  # Amplify threats
        "negative_events": 0.3,
        "positive_events": -0.1
    }
}

# Memory Context Weighting
MEMORY_SIMILARITY_BOOST = 0.2  # Boost importance if similar to important memories
MEMORY_DENSITY_THRESHOLD = 100  # If more than this many memories, increase threshold

# LLM Settings
LLM_TIMEOUT = 30  # seconds
LLM_MAX_RETRIES = 3
LLM_TEMPERATURE = 0.7

# Event Processing
BATCH_SIZE = 10
MAX_EVENT_QUEUE = 100

# Episodic Memory (low-priority)
EPISODIC_MEMORY_THRESHOLD = 0.3  # Below this, store as episodic
EPISODIC_DECAY_RATE = 0.95  # Decay factor per time period

