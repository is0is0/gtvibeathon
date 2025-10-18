"""Data models for the 3DAgency system."""

from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Optional

from pydantic import BaseModel, Field


class AgentRole(str, Enum):
    """Agent roles in the system."""

    CONCEPT = "concept"
    BUILDER = "builder"
    TEXTURE = "texture"
    RENDER = "render"
    ANIMATION = "animation"
    REVIEWER = "reviewer"
    # Advanced agents
    GEOMETRY_NODES = "geometry_nodes"
    PHYSICS = "physics"
    PARTICLES = "particles"
    SCENE_ANALYZER = "scene_analyzer"
    IMPORTER = "importer"


class MessageRole(str, Enum):
    """Message roles for agent communication."""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class Message(BaseModel):
    """A message in the agent conversation."""

    role: MessageRole
    content: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class AgentResponse(BaseModel):
    """Response from an agent."""

    agent_role: AgentRole
    content: str
    script: Optional[str] = None
    reasoning: Optional[str] = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.now)


class BlenderScriptResult(BaseModel):
    """Result of executing a Blender script."""

    success: bool
    stdout: str = ""
    stderr: str = ""
    execution_time: float = 0.0
    script_path: Optional[Path] = None


class SceneResult(BaseModel):
    """Final result of scene generation."""

    success: bool
    prompt: str
    concept: Optional[str] = None
    output_path: Optional[Path] = None
    scripts: list[Path] = Field(default_factory=list)
    render_time: float = 0.0
    iterations: int = 0
    messages: list[Message] = Field(default_factory=list)
    agent_responses: list[AgentResponse] = Field(default_factory=list)
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)

    class Config:
        arbitrary_types_allowed = True


class ReviewFeedback(BaseModel):
    """Feedback from the reviewer agent."""

    rating: int = Field(..., ge=1, le=10, description="Quality rating 1-10")
    strengths: list[str] = Field(default_factory=list)
    improvements: list[str] = Field(default_factory=list)
    suggestions: str = ""
    should_refine: bool = False
