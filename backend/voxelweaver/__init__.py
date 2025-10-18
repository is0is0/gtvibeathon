"""
VoxelWeaver - AI-Powered Procedural 3D Scene Generation Subsystem
==================================================================

VoxelWeaver is a core procedural subsystem for AI 3D Scene Generation that handles
voxel-level geometry reasoning and procedural scene composition for Blender.

Main Components:
- VoxelWeaverCore: Main orchestration layer
- GeometryHandler: Voxel geometry generation and import
- ProportionAnalyzer: Real-world scale and proportion analysis
- ContextAlignment: Spatial positioning and collision detection
- LightingEngine: Realistic and stylized lighting
- TextureMapper: Material and texture generation
- BlenderBridge: Blender integration interface
- SearchScraper: Online reference gathering
- ModelFormatter: 3D model format conversion
- SceneValidator: Quality assurance and validation

Usage:
    from voxelweaver import VoxelWeaverCore

    weaver = VoxelWeaverCore()
    weaver.generate_scene(
        prompt="A cozy living room with a sofa and coffee table",
        style="realistic"
    )
"""

from .voxelweaver_core import VoxelWeaverCore
from .geometry_handler import GeometryHandler
from .proportion_analyzer import ProportionAnalyzer
from .context_alignment import ContextAlignment
from .lighting_engine import LightingEngine
from .texture_mapper import TextureMapper
from .blender_bridge import BlenderBridge
from .search_scraper import SearchScraper
from .model_formatter import ModelFormatter
from .scene_validator import SceneValidator

__version__ = "0.1.0"
__author__ = "VoxelWeaver Team"

__all__ = [
    "VoxelWeaverCore",
    "GeometryHandler",
    "ProportionAnalyzer",
    "ContextAlignment",
    "LightingEngine",
    "TextureMapper",
    "BlenderBridge",
    "SearchScraper",
    "ModelFormatter",
    "SceneValidator",
]
