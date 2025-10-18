"""AI agents for the Voxel system."""

# Core agents
from voxel.agents.concept import ConceptAgent
from voxel.agents.builder import BuilderAgent
from voxel.agents.render import RenderAgent
from voxel.agents.animation import AnimationAgent
from voxel.agents.reviewer import ReviewerAgent

# Advanced agents
from voxel.agents.geometry_nodes import GeometryNodesAgent
from voxel.agents.physics import PhysicsAgent
from voxel.agents.particles import ParticlesAgent
from voxel.agents.scene_analyzer import SceneAnalyzerAgent
from voxel.agents.importer import ImporterAgent

# New enhancement agents
from voxel.agents.rigging import RiggingAgent
from voxel.agents.compositing import CompositingAgent
from voxel.agents.sequence import SequenceAgent

# Specialized agents - import only when needed to avoid circular imports
# from voxel.agents.shader import ShaderAgent
# from voxel.agents.hdr import HDRAgent

# Import TextureAgent directly to avoid circular import
try:
    from voxel.agents.texture import TextureAgent
except ImportError:
    # Fallback if there are import issues
    TextureAgent = None

__all__ = [
    # Core agents
    "ConceptAgent",
    "BuilderAgent",
    "TextureAgent",
    "RenderAgent",
    "AnimationAgent",
    "ReviewerAgent",
    # Advanced agents
    "GeometryNodesAgent",
    "PhysicsAgent",
    "ParticlesAgent",
    "SceneAnalyzerAgent",
    "ImporterAgent",
    # New enhancement agents
    "RiggingAgent",
    "CompositingAgent",
    "SequenceAgent",
    # Specialized agents (commented out to avoid circular imports)
    # "ShaderAgent",
    # "HDRAgent",
]
