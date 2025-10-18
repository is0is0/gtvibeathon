"""Main Voxel class for high-level API."""

import logging
from typing import Optional, List, Dict, Any, Callable

from voxel.core.config import Config
from voxel.core.models import SceneResult
from voxel.orchestrator import WorkflowOrchestrator
from voxel.database import DatabaseManager, DatabaseQueries
from voxel.database.models import Project

logger = logging.getLogger(__name__)


class Voxel:
    """Main class for the Voxel system."""

    def __init__(self, config: Optional[Config] = None):
        """
        Initialize Voxel.

        Args:
            config: Configuration object (will create default if None)
        """
        self.config = config or Config()

        # Validate configuration
        try:
            self.config.validate_api_keys()
            self.config.validate_paths()
        except ValueError as e:
            logger.error(f"Configuration error: {e}")
            raise

        # Initialize database
        self.db_manager = DatabaseManager(self.config.database_url)
        self.db_queries = DatabaseQueries(self.db_manager)
        
        # Create database tables if they don't exist
        self.db_manager.create_tables()

        # Initialize orchestrator
        self.orchestrator = WorkflowOrchestrator(self.config)

        # Agent configuration
        self.active_agents = None
        self.progress_callback = None
        self.context_data = []

        logger.info("Voxel initialized successfully")

    def configure_agents(self, agent_ids: List[str]) -> None:
        """
        Configure which agents to use for generation.

        Args:
            agent_ids: List of agent IDs to activate
        """
        self.active_agents = agent_ids
        logger.info(f"Configured agents: {', '.join(agent_ids)}")

    def add_context(self, context_data: Dict[str, Any]) -> None:
        """
        Add context data from uploaded files.

        Args:
            context_data: Context information from files
        """
        self.context_data.append(context_data)
        logger.info(f"Added context: {context_data.get('type', 'unknown')}")

    def set_progress_callback(self, callback: Callable[[str, str, str], None]) -> None:
        """
        Set a callback function for progress updates.

        Args:
            callback: Function that takes (stage, agent, message)
        """
        self.progress_callback = callback
        self.orchestrator.progress_callback = callback

    def create_scene(
        self,
        prompt: str,
        session_name: Optional[str] = None,
        enable_review: Optional[bool] = None,
        max_iterations: Optional[int] = None,
    ) -> SceneResult:
        """
        Create a 3D scene from a text prompt.

        Args:
            prompt: Natural language description of the scene
            session_name: Optional name for this generation session
            enable_review: Override config to enable/disable reviewer
            max_iterations: Override config for max refinement iterations

        Returns:
            SceneResult with all generation details

        Example:
            >>> agency = Agency3D()
            >>> result = agency.create_scene("a cozy cyberpunk cafe at sunset")
            >>> print(f"Render saved to: {result.output_path}")
        """
        # Override config if parameters provided
        if enable_review is not None:
            original_review = self.config.enable_reviewer
            self.config.enable_reviewer = enable_review

        if max_iterations is not None:
            original_iterations = self.config.max_iterations
            self.config.max_iterations = max_iterations

        try:
            # Execute workflow
            result = self.orchestrator.execute_workflow(prompt, session_name)
            return result

        finally:
            # Restore original config
            if enable_review is not None:
                self.config.enable_reviewer = original_review
            if max_iterations is not None:
                self.config.max_iterations = original_iterations

    # Database query methods
    def get_projects(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all projects, optionally filtered by status."""
        projects = self.db_manager.get_projects(status)
        return [
            {
                "id": p.id,
                "name": p.name,
                "description": p.description,
                "status": p.status.value,
                "created_at": p.created_at.isoformat(),
                "updated_at": p.updated_at.isoformat(),
                "settings": p.settings_json
            }
            for p in projects
        ]

    def get_project_history(self, project_id: int) -> List[Dict[str, Any]]:
        """Get generation history for a project."""
        generations = self.db_queries.get_project_history(project_id)
        return [
            {
                "id": g.id,
                "session_id": g.session_id,
                "prompt": g.prompt,
                "status": g.status.value,
                "created_at": g.created_at.isoformat(),
                "completed_at": g.completed_at.isoformat() if g.completed_at else None,
                "quality_score": g.quality_score,
                "iteration_count": g.iteration_count,
                "output_path": g.output_path
            }
            for g in generations
        ]

    def get_generation_details(self, generation_id: int) -> Dict[str, Any]:
        """Get detailed information about a generation."""
        return self.db_queries.get_generation_details(generation_id)

    def get_system_analytics(self, days: int = 30) -> Dict[str, Any]:
        """Get system-wide analytics."""
        return self.db_queries.get_system_analytics(days)

    def get_project_statistics(self, project_id: int) -> Dict[str, Any]:
        """Get statistics for a specific project."""
        return self.db_queries.get_project_statistics(project_id)

    def search_generations(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Search generations by prompt text."""
        generations = self.db_queries.search_generations(query, limit)
        return [
            {
                "id": g.id,
                "project_id": g.project_id,
                "prompt": g.prompt,
                "status": g.status.value,
                "created_at": g.created_at.isoformat(),
                "quality_score": g.quality_score
            }
            for g in generations
        ]

    def create_project(self, name: str, description: Optional[str] = None, settings: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create a new project."""
        with self.db_manager.get_session() as session:
            project = Project(
                name=name,
                description=description,
                settings_json=settings
            )
            session.add(project)
            session.flush()  # Get the ID
            session.refresh(project)
            
            # Return project data while session is active
            return {
                "id": project.id,
                "name": project.name,
                "description": project.description,
                "status": project.status.value,
                "created_at": project.created_at.isoformat(),
                "settings": project.settings_json
            }

    def get_agent_performance(self, agent_type: str, days: int = 30) -> Dict[str, Any]:
        """Get performance metrics for a specific agent type."""
        return self.db_queries.get_agent_performance(agent_type, days)

    def get_quality_trends(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get quality score trends over time."""
        return self.db_queries.get_quality_trends(days)

    def get_failed_generations(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recently failed generations for debugging."""
        generations = self.db_queries.get_failed_generations(limit)
        return [
            {
                "id": g.id,
                "project_id": g.project_id,
                "prompt": g.prompt,
                "status": g.status.value,
                "created_at": g.created_at.isoformat(),
                "error_message": getattr(g, 'error_message', None)
            }
            for g in generations
        ]

    def close(self):
        """Close database connections and cleanup."""
        if hasattr(self, 'db_manager'):
            self.db_manager.close()
        logger.info("Voxel closed successfully")
