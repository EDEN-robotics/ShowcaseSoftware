"""
EDEN Context Gathering Layer
Analyzes frames to determine importance and generate rich context descriptions
"""

from .context_analyzer import ContextAnalyzer
from .frame_importance import FrameImportanceAnalyzer

__all__ = ['ContextAnalyzer', 'FrameImportanceAnalyzer']

