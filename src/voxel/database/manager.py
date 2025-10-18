"""
Database manager for Voxel.

This module provides the main database interface for creating, managing,
and querying the Voxel database.
"""

import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
from contextlib import contextmanager
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError

from .models import Base, Project, Generation, AgentExecution, Script, Render, Review, Tag, GenerationTag, Analytics
from .queries import DatabaseQueries

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Main database manager for Voxel."""

    def __init__(self, database_url: str = "sqlite:///database/voxel.db"):
        """
        Initialize database manager.

        Args:
            database_url: SQLAlchemy database URL
        """
        self.database_url = database_url
        self.engine = create_engine(
            database_url,
            echo=False,  # Set to True for SQL debugging
            pool_pre_ping=True,
        )
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.queries = DatabaseQueries(self)

    def create_tables(self) -> None:
        """Create all database tables."""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database tables created successfully")
        except SQLAlchemyError as e:
            logger.error(f"Failed to create database tables: {e}")
            raise

    def drop_tables(self) -> None:
        """Drop all database tables."""
        try:
            Base.metadata.drop_all(bind=self.engine)
            logger.info("Database tables dropped successfully")
        except SQLAlchemyError as e:
            logger.error(f"Failed to drop database tables: {e}")
            raise

    def check_connection(self) -> bool:
        """Check if database connection is working."""
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except SQLAlchemyError as e:
            logger.error(f"Database connection failed: {e}")
            return False

    @contextmanager
    def get_session(self) -> Session:
        """Get database session with automatic cleanup."""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()

    def get_session_sync(self) -> Session:
        """Get database session (caller responsible for cleanup)."""
        return self.SessionLocal()

    # Project management methods
    def create_project(self, name: str, description: Optional[str] = None, settings: Optional[Dict[str, Any]] = None) -> Project:
        """Create a new project."""
        with self.get_session() as session:
            project = Project(
                name=name,
                description=description,
                settings_json=settings
            )
            session.add(project)
            session.flush()  # Get the ID
            session.refresh(project)
            logger.info(f"Created project: {project.name} (ID: {project.id})")
            # Return the project object while still in session
            return project

    def get_project(self, project_id: int) -> Optional[Project]:
        """Get project by ID."""
        with self.get_session() as session:
            return session.query(Project).filter(Project.id == project_id).first()

    def get_projects(self, status: Optional[str] = None) -> List[Project]:
        """Get all projects, optionally filtered by status."""
        with self.get_session() as session:
            query = session.query(Project)
            if status:
                query = query.filter(Project.status == status)
            return query.order_by(Project.created_at.desc()).all()

    def update_project(self, project_id: int, **kwargs) -> Optional[Project]:
        """Update project fields."""
        with self.get_session() as session:
            project = session.query(Project).filter(Project.id == project_id).first()
            if not project:
                return None
            
            for key, value in kwargs.items():
                if hasattr(project, key):
                    setattr(project, key, value)
            
            session.flush()
            session.refresh(project)
            logger.info(f"Updated project: {project.name} (ID: {project.id})")
            return project

    # Generation management methods
    def create_generation(self, project_id: int, session_id: str, prompt: str) -> Generation:
        """Create a new generation."""
        with self.get_session() as session:
            generation = Generation(
                project_id=project_id,
                session_id=session_id,
                prompt=prompt
            )
            session.add(generation)
            session.flush()
            session.refresh(generation)
            logger.info(f"Created generation: {generation.id} for project {project_id}")
            return generation

    def get_generation(self, generation_id: int) -> Optional[Generation]:
        """Get generation by ID."""
        with self.get_session() as session:
            return session.query(Generation).filter(Generation.id == generation_id).first()

    def update_generation(self, generation_id: int, **kwargs) -> Optional[Generation]:
        """Update generation fields."""
        with self.get_session() as session:
            generation = session.query(Generation).filter(Generation.id == generation_id).first()
            if not generation:
                return None
            
            for key, value in kwargs.items():
                if hasattr(generation, key):
                    setattr(generation, key, value)
            
            session.flush()
            session.refresh(generation)
            return generation

    # Agent execution tracking
    def log_agent_execution(
        self,
        generation_id: int,
        agent_type: str,
        prompt: str,
        response_text: str,
        execution_time_ms: Optional[int] = None,
        token_count: Optional[int] = None,
        status: str = "success",
        error_message: Optional[str] = None,
        iteration_number: int = 1
    ) -> AgentExecution:
        """Log an agent execution."""
        with self.get_session() as session:
            execution = AgentExecution(
                generation_id=generation_id,
                agent_type=agent_type,
                iteration_number=iteration_number,
                prompt=prompt,
                response_text=response_text,
                execution_time_ms=execution_time_ms,
                token_count=token_count,
                status=status,
                error_message=error_message
            )
            session.add(execution)
            session.flush()
            session.refresh(execution)
            logger.debug(f"Logged agent execution: {agent_type} for generation {generation_id}")
            return execution

    # Script management
    def save_script(
        self,
        generation_id: int,
        agent_type: str,
        script_content: str,
        file_path: Optional[str] = None,
        iteration_number: int = 1
    ) -> Script:
        """Save a generated script."""
        with self.get_session() as session:
            script = Script(
                generation_id=generation_id,
                agent_type=agent_type,
                iteration_number=iteration_number,
                script_content=script_content,
                file_path=file_path
            )
            session.add(script)
            session.flush()
            session.refresh(script)
            logger.debug(f"Saved script: {agent_type} for generation {generation_id}")
            return script

    # Render tracking
    def log_render(
        self,
        generation_id: int,
        file_path: str,
        render_time_seconds: Optional[float] = None,
        samples: Optional[int] = None,
        resolution_x: Optional[int] = None,
        resolution_y: Optional[int] = None,
        engine: Optional[str] = None,
        iteration_number: int = 1
    ) -> Render:
        """Log a render output."""
        with self.get_session() as session:
            render = Render(
                generation_id=generation_id,
                iteration_number=iteration_number,
                file_path=file_path,
                render_time_seconds=render_time_seconds,
                samples=samples,
                resolution_x=resolution_x,
                resolution_y=resolution_y,
                engine=engine
            )
            session.add(render)
            session.flush()
            session.refresh(render)
            logger.debug(f"Logged render: {file_path} for generation {generation_id}")
            return render

    # Review tracking
    def save_review(
        self,
        generation_id: int,
        rating: int,
        feedback_text: str,
        suggestions: Optional[str] = None,
        iteration_number: int = 1
    ) -> Review:
        """Save reviewer feedback."""
        with self.get_session() as session:
            review = Review(
                generation_id=generation_id,
                iteration_number=iteration_number,
                rating=rating,
                feedback_text=feedback_text,
                suggestions=suggestions
            )
            session.add(review)
            session.flush()
            session.refresh(review)
            logger.debug(f"Saved review: rating {rating} for generation {generation_id}")
            return review

    # Tag management
    def create_tag(self, name: str, category: Optional[str] = None) -> Tag:
        """Create or get existing tag."""
        with self.get_session() as session:
            tag = session.query(Tag).filter(Tag.name == name).first()
            if not tag:
                tag = Tag(name=name, category=category)
                session.add(tag)
                session.flush()
                session.refresh(tag)
                logger.debug(f"Created tag: {name}")
            return tag

    def add_tag_to_generation(self, generation_id: int, tag_name: str, category: Optional[str] = None) -> GenerationTag:
        """Add tag to generation."""
        with self.get_session() as session:
            tag = self.create_tag(tag_name, category)
            
            # Check if relationship already exists
            existing = session.query(GenerationTag).filter(
                GenerationTag.generation_id == generation_id,
                GenerationTag.tag_id == tag.id
            ).first()
            
            if not existing:
                generation_tag = GenerationTag(
                    generation_id=generation_id,
                    tag_id=tag.id
                )
                session.add(generation_tag)
                session.flush()
                session.refresh(generation_tag)
                logger.debug(f"Added tag {tag_name} to generation {generation_id}")
                return generation_tag
            return existing

    # Analytics
    def update_analytics(self, date: str, **kwargs) -> Analytics:
        """Update or create analytics record."""
        with self.get_session() as session:
            analytics = session.query(Analytics).filter(Analytics.date == date).first()
            if not analytics:
                analytics = Analytics(date=date)
                session.add(analytics)
            
            for key, value in kwargs.items():
                if hasattr(analytics, key):
                    setattr(analytics, key, value)
            
            session.flush()
            session.refresh(analytics)
            return analytics

    def get_analytics(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[Analytics]:
        """Get analytics data."""
        with self.get_session() as session:
            query = session.query(Analytics)
            if start_date:
                query = query.filter(Analytics.date >= start_date)
            if end_date:
                query = query.filter(Analytics.date <= end_date)
            return query.order_by(Analytics.date.desc()).all()

    def close(self):
        """Close database connections."""
        self.engine.dispose()
        logger.info("Database connections closed")
