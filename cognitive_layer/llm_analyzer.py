"""
EDEN LLM Cognitive Analyzer
Uses Ollama to perform deep cognitive analysis of events
"""

import json
import requests
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from cognitive_layer import config


@dataclass
class LLMAnalysisResult:
    """Result from LLM cognitive analysis"""
    importance: float
    reasoning: str
    node_type: str
    threshold: float
    confidence: float = 0.8
    emotional_impact: Optional[str] = None
    key_insights: Optional[List[str]] = None


class CognitiveAnalyzer:
    """LLM-powered cognitive analyzer for event importance evaluation"""
    
    def __init__(self, ollama_url: str = None, model_name: str = None):
        self.ollama_url = ollama_url or config.OLLAMA_BASE_URL
        self.model_name = model_name or config.DEFAULT_MODEL
        self.timeout = config.LLM_TIMEOUT
        self.max_retries = config.LLM_MAX_RETRIES
    
    def _check_ollama_available(self) -> bool:
        """Check if Ollama is available"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def _create_analysis_prompt(self, event: Dict, personality: Dict, relevant_memories: List[Dict]) -> str:
        """Create a sophisticated prompt for cognitive analysis"""
        
        # Format relevant memories
        memory_context = ""
        if relevant_memories:
            memory_context = "Relevant Past Memories:\n"
            for mem in relevant_memories[:5]:  # Top 5 most relevant
                memory_context += f"- {mem.get('content', '')[:100]} (importance: {mem.get('importance', 0.5):.2f})\n"
        else:
            memory_context = "No directly relevant memories found."
        
        # Format event description
        event_desc = event.get('description', '')
        if event.get('detected_actions'):
            event_desc += f"\nDetected Actions: {', '.join(event.get('detected_actions', []))}"
        if event.get('emotional_tone'):
            event_desc += f"\nEmotional Tone: {event.get('emotional_tone')}"
        
        prompt = f"""You are EDEN, a humanoid robot with a sophisticated cognitive system. Analyze this event through the lens of your current personality and memory context.

CURRENT PERSONALITY STATE:
- Openness: {personality.get('Openness', 0.5):.2f} (curiosity, creativity)
- Conscientiousness: {personality.get('Conscientiousness', 0.5):.2f} (organization, achievement)
- Extroversion: {personality.get('Extroversion', 0.5):.2f} (social energy)
- Agreeableness: {personality.get('Agreeableness', 0.5):.2f} (kindness, cooperation)
- Neuroticism: {personality.get('Neuroticism', 0.5):.2f} (anxiety, emotional reactivity)

{memory_context}

EVENT TO ANALYZE:
{event_desc}

User: {event.get('user_name', event.get('user_id', 'Unknown'))}
Source: {event.get('source', 'unknown')}
Timestamp: {event.get('timestamp', 'unknown')}

TASK: Perform cognitive analysis considering:
1. How significant is this event given your personality traits?
2. How does it relate to your past memories?
3. What emotional or cognitive impact might it have?
4. Should this be remembered long-term?

Respond STRICTLY in valid JSON format with these exact fields:
{{
    "importance": <float 0.0-1.0>,
    "reasoning": "<detailed explanation of why this is important/unimportant>",
    "node_type": "<one of: memory, trauma, joy, threat, interaction, achievement, routine>",
    "threshold": <float 0.0-1.0, the threshold that should apply>,
    "confidence": <float 0.0-1.0, how confident you are in this analysis>,
    "emotional_impact": "<brief description of emotional impact if any>",
    "key_insights": ["<insight1>", "<insight2>", ...]
}}

