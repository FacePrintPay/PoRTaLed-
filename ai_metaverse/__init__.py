"""
AI Metaverse System

A distributed system of specialized AI assistants working together to create, 
optimize, and maintain code for the AI Metaverse project.
"""

from .orchestrator import AIMetaverseOrchestrator
from .main import AIMetaverseSystem

__version__ = '1.0.0'
__author__ = 'AI Metaverse Team'

__all__ = ['AIMetaverseOrchestrator', 'AIMetaverseSystem']