"""
Scene Orchestrator - Main Coordinator for Multi-Subsystem Scene Generation
===========================================================================

This module coordinates all subsystems to generate complete 3D scenes:
- Prompt interpretation and scene planning
- VoxelWeaver backend integration
- Texture synthesis and material creation
- Intelligent lighting setup
- Spatial validation and physics checking
- Render orchestration and optimization
- Asset management and caching

The orchestrator manages the entire workflow from prompt to final render.

Author: VoxelWeaver Team
Version: 1.0.0
"""

import asyncio
import time
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
import json

from utils.logger import get_logger
from voxel_weaver.voxel_weaver_core import (
    VoxelWeaverIntegration,
    SceneGenerationRequest,
    SceneGenerationResult,
    SceneStyle,
    GenerationQuality
)
from subsystems.prompt_interpreter import PromptInterpreter, SceneGraph
from subsystems.texture_synth import TextureSynthesizer, TextureRequest
from subsystems.lighting_ai import LightingAI, LightingSetup
from subsystems.spatial_validator import SpatialValidator, ValidationResult
from subsystems.render_director import RenderDirector, RenderPlan
from subsystems.asset_registry import AssetRegistry
from utils.blender_api_tools import BlenderAPIWrapper

logger = get_logger(__name__)


class WorkflowStage(Enum):
    """Stages in the scene generation workflow."""
    INITIALIZATION = "initialization"
    PROMPT_ANALYSIS = "prompt_analysis"
    SCENE_GENERATION = "scene_generation"
    TEXTURE_SYNTHESIS = "texture_synthesis"
    LIGHTING_SETUP = "lighting_setup"
    SPATIAL_VALIDATION = "spatial_validation"
    RENDER_PLANNING = "render_planning"
    RENDER_EXECUTION = "render_execution"
    POSTPROCESSING = "postprocessing"
    FINALIZATION = "finalization"


@dataclass
class OrchestrationConfig:
    """Configuration for scene orchestration."""
    # Generation settings
    style: SceneStyle = SceneStyle.REALISTIC
    quality: GenerationQuality = GenerationQuality.MEDIUM
    seed: Optional[int] = None

    # Subsystem toggles
    enable_prompt_enhancement: bool = True
    enable_texture_synthesis: bool = True
    enable_lighting_ai: bool = True
    enable_spatial_validation: bool = True
    enable_render_optimization: bool = True
    enable_asset_registry: bool = True

    # Error handling
    continue_on_error: bool = True
    max_retries: int = 3
    retry_delay: float = 1.0

    # Performance
    enable_async: bool = False
    enable_caching: bool = True
    cache_dir: Optional[str] = None

    # Output
    output_dir: str = "output/orchestrated"
    save_intermediate: bool = True
    blend_file: Optional[str] = None


@dataclass
class OrchestrationMetrics:
    """Metrics collected during orchestration."""
    total_time: float = 0.0
    stage_times: Dict[str, float] = field(default_factory=dict)
    subsystem_calls: Dict[str, int] = field(default_factory=dict)
    cache_hits: int = 0
    cache_misses: int = 0
    retries: int = 0
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


@dataclass
class OrchestrationResult:
    """Result of complete scene orchestration."""
    success: bool
    output_path: Optional[str] = None
    blend_file: Optional[str] = None
    render_path: Optional[str] = None
    scene_graph: Optional[SceneGraph] = None
    scene_data: Optional[Dict[str, Any]] = None
    metrics: OrchestrationMetrics = field(default_factory=OrchestrationMetrics)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