Think step by step, then provide the JSON response."""
        
        return prompt
    
    def analyze_event_importance(self, event: Dict, personality: Dict, relevant_memories: List[Dict]) -> LLMAnalysisResult:
        """
        Analyze event importance using LLM cognitive reasoning
        
        Args:
            event: EventFrame as dictionary
            personality: PersonalityVector as dictionary
            relevant_memories: List of relevant MemoryNode dictionaries
        
        Returns:
            LLMAnalysisResult with importance score and reasoning
        """
        
        if not self._check_ollama_available():
            # Fallback to heuristic analysis
            return self._fallback_analysis(event, personality)
        
        prompt = self._create_analysis_prompt(event, personality, relevant_memories)
        
        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    f"{self.ollama_url}/api/generate",
                    json={
                        "model": self.model_name,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": config.LLM_TEMPERATURE,
                            "num_predict": 1000
                        }
                    },
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    result_text = response.json().get("response", "")
                    
                    # Extract JSON from response (handle markdown code blocks)
                    json_start = result_text.find("{")
                    json_end = result_text.rfind("}") + 1
                    if json_start >= 0 and json_end > json_start:
                        json_text = result_text[json_start:json_end]
                        analysis = json.loads(json_text)
                        
                        return LLMAnalysisResult(
                            importance=float(analysis.get("importance", 0.5)),
                            reasoning=analysis.get("reasoning", "No reasoning provided"),
                            node_type=analysis.get("node_type", "memory"),
                            threshold=float(analysis.get("threshold", 0.5)),
                            confidence=float(analysis.get("confidence", 0.8)),
                            emotional_impact=analysis.get("emotional_impact"),
                            key_insights=analysis.get("key_insights", [])
                        )
                    else:
                        # Try to parse as plain text response
                        return self._parse_text_response(result_text, event)
                        
            except json.JSONDecodeError as e:
                if attempt < self.max_retries - 1:
                    continue
                print(f"LLM JSON parsing error: {e}")
                return self._fallback_analysis(event, personality)
            except requests.RequestException as e:
                if attempt < self.max_retries - 1:
                    continue
                print(f"LLM request error: {e}")
                return self._fallback_analysis(event, personality)
            except Exception as e:
                print(f"LLM analysis error: {e}")
                return self._fallback_analysis(event, personality)
        
        # All retries failed
        return self._fallback_analysis(event, personality)
    
    def _parse_text_response(self, text: str, event: Dict) -> LLMAnalysisResult:
        """Parse text response and extract importance score"""
        text_lower = text.lower()
        
        # Try to extract importance from text
        importance = 0.5
        if "very important" in text_lower or "critical" in text_lower or "significant" in text_lower:
            importance = 0.8
        elif "important" in text_lower:
            importance = 0.6
        elif "not important" in text_lower or "trivial" in text_lower or "routine" in text_lower:
            importance = 0.3
        
        # Determine node type
        node_type = "memory"
        if "trauma" in text_lower or "threat" in text_lower:
            node_type = "threat"
        elif "joy" in text_lower or "happy" in text_lower or "positive" in text_lower:
            node_type = "joy"
        elif "achievement" in text_lower or "completed" in text_lower:
            node_type = "achievement"
        
        return LLMAnalysisResult(
            importance=importance,
            reasoning=text[:500],  # First 500 chars
            node_type=node_type,
            threshold=0.5,
            confidence=0.6
        )
    
    def _fallback_analysis(self, event: Dict, personality: Dict) -> LLMAnalysisResult:
        """Fallback heuristic analysis when LLM is unavailable"""
        description = event.get('description', '').lower()
        
        # Heuristic importance scoring
        importance = 0.5
        
        # High importance indicators
        high_importance_keywords = ['finished', 'completed', 'achievement', 'important', 'significant', 
                                   'milestone', 'breakthrough', 'accomplished', 'success']
        if any(kw in description for kw in high_importance_keywords):
            importance = 0.8
        
        # Low importance indicators
        low_importance_keywords = ['cool', 'nice', 'casual', 'routine', 'normal', 'typical', 'just']
        if any(kw in description for kw in low_importance_keywords):
            importance = 0.3
        
        # Determine node type
        node_type = "memory"
        if 'threat' in description or 'danger' in description or 'aggressive' in description:
            node_type = "threat"
        elif 'happy' in description or 'joy' in description or 'positive' in description:
            node_type = "joy"
        elif 'finished' in description or 'completed' in description:
            node_type = "achievement"
        
        return LLMAnalysisResult(
            importance=importance,
            reasoning=f"Heuristic analysis: Event contains {'high' if importance > 0.6 else 'low' if importance < 0.4 else 'moderate'} importance indicators.",
            node_type=node_type,
            threshold=config.THRESHOLDS.get(node_type, config.THRESHOLDS['default']),
            confidence=0.5
        )
    
    def classify_event_type(self, event: Dict) -> str:
        """Classify event type using LLM"""
        if not self._check_ollama_available():
            return self._fallback_analysis(event, {}).node_type
        
        prompt = f"""Classify this event into one of these types: memory, trauma, joy, threat, interaction, achievement, routine.

Event: {event.get('description', '')}

Respond with ONLY the type name."""
        
        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json().get("response", "").strip().lower()
                valid_types = ["memory", "trauma", "joy", "threat", "interaction", "achievement", "routine"]
                for t in valid_types:
                    if t in result:
                        return t
        except:
            pass
        
        return "memory"
    
    def determine_threshold(self, event_type: str, context: Dict) -> float:
        """Determine dynamic threshold based on event type and context"""
        base_threshold = config.THRESHOLDS.get(event_type, config.THRESHOLDS['default'])
        
        # Adjust based on memory density
        memory_count = context.get('memory_count', 0)
        if memory_count > config.MEMORY_DENSITY_THRESHOLD:
            base_threshold += 0.1  # Higher threshold when memory is dense
        
        # Adjust based on personality
        personality = context.get('personality', {})
        if event_type in ['threat', 'trauma']:
            neuroticism = personality.get('Neuroticism', 0.5)
            if neuroticism > 0.7:
                base_threshold -= 0.2  # Lower threshold for threats if high neuroticism
        
        return max(0.1, min(0.9, base_threshold))

