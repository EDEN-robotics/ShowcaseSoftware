"""
Frame Importance Analyzer
Determines why frames are important using multi-factor analysis
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
import requests
import json
from .config import *


class FrameImportanceAnalyzer:
    """Analyzes frames to determine importance and reasoning"""
    
    def __init__(self):
        self.vlm_model = VLM_MODEL
        self.vlm_url = f"{VLM_BASE_URL}/api/chat"
    
    def calculate_motion_importance(self, motion_score: float) -> Tuple[float, str]:
        """
        Calculate importance based on motion.
        
        Returns:
            (importance_score, reasoning)
        """
        if motion_score < MOTION_THRESHOLD_FOR_ANALYSIS:
            return 0.2, "Low motion detected - likely static scene"
        elif motion_score < 50:
            return 0.5, f"Moderate motion ({motion_score:.1f}) - some activity"
        elif motion_score < 100:
            return 0.7, f"High motion ({motion_score:.1f}) - significant movement"
        else:
            return 0.9, f"Very high motion ({motion_score:.1f}) - major activity or change"
    
    def calculate_detection_importance(self, detections: List[Dict]) -> Tuple[float, str]:
        """
        Calculate importance based on detected objects.
        
        Returns:
            (importance_score, reasoning)
        """
        if not detections:
            return 0.2, "No objects detected"
        
        # Count high-confidence detections
        high_conf_detections = [d for d in detections if d.get("confidence", 0) > MIN_CONFIDENCE_FOR_IMPORTANCE]
        
        if len(high_conf_detections) == 0:
            return 0.3, "Objects detected but low confidence"
        
        # Check for important object types
        important_objects = ["person", "human", "face", "hand"]
        detected_important = any(
            any(obj in det.get("class", "").lower() for obj in important_objects)
            for det in high_conf_detections
        )
        
        if detected_important:
            importance = min(0.9, 0.5 + len(high_conf_detections) * 0.1)
            reasoning = f"Detected {len(high_conf_detections)} important objects (person/human)"
        else:
            importance = min(0.7, 0.4 + len(high_conf_detections) * 0.1)
            reasoning = f"Detected {len(high_conf_detections)} objects"
        
        return importance, reasoning
    
    def calculate_novelty_score(self, current_objects: List[str], previous_objects: List[str]) -> Tuple[float, str]:
        """
        Calculate novelty based on object changes.
        
        Returns:
            (novelty_score, reasoning)
        """
        if not previous_objects:
            return 0.6, "First frame - baseline established"
        
        current_set = set(obj.lower() for obj in current_objects)
        previous_set = set(obj.lower() for obj in previous_objects)
        
        new_objects = current_set - previous_set
        removed_objects = previous_set - current_set
        
        if new_objects or removed_objects:
            novelty = min(0.8, 0.5 + (len(new_objects) + len(removed_objects)) * 0.1)
            reasoning = f"Scene change: {len(new_objects)} new, {len(removed_objects)} removed objects"
        else:
            novelty = 0.3
            reasoning = "No significant object changes"
        
        return novelty, reasoning
    
    async def analyze_importance_with_vlm(
        self, 
        motion_score: float,
        detections: List[Dict],
        scene_description: str
    ) -> Dict:
        """
        Use VLM to analyze why frame is important.
        
        Returns:
            Dictionary with importance analysis
        """
        if not IMPORTANCE_ANALYSIS_ENABLED:
            return {"reasoning": "VLM analysis disabled"}
        
        # Extract detected objects
        detected_objects = [d.get("class", "unknown") for d in detections]
        
        prompt = IMPORTANCE_REASONING_PROMPT.format(
            motion_score=motion_score,
            detected_objects=", ".join(detected_objects) if detected_objects else "None",
            scene_description=scene_description[:200]  # Truncate if too long
        )
        
        try:
            response = requests.post(
                self.vlm_url,
                json={
                    "model": self.vlm_model,
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "stream": False
                },
                timeout=VLM_TIMEOUT
            )
            
            if response.status_code == 200:
                result = response.json()
                reasoning = result.get("message", {}).get("content", "")
                return {"reasoning": reasoning.strip()}
            else:
                return {"reasoning": f"VLM API error: {response.status_code}"}
                
        except Exception as e:
            return {"reasoning": f"VLM analysis error: {str(e)}"}
    
    def analyze_frame_importance(
        self,
        motion_score: float,
        detections: List[Dict],
        previous_objects: Optional[List[str]] = None
    ) -> Dict:
        """
        Comprehensive importance analysis combining multiple factors.
        
        Returns:
            Dictionary with importance scores and reasoning
        """
        # Calculate individual importance scores
        motion_importance, motion_reasoning = self.calculate_motion_importance(motion_score)
        detection_importance, detection_reasoning = self.calculate_detection_importance(detections)
        
        # Novelty analysis
        current_objects = [d.get("class", "") for d in detections]
        novelty_score, novelty_reasoning = self.calculate_novelty_score(
            current_objects,
            previous_objects or []
        )
        
        # Weighted combination
        combined_importance = (
            motion_importance * MOTION_WEIGHT +
            detection_importance * DETECTION_WEIGHT +
            novelty_score * NOVELTY_WEIGHT
        )
        
        # Determine if frame is important
        is_important = combined_importance > 0.5
        
        return {
            "importance_score": combined_importance,
            "is_important": is_important,
            "motion_score": motion_score,
            "motion_importance": motion_importance,
            "motion_reasoning": motion_reasoning,
            "detection_importance": detection_importance,
            "detection_reasoning": detection_reasoning,
            "novelty_score": novelty_score,
            "novelty_reasoning": novelty_reasoning,
            "detected_objects": current_objects,
            "reasoning_summary": f"Motion: {motion_reasoning}. Detection: {detection_reasoning}. Novelty: {novelty_reasoning}."
        }

