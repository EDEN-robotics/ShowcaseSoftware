"""
Ollama Fallback Planner
Uses prompt-engineered Ollama models for physics reasoning when Cosmos unavailable
"""

import requests
import json
import time
import re
from typing import Dict, List, Optional, Tuple
from .config import *


class OllamaPlanner:
    """Fallback planner using Ollama with physics reasoning prompts"""
    
    def __init__(self, model_name: Optional[str] = None):
        self.model_name = model_name or OLLAMA_MODEL
        self.ollama_url = f"{OLLAMA_BASE_URL}/api/generate"
        self.available = self._check_ollama()
    
    def _check_ollama(self) -> bool:
        """Check if Ollama is available"""
        try:
            response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            print("[OllamaPlanner] Ollama not available. Planning will fail.")
            return False
    
    def _construct_physics_prompt(self, goal: str, scene_description: str) -> str:
        """Construct prompt engineered for physics reasoning"""
        # Truncate scene description if too long
        if len(scene_description) > MAX_SCENE_DESCRIPTION_LENGTH:
            scene_description = scene_description[:MAX_SCENE_DESCRIPTION_LENGTH] + "..."
        
        prompt = f"""You are a robot planner. Create a step-by-step action plan.

SCENE: {scene_description[:500]}
GOAL: {goal}

Provide:
REASONING: [Brief physics analysis]
ACTIONS:
- [Action 1]
- [Action 2]
- [Action 3]

Keep actions concise and specific."""
        
        return prompt
    
    def _parse_response(self, response_text: str) -> tuple[str, List[str]]:
        """Parse Ollama response to extract reasoning and actions"""
        reasoning = ""
        actions = []
        
        # Try to extract reasoning section
        reasoning_match = re.search(r'REASONING:\s*(.*?)(?=ACTIONS:|$)', response_text, re.DOTALL | re.IGNORECASE)
        if reasoning_match:
            reasoning = reasoning_match.group(1).strip()
        
        # Try to extract actions section
        actions_match = re.search(r'ACTIONS:\s*(.*?)$', response_text, re.DOTALL | re.IGNORECASE)
        if actions_match:
            actions_text = actions_match.group(1).strip()
            # Split by lines (numbered or bulleted)
            action_lines = []
            for line in actions_text.split('\n'):
                line = line.strip()
                # Remove numbering/bullets
                line = re.sub(r'^[-•\d+\.\)]\s*', '', line)
                if line and len(line) > 10:  # Filter out very short lines
                    action_lines.append(line)
            actions = action_lines
        
        # Fallback: if no structured format, try to extract from response
        if not actions:
            # Look for action-like sentences
            sentences = response_text.split('.')
            for sentence in sentences:
                sentence = sentence.strip()
                # Heuristic: actions are imperative or contain action verbs
                action_verbs = ['move', 'grasp', 'open', 'close', 'lift', 'rotate', 'approach', 'retract', 'position']
                if any(verb in sentence.lower() for verb in action_verbs) and len(sentence) > 15:
                    actions.append(sentence)
        
        # If still no actions, use the whole response as reasoning
        if not actions and not reasoning:
            reasoning = response_text[:500]  # First 500 chars
            # Try to extract any action-like sentences
            sentences = response_text.split('.')
            actions = [s.strip() for s in sentences if len(s.strip()) > 20 and len(s.strip()) < 200][:5]
        
        return reasoning, actions
    
    def plan(self, goal: str, scene_description: str, context: Optional[Dict] = None) -> Dict:
        """
        Generate action plan using Ollama.
        
        Args:
            goal: The goal to achieve
            scene_description: Description of current scene
            context: Optional context from cognitive layer
        
        Returns:
            Dictionary with actions, reasoning, confidence
        """
        if not self.available:
            raise RuntimeError("Ollama not available. Check if Ollama is running.")
        
        start_time = time.time()
        
        try:
            # Construct prompt
            prompt = self._construct_physics_prompt(goal, scene_description)
            
            # Call Ollama API
            response = requests.post(
                self.ollama_url,
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": TEMPERATURE,
                        "num_predict": MAX_TOKENS
                    }
                },
                timeout=OLLAMA_TIMEOUT
            )
            
            if response.status_code != 200:
                raise Exception(f"Ollama API error: {response.status_code}")
            
            response_data = response.json()
            response_text = response_data.get("response", "")
            
            # Parse response
            reasoning, actions = self._parse_response(response_text)
            
            inference_time = time.time() - start_time
            
            # Calculate confidence (slightly lower than Cosmos since it's fallback)
            confidence = self._calculate_confidence(response_text, reasoning, actions)
            
            return {
                "actions": actions,
                "reasoning": reasoning,
                "confidence": confidence,
                "model_used": f"ollama-{self.model_name}",
                "inference_time": inference_time,
                "raw_response": response_text[:200] if len(response_text) > 200 else response_text
            }
            
        except requests.exceptions.RequestException as e:
            print(f"[OllamaPlanner] Request error: {e}")
            raise
        except Exception as e:
            print(f"[OllamaPlanner] Planning error: {e}")
            raise
    
    def _calculate_confidence(self, response_text: str, reasoning: str, actions: List[str]) -> float:
        """Calculate confidence score"""
        confidence = 0.4  # Base confidence (lower than Cosmos)
        
        # Boost if reasoning is present
        if reasoning and len(reasoning) > 30:
            confidence += 0.2
        
        # Boost if actions are present
        if actions and len(actions) > 0:
            confidence += 0.2
        
        # Boost if response contains physics terms
        physics_terms = ['velocity', 'force', 'distance', 'grasp', 'move', 'rotate', 'position', 'speed']
        if any(term in response_text.lower() for term in physics_terms):
            confidence += 0.1
        
        return min(0.85, confidence)  # Cap at 0.85 for fallback
    
    def is_available(self) -> bool:
        """Check if Ollama planner is available"""
        return self.available

