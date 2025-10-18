"""
VoxelWeaver Core Module
-----------------------
Handles AI-guided procedural voxel scene creation and composition.

This is the main orchestration layer that coordinates all VoxelWeaver subsystems
to generate complete, production-ready Blender scenes from natural language prompts.
"""

import logging
from typing import Dict, List, Any, Optional
from pathlib import Path

from .geometry_handler import GeometryHandler
from .proportion_analyzer import ProportionAnalyzer
from .context_alignment import ContextAlignment
from .lighting_engine import LightingEngine
from .texture_mapper import TextureMapper
from .scene_validator import SceneValidator
from .blender_bridge import BlenderBridge
from .search_scraper import SearchScraper

logger = logging.getLogger(__name__)


class VoxelWeaverConfig:
    """Configuration for VoxelWeaver scene generation."""

    def __init__(
        self,
        style: str = "realistic",
        voxel_resolution: float = 0.1,
        search_references: bool = True,
        validate_scene: bool = True,
        auto_lighting: bool = True,
        export_format: str = "blend",
        output_dir: Path = Path("output/voxelweaver"),
    ):
        """
        Initialize VoxelWeaver configuration.

        Args:
            style: Visual style ('realistic', 'stylized', 'lowpoly', 'cartoon')
            voxel_resolution: Voxel grid resolution in Blender units
            search_references: Whether to search for online references
            validate_scene: Whether to run scene validation
            auto_lighting: Whether to automatically apply lighting
            export_format: Output format ('blend', 'glb', 'fbx', 'obj')
            output_dir: Output directory for generated scenes
        """
        self.style = style
        self.voxel_resolution = voxel_resolution
        self.search_references = search_references
        self.validate_scene = validate_scene
        self.auto_lighting = auto_lighting
        self.export_format = export_format
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)


class SceneData:
    """Container for scene generation data."""

    def __init__(self, prompt: str, config: VoxelWeaverConfig):
        """
        Initialize scene data container.

        Args:
            prompt: User's scene description
            config: VoxelWeaver configuration
        """
        self.prompt = prompt
        self.config = config
        self.raw_objects: List[Dict[str, Any]] = []
        self.scaled_objects: List[Dict[str, Any]] = []
        self.positioned_objects: List[Dict[str, Any]] = []
        self.lit_scene: Dict[str, Any] = {}
        self.textured_scene: Dict[str, Any] = {}
        self.validated_scene: Dict[str, Any] = {}
        self.reference_data: Dict[str, Any] = {}
        self.metadata: Dict[str, Any] = {
            "prompt": prompt,
            "style": config.style,
            "status": "initializing"
        }


