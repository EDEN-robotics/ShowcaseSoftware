"""
EDEN Camera Server: Captures frames, runs YOLO detection, and sends important frames via WebSocket
"""

import asyncio
import websockets
import json
import cv2
import base64
import time
import numpy as np
from collections import deque
from ultralytics import YOLO
import torch
from typing import Set, Optional
from .config import *


class CameraServer:
    """WebSocket server that captures camera frames and sends important ones"""
    
    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path or YOLO_MODEL_PATH
        self.device = "cuda" if torch.cuda.is_available() and YOLO_DEVICE == "cuda" else "cpu"
        self.connected_clients: Set[websockets.WebSocketServerProtocol] = set()
        self.frame_history = deque(maxlen=MOTION_MEMORY_SIZE)
        self.model = None
        self.cap = None
        self.last_send_time = 0
        
    def load_model(self):
        """Load YOLO model"""
        import os
        
        # Try multiple possible paths
        possible_paths = [
            self.model_path,
            os.path.join("input_layer", "YOLOv11obj_model.pt"),
            os.path.join("input_layer", "Input-Layer-main", "YOLOv11obj_model.pt"),
            os.path.join(os.path.dirname(__file__), "YOLOv11obj_model.pt"),
            os.path.join(os.path.dirname(__file__), "Input-Layer-main", "YOLOv11obj_model.pt"),
        ]
        
        model_file = None
        for path in possible_paths:
            if os.path.exists(path):
                model_file = path
                break
        
        if not model_file:
            print(f"[CameraServer] Error: YOLO model not found. Tried: {possible_paths}")
            return False
        
        try:
            print(f"[CameraServer] Loading YOLO model from {model_file} on {self.device.upper()}...")
            self.model = YOLO(model_file).to(self.device)
            print(f"[CameraServer] Model loaded successfully on {self.device.upper()}")
            return True
        except Exception as e:
            print(f"[CameraServer] Error loading model: {e}")
            return False
    
    def initialize_camera(self, camera_index: int = None):
        """Initialize camera capture"""
        camera_idx = camera_index if camera_index is not None else CAMERA_INDEX
        self.cap = cv2.VideoCapture(camera_idx)
        
        if not self.cap.isOpened():
            print(f"[CameraServer] Error: Cannot open camera {camera_idx}")
            return False
        
        # Set camera properties
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)
        self.cap.set(cv2.CAP_PROP_FPS, FPS)
        
        print(f"[CameraServer] Camera {camera_idx} initialized ({CAMERA_WIDTH}x{CAMERA_HEIGHT} @ {FPS}fps)")
        return True
    
    def is_important_frame(self, frame: np.ndarray, detections) -> tuple[bool, float]:
        """
        Determine if frame is important enough to send.
        Criteria: motion magnitude + high-confidence detections.
        
        Returns:
            (is_important, motion_score)
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        self.frame_history.append(gray)
        
        # Compute motion intensity (vs. previous frame)
        motion_score = 0.0
        if len(self.frame_history) > 1:
            diff = cv2.absdiff(self.frame_history[-1], self.frame_history[-2])
            motion_score = float(np.mean(diff))
        
        # Check YOLO detection confidence
        has_strong_detection = False
        if detections and len(detections) > 0:
            for box in detections:
                if hasattr(box, 'conf') and len(box.conf) > 0:
                    conf = float(box.conf[0])
                    if conf > YOLO_CONFIDENCE_THRESHOLD:
                        has_strong_detection = True
                        break
        
        importance = (motion_score > MOTION_THRESHOLD) or has_strong_detection
        return importance, motion_score
    
    def prepare_detections(self, detections) -> list:
        """Convert YOLO detections to JSON-serializable format"""
        detection_list = []
        
        if not detections or len(detections) == 0:
            return detection_list
        
        for box in detections:
            try:
                cls = int(box.cls[0]) if hasattr(box, 'cls') and len(box.cls) > 0 else 0
                conf = float(box.conf[0]) if hasattr(box, 'conf') and len(box.conf) > 0 else 0.0
                xyxy = box.xyxy[0].tolist() if hasattr(box, 'xyxy') and len(box.xyxy) > 0 else [0, 0, 0, 0]
                
                class_name = self.model.names.get(cls, f"class_{cls}") if self.model else f"class_{cls}"
                
                detection_list.append({
                    "class": class_name,
                    "confidence": conf,
                    "bbox": xyxy,
                })
            except Exception as e:
                print(f"[CameraServer] Error processing detection: {e}")
                continue
        
        return detection_list
    
    def encode_frame(self, frame: np.ndarray) -> str:
        """Encode frame to Base64 JPEG"""
        encode_params = [cv2.IMWRITE_JPEG_QUALITY, FRAME_QUALITY]
        _, buffer = cv2.imencode('.jpg', frame, encode_params)
        frame_b64 = base64.b64encode(buffer).decode("utf-8")
        return frame_b64
    
    async def websocket_handler(self, websocket, path=None):
        """Handle WebSocket client connections"""
        self.connected_clients.add(websocket)
        client_addr = websocket.remote_address if hasattr(websocket, 'remote_address') else "unknown"
        print(f"[CameraServer] Client connected from {client_addr} ({len(self.connected_clients)} total)")
        
        try:
            await websocket.wait_closed()
        except Exception as e:
            print(f"[CameraServer] WebSocket error: {e}")
        finally:
            self.connected_clients.discard(websocket)
            print(f"[CameraServer] Client disconnected ({len(self.connected_clients)} remaining)")
    
    async def frame_capture_loop(self):
        """Main loop: capture frames, detect objects, send important ones"""
        if not self.cap or not self.cap.isOpened():
            print("[CameraServer] Camera not initialized")
            return
        
        frame_count = 0
        
        while True:
            ret, frame = self.cap.read()
            if not ret:
                await asyncio.sleep(0.05)
                continue
            
            frame_count += 1
            
            # Run YOLO inference
            try:
                results = self.model(frame, verbose=False)
                detections = results[0].boxes if hasattr(results[0], "boxes") else []
            except Exception as e:
                print(f"[CameraServer] YOLO inference error: {e}")
                await asyncio.sleep(0.1)
                continue
            
            # Check if frame is important
            important, motion_score = self.is_important_frame(frame, detections)
            
            # Throttle sending
            current_time = time.time()
            time_since_last_send = current_time - self.last_send_time
            
            if important and time_since_last_send >= SEND_INTERVAL:
                self.last_send_time = current_time
                
                # Prepare metadata
                detections_list = self.prepare_detections(detections)
                
                metadata = {
                    "timestamp": current_time,
                    "frame_id": f"frame_{frame_count}_{int(current_time * 1000)}",
                    "motion_score": motion_score,
                    "detections": detections_list,
                    "detection_count": len(detections_list),
                    "camera_index": CAMERA_INDEX,
                }
                
                # Encode frame
                frame_b64 = self.encode_frame(frame)
                
                # Prepare payload
                payload = {
                    "metadata": metadata,
                    "frame": frame_b64
                }
                
                # Broadcast to all connected clients
                if self.connected_clients:
                    data = json.dumps(payload)
                    print(f"[CameraServer] Broadcasting frame {metadata['frame_id']} "
                          f"(motion={motion_score:.1f}, detections={len(detections_list)}) "
                          f"to {len(self.connected_clients)} client(s)")
                    
                    # Send to all clients (handle disconnections gracefully)
                    disconnected = set()
                    for ws in list(self.connected_clients):
                        try:
                            await ws.send(data)
                        except Exception as e:
                            print(f"[CameraServer] Send error to client: {e}")
                            disconnected.add(ws)
                    
                    # Remove disconnected clients
                    self.connected_clients -= disconnected
            
            await asyncio.sleep(0.01)  # Small delay to prevent CPU spinning
    
    async def start(self):
        """Start the camera server"""
        if not self.load_model():
            return False
        
        if not self.initialize_camera():
            return False
        
        # Start WebSocket server
        server = await websockets.serve(
            self.websocket_handler,
            WS_HOST,
            WS_PORT,
            max_size=None  # Allow large frames
        )
        
        print(f"[CameraServer] WebSocket server running on ws://{WS_HOST}:{WS_PORT}")
        print(f"[CameraServer] Camera: {CAMERA_INDEX}, Model: {self.model_path}")
        print(f"[CameraServer] Motion threshold: {MOTION_THRESHOLD}, Send interval: {SEND_INTERVAL}s")
        
        # Start frame capture loop
        capture_task = asyncio.create_task(self.frame_capture_loop())
        
        try:
            await server.wait_closed()
        finally:
            capture_task.cancel()
            if self.cap:
                self.cap.release()
            print("[CameraServer] Server stopped")
    
    def cleanup(self):
        """Cleanup resources"""
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()


async def main():
    """Main entry point"""
    server = CameraServer()
    await server.start()


if __name__ == "__main__":
    asyncio.run(main())

