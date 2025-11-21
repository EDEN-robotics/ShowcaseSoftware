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
        
        prompt = f"""You are an advanced robot planner with expertise in physics, spatial reasoning, and motion planning. Analyze the scene and create a detailed, step-by-step action plan.

SCENE DESCRIPTION:
{scene_description[:800]}

GOAL:
{goal}

TASK:
1. Analyze the physics constraints (distances, obstacles, object properties, forces)
2. Consider spatial relationships and safe motion paths
3. Generate a detailed action plan with reasoning

CRITICAL REQUIREMENTS:
- Use REALISTIC distances (0.3-2.0 meters for movements, NEVER use 0)
- Use REALISTIC speeds (0.1-0.5 m/s, NEVER use 0)
- Use REALISTIC angles (15-180 degrees, NEVER use 0)
- If you don't know exact distances, estimate based on typical room sizes (rooms are 3-5m across)
- Be specific: "Move forward 1.2 meters" NOT "Move forward 0 meters"

OUTPUT FORMAT:
REASONING: [Your overall physics analysis - consider distances, forces, obstacles, object properties, and motion constraints. Be specific about why the plan is necessary.]

ACTIONS:
1. Action: [Specific action command with realistic values]
   Reasoning: [Why this step is necessary - physics/obstacle reasoning]

2. Action: [Specific action command with realistic values]
   Reasoning: [Why this step is necessary - physics/obstacle reasoning]

3. Action: [Continue as needed...]
   Reasoning: [Continue as needed...]

Make actions detailed enough for a robot to execute. Include realistic distances (0.3-2.0m), directions, speeds (0.1-0.5 m/s), and object interactions."""
        
        return prompt
    
    def _parse_response(self, response_text: str) -> tuple[str, List[Dict]]:
        """Parse Ollama response to extract reasoning and actions with Action/Reasoning pairs"""
        reasoning = ""
        actions = []
        
        # Try to extract overall reasoning section
        reasoning_match = re.search(r'REASONING:\s*(.*?)(?=ACTIONS:|$)', response_text, re.DOTALL | re.IGNORECASE)
        if reasoning_match:
            reasoning = reasoning_match.group(1).strip()
        
        # Try to extract actions section with Action/Reasoning pairs
        actions_match = re.search(r'ACTIONS:\s*(.*?)$', response_text, re.DOTALL | re.IGNORECASE)
        if actions_match:
            actions_text = actions_match.group(1).strip()
            
            # Try to parse numbered Action/Reasoning pairs
            # Pattern: "1. Action: ...\n   Reasoning: ..."
            action_pattern = r'(\d+)\.\s*Action:\s*(.*?)(?=\s+Reasoning:|\n\d+\.|$)'
            reasoning_pattern = r'Reasoning:\s*(.*?)(?=\n\d+\.|$)'
            
            # Find all action blocks
            action_blocks = re.finditer(
                r'(\d+)\.\s*Action:\s*(.*?)(?:\s+Reasoning:\s*(.*?))?(?=\n\d+\.|$)',
                actions_text,
                re.DOTALL | re.IGNORECASE
            )
            
            for match in action_blocks:
                action_text = match.group(2).strip()
                action_reasoning = match.group(3).strip() if match.group(3) else ""
                
                # Clean up action text
                action_text = re.sub(r'^\*\s*', '', action_text)  # Remove asterisks
                action_text = re.sub(r'^\*\*', '', action_text)  # Remove double asterisks
                action_text = action_text.strip()
                
                # Filter out zero values and fix them
                action_text = self._fix_zero_values(action_text)
                
                if action_text and len(action_text) > 10:
                    actions.append({
                        "action": action_text,
                        "reasoning": action_reasoning if action_reasoning else "This step is necessary to progress toward the goal."
                    })
            
            # If no structured pairs found, try simple bullet format
            if not actions:
                for line in actions_text.split('\n'):
                    line = line.strip()
                    # Remove numbering/bullets
                    line = re.sub(r'^[-•\d+\.\)]\s*', '', line)
                    # Remove "Action:" prefix if present
                    line = re.sub(r'^Action:\s*', '', line, flags=re.IGNORECASE)
                    line = self._fix_zero_values(line)
                    if line and len(line) > 10 and not line.lower().startswith('reasoning'):
                        actions.append({
                            "action": line,
                            "reasoning": ""
                        })
        
        # Fallback: if no structured format, try to extract from response
        if not actions:
            # Look for action-like sentences
            sentences = response_text.split('.')
            for sentence in sentences:
                sentence = sentence.strip()
                # Heuristic: actions are imperative or contain action verbs
                action_verbs = ['move', 'grasp', 'open', 'close', 'lift', 'rotate', 'approach', 'retract', 'position']
                if any(verb in sentence.lower() for verb in action_verbs) and len(sentence) > 15:
                    sentence = self._fix_zero_values(sentence)
                    actions.append({
                        "action": sentence,
                        "reasoning": ""
                    })
        
        # If still no actions, use the whole response as reasoning
        if not actions and not reasoning:
            reasoning = response_text[:500]  # First 500 chars
        
        return reasoning, actions
    
    def _fix_zero_values(self, text: str) -> str:
        """Fix zero values in action text by replacing with realistic estimates"""
        import re
        
        # Fix "0 meters" -> "1.0 meters" (typical movement)
        text = re.sub(r'\b0\s*meters?\b', '1.0 meters', text, flags=re.IGNORECASE)
        text = re.sub(r'\b0\s*m\b', '1.0 m', text, flags=re.IGNORECASE)
        
        # Fix "0 cm" -> "30 cm" (typical arm extension)
        text = re.sub(r'\b0\s*cm\b', '30 cm', text, flags=re.IGNORECASE)
        
        # Fix "speed of 0" -> "speed of 0.3" (typical speed)
        text = re.sub(r'speed\s+of\s+0\b', 'speed of 0.3 m/s', text, flags=re.IGNORECASE)
        
        # Fix "distance of 0" -> "distance of 0.5" (typical distance)
        text = re.sub(r'distance\s+of\s+0\b', 'distance of 0.5 meters', text, flags=re.IGNORECASE)
        
        # Fix "0 degrees" -> "90 degrees" (typical turn)
        text = re.sub(r'\b0\s*degrees?\b', '90 degrees', text, flags=re.IGNORECASE)
        
        return text
    
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
                        "num_predict": MAX_TOKENS,
                        "top_p": 0.9,
                        "top_k": 40
                    }
                },
                timeout=OLLAMA_TIMEOUT
            )
            
            if response.status_code != 200:
                raise Exception(f"Ollama API error: {response.status_code}")
            
            response_data = response.json()
            response_text = response_data.get("response", "")
            
            # Parse response
            reasoning, actions_list = self._parse_response(response_text)
            
            inference_time = time.time() - start_time
            
            # Convert actions list to format expected by frontend
            # actions_list is now List[Dict] with "action" and "reasoning" keys
            actions = []
            for i, action_item in enumerate(actions_list):
                if isinstance(action_item, dict):
                    actions.append(action_item["action"])
                else:
                    actions.append(str(action_item))
            
            # Calculate confidence (slightly lower than Cosmos since it's fallback)
            confidence = self._calculate_confidence(response_text, reasoning, actions)
            
            return {
                "actions": actions,
                "actions_detailed": actions_list,  # Include detailed format with reasoning
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
    
    def _calculate_confidence(self, response_text: str, reasoning: str, actions: List) -> float:
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
        
        # Penalize if zero values are present (indicates poor planning)
        if '0 meters' in response_text.lower() or '0 m' in response_text.lower() or 'speed of 0' in response_text.lower():
            confidence -= 0.1
        
        return min(0.85, max(0.3, confidence))  # Cap at 0.85, min 0.3 for fallback
    
    def is_available(self) -> bool:
        """Check if Ollama planner is available"""
        return self.available

