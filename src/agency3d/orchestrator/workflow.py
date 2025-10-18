"""Workflow orchestrator for coordinating agents."""

import logging
from pathlib import Path
from typing import Optional

from agency3d.agents import (
    AnimationAgent,
    BuilderAgent,
    ConceptAgent,
    RenderAgent,
    ReviewerAgent,
    TextureAgent,
)
from agency3d.blender import BlenderExecutor, ScriptManager
from agency3d.core.agent import AgentConfig
from agency3d.core.config import Config
from agency3d.core.models import ReviewFeedback, SceneResult

logger = logging.getLogger(__name__)


class WorkflowOrchestrator:
    """Orchestrates the multi-agent workflow for scene generation."""

    def __init__(self, config: Config):
        """
        Initialize the workflow orchestrator.

        Args:
            config: Application configuration
        """
        self.config = config
        self.script_manager = ScriptManager(config.output_dir)
        self.blender_executor = BlenderExecutor(config)

        # Initialize agents
        agent_config = AgentConfig(
            provider=config.ai_provider,
            model=config.ai_model,
            temperature=config.agent_temperature,
            max_tokens=config.agent_max_tokens,
            api_key=(
                config.anthropic_api_key
                if config.ai_provider == "anthropic"
                else config.openai_api_key
            ),
        )

        self.concept_agent = ConceptAgent(agent_config)
        self.builder_agent = BuilderAgent(agent_config)
        self.texture_agent = TextureAgent(agent_config)
        self.render_agent = RenderAgent(agent_config)
        self.animation_agent = AnimationAgent(agent_config)
        self.reviewer_agent = ReviewerAgent(agent_config) if config.enable_reviewer else None

    def execute_workflow(
        self,
        prompt: str,
        session_name: Optional[str] = None,
    ) -> SceneResult:
        """
        Execute the complete workflow to generate a scene.

        Args:
            prompt: User's scene description
            session_name: Optional session name

        Returns:
            SceneResult with all generation details
        """
        logger.info(f"Starting workflow for prompt: {prompt}")

        # Create session directory
        session_dir = self.script_manager.create_session_dir(session_name)

        result = SceneResult(
            success=False,
            prompt=prompt,
        )

        try:
            iteration = 0
            max_iterations = self.config.max_iterations if self.config.auto_refine else 1

            while iteration < max_iterations:
                iteration += 1
                logger.info(f"Starting iteration {iteration}/{max_iterations}")

                # Step 1: Generate concept
                concept_response = self._generate_concept(prompt, iteration)
                result.concept = concept_response.content
                result.agent_responses.append(concept_response)

                # Save concept
                self.script_manager.save_concept(concept_response.content, session_dir)

                # Step 2: Generate builder script
                builder_response = self._generate_builder_script(concept_response.content)
                result.agent_responses.append(builder_response)

                if builder_response.script:
                    builder_script_path = self.script_manager.save_script(
                        builder_response.script,
                        f"01_builder_iter{iteration}",
                        session_dir,
                    )
                    result.scripts.append(builder_script_path)

                # Step 3: Generate texture script
                texture_response = self._generate_texture_script(
                    concept_response.content, builder_response.script or ""
                )
                result.agent_responses.append(texture_response)

                if texture_response.script:
                    texture_script_path = self.script_manager.save_script(
                        texture_response.script,
                        f"02_texture_iter{iteration}",
                        session_dir,
                    )
                    result.scripts.append(texture_script_path)

                # Step 4: Generate render script
                render_response = self._generate_render_script(concept_response.content)
                result.agent_responses.append(render_response)

                if render_response.script:
                    render_script_path = self.script_manager.save_script(
                        render_response.script,
                        f"03_render_iter{iteration}",
                        session_dir,
                    )
                    result.scripts.append(render_script_path)

                # Step 5: Generate animation script
                animation_response = self._generate_animation_script(
                    concept_response.content, builder_response.script or ""
                )
                result.agent_responses.append(animation_response)

                animation_script_path = None
                if animation_response.script:
                    animation_script_path = self.script_manager.save_script(
                        animation_response.script,
                        f"04_animation_iter{iteration}",
                        session_dir,
                    )
                    result.scripts.append(animation_script_path)

                # Step 6: Combine and execute scripts
                scripts_to_combine = [builder_script_path, texture_script_path, render_script_path]
                if animation_script_path:
                    scripts_to_combine.append(animation_script_path)

                combined_script = self.script_manager.combine_scripts(
                    scripts_to_combine,
                    f"combined_iter{iteration}",
                    session_dir,
                )

                # Execute the combined script
                exec_result = self.blender_executor.execute_script(combined_script)

                if not exec_result.success:
                    result.error = f"Script execution failed: {exec_result.stderr}"
                    logger.error(result.error)
                    break

                # Step 7: Render the scene
                blend_file = session_dir / "scene.blend"
                output_image = session_dir / "renders" / f"render_iter{iteration}.png"

                # Save the scene first
                save_script = self._create_save_script(blend_file)
                save_script_path = self.script_manager.save_script(
                    save_script,
                    f"05_save_iter{iteration}",
                    session_dir,
                )

                save_result = self.blender_executor.execute_script(save_script_path)

                if not save_result.success:
                    logger.warning(f"Failed to save blend file: {save_result.stderr}")

                # Now render
                if blend_file.exists():
                    render_result = self.blender_executor.render_scene(
                        blend_file,
                        output_image,
                        samples=self.config.render_samples,
                        engine=self.config.render_engine,
                    )

                    result.render_time += render_result.execution_time

                    if render_result.success:
                        result.output_path = output_image
                        logger.info(f"Render saved to: {output_image}")
                    else:
                        result.error = f"Render failed: {render_result.stderr}"
                        logger.error(result.error)
                        break

                # Step 8: Review (if enabled)
                should_refine = False
                if self.reviewer_agent and iteration < max_iterations:
                    review_response = self._review_scene(
                        prompt,
                        concept_response.content,
                        [builder_response, texture_response, render_response, animation_response],
                    )
                    result.agent_responses.append(review_response)

                    feedback = ReviewFeedback(**review_response.metadata.get("feedback", {}))
                    should_refine = feedback.should_refine and self.config.auto_refine

                    logger.info(
                        f"Review rating: {feedback.rating}/10, "
                        f"Refine: {should_refine}"
                    )

                if not should_refine:
                    logger.info("Review satisfactory or max iterations reached")
                    break

                # Reset agents for next iteration
                self.concept_agent.reset()
                self.builder_agent.reset()
                self.texture_agent.reset()
                self.render_agent.reset()
                self.animation_agent.reset()

            result.success = result.output_path is not None
            result.iterations = iteration

            # Save metadata
            metadata = {
                "prompt": prompt,
                "iterations": iteration,
                "success": result.success,
                "config": {
                    "ai_provider": self.config.ai_provider,
                    "ai_model": self.config.ai_model,
                    "render_samples": self.config.render_samples,
                    "render_engine": self.config.render_engine,
                },
            }
            self.script_manager.save_metadata(metadata, session_dir)

            logger.info(
                f"Workflow completed: success={result.success}, "
                f"iterations={iteration}"
            )

        except Exception as e:
            logger.error(f"Workflow error: {e}", exc_info=True)
            result.error = str(e)

        return result

    def _generate_concept(self, prompt: str, iteration: int) -> any:
        """Generate scene concept."""
        logger.info("Generating scene concept...")

        if iteration > 1:
            message = f"Refine the previous concept based on feedback. Original prompt: {prompt}"
        else:
            message = f"Create a detailed 3D scene concept for: {prompt}"

        return self.concept_agent.generate_response(message)

    def _generate_builder_script(self, concept: str) -> any:
        """Generate builder script."""
        logger.info("Generating builder script...")

        message = f"""Based on this scene concept, write a Blender Python script to create the 3D geometry:

{concept}

Remember to:
- Clear the scene at the start
- Create all objects described in the concept
- Use appropriate scales and positions
- Organize objects in collections
"""

        return self.builder_agent.generate_response(message)

    def _generate_texture_script(self, concept: str, builder_script: str) -> any:
        """Generate texture script."""
        logger.info("Generating texture script...")

        message = f"""Based on this scene concept and builder script, write a Blender Python script to create and apply materials:

CONCEPT:
{concept}

BUILDER SCRIPT (for object names):
{builder_script}

Create appropriate materials for all objects, considering the mood and style from the concept.
"""

        return self.texture_agent.generate_response(message)

    def _generate_render_script(self, concept: str) -> any:
        """Generate render setup script."""
        logger.info("Generating render script...")

        message = f"""Based on this scene concept, write a Blender Python script to set up the camera and lighting:

{concept}

Configure:
- Camera position and angle for good composition
- Appropriate lighting for the scene mood
- Render settings
"""

        return self.render_agent.generate_response(message)

    def _generate_animation_script(self, concept: str, builder_script: str) -> any:
        """Generate animation script."""
        logger.info("Generating animation script...")

        message = f"""Based on this scene concept and builder script, write a Blender Python script to create animations:

CONCEPT:
{concept}

BUILDER SCRIPT (for object names):
{builder_script}

Create cinematic animations with:
- Multiple animated objects (5-10+ objects)
- Varied animation types (location, rotation, scale)
- Camera animation for dynamic shots
- Material animations where appropriate
- Proper easing for natural motion
- Frame range of 120-250 frames
"""

        return self.animation_agent.generate_response(message)

    def _review_scene(self, prompt: str, concept: str, agent_responses: list) -> any:
        """Review the generated scene."""
        logger.info("Reviewing scene...")

        scripts_summary = "\n\n".join(
            [
                f"=== {resp.agent_role.value.upper()} ===\n{resp.script or resp.content[:500]}"
                for resp in agent_responses
            ]
        )

        message = f"""Review this 3D scene generation:

ORIGINAL PROMPT: {prompt}

CONCEPT:
{concept}

GENERATED SCRIPTS:
{scripts_summary}

Provide your review following the specified format.
"""

        return self.reviewer_agent.generate_response(message)

    def _create_save_script(self, blend_file: Path) -> str:
        """Create a script to save the Blender file."""
        return f"""
import bpy

# Save the blend file
bpy.ops.wm.save_as_mainfile(filepath="{blend_file}")
print(f"Saved: {blend_file}")
"""
