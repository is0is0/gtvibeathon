"""AI agents for the Voxel system."""

from agency3d.agents.concept import ConceptAgent
from agency3d.agents.builder import BuilderAgent
from agency3d.agents.texture import TextureAgent
from agency3d.agents.render import RenderAgent
from agency3d.agents.animation import AnimationAgent
from agency3d.agents.reviewer import ReviewerAgent

# Advanced agents
from agency3d.agents.geometry_nodes import GeometryNodesAgent
from agency3d.agents.physics import PhysicsAgent
from agency3d.agents.particles import ParticlesAgent
from agency3d.agents.scene_analyzer import SceneAnalyzerAgent
from agency3d.agents.importer import ImporterAgent

# New enhancement agents
from agency3d.agents.rigging import RiggingAgent
from agency3d.agents.compositing import CompositingAgent
from agency3d.agents.sequence import SequenceAgent

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
]
