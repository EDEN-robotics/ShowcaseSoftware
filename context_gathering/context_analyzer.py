"""
Context Analyzer
Uses VLM to analyze frames and generate rich context descriptions
"""

import asyncio
import base64
import cv2
import numpy as np
import requests
import json
from typing import Dict, List, Optional
from datetime import datetime
from .config import *
from .frame_importance import FrameImportanceAnalyzer


class ContextAnalyzer:
    """
    Analyzes frames using VLM to generate context descriptions
    and formats them for the cognitive layer
    """
    
    def __init__(self):
        self.vlm_model = VLM_MODEL
        self.vlm_url = f"{VLM_BASE_URL}/api/chat"
        self.importance_analyzer = FrameImportanceAnalyzer()
        self.previous_objects: List[str] = []
    
    async def analyze_frame_with_vlm(self, frame: np.ndarray) -> Optional[str]:
        """
        Analyze frame using Ollama VLM to generate scene description.
        
        Args:
            frame: OpenCV frame (BGR format)
        
        Returns:
            VLM-generated description or None if error
        """
        try:
            # Encode frame as base64 JPEG
            encode_params = [cv2.IMWRITE_JPEG_QUALITY, 85]
            _, buffer = cv2.imencode('.jpg', frame, encode_params)
            frame_b64 = base64.b64encode(buffer).decode("utf-8")
            
            # Call Ollama VLM
            response = requests.post(
                self.vlm_url,
                json={
                    "model": self.vlm_model,
                    "messages": [
                        {
                            "role": "user",
                            "content": SCENE_ANALYSIS_PROMPT,
                            "images": [frame_b64]
                        }
                    ],
                    "stream": False
                },
                timeout=VLM_TIMEOUT
            )
            
            if response.status_code == 200:
                result = response.json()
                description = result.get("message", {}).get("content", "")
                return description.strip()
            else:
                print(f"[ContextAnalyzer] VLM API error: {response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"[ContextAnalyzer] VLM request error: {e}")
            return None
        except Exception as e:
            print(f"[ContextAnalyzer] VLM error: {e}")
            return None
    
    def extract_structured_info(self, vlm_description: str, detections: List[Dict]) -> Dict:
        """
        Extract structured information from VLM description.
        
        Returns:
            Dictionary with extracted information
        """
        description_lower = vlm_description.lower()
        
        # Extract detected objects from YOLO
        detected_objects = [d.get("class", "unknown") for d in detections]
        
        # Extract actions (heuristic-based)
        actions = []
        action_keywords = {
            "waving": ["wave", "waving", "waves"],
            "pointing": ["point", "pointing", "points"],
            "walking": ["walk", "walking", "walks", "moving"],
            "sitting": ["sit", "sitting", "sits"],
            "standing": ["stand", "standing", "stands"],
            "talking": ["talk", "talking", "talks", "speaking", "speaks", "say", "saying"],
            "smiling": ["smile", "smiling", "smiles", "happy"],
            "looking": ["look", "looking", "looks", "gaze", "gazing", "watch", "watching"],
            "gesturing": ["gesture", "gesturing", "gestures"],
            "interacting": ["interact", "interacting", "interaction"],
        }
        
        for action, keywords in action_keywords.items():
            if any(kw in description_lower for kw in keywords):
                actions.append(action)
        
        # Extract emotional tone
        emotional_tone = None
        if INCLUDE_EMOTIONAL_TONE:
            tone_keywords = {
                "positive": ["happy", "smiling", "joyful", "excited", "positive", "friendly"],
                "negative": ["sad", "angry", "frustrated", "negative", "unhappy"],
                "neutral": ["calm", "neutral", "normal", "ordinary"],
                "engaged": ["engaged", "focused", "attentive", "interested"],
            }
            
            for tone, keywords in tone_keywords.items():
                if any(kw in description_lower for kw in keywords):
                    emotional_tone = tone
                    break
        
        # Extract spatial relationships
        spatial_info = []
        if INCLUDE_SPATIAL_RELATIONSHIPS:
            spatial_keywords = ["near", "beside", "behind", "in front", "left", "right", "above", "below"]
            for keyword in spatial_keywords:
                if keyword in description_lower:
                    # Extract sentence containing spatial keyword
                    sentences = vlm_description.split('.')
                    for sentence in sentences:
                        if keyword in sentence.lower():
                            spatial_info.append(sentence.strip())
                            break
        
        return {
            "detected_objects": detected_objects,
            "detected_actions": actions,
            "emotional_tone": emotional_tone,
            "spatial_relationships": spatial_info if spatial_info else None,
        }
    
    async def gather_context(
        self,
        frame: np.ndarray,
        metadata: Dict,
        previous_objects: Optional[List[str]] = None
    ) -> Dict:
        """
        Main method: Gather comprehensive context from frame.
        
        Args:
            frame: OpenCV frame
            metadata: Frame metadata (motion_score, detections, etc.)
            previous_objects: List of objects from previous frame (for novelty)
        
        Returns:
            Complete context dictionary formatted for cognitive layer
        """
        frame_id = metadata.get("frame_id", f"frame_{int(datetime.now().timestamp())}")
        timestamp = metadata.get("timestamp", datetime.now().isoformat())
        motion_score = metadata.get("motion_score", 0.0)
        detections = metadata.get("detections", [])
        
        print(f"[ContextAnalyzer] Analyzing frame {frame_id}...")
        
        # Step 1: Analyze importance
        importance_analysis = self.importance_analyzer.analyze_frame_importance(
            motion_score=motion_score,
            detections=detections,
            previous_objects=previous_objects or self.previous_objects
        )
        
        # Step 2: Generate VLM description
        vlm_description = await self.analyze_frame_with_vlm(frame)
        
        if not vlm_description:
            print(f"[ContextAnalyzer] ⚠️ No VLM description for frame {frame_id}")
            # Fallback to basic description
            vlm_description = f"Frame shows {len(detections)} detected objects with motion score {motion_score:.1f}"
        
        print(f"[ContextAnalyzer] ✓ VLM description: {vlm_description[:100]}...")
        
        # Step 3: Extract structured information
        structured_info = self.extract_structured_info(vlm_description, detections)
        
        # Step 4: Get VLM importance reasoning (optional, async)
        importance_reasoning = None
        if IMPORTANCE_ANALYSIS_ENABLED:
            importance_reasoning_data = await self.importance_analyzer.analyze_importance_with_vlm(
                motion_score=motion_score,
                detections=detections,
                scene_description=vlm_description
            )
            importance_reasoning = importance_reasoning_data.get("reasoning")
        
        # Step 5: Update previous objects for next frame
        current_objects = structured_info["detected_objects"]
        self.previous_objects = current_objects.copy()
        
        # Step 6: Format for cognitive layer
        context_data = {
            "frame_id": frame_id,
            "timestamp": timestamp if isinstance(timestamp, str) else datetime.fromtimestamp(timestamp).isoformat(),
            "description": vlm_description,
            "detected_objects": structured_info["detected_objects"],
            "detected_actions": structured_info["detected_actions"],
            "emotional_tone": structured_info["emotional_tone"],
            "scene_context": vlm_description[:200] if len(vlm_description) > 200 else vlm_description,
            "source": "camera_frame",
            "metadata": {
                "motion_score": motion_score,
                "detection_count": len(detections),
                "importance_score": importance_analysis["importance_score"],
                "is_important": importance_analysis["is_important"],
                "importance_reasoning": importance_reasoning or importance_analysis["reasoning_summary"],
                "yolo_detections": detections,
                "spatial_relationships": structured_info["spatial_relationships"],
            }
        }
        
        # Add detailed description if enabled
        if INCLUDE_DETAILED_DESCRIPTION:
            context_data["detailed_description"] = vlm_description
        
        print(f"[ContextAnalyzer] ✓ Context gathered: importance={importance_analysis['importance_score']:.3f}, "
              f"objects={len(structured_info['detected_objects'])}, actions={len(structured_info['detected_actions'])}")
        
        return context_data
    
    def reset_context(self):
        """Reset context state (e.g., for new session)"""
        self.previous_objects = []

