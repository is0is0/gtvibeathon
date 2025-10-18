"""
Voxel - AI-powered autonomous 3D scene generation system for Blender.

This package provides a multi-agent system for automatically creating
complete 3D scenes in Blender from natural language descriptions.
"""

from agency3d.core.agency import Agency3D
from agency3d.core.config import Config
from agency3d.core.models import SceneResult

__version__ = "0.1.0"
__all__ = ["Agency3D", "Config", "SceneResult"]
