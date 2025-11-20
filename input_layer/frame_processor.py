"""
EDEN Frame Processor: Receives frames, generates VLM descriptions, and sends to cognitive layer
"""

import asyncio
import websockets
import json
import base64
import cv2
import numpy as np
import requests
import time
import sys
import os
from typing import Optional, Dict
from datetime import datetime

# Add parent directory to path for context_gathering import
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from context_gathering import ContextAnalyzer
from .config import *


class FrameProcessor:
    """Processes frames from camera server, generates VLM descriptions, and sends to cognitive layer"""
    
    def __init__(self, cognitive_layer_url: Optional[str] = None):
        self.cognitive_layer_url = cognitive_layer_url or COGNITIVE_LAYER_URL
        self.cognitive_endpoint = f"{self.cognitive_layer_url}{COGNITIVE_LAYER_ENDPOINT}"
        self.enable_cognitive = ENABLE_COGNITIVE_PROCESSING
        self.vlm_model = VLM_MODEL
        self.frame_count = 0
        # Initialize context analyzer
        self.context_analyzer = ContextAnalyzer()
        
    async def analyze_with_vlm(self, frame: np.ndarray) -> Optional[str]:
        """
        Send frame to Ollama VLM for description using HTTP API.
        
        Args:
            frame: OpenCV frame (BGR format)
        
        Returns:
            VLM description text or None if error
        """
        try:
            # Encode frame as base64 JPEG
            encode_params = [cv2.IMWRITE_JPEG_QUALITY, FRAME_QUALITY]
            _, buffer = cv2.imencode('.jpg', frame, encode_params)
            frame_b64 = base64.b64encode(buffer).decode("utf-8")
            
            # Call Ollama VLM via HTTP API
            ollama_url = "http://localhost:11434/api/chat"
            
            payload = {
                "model": self.vlm_model,
                "messages": [
                    {
                        "role": "user",
                        "content": VLM_PROMPT,
                        "images": [frame_b64]
                    }
                ],
                "stream": False
            }
            
            response = requests.post(
                ollama_url,
                json=payload,
                timeout=VLM_TIMEOUT
            )
            
            if response.status_code == 200:
                result = response.json()
                text = result.get("message", {}).get("content", "")
                return text.strip()
            else:
                print(f"[FrameProcessor] Ollama API error: {response.status_code} - {response.text}")
                return None
            
        except requests.exceptions.RequestException as e:
            print(f"[FrameProcessor] VLM request error: {e}")
            return None
        except Exception as e:
            print(f"[FrameProcessor] VLM error: {e}")
            return None
    
    def extract_detected_objects(self, detections: list) -> list:
        """Extract list of detected object names from detections"""
        objects = []
        for det in detections:
            class_name = det.get("class", "unknown")
            confidence = det.get("confidence", 0.0)
            if confidence > YOLO_CONFIDENCE_THRESHOLD:
                objects.append(class_name)
        return objects
    
    def extract_detected_actions(self, detections: list, vlm_description: str) -> list:
        """
        Extract detected actions from VLM description.
        This is a simple heuristic - could be enhanced with NLP.
        """
        actions = []
        description_lower = vlm_description.lower() if vlm_description else ""
        
        # Common action keywords
        action_keywords = {
            "waving": ["wave", "waving", "waves"],
            "pointing": ["point", "pointing", "points"],
            "walking": ["walk", "walking", "walks"],
            "sitting": ["sit", "sitting", "sits"],
            "standing": ["stand", "standing", "stands"],
            "talking": ["talk", "talking", "talks", "speaking", "speaks"],
            "smiling": ["smile", "smiling", "smiles"],
            "looking": ["look", "looking", "looks", "gaze", "gazing"],
        }
        
        for action, keywords in action_keywords.items():
            if any(kw in description_lower for kw in keywords):
                actions.append(action)
        
        return actions
    
    async def send_to_cognitive_layer(self, event_data: Dict) -> Optional[Dict]:
        """
        Send processed event to cognitive layer API.
        
        Args:
            event_data: EventFrame dictionary
        
        Returns:
            Response from cognitive layer or None if error
        """
        if not self.enable_cognitive:
            return None
        
        try:
            response = requests.post(
                self.cognitive_endpoint,
                json=event_data,
                timeout=10,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"[FrameProcessor] Cognitive layer API error: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"[FrameProcessor] Error sending to cognitive layer: {e}")
            return None
    
    async def process_frame(self, metadata: Dict, frame: np.ndarray) -> Dict:
        """
        Process a single frame using context gathering layer: analyze importance,
        generate VLM description, and send to cognitive layer.
        
        Args:
            metadata: Frame metadata from camera server
            frame: Decoded frame image
        
        Returns:
            Processing result dictionary
        """
        self.frame_count += 1
        processing_start = time.time()
        
        # Extract metadata
        frame_id = metadata.get("frame_id", f"frame_{self.frame_count}")
        timestamp = metadata.get("timestamp", time.time())
        
        # Use context gathering layer to analyze frame
        print(f"[FrameProcessor] Gathering context for frame {frame_id}...")
        context_start = time.time()
        
        try:
            # Gather comprehensive context
            context_data = await self.context_analyzer.gather_context(
                frame=frame,
                metadata=metadata
            )
            context_time = time.time() - context_start
            
            print(f"[FrameProcessor] ✓ Context gathered ({context_time:.2f}s)")
            print(f"  Importance: {context_data['metadata']['importance_score']:.3f}")
            print(f"  Reasoning: {context_data['metadata']['importance_reasoning'][:80]}...")
            
            # Send to cognitive layer
            cognitive_result = None
            if self.enable_cognitive:
                cognitive_start = time.time()
                cognitive_result = await self.send_to_cognitive_layer(context_data)
                cognitive_time = time.time() - cognitive_start
                
                if cognitive_result:
                    importance = cognitive_result.get("importance", 0.0)
                    added = cognitive_result.get("added_to_graph", False)
                    print(f"[FrameProcessor] ✓ Cognitive layer: importance={importance:.3f}, "
                          f"added_to_graph={added} ({cognitive_time:.2f}s)")
                else:
                    print(f"[FrameProcessor] ⚠️ Cognitive layer processing failed")
            
            total_time = time.time() - processing_start
            
            return {
                "status": "processed",
                "frame_id": frame_id,
                "context_data": context_data,
                "cognitive_result": cognitive_result,
                "processing_time": total_time,
                "context_time": context_time,
            }
            
        except Exception as e:
            print(f"[FrameProcessor] Error processing frame: {e}")
            import traceback
            traceback.print_exc()
            return {
                "status": "error",
                "frame_id": frame_id,
                "error": str(e)
            }
    
    async def listen_and_process(self):
        """Main loop: connect to camera server and process incoming frames"""
        uri = f"ws://{WS_HOST}:{WS_PORT}"
        
        print(f"[FrameProcessor] Connecting to camera server at {uri}...")
        print(f"[FrameProcessor] VLM Model: {self.vlm_model}")
        print(f"[FrameProcessor] Cognitive Layer: {self.cognitive_endpoint if self.enable_cognitive else 'DISABLED'}")
        
        while True:
            try:
                async with websockets.connect(uri, max_size=None) as websocket:
                    print("[FrameProcessor] ✓ Connected to camera server")
                    
                    async for message in websocket:
                        try:
                            data = json.loads(message)
                        except json.JSONDecodeError as e:
                            print(f"[FrameProcessor] JSON decode error: {e}")
                            continue
                        
                        metadata = data.get("metadata", {})
                        frame_b64 = data.get("frame")
                        
                        if not frame_b64:
                            print("[FrameProcessor] No frame data in message")
                            continue
                        
                        # Decode frame
                        try:
                            img_bytes = base64.b64decode(frame_b64)
                            np_arr = np.frombuffer(img_bytes, np.uint8)
                            frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
                        except Exception as e:
                            print(f"[FrameProcessor] Frame decode error: {e}")
                            continue
                        
                        if frame is None:
                            print("[FrameProcessor] Decoded frame is None")
                            continue
                        
                        # Process frame
                        result = await self.process_frame(metadata, frame)
                        
                        # Optional: Display frame with detections (for debugging)
                        if False:  # Set to True to enable display
                            display_frame = frame.copy()
                            detections = metadata.get("detections", [])
                            for det in detections:
                                bbox = det.get("bbox", [])
                                if len(bbox) == 4:
                                    x1, y1, x2, y2 = map(int, bbox)
                                    cls = det.get("class", "unknown")
                                    conf = det.get("confidence", 0.0)
                                    cv2.rectangle(display_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                                    cv2.putText(display_frame, f"{cls} {conf:.2f}", 
                                              (x1, max(20, y1 - 10)),
                                              cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                            
                            cv2.imshow("Frame Processor", display_frame)
                            if cv2.waitKey(1) & 0xFF == ord("q"):
                                break
                        
            except websockets.exceptions.ConnectionClosed:
                print("[FrameProcessor] Connection closed, reconnecting in 5 seconds...")
                await asyncio.sleep(5)
            except Exception as e:
                print(f"[FrameProcessor] Error: {e}")
                print("[FrameProcessor] Reconnecting in 5 seconds...")
                await asyncio.sleep(5)
        
        cv2.destroyAllWindows()


async def main():
    """Main entry point"""
    processor = FrameProcessor()
    await processor.listen_and_process()


if __name__ == "__main__":
    asyncio.run(main())

