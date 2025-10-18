"""
SQLAlchemy ORM models for Voxel database.

This module defines all database tables and relationships for tracking
projects, generations, agent executions, and analytics.
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Float, Boolean, ForeignKey,
    JSON, Enum as SQLEnum, Index
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
import enum

Base = declarative_base()


class ProjectStatus(enum.Enum):
    """Project status enumeration."""
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class GenerationStatus(enum.Enum):
    """Generation status enumeration."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class AgentType(enum.Enum):
    """Agent type enumeration."""
    CONCEPT = "concept"
    BUILDER = "builder"
    TEXTURE = "texture"
    RENDER = "render"
    ANIMATION = "animation"
    REVIEWER = "reviewer"


class ExecutionStatus(enum.Enum):
    """Execution status enumeration."""
    SUCCESS = "success"
    FAILED = "failed"


class RenderEngine(enum.Enum):
    """Render engine enumeration."""
    CYCLES = "CYCLES"
    EEVEE = "EEVEE"


class Project(Base):
    """Top-level project tracking."""
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())
    status: Mapped[ProjectStatus] = mapped_column(SQLEnum(ProjectStatus), default=ProjectStatus.DRAFT)
    settings_json: Mapped[Optional[dict]] = mapped_column(JSON)

    # Relationships
    generations: Mapped[List["Generation"]] = relationship("Generation", back_populates="project", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Project(id={self.id}, name='{self.name}', status='{self.status.value}')>"


class Generation(Base):
    """Individual scene generation attempts."""
    __tablename__ = "generations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey("projects.id"), nullable=False)
    session_id: Mapped[str] = mapped_column(String(255), nullable=False)
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    status: Mapped[GenerationStatus] = mapped_column(SQLEnum(GenerationStatus), default=GenerationStatus.PENDING)
    iteration_count: Mapped[int] = mapped_column(Integer, default=0)
    quality_score: Mapped[Optional[float]] = mapped_column(Float)
    output_path: Mapped[Optional[str]] = mapped_column(String(500))

    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="generations")
    agent_executions: Mapped[List["AgentExecution"]] = relationship("AgentExecution", back_populates="generation", cascade="all, delete-orphan")
    scripts: Mapped[List["Script"]] = relationship("Script", back_populates="generation", cascade="all, delete-orphan")
    renders: Mapped[List["Render"]] = relationship("Render", back_populates="generation", cascade="all, delete-orphan")
    reviews: Mapped[List["Review"]] = relationship("Review", back_populates="generation", cascade="all, delete-orphan")
    generation_tags: Mapped[List["GenerationTag"]] = relationship("GenerationTag", back_populates="generation", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Generation(id={self.id}, project_id={self.project_id}, status='{self.status.value}')>"


class AgentExecution(Base):
    """Track each agent's work."""
    __tablename__ = "agent_executions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    generation_id: Mapped[int] = mapped_column(Integer, ForeignKey("generations.id"), nullable=False)
    agent_type: Mapped[AgentType] = mapped_column(SQLEnum(AgentType), nullable=False)
    iteration_number: Mapped[int] = mapped_column(Integer, default=1)
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    response_text: Mapped[str] = mapped_column(Text, nullable=False)
    execution_time_ms: Mapped[Optional[int]] = mapped_column(Integer)
    token_count: Mapped[Optional[int]] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    status: Mapped[ExecutionStatus] = mapped_column(SQLEnum(ExecutionStatus), default=ExecutionStatus.SUCCESS)
    error_message: Mapped[Optional[str]] = mapped_column(Text)

    # Relationships
    generation: Mapped["Generation"] = relationship("Generation", back_populates="agent_executions")

    # Indexes
    __table_args__ = (
        Index('idx_agent_executions_generation', 'generation_id'),
        Index('idx_agent_executions_agent_type', 'agent_type'),
        Index('idx_agent_executions_created', 'created_at'),
    )

    def __repr__(self):
        return f"<AgentExecution(id={self.id}, agent_type='{self.agent_type.value}', status='{self.status.value}')>"


class Script(Base):
    """Generated Blender scripts."""
    __tablename__ = "scripts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    generation_id: Mapped[int] = mapped_column(Integer, ForeignKey("generations.id"), nullable=False)
    agent_type: Mapped[AgentType] = mapped_column(SQLEnum(AgentType), nullable=False)
    iteration_number: Mapped[int] = mapped_column(Integer, default=1)
    script_content: Mapped[str] = mapped_column(Text, nullable=False)
    file_path: Mapped[Optional[str]] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    # Relationships
    generation: Mapped["Generation"] = relationship("Generation", back_populates="scripts")

    # Indexes
    __table_args__ = (
        Index('idx_scripts_generation', 'generation_id'),
        Index('idx_scripts_agent_type', 'agent_type'),
    )

    def __repr__(self):
        return f"<Script(id={self.id}, agent_type='{self.agent_type.value}', generation_id={self.generation_id})>"


class Render(Base):
    """Rendered outputs."""
    __tablename__ = "renders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    generation_id: Mapped[int] = mapped_column(Integer, ForeignKey("generations.id"), nullable=False)
    iteration_number: Mapped[int] = mapped_column(Integer, default=1)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    render_time_seconds: Mapped[Optional[float]] = mapped_column(Float)
    samples: Mapped[Optional[int]] = mapped_column(Integer)
    resolution_x: Mapped[Optional[int]] = mapped_column(Integer)
    resolution_y: Mapped[Optional[int]] = mapped_column(Integer)
    engine: Mapped[Optional[RenderEngine]] = mapped_column(SQLEnum(RenderEngine))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    # Relationships
    generation: Mapped["Generation"] = relationship("Generation", back_populates="renders")

    # Indexes
    __table_args__ = (
        Index('idx_renders_generation', 'generation_id'),
        Index('idx_renders_created', 'created_at'),
    )

    def __repr__(self):
        return f"<Render(id={self.id}, generation_id={self.generation_id}, file_path='{self.file_path}')>"


class Review(Base):
    """Reviewer agent feedback."""
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    generation_id: Mapped[int] = mapped_column(Integer, ForeignKey("generations.id"), nullable=False)
    iteration_number: Mapped[int] = mapped_column(Integer, default=1)
    rating: Mapped[int] = mapped_column(Integer, nullable=False)  # 1-10 scale
    feedback_text: Mapped[str] = mapped_column(Text, nullable=False)
    suggestions: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    # Relationships
    generation: Mapped["Generation"] = relationship("Generation", back_populates="reviews")

    # Indexes
    __table_args__ = (
        Index('idx_reviews_generation', 'generation_id'),
        Index('idx_reviews_rating', 'rating'),
    )

    def __repr__(self):
        return f"<Review(id={self.id}, generation_id={self.generation_id}, rating={self.rating})>"


class Tag(Base):
    """Categorization tags."""
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    category: Mapped[Optional[str]] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    # Relationships
    generation_tags: Mapped[List["GenerationTag"]] = relationship("GenerationTag", back_populates="tag", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Tag(id={self.id}, name='{self.name}', category='{self.category}')>"


class GenerationTag(Base):
    """Many-to-many relationship between generations and tags."""
    __tablename__ = "generation_tags"

    generation_id: Mapped[int] = mapped_column(Integer, ForeignKey("generations.id"), primary_key=True)
    tag_id: Mapped[int] = mapped_column(Integer, ForeignKey("tags.id"), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    # Relationships
    generation: Mapped["Generation"] = relationship("Generation", back_populates="generation_tags")
    tag: Mapped["Tag"] = relationship("Tag", back_populates="generation_tags")

    def __repr__(self):
        return f"<GenerationTag(generation_id={self.generation_id}, tag_id={self.tag_id})>"


class Analytics(Base):
    """Usage statistics."""
    __tablename__ = "analytics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    total_generations: Mapped[int] = mapped_column(Integer, default=0)
    successful_generations: Mapped[int] = mapped_column(Integer, default=0)
    avg_quality_score: Mapped[Optional[float]] = mapped_column(Float)
    avg_render_time: Mapped[Optional[float]] = mapped_column(Float)
    total_tokens_used: Mapped[Optional[int]] = mapped_column(Integer)
    total_cost_estimate: Mapped[Optional[float]] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    # Indexes
    __table_args__ = (
        Index('idx_analytics_date', 'date'),
    )

    def __repr__(self):
        return f"<Analytics(id={self.id}, date={self.date}, total_generations={self.total_generations})>"