class SceneOrchestrator:
    """
    Main coordinator for multi-subsystem 3D scene generation.

    The orchestrator manages the complete workflow:
    1. Prompt interpretation and scene planning
    2. Backend scene generation via VoxelWeaver
    3. Advanced texture synthesis
    4. AI-driven lighting setup
    5. Spatial and physics validation
    6. Render planning and optimization
    7. Final render execution
    8. Post-processing and output

    Attributes:
        config: Orchestration configuration
        voxel_weaver: VoxelWeaver integration
        prompt_interpreter: Prompt analysis subsystem
        texture_synthesizer: Texture generation subsystem
        lighting_ai: Lighting setup subsystem
        spatial_validator: Physics validation subsystem
        render_director: Render orchestration subsystem
        asset_registry: Asset management subsystem
        blender_api: Blender API wrapper

    Example:
        >>> config = OrchestrationConfig(
        ...     style=SceneStyle.REALISTIC,
        ...     quality=GenerationQuality.HIGH
        ... )
        >>> orchestrator = SceneOrchestrator(config)
        >>> result = orchestrator.generate_complete_scene(
        ...     "A cozy cyberpunk cafe at night"
        ... )
        >>> if result.success:
        ...     print(f"Scene rendered to: {result.render_path}")
    """

    def __init__(self, config: Optional[OrchestrationConfig] = None):
        """
        Initialize scene orchestrator.

        Args:
            config: Orchestration configuration (uses defaults if None)
        """
        self.config = config or OrchestrationConfig()
        self.metrics = OrchestrationMetrics()
        self.current_stage = None

        # Initialize subsystems
        logger.info("Initializing SceneOrchestrator subsystems...")

        self.voxel_weaver = VoxelWeaverIntegration(
            cache_dir=self.config.cache_dir or "cache/voxelweaver"
        )

        self.prompt_interpreter = PromptInterpreter()

        if self.config.enable_texture_synthesis:
            self.texture_synthesizer = TextureSynthesizer()
        else:
            self.texture_synthesizer = None

        if self.config.enable_lighting_ai:
            self.lighting_ai = LightingAI()
        else:
            self.lighting_ai = None

        if self.config.enable_spatial_validation:
            self.spatial_validator = SpatialValidator()
        else:
            self.spatial_validator = None

        if self.config.enable_render_optimization:
            self.render_director = RenderDirector()
        else:
            self.render_director = None

        if self.config.enable_asset_registry:
            self.asset_registry = AssetRegistry()
        else:
            self.asset_registry = None

        self.blender_api = BlenderAPIWrapper()

        logger.info("SceneOrchestrator initialized successfully")

    def generate_complete_scene(
        self,
        prompt: str,
        output_name: Optional[str] = None
    ) -> OrchestrationResult:
        """
        Generate complete 3D scene from text prompt.

        This is the main entry point that coordinates all subsystems
        to create a complete, rendered 3D scene.

        Args:
            prompt: Natural language scene description
            output_name: Optional output name (auto-generated if None)

        Returns:
            OrchestrationResult with paths and metrics

        Example:
            >>> result = orchestrator.generate_complete_scene(
            ...     "A medieval castle on a cliff overlooking the ocean at sunset"
            ... )
        """
        start_time = time.time()
        self.metrics = OrchestrationMetrics()

        logger.info(f"Starting scene orchestration: '{prompt}'")

        try:
            # Stage 1: Initialization
            self._set_stage(WorkflowStage.INITIALIZATION)
            output_dir = self._setup_output_directory(output_name)

            # Stage 2: Prompt Analysis
            self._set_stage(WorkflowStage.PROMPT_ANALYSIS)
            scene_graph = self._analyze_prompt(prompt)

            # Stage 3: Scene Generation
            self._set_stage(WorkflowStage.SCENE_GENERATION)
            generation_result = self._generate_base_scene(prompt, scene_graph)

            if not generation_result.success:
                raise RuntimeError(f"Scene generation failed: {generation_result.errors}")

            scene_data = generation_result.scene_data

            # Stage 4: Texture Synthesis
            if self.config.enable_texture_synthesis:
                self._set_stage(WorkflowStage.TEXTURE_SYNTHESIS)
                scene_data = self._synthesize_textures(scene_data, scene_graph)

            # Stage 5: Lighting Setup
            if self.config.enable_lighting_ai:
                self._set_stage(WorkflowStage.LIGHTING_SETUP)
                scene_data = self._setup_lighting(scene_data, scene_graph)

            # Stage 6: Spatial Validation
            if self.config.enable_spatial_validation:
                self._set_stage(WorkflowStage.SPATIAL_VALIDATION)
                scene_data, validation_result = self._validate_spatial(scene_data)

                if not validation_result.is_valid and not self.config.continue_on_error:
                    raise RuntimeError(f"Spatial validation failed: {validation_result.errors}")

            # Stage 7: Render Planning
            if self.config.enable_render_optimization:
                self._set_stage(WorkflowStage.RENDER_PLANNING)
                render_plan = self._plan_render(scene_data, scene_graph)
            else:
                render_plan = None

            # Stage 8: Render Execution
            self._set_stage(WorkflowStage.RENDER_EXECUTION)
            render_path = self._execute_render(scene_data, render_plan, output_dir)

            # Stage 9: Post-processing
            self._set_stage(WorkflowStage.POSTPROCESSING)
            render_path = self._postprocess_render(render_path, render_plan)

            # Stage 10: Finalization
            self._set_stage(WorkflowStage.FINALIZATION)
            blend_file = self._save_blend_file(scene_data, output_dir)
            self._save_metadata(scene_data, scene_graph, output_dir)

            # Calculate metrics
            self.metrics.total_time = time.time() - start_time

            logger.info(
                f"Scene orchestration complete in {self.metrics.total_time:.2f}s"
            )

            return OrchestrationResult(
                success=True,
                output_path=str(output_dir),
                blend_file=blend_file,
                render_path=render_path,
                scene_graph=scene_graph,
                scene_data=scene_data,
                metrics=self.metrics,
                errors=self.metrics.errors,
                warnings=self.metrics.warnings
            )

        except Exception as e:
            logger.exception(f"Scene orchestration failed: {e}")
            self.metrics.total_time = time.time() - start_time
            self.metrics.errors.append(str(e))

            return OrchestrationResult(
                success=False,
                metrics=self.metrics,
                errors=[str(e)]
            )

    def _set_stage(self, stage: WorkflowStage):
        """Set current workflow stage and start timing."""
        if self.current_stage:
            # Record time for previous stage
            stage_name = self.current_stage.value
            elapsed = time.time() - self._stage_start_time
            self.metrics.stage_times[stage_name] = elapsed
            logger.debug(f"Stage '{stage_name}' completed in {elapsed:.2f}s")

        self.current_stage = stage
        self._stage_start_time = time.time()
        logger.info(f"Starting stage: {stage.value}")

    def _setup_output_directory(self, output_name: Optional[str]) -> Path:
        """Setup output directory for this generation."""
        if not output_name:
            from datetime import datetime
            output_name = f"scene_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        output_dir = Path(self.config.output_dir) / output_name
        output_dir.mkdir(parents=True, exist_ok=True)

        logger.debug(f"Output directory: {output_dir}")
        return output_dir

    def _analyze_prompt(self, prompt: str) -> SceneGraph:
        """Analyze prompt and create scene graph."""
        logger.info("Analyzing prompt...")
        scene_graph = self.prompt_interpreter.parse_prompt(prompt)

        if self.config.save_intermediate:
            logger.debug(f"Scene graph: {scene_graph.objects} objects, {scene_graph.relationships} relationships")

        self._increment_subsystem_call('prompt_interpreter')
        return scene_graph

    def _generate_base_scene(
        self,
        prompt: str,
        scene_graph: SceneGraph
    ) -> SceneGenerationResult:
        """Generate base scene using VoxelWeaver."""
        logger.info("Generating base scene...")

        request = SceneGenerationRequest(
            prompt=prompt,
            style=self.config.style,
            quality=self.config.quality,
            seed=self.config.seed,
            enhance_prompt=self.config.enable_prompt_enhancement,
            enable_caching=self.config.enable_caching
        )

        result = self.voxel_weaver.generate_scene(request)

        if result.metrics.cache_hit:
            self.metrics.cache_hits += 1
        else:
            self.metrics.cache_misses += 1

        self._increment_subsystem_call('voxel_weaver')
        return result

    def _synthesize_textures(
        self,
        scene_data: Dict[str, Any],
        scene_graph: SceneGraph
    ) -> Dict[str, Any]:
        """Synthesize advanced textures for scene objects."""
        if not self.texture_synthesizer:
            return scene_data

        logger.info("Synthesizing textures...")

        enhanced_materials = []
        for material in scene_data.get('materials', []):
            try:
                # Create texture request based on scene graph style
                texture_request = TextureRequest(
                    material_name=material.get('name', 'Material'),
                    style=scene_graph.style or 'realistic',
                    resolution=2048 if self.config.quality == GenerationQuality.HIGH else 1024
                )

                enhanced_material = self.texture_synthesizer.synthesize_material(
                    material,
                    texture_request
                )
                enhanced_materials.append(enhanced_material)

            except Exception as e:
                logger.warning(f"Texture synthesis failed for material: {e}")
                self.metrics.warnings.append(f"Texture synthesis error: {e}")
                enhanced_materials.append(material)

        scene_data['materials'] = enhanced_materials
        self._increment_subsystem_call('texture_synthesizer')
        return scene_data

    def _setup_lighting(
        self,
        scene_data: Dict[str, Any],
        scene_graph: SceneGraph
    ) -> Dict[str, Any]:
        """Setup intelligent lighting based on scene analysis."""
        if not self.lighting_ai:
            return scene_data

        logger.info("Setting up intelligent lighting...")

        try:
            # Analyze scene for lighting requirements
            lighting_setup = self.lighting_ai.auto_place_lights(
                scene_data,
                scene_graph
            )

            scene_data['lights'] = lighting_setup.lights
            scene_data['environment'] = lighting_setup.environment

            self._increment_subsystem_call('lighting_ai')

        except Exception as e:
            logger.warning(f"Lighting AI failed: {e}")
            self.metrics.warnings.append(f"Lighting setup error: {e}")

        return scene_data

    def _validate_spatial(
        self,
        scene_data: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], ValidationResult]:
        """Validate and fix spatial/physics issues."""
        if not self.spatial_validator:
            return scene_data, ValidationResult(is_valid=True)

        logger.info("Validating spatial relationships...")

        validation_result = self.spatial_validator.validate_scene(scene_data)

        if not validation_result.is_valid:
            logger.warning(
                f"Spatial validation found {len(validation_result.errors)} issues"
            )

            # Attempt auto-fix
            if validation_result.can_auto_fix:
                scene_data = self.spatial_validator.fix_issues(
                    scene_data,
                    validation_result
                )
                logger.info("Spatial issues auto-fixed")
            else:
                self.metrics.errors.extend(validation_result.errors)

        self._increment_subsystem_call('spatial_validator')
        return scene_data, validation_result

    def _plan_render(
        self,
        scene_data: Dict[str, Any],
        scene_graph: SceneGraph
    ) -> Optional[RenderPlan]:
        """Plan render strategy and optimization."""
        if not self.render_director:
            return None

        logger.info("Planning render strategy...")

        try:
            render_plan = self.render_director.plan_render(
                scene_data,
                scene_graph,
                quality=self.config.quality
            )

            self._increment_subsystem_call('render_director')
            return render_plan

        except Exception as e:
            logger.warning(f"Render planning failed: {e}")
            self.metrics.warnings.append(f"Render planning error: {e}")
            return None

    def _execute_render(
        self,
        scene_data: Dict[str, Any],
        render_plan: Optional[RenderPlan],
        output_dir: Path
    ) -> str:
        """Execute scene rendering."""
        logger.info("Executing render...")

        render_path = str(output_dir / "render.png")

        # Build Blender script for rendering
        script = self._build_render_script(scene_data, render_plan, render_path)

        # Execute via Blender API
        result = self.blender_api.execute_in_blender(script)

        if not result.success:
            raise RuntimeError(f"Render execution failed: {result.error_message}")

        logger.info(f"Render complete: {render_path}")
        return render_path

    def _build_render_script(
        self,
        scene_data: Dict[str, Any],
        render_plan: Optional[RenderPlan],
        output_path: str
    ) -> str:
        """Build Blender Python script for rendering."""
        # This would generate comprehensive Blender Python code
        # to recreate the entire scene and render it

        script = f"""
import bpy
import math

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create objects
for obj_data in {scene_data.get('objects', [])}:
    obj_type = obj_data.get('type', 'CUBE')
    location = obj_data.get('location', (0, 0, 0))

    if obj_type == 'CUBE':
        bpy.ops.mesh.primitive_cube_add(location=location)
    elif obj_type == 'SPHERE':
        bpy.ops.mesh.primitive_uv_sphere_add(location=location)
    elif obj_type == 'CYLINDER':
        bpy.ops.mesh.primitive_cylinder_add(location=location)

    obj = bpy.context.active_object
    obj.name = obj_data.get('name', 'Object')

    if 'scale' in obj_data:
        obj.scale = obj_data['scale']
    if 'rotation' in obj_data:
        obj.rotation_euler = obj_data['rotation']

# Setup camera
camera_data = {scene_data.get('camera', {{}})}
if 'Camera' not in bpy.data.objects:
    cam = bpy.data.cameras.new('Camera')
    cam_obj = bpy.data.objects.new('Camera', cam)
    bpy.context.scene.collection.objects.link(cam_obj)
else:
    cam_obj = bpy.data.objects['Camera']

cam_obj.location = camera_data.get('location', (7.5, -7.5, 5.5))
cam_obj.rotation_euler = camera_data.get('rotation', (1.1, 0, 0.785))
bpy.context.scene.camera = cam_obj

# Render settings
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.render.resolution_x = {1920 if self.config.quality != GenerationQuality.DRAFT else 1280}
scene.render.resolution_y = {1080 if self.config.quality != GenerationQuality.DRAFT else 720}
scene.cycles.samples = {256 if self.config.quality == GenerationQuality.HIGH else 128}
scene.render.filepath = '{output_path}'

# Render
bpy.ops.render.render(write_still=True)
print("Render complete")
"""
        return script

    def _postprocess_render(
        self,
        render_path: str,
        render_plan: Optional[RenderPlan]
    ) -> str:
        """Post-process rendered image."""
        if not self.render_director or not render_plan:
            return render_path

        logger.info("Post-processing render...")

        try:
            processed_path = self.render_director.post_process(render_path, render_plan)
            return processed_path
        except Exception as e:
            logger.warning(f"Post-processing failed: {e}")
            return render_path

    def _save_blend_file(self, scene_data: Dict[str, Any], output_dir: Path) -> str:
        """Save scene as .blend file."""
        blend_path = str(output_dir / "scene.blend")

        script = f"""
import bpy
bpy.ops.wm.save_as_mainfile(filepath='{blend_path}')
"""
        self.blender_api.execute_in_blender(script)

        logger.info(f"Blend file saved: {blend_path}")
        return blend_path

    def _save_metadata(
        self,
        scene_data: Dict[str, Any],
        scene_graph: SceneGraph,
        output_dir: Path
    ):
        """Save generation metadata."""
        metadata = {
            'config': asdict(self.config),
            'metrics': asdict(self.metrics),
            'scene_graph': {
                'objects': scene_graph.objects,
                'relationships': scene_graph.relationships,
                'style': scene_graph.style,
                'mood': scene_graph.mood
            },
            'scene_stats': {
                'object_count': len(scene_data.get('objects', [])),
                'material_count': len(scene_data.get('materials', [])),
                'light_count': len(scene_data.get('lights', []))
            }
        }

        metadata_path = output_dir / "metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)

        logger.debug(f"Metadata saved: {metadata_path}")

    def _increment_subsystem_call(self, subsystem: str):
        """Track subsystem usage."""
        if subsystem not in self.metrics.subsystem_calls:
            self.metrics.subsystem_calls[subsystem] = 0
        self.metrics.subsystem_calls[subsystem] += 1


# Example usage
if __name__ == "__main__":
    # Create orchestrator with custom config
    config = OrchestrationConfig(
        style=SceneStyle.REALISTIC,
        quality=GenerationQuality.HIGH,
        enable_texture_synthesis=True,
        enable_lighting_ai=True,
        enable_spatial_validation=True,
        output_dir="output/orchestrated_scenes"
    )

    orchestrator = SceneOrchestrator(config)

    # Generate complete scene
    prompts = [
        "A cozy cyberpunk cafe at night with neon signs",
        "Medieval castle throne room with tapestries",
        "Futuristic laboratory with holographic displays"
    ]

    for prompt in prompts:
        print(f"\n{'='*60}")
        print(f"Generating: {prompt}")
        print(f"{'='*60}\n")

        result = orchestrator.generate_complete_scene(prompt)

        if result.success:
            print(f"Success!")
            print(f"Output: {result.output_path}")
            print(f"Render: {result.render_path}")
            print(f"Blend: {result.blend_file}")
            print(f"Total time: {result.metrics.total_time:.2f}s")
            print(f"Subsystem calls: {result.metrics.subsystem_calls}")
        else:
            print(f"Failed: {result.errors}")
