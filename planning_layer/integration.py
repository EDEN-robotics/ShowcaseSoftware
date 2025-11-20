"""
Integration helpers for Cognitive Layer → Planning Layer communication
"""

import requests
from typing import Dict, Optional, List
from .config import *


class PlanningLayerClient:
    """Client for communicating with planning layer service"""
    
    def __init__(self, planning_service_url: str = "http://localhost:8001"):
        self.service_url = planning_service_url
        self.plan_endpoint = f"{self.service_url}/api/plan/generate"
    
    def generate_plan(
        self,
        goal: str,
        scene_description: str,
        context: Optional[Dict] = None,
        user_id: Optional[str] = None,
        user_name: Optional[str] = None
    ) -> Dict:
        """
        Request plan generation from planning layer.
        
        Args:
            goal: Goal from cognitive layer decision
            scene_description: Scene description from VLM/context gathering
            context: Additional context from cognitive layer
            user_id: Optional user identifier
            user_name: Optional user name
        
        Returns:
            Planning result with actions, reasoning, confidence
        """
        try:
            payload = {
                "goal": goal,
                "scene_description": scene_description,
                "context": context or {},
                "user_id": user_id,
                "user_name": user_name
            }
            
            response = requests.post(
                self.plan_endpoint,
                json=payload,
                timeout=60  # Longer timeout for planning
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"[PlanningLayerClient] Planning service error: {response.status_code}")
                return {
                    "error": f"Planning service returned {response.status_code}",
                    "actions": [],
                    "reasoning": "Planning service unavailable",
                    "confidence": 0.0
                }
                
        except requests.exceptions.RequestException as e:
            print(f"[PlanningLayerClient] Connection error: {e}")
            return {
                "error": str(e),
                "actions": [],
                "reasoning": "Could not connect to planning service",
                "confidence": 0.0
            }
    
    def check_service_available(self) -> bool:
        """Check if planning service is available"""
        try:
            response = requests.get(f"{self.service_url}/", timeout=5)
            return response.status_code == 200
        except:
            return False


def format_cognitive_output_for_planning(cognitive_result: Dict) -> Dict:
    """
    Format cognitive layer output for planning layer input.
    
    Args:
        cognitive_result: Result from cognitive layer processing
    
    Returns:
        Formatted data for planning layer
    """
    # Extract goal from cognitive result
    # This would come from user interaction or cognitive decision
    goal = cognitive_result.get("goal", "")
    
    # Extract scene description from context gathering
    context_data = cognitive_result.get("context_data", {})
    scene_description = context_data.get("description", "") or context_data.get("scene_context", "")
    
    # Add detected objects and actions to scene description
    detected_objects = context_data.get("detected_objects", [])
    detected_actions = context_data.get("detected_actions", [])
    
    if detected_objects:
        scene_description += f"\nDetected objects: {', '.join(detected_objects)}"
    if detected_actions:
        scene_description += f"\nDetected actions: {', '.join(detected_actions)}"
    
    # Add emotional tone if available
    emotional_tone = context_data.get("emotional_tone")
    if emotional_tone:
        scene_description += f"\nEmotional context: {emotional_tone}"
    
    return {
        "goal": goal,
        "scene_description": scene_description,
        "context": {
            "importance_score": context_data.get("metadata", {}).get("importance_score", 0.5),
            "cognitive_reasoning": cognitive_result.get("reasoning_trace", {}).get("llm_reasoning", ""),
            "personality_state": cognitive_result.get("personality_state", {})
        }
    }


def integrate_planning_with_cognitive(
    cognitive_result: Dict,
    planning_client: PlanningLayerClient
) -> Dict:
    """
    Integrate planning layer with cognitive layer output.
    
    Args:
        cognitive_result: Result from cognitive layer
        planning_client: Planning layer client
    
    Returns:
        Combined result with planning added
    """
    # Format cognitive output for planning
    planning_input = format_cognitive_output_for_planning(cognitive_result)
    
    # Generate plan
    planning_result = planning_client.generate_plan(
        goal=planning_input["goal"],
        scene_description=planning_input["scene_description"],
        context=planning_input["context"]
    )
    
    # Combine results
    return {
        **cognitive_result,
        "planning": planning_result,
        "has_plan": "actions" in planning_result and len(planning_result.get("actions", [])) > 0
    }

