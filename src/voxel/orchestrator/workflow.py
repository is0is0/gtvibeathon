"""Workflow orchestrator for coordinating agents."""

import logging
from pathlib import Path
from typing import Optional, List, Dict, Any

from voxel.agents import (
    AnimationAgent,
    BuilderAgent,
    ConceptAgent,
    RenderAgent,
    ReviewerAgent,
    RiggingAgent,
    CompositingAgent,
    SequenceAgent,
)
from voxel.agents.hdr import HDRAgent

# Import TextureAgent directly to avoid circular import issues
try:
    from voxel.agents.texture import TextureAgent
except ImportError:
    TextureAgent = None
from voxel.blender import BlenderExecutor, ScriptManager
from voxel.core.agent import AgentConfig
from voxel.core.config import Config
from voxel.core.models import ReviewFeedback, SceneResult, AgentRole
from voxel.core.agent_context import AgentContext, ContextType
from voxel.core.error_recovery import ErrorRecoverySystem, ErrorContext, ErrorType
from voxel.core.performance import PerformanceOptimizer

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

        # Create shared context for agent collaboration
        self.shared_context = AgentContext()

        # Initialize error recovery system
        self.error_recovery = ErrorRecoverySystem()
        self._setup_error_recovery()

        # Initialize performance optimizer
        self.performance_optimizer = PerformanceOptimizer(
            cache_size=1000,
            max_workers=4
        )

        # Progress callback
        self.progress_callback = None

        # Initialize agents with shared context
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

        self.concept_agent = ConceptAgent(agent_config, self.shared_context)
        self.builder_agent = BuilderAgent(agent_config, self.shared_context)
        self.texture_agent = TextureAgent(agent_config, self.shared_context) if TextureAgent else None
        self.hdr_agent = HDRAgent(agent_config, self.shared_context)  # HDR environment/lighting
        self.render_agent = RenderAgent(agent_config, self.shared_context)
        self.animation_agent = AnimationAgent(agent_config, self.shared_context)
        self.reviewer_agent = ReviewerAgent(agent_config, self.shared_context) if config.enable_reviewer else None

        # New enhancement agents
        self.rigging_agent = RiggingAgent(agent_config, self.shared_context)
        self.compositing_agent = CompositingAgent(agent_config, self.shared_context)
        self.sequence_agent = SequenceAgent(agent_config, self.shared_context)
        
        # Enable real-time updates for all agents
        self._enable_realtime_updates()

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
            # Enable agent collaboration
            self._enable_agent_collaboration(prompt)
            
            iteration = 0
            max_iterations = self.config.max_iterations if self.config.auto_refine else 1

            while iteration < max_iterations:
                iteration += 1
                logger.info(f"Starting iteration {iteration}/{max_iterations}")

                # Step 1: Generate concept with collaboration
                concept_response = self._generate_concept(prompt, iteration)
                result.concept = concept_response.content
                result.agent_responses.append(concept_response)
                
                # Share concept insights with other agents
                self.concept_agent.add_context(
                    ContextType.FEEDBACK,
                    f"Scene concept: {concept_response.content[:200]}...",
                    metadata={"iteration": iteration, "type": "concept"}
                )

                # Save concept
                self.script_manager.save_concept(concept_response.content, session_dir)

                # Initialize script paths
                builder_script_path = None
                texture_script_path = None
                render_script_path = None
                animation_script_path = None

                # Step 2: Generate builder script with collaboration
                enhanced_concept = self._enhance_agent_prompts_with_context(
                    self.builder_agent, concept_response.content, ContextType.GEOMETRY
                )
                builder_response = self._generate_builder_script(enhanced_concept)
                result.agent_responses.append(builder_response)
                
                # Share builder insights
                if builder_response.script:
                    self.builder_agent.add_context(
                        ContextType.GEOMETRY,
                        f"Created geometry: {self._extract_geometry_info(builder_response.script)}",
                        metadata={"iteration": iteration, "script_length": len(builder_response.script)}
                    )

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

                # Step 4: Generate HDR environment script
                hdr_response = self._generate_hdr_script(concept_response.content)
                result.agent_responses.append(hdr_response)

                if hdr_response.script:
                    hdr_script_path = self.script_manager.save_script(
                        hdr_response.script,
                        f"03_hdr_iter{iteration}",
                        session_dir,
                    )
                    result.scripts.append(hdr_script_path)

                # Step 5: Generate render script
                render_response = self._generate_render_script(concept_response.content)
                result.agent_responses.append(render_response)

                if render_response.script:
                    render_script_path = self.script_manager.save_script(
                        render_response.script,
                        f"04_render_iter{iteration}",
                        session_dir,
                    )
                    result.scripts.append(render_script_path)

                # Step 6: Generate animation script
                animation_response = self._generate_animation_script(
                    concept_response.content, builder_response.script or ""
                )
                result.agent_responses.append(animation_response)

                animation_script_path = None
                if animation_response.script:
                    animation_script_path = self.script_manager.save_script(
                        animation_response.script,
                        f"05_animation_iter{iteration}",
                        session_dir,
                    )
                    result.scripts.append(animation_script_path)

                # Step 7: Combine and execute scripts
                scripts_to_combine = [builder_script_path, texture_script_path, hdr_script_path, render_script_path]
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

                # Step 8: Render the scene
                blend_file = session_dir / "scene.blend"
                output_image = session_dir / "renders" / f"render_iter{iteration}.png"

                # Save the scene first
                save_script = self._create_save_script(blend_file)
                save_script_path = self.script_manager.save_script(
                    save_script,
                    f"06_save_iter{iteration}",
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

                # Step 9: Review (if enabled)
                should_refine = False
                if self.reviewer_agent and iteration < max_iterations:
                    review_response = self._review_scene(
                        prompt,
                        concept_response.content,
                        [builder_response, texture_response, hdr_response, render_response, animation_response],
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
                if self.texture_agent is not None:
                    self.texture_agent.reset()
                self.render_agent.reset()
                if self.animation_agent is not None:
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
        self._emit_progress("concept_generation", "ConceptAgent", "Analyzing prompt and creating scene concept...")

        if iteration > 1:
            message = f"Refine the previous concept based on feedback. Original prompt: {prompt}"
        else:
            message = f"Create a detailed 3D scene concept for: {prompt}"

        return self.concept_agent.generate_response(message)

    def _emit_progress(self, stage: str, agent: str, message: str) -> None:
        """Emit progress update if callback is set."""
        if self.progress_callback:
            try:
                self.progress_callback(stage, agent, message)
            except Exception as e:
                logger.warning(f"Progress callback error: {e}")

    def _generate_builder_script(self, concept: str) -> any:
        """Generate builder script."""
        logger.info("Generating builder script...")
        self._emit_progress("geometry_creation", "BuilderAgent", "Creating 3D geometry and models...")

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
        self._emit_progress("material_creation", "TextureAgent", "Creating materials and shaders...")

        message = f"""Based on this scene concept and builder script, write a Blender Python script to create and apply materials:

CONCEPT:
{concept}

BUILDER SCRIPT (for object names):
{builder_script}

Create appropriate materials for all objects, considering the mood and style from the concept.
"""

        if self.texture_agent is None:
            # Fallback: create a simple texture script
            from voxel.core.models import AgentResponse, AgentRole
            from datetime import datetime
            
            texture_script = f"""
# Basic texture setup for the house scene
import bpy

# Create materials
house_material = bpy.data.materials.new(name="House_Material")
house_material.use_nodes = True
house_material.node_tree.nodes.clear()

# Add Principled BSDF
bsdf = house_material.node_tree.nodes.new(type='ShaderNodeBsdfPrincipled')
output = house_material.node_tree.nodes.new(type='ShaderNodeOutputMaterial')
house_material.node_tree.links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

# Set material properties
bsdf.inputs['Base Color'].default_value = (0.8, 0.6, 0.4, 1.0)  # Beige color
bsdf.inputs['Roughness'].default_value = 0.6
bsdf.inputs['Metallic'].default_value = 0.0

# Apply to house objects
for obj in bpy.data.objects:
    if 'House' in obj.name or 'Roof' in obj.name:
        if obj.data.materials:
            obj.data.materials[0] = house_material
        else:
            obj.data.materials.append(house_material)

# Create grass material
grass_material = bpy.data.materials.new(name="Grass_Material")
grass_material.use_nodes = True
grass_material.node_tree.nodes.clear()

bsdf_grass = grass_material.node_tree.nodes.new(type='ShaderNodeBsdfPrincipled')
output_grass = grass_material.node_tree.nodes.new(type='ShaderNodeOutputMaterial')
grass_material.node_tree.links.new(bsdf_grass.outputs['BSDF'], output_grass.inputs['Surface'])

bsdf_grass.inputs['Base Color'].default_value = (0.2, 0.8, 0.2, 1.0)  # Green color
bsdf_grass.inputs['Roughness'].default_value = 0.8

# Apply to terrain
for obj in bpy.data.objects:
    if 'Terrain' in obj.name or 'Grass' in obj.name:
        if obj.data.materials:
            obj.data.materials[0] = grass_material
        else:
            obj.data.materials.append(grass_material)
"""
            
            return AgentResponse(
                agent_role=AgentRole.TEXTURE,
                content=texture_script,
                script=texture_script,
                reasoning="Applied basic materials to house and grass objects",
                metadata={'script_type': 'texture'},
                timestamp=datetime.now()
            )
        
        return self.texture_agent.generate_response(message)

    def _generate_hdr_script(self, concept: str) -> any:
        """Generate HDR environment script."""
        logger.info("Generating HDR environment script...")
        self._emit_progress("hdr_setup", "HDRAgent", "Creating HDR environment and world lighting...")

        message = f"""Based on this scene concept, write a Blender Python script to create an HDR environment:

{concept}

Create:
- Realistic HDR sky or environment lighting
- Appropriate atmosphere for the scene (outdoor/indoor/studio/night/etc.)
- Proper color temperature and lighting mood
- World background that complements the scene
"""

        return self.hdr_agent.generate_response(message)

    def _generate_render_script(self, concept: str) -> any:
        """Generate render setup script."""
        logger.info("Generating render script...")
        self._emit_progress("render_setup", "RenderAgent", "Setting up camera and lighting...")

        message = f"""Based on this scene concept, write a Blender Python script to set up the camera and lighting:

{concept}

Configure:
- Camera position and angle for good composition
- Appropriate three-point lighting for the scene mood
- Render settings (quality, denoising, etc.)
"""

        return self.render_agent.generate_response(message)

    def _generate_animation_script(self, concept: str, builder_script: str) -> any:
        """Generate animation script."""
        logger.info("Generating animation script...")
        self._emit_progress("animation_creation", "AnimationAgent", "Creating animations and keyframes...")

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
    
    def _enable_agent_collaboration(self, prompt: str) -> None:
        """Enable agent collaboration based on prompt analysis."""
        # Clear previous context for new scene
        self.shared_context.clear_context()
        
        # Analyze prompt for collaboration needs
        collaboration_needs = self._analyze_collaboration_needs(prompt)
        
        # Set up context based on needs
        for need in collaboration_needs:
            self.shared_context.add_context(
                context_type=need,
                source_agent=AgentRole.CONCEPT,
                content=f"Scene requires {need.value} capabilities",
                metadata={"prompt_analysis": True},
                confidence=0.8,
                tags={"collaboration_setup"}
            )
        
        logger.info(f"Enabled collaboration for: {[n.value for n in collaboration_needs]}")
    
    def _analyze_collaboration_needs(self, prompt: str) -> list[ContextType]:
        """Analyze prompt to determine what collaboration is needed."""
        needs = []
        prompt_lower = prompt.lower()
        
        # Check for rigging needs
        rigging_keywords = ['character', 'human', 'person', 'creature', 'animal', 'rig', 'armature', 'bone']
        if any(keyword in prompt_lower for keyword in rigging_keywords):
            needs.append(ContextType.RIGGING)
        
        # Check for compositing needs
        compositing_keywords = ['cinematic', 'film', 'movie', 'dramatic', 'atmospheric', 'effects', 'post-processing']
        if any(keyword in prompt_lower for keyword in compositing_keywords):
            needs.append(ContextType.COMPOSITING)
        
        # Check for sequence needs
        sequence_keywords = ['video', 'sequence', 'trailer', 'animation', 'multi-shot', 'cinematic']
        if any(keyword in prompt_lower for keyword in sequence_keywords):
            needs.append(ContextType.SEQUENCE)
        
        # Always include basic context types
        needs.extend([ContextType.GEOMETRY, ContextType.MATERIALS, ContextType.LIGHTING, ContextType.ANIMATION])
        
        return list(set(needs))  # Remove duplicates
    
    def _enhance_agent_prompts_with_context(self, agent, base_prompt: str, context_type: ContextType) -> str:
        """Enhance agent prompts with relevant context from other agents."""
        return agent.get_enhanced_prompt(base_prompt, context_type)
    
    def _share_agent_insights(self, agent, insights: dict) -> None:
        """Share insights from an agent with other agents."""
        agent.set_agent_insights(insights)
        agent.add_collaboration_event("insights_shared", {"insights_count": len(insights)})
    
    def _get_collaboration_summary(self) -> str:
        """Get a summary of agent collaboration."""
        return self.shared_context.get_collaboration_summary()
    
    def _get_context_stats(self) -> dict:
        """Get statistics about agent collaboration."""
        return self.shared_context.get_context_stats()
    
    def _extract_geometry_info(self, script: str) -> str:
        """Extract geometry information from a builder script."""
        # Simple extraction of geometry info
        lines = script.split('\n')
        geometry_info = []
        
        for line in lines:
            if 'bpy.ops.mesh.primitive_' in line or 'bpy.ops.object.' in line:
                geometry_info.append(line.strip())
            if len(geometry_info) >= 3:  # Limit to first 3 objects
                break
        
        return '; '.join(geometry_info) if geometry_info else "No geometry detected"
    
    def _enable_realtime_updates(self) -> None:
        """Enable real-time context updates for all agents."""
        agents = [
            self.concept_agent,
            self.builder_agent,
            self.texture_agent,
            self.hdr_agent,
            self.render_agent,
            self.animation_agent,
            self.rigging_agent,
            self.compositing_agent,
            self.sequence_agent
        ]

        if self.reviewer_agent:
            agents.append(self.reviewer_agent)

        for agent in agents:
            if agent is not None:
                agent.setup_realtime_updates()

        logger.info("Enabled real-time updates for all agents")
    
    def _simulate_realtime_collaboration(self, prompt: str) -> None:
        """Simulate real-time collaboration by showing how agents respond to each other's changes."""
        logger.info("Simulating real-time collaboration...")
        
        # Example: BuilderAgent creates geometry
        self.builder_agent.add_context(
            ContextType.GEOMETRY,
            "Created a humanoid character mesh with 1000 vertices"
        )
        
        # TextureAgent should immediately get this update
        # RiggingAgent should immediately get this update
        # AnimationAgent should immediately get this update
        
        # Example: RiggingAgent creates armature
        self.rigging_agent.add_context(
            ContextType.RIGGING,
            "Created armature with 15 bones for humanoid character"
        )
        
        # AnimationAgent should immediately get this update
        # TextureAgent should be aware of rigging constraints
        
        logger.info("Real-time collaboration simulation complete")
    
    def _setup_error_recovery(self) -> None:
        """Set up error recovery system with fallback agents."""
        # Set up fallback agents
        self.error_recovery.set_fallback_agent("RiggingAgent", "BuilderAgent")
        self.error_recovery.set_fallback_agent("CompositingAgent", "RenderAgent")
        self.error_recovery.set_fallback_agent("SequenceAgent", "AnimationAgent")
        
        logger.info("Error recovery system configured")
    
    def _handle_agent_error(self, agent, error_message: str, context: str = None) -> bool:
        """Handle agent errors with recovery strategies."""
        error_context = ErrorContext(
            error_type=ErrorType.AGENT_FAILURE,
            error_message=error_message,
            agent_role=agent.role.value if hasattr(agent, 'role') else None,
            script_content=context
        )
        
        success, result = self.error_recovery.handle_error(error_context)
        
        if success:
            logger.info(f"Error recovery successful: {result}")
            return True
        else:
            logger.error(f"Error recovery failed for agent: {agent.role.value if hasattr(agent, 'role') else 'unknown'}")
            return False
    
    def _handle_script_error(self, script_content: str, error_message: str) -> str:
        """Handle script execution errors with recovery strategies."""
        error_context = ErrorContext(
            error_type=ErrorType.SCRIPT_EXECUTION,
            error_message=error_message,
            script_content=script_content
        )
        
        success, result = self.error_recovery.handle_error(error_context)
        
        if success and "simplified_script" in result:
            logger.info("Using simplified script after error recovery")
            return result["simplified_script"]
        else:
            logger.error("Script error recovery failed")
            return script_content  # Return original script
    
    def _handle_context_error(self, context_type: str, error_message: str) -> bool:
        """Handle context update errors with recovery strategies."""
        error_context = ErrorContext(
            error_type=ErrorType.CONTEXT_UPDATE,
            error_message=error_message
        )
        
        success, result = self.error_recovery.handle_error(error_context)
        
        if success:
            logger.info(f"Context error recovery successful: {result}")
            return True
        else:
            logger.error("Context error recovery failed")
            return False
    
    def get_error_statistics(self) -> dict:
        """Get error recovery statistics."""
        return self.error_recovery.get_error_statistics()
    
    def get_recent_errors(self, limit: int = 10) -> list:
        """Get recent errors for debugging."""
        return self.error_recovery.get_recent_errors(limit)
    
    async def _optimized_agent_generation(self, agents: List[Any], method: str, *args, **kwargs) -> List[Any]:
        """Execute agent generation with performance optimization."""
        # Try to get cached results first
        cached_results = []
        uncached_agents = []
        
        for i, agent in enumerate(agents):
            try:
                result = await self.performance_optimizer.cached_agent_call(agent, method, *args, **kwargs)
                cached_results.append((i, result))
            except:
                uncached_agents.append((i, agent))
        
        # Execute uncached agents in parallel
        if uncached_agents:
            tasks = [(getattr(agent, method), args, kwargs) for _, agent in uncached_agents]
            uncached_results = await self.performance_optimizer.execute_agents_async(
                [agent for _, agent in uncached_agents], method, *args, **kwargs
            )
            
            # Combine results
            for (original_index, _), result in zip(uncached_agents, uncached_results):
                cached_results.append((original_index, result))
        
        # Sort results by original index
        cached_results.sort(key=lambda x: x[0])
        return [result for _, result in cached_results]
    
    def _cache_script_if_successful(self, prompt: str, script: str, success: bool) -> None:
        """Cache script if generation was successful."""
        if success and script:
            self.performance_optimizer.cache_script(prompt, script)
            logger.debug(f"Cached successful script for prompt: {prompt[:50]}...")
    
    def _get_cached_script(self, prompt: str) -> Optional[str]:
        """Get cached script if available."""
        cached_script = self.performance_optimizer.get_cached_script(prompt)
        if cached_script:
            logger.debug(f"Using cached script for prompt: {prompt[:50]}...")
        return cached_script
    
    def _optimize_parallel_agents(self, agents: List[Any], method: str, *args, **kwargs) -> List[Any]:
        """Execute multiple agents in parallel for better performance."""
        return self.performance_optimizer.execute_agents_parallel(agents, method, *args, **kwargs)
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get comprehensive performance statistics."""
        return self.performance_optimizer.get_performance_stats()
    
    def clear_performance_caches(self) -> None:
        """Clear all performance caches."""
        self.performance_optimizer.clear_all_caches()
        logger.info("Performance caches cleared")
    
    def shutdown_performance_optimizer(self) -> None:
        """Shutdown the performance optimizer."""
        self.performance_optimizer.shutdown()
        logger.info("Performance optimizer shutdown")
