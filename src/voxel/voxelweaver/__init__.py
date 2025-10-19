"""
VoxelWeaver - AI-powered procedural 3D scene generation system.
Integrates external references, real-world proportions, and intelligent scene analysis.
"""

from .voxelweaver_core import VoxelWeaverCore, VoxelWeaverConfig
from .search_scraper import ReferenceSearcher, ExternalReference
from .proportion_analyzer import ProportionAnalyzer, ProportionCheck
from .geometry_handler import GeometryHandler, GeometryType, ComplexityLevel, GeometryHint
from .context_alignment import ContextAligner, BoundingBox, AlignedObject, PlacementStrategy
from .lighting_engine import LightingEngine, LightConfig, LightingStyle, TimeOfDay
from .texture_mapper import TextureMapper, MaterialSuggestion, MaterialType
from .scene_validator import SceneValidator, ValidationLevel, ValidationIssue, IssueLevel
from .blender_bridge import BlenderBridge

__all__ = [
    # Core
    "VoxelWeaverCore",
    "VoxelWeaverConfig",

    # Search & References
    "ReferenceSearcher",
    "ExternalReference",

    # Proportions
    "ProportionAnalyzer",
    "ProportionCheck",

    # Geometry
    "GeometryHandler",
    "GeometryType",
    "ComplexityLevel",
    "GeometryHint",

    # Spatial Alignment
    "ContextAligner",
    "BoundingBox",
    "AlignedObject",
    "PlacementStrategy",

    # Lighting
    "LightingEngine",
    "LightConfig",
    "LightingStyle",
    "TimeOfDay",

    # Materials
    "TextureMapper",
    "MaterialSuggestion",
    "MaterialType",

    # Validation
    "SceneValidator",
    "ValidationLevel",
    "ValidationIssue",
    "IssueLevel",

    # Blender Integration
    "BlenderBridge",
]

__version__ = "1.0.0"