class VoxelWeaverCore:
    """
    Main orchestration class for VoxelWeaver.

    Coordinates all subsystems to generate complete Blender scenes from
    natural language descriptions.

    Example:
        >>> weaver = VoxelWeaverCore()
        >>> result = weaver.generate_scene(
        ...     prompt="A modern kitchen with appliances",
        ...     style="realistic"
        ... )
        >>> print(f"Scene saved to: {result['output_path']}")
    """

    def __init__(self, config: Optional[VoxelWeaverConfig] = None):
        """
        Initialize VoxelWeaver core system.

        Args:
            config: Optional configuration. Uses defaults if not provided.
        """
        self.config = config or VoxelWeaverConfig()

        # Initialize all subsystems
        self.geometry = GeometryHandler(voxel_resolution=self.config.voxel_resolution)
        self.proportion = ProportionAnalyzer()
        self.context = ContextAlignment()
        self.lighting = LightingEngine()
        self.texture = TextureMapper()
        self.validator = SceneValidator()
        self.bridge = BlenderBridge()
        self.scraper = SearchScraper() if self.config.search_references else None

        logger.info("VoxelWeaver initialized successfully")

    def generate_scene(
        self,
        prompt: str,
        style: Optional[str] = None,
        custom_config: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Generate a complete Blender scene from a text prompt.

        This is the main entry point for scene generation. It orchestrates
        all subsystems in the correct order and returns the final scene data.

        Args:
            prompt: Natural language scene description
            style: Visual style override ('realistic', 'stylized', 'lowpoly', 'cartoon')
            custom_config: Optional custom configuration overrides

        Returns:
            Dictionary containing:
                - success: bool
                - output_path: Path to generated scene file
                - metadata: Scene metadata and statistics
                - objects: List of generated objects
                - errors: List of any errors encountered

        Example:
            >>> weaver = VoxelWeaverCore()
            >>> result = weaver.generate_scene(
            ...     prompt="A cozy living room with a sofa, coffee table, and lamp",
            ...     style="realistic"
            ... )
            >>> if result['success']:
            ...     print(f"Scene generated: {result['output_path']}")
        """
        # Override style if provided
        if style:
            self.config.style = style

        # Apply custom config if provided
        if custom_config:
            for key, value in custom_config.items():
                if hasattr(self.config, key):
                    setattr(self.config, key, value)

        logger.info(f"Starting scene generation for prompt: {prompt}")

        # Create scene data container
        scene_data = SceneData(prompt, self.config)

        try:
            # Step 1: Search for references (if enabled)
            if self.scraper:
                scene_data.metadata['status'] = 'searching_references'
                scene_data.reference_data = self._gather_references(prompt)
                logger.info(f"Gathered {len(scene_data.reference_data.get('models', []))} reference models")

            # Step 2: Generate or import geometry
            scene_data.metadata['status'] = 'generating_geometry'
            scene_data.raw_objects = self._generate_geometry(prompt, scene_data.reference_data)
            logger.info(f"Generated {len(scene_data.raw_objects)} objects")

            # Step 3: Analyze and normalize proportions
            scene_data.metadata['status'] = 'normalizing_proportions'
            scene_data.scaled_objects = self._normalize_proportions(
                scene_data.raw_objects,
                scene_data.reference_data
            )
            logger.info("Normalized object proportions")

            # Step 4: Position objects and handle collision
            scene_data.metadata['status'] = 'positioning_objects'
            scene_data.positioned_objects = self._align_objects(scene_data.scaled_objects)
            logger.info("Positioned objects in scene")

            # Step 5: Apply lighting (if enabled)
            if self.config.auto_lighting:
                scene_data.metadata['status'] = 'applying_lighting'
                scene_data.lit_scene = self._apply_lighting(
                    scene_data.positioned_objects,
                    style=self.config.style
                )
                logger.info("Applied scene lighting")
            else:
                scene_data.lit_scene = {"objects": scene_data.positioned_objects}

            # Step 6: Apply textures and materials
            scene_data.metadata['status'] = 'applying_textures'
            scene_data.textured_scene = self._apply_textures(
                scene_data.lit_scene,
                style=self.config.style
            )
            logger.info("Applied textures and materials")

            # Step 7: Validate scene (if enabled)
            if self.config.validate_scene:
                scene_data.metadata['status'] = 'validating_scene'
                validation_result = self._validate_scene(scene_data.textured_scene)
                scene_data.validated_scene = validation_result['scene']
                scene_data.metadata['validation'] = validation_result['report']
                logger.info(f"Scene validation: {validation_result['status']}")
            else:
                scene_data.validated_scene = scene_data.textured_scene

            # Step 8: Export to Blender
            scene_data.metadata['status'] = 'exporting'
            export_result = self._export_scene(scene_data)
            logger.info(f"Exported scene to: {export_result['path']}")

            # Build result
            result = {
                'success': True,
                'output_path': export_result['path'],
                'metadata': {
                    **scene_data.metadata,
                    'status': 'completed',
                    'object_count': len(scene_data.validated_scene.get('objects', [])),
                    'export_format': self.config.export_format,
                },
                'objects': scene_data.validated_scene.get('objects', []),
                'lighting': scene_data.validated_scene.get('lighting', {}),
                'errors': []
            }

            logger.info("Scene generation completed successfully")
            return result

        except Exception as e:
            logger.error(f"Scene generation failed: {e}", exc_info=True)
            return {
                'success': False,
                'output_path': None,
                'metadata': {
                    **scene_data.metadata,
                    'status': 'failed',
                    'error': str(e)
                },
                'objects': [],
                'errors': [str(e)]
            }

    def _gather_references(self, prompt: str) -> Dict[str, Any]:
        """
        Gather reference data from online sources.

        Args:
            prompt: Scene description

        Returns:
            Dictionary containing reference models and measurements
        """
        logger.info("Gathering reference data...")
        return self.scraper.search_references(prompt)

    def _generate_geometry(
        self,
        prompt: str,
        references: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Generate or import 3D geometry.

        Args:
            prompt: Scene description
            references: Reference data from scraper

        Returns:
            List of raw geometry objects
        """
        logger.info("Generating geometry...")
        return self.geometry.generate_from_prompt(prompt, references)

    def _normalize_proportions(
        self,
        objects: List[Dict[str, Any]],
        references: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Normalize object scales and proportions.

        Args:
            objects: Raw objects to normalize
            references: Reference data for scale information

        Returns:
            List of scaled objects
        """
        logger.info("Normalizing proportions...")
        return self.proportion.normalize(objects, references)

    def _align_objects(self, objects: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Position objects in 3D space without collisions.

        Args:
            objects: Scaled objects to position

        Returns:
            List of positioned objects
        """
        logger.info("Aligning objects...")
        return self.context.align(objects)

    def _apply_lighting(
        self,
        scene: List[Dict[str, Any]],
        style: str
    ) -> Dict[str, Any]:
        """
        Apply lighting to the scene.

        Args:
            scene: Positioned objects
            style: Lighting style

        Returns:
            Scene with lighting data
        """
        logger.info(f"Applying {style} lighting...")
        return self.lighting.apply(scene, style=style)

    def _apply_textures(
        self,
        scene: Dict[str, Any],
        style: str
    ) -> Dict[str, Any]:
        """
        Apply textures and materials.

        Args:
            scene: Scene with lighting
            style: Material style

        Returns:
            Scene with texture data
        """
        logger.info(f"Applying {style} textures...")
        return self.texture.apply(scene, style=style)

    def _validate_scene(self, scene: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate scene quality and correctness.

        Args:
            scene: Complete scene to validate

        Returns:
            Validation result with report
        """
        logger.info("Validating scene...")
        return self.validator.check(scene)

    def _export_scene(self, scene_data: SceneData) -> Dict[str, Any]:
        """
        Export scene to Blender file.

        Args:
            scene_data: Complete scene data

        Returns:
            Export result with file path
        """
        logger.info(f"Exporting scene as {self.config.export_format}...")
        return self.bridge.export_scene(
            scene_data.validated_scene,
            format=self.config.export_format,
            output_dir=self.config.output_dir
        )

    def generate_batch(
        self,
        prompts: List[str],
        style: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate multiple scenes in batch.

        Args:
            prompts: List of scene descriptions
            style: Optional style for all scenes

        Returns:
            List of generation results

        Example:
            >>> weaver = VoxelWeaverCore()
            >>> results = weaver.generate_batch([
            ...     "A bedroom with a bed and nightstand",
            ...     "A kitchen with modern appliances",
            ...     "An office with a desk and computer"
            ... ], style="realistic")
            >>> for i, result in enumerate(results):
            ...     print(f"Scene {i+1}: {result['output_path']}")
        """
        logger.info(f"Starting batch generation for {len(prompts)} scenes")
        results = []

        for i, prompt in enumerate(prompts):
            logger.info(f"Generating scene {i+1}/{len(prompts)}")
            result = self.generate_scene(prompt, style=style)
            results.append(result)

        logger.info(f"Batch generation complete: {sum(1 for r in results if r['success'])}/{len(results)} successful")
        return results


# Example usage
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)

    # Create VoxelWeaver instance
    config = VoxelWeaverConfig(
        style="realistic",
        voxel_resolution=0.1,
        search_references=True,
        validate_scene=True
    )
    weaver = VoxelWeaverCore(config)

    # Generate a scene
    result = weaver.generate_scene(
        prompt="A cozy living room with a sofa, coffee table, and floor lamp",
        style="realistic"
    )

    if result['success']:
        print(f"✓ Scene generated successfully!")
        print(f"  Output: {result['output_path']}")
        print(f"  Objects: {result['metadata']['object_count']}")
    else:
        print(f"✗ Scene generation failed:")
        for error in result['errors']:
            print(f"  - {error}")
