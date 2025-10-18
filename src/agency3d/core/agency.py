"""Main Agency3D class for high-level API."""

import logging
from typing import Optional

from agency3d.core.config import Config
from agency3d.core.models import SceneResult
from agency3d.orchestrator import WorkflowOrchestrator

logger = logging.getLogger(__name__)


class Agency3D:
    """Main class for the 3DAgency system."""

    def __init__(self, config: Optional[Config] = None):
        """
        Initialize Agency3D.

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

        # Initialize orchestrator
        self.orchestrator = WorkflowOrchestrator(self.config)

        logger.info("Agency3D initialized successfully")

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
