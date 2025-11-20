"""
EDEN Input Layer Package
Handles camera input, object detection, and VLM-based frame description
"""

from .camera_server import CameraServer
from .frame_processor import FrameProcessor

__all__ = ['CameraServer', 'FrameProcessor']

