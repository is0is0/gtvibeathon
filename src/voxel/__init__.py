"""
Voxel - AI-powered autonomous 3D scene generation system for Blender.

This package provides a multi-agent system for automatically creating
complete 3D scenes in Blender from natural language descriptions.
"""

from voxel.core.agency import Voxel
from voxel.core.config import Config
from voxel.core.models import SceneResult

__version__ = "0.1.0"
__all__ = ["Voxel", "Config", "SceneResult"]
