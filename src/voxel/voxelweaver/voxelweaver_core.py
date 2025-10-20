"""
VoxelWeaver Core - Main orchestration for AI-powered procedural 3D scene generation.
Integrates all subsystems for coherent, production-ready Blender scene creation.
"""

from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import logging

from .search_scraper import ReferenceSearcher
from .proportion_analyzer import ProportionAnalyzer
from .geometry_handler import GeometryHandler
from .context_alignment import ContextAligner
from .lighting_engine import LightingEngine
from .texture_mapper import TextureMapper
from .scene_validator import SceneValidator

logger = logging.getLogger(__name__)


@dataclass
class VoxelWeaverConfig:
    """Configuration for VoxelWeaver system."""
    style: str = "realistic"  # realistic, stylized, abstract
    voxel_resolution: float = 0.1  # meters per voxel
    search_references: bool = True  # Search external repos
    use_procedural: bool = True  # Generate when no refs found
    validate_scene: bool = True  # Run quality checks
    max_references: int = 50  # Max external references to fetch
    collision_tolerance: float = 0.01  # Meters
    output_formats: List[str] = None  # ['blend', 'glb', 'fbx']

    def __post_init__(self):
        if self.output_formats is None:
            self.output_formats = ['blend']


class VoxelWeaverCore:
    """
    Core orchestrator for VoxelWeaver system.
    Ensures all scene generation is coherent and production-ready.
    """

    def __init__(self, config: VoxelWeaverConfig):
        """Initialize VoxelWeaver with configuration."""
        self.config = config

        # Initialize all subsystems
        self.reference_searcher = ReferenceSearcher(
            max_results=config.max_references,
            enabled=config.search_references
        )
        self.proportion_analyzer = ProportionAnalyzer()
        self.geometry_handler = GeometryHandler(
            voxel_resolution=config.voxel_resolution,
            use_procedural=config.use_procedural
        )
        self.context_aligner = ContextAligner(
            collision_tolerance=config.collision_tolerance
        )
        self.lighting_engine = LightingEngine(style=config.style)
        self.texture_mapper = TextureMapper()
        self.scene_validator = SceneValidator()

        logger.info(f"VoxelWeaver initialized with style={config.style}, resolution={config.voxel_resolution}")

    def process_scene_concept(self, concept: str, prompt: str) -> Dict[str, Any]:
        """
        Process scene concept through VoxelWeaver pipeline.

        Args:
            concept: Detailed scene concept from ConceptAgent
            prompt: Original user prompt

        Returns:
            Enriched scene data with references, proportions, and validation
        """
        logger.info("VoxelWeaver processing scene concept...")

        result = {
            'references': [],
            'proportions': {},
            'geometry_hints': {},
            'lighting_config': {},
            'texture_suggestions': {},
            'validation_results': {},
            'coherence_score': 0.0
        }

        try:
            # Step 1: Search for external references
            if self.config.search_references:
                logger.info("Searching external Blender repositories...")
                result['references'] = self.reference_searcher.search_concept(concept, prompt)
                logger.info(f"Found {len(result['references'])} external references")

            # Step 2: Analyze proportions for realism
            logger.info("Analyzing real-world proportions...")
            result['proportions'] = self.proportion_analyzer.analyze_concept(concept)

            # Step 3: Generate geometry guidance
            logger.info("Generating geometry guidance...")
            result['geometry_hints'] = self.geometry_handler.analyze_requirements(
                concept, result['proportions']
            )

            # Step 4: Configure lighting
            logger.info("Configuring lighting...")
            result['lighting_config'] = self.lighting_engine.configure_from_concept(concept)

            # Step 5: Suggest textures based on references
            logger.info("Generating texture suggestions...")
            result['texture_suggestions'] = self.texture_mapper.suggest_materials(
                concept, result['references']
            )

            # Step 6: Calculate coherence score
            result['coherence_score'] = self._calculate_coherence(result)

            logger.info(f"VoxelWeaver processing complete. Coherence: {result['coherence_score']:.2f}")

        except Exception as e:
            logger.error(f"VoxelWeaver processing error: {e}", exc_info=True)
            result['error'] = str(e)

        return result

    def validate_generated_scene(self, scene_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate a generated scene for quality and coherence.

        Args:
            scene_data: Scene metadata (objects, materials, etc.)

        Returns:
            Validation results with issues and suggestions
        """
        if not self.config.validate_scene:
            return {'validated': False, 'skipped': True}

        logger.info("Validating scene quality...")

        validation = self.scene_validator.validate({
            **scene_data,
            'config': {
                'style': self.config.style,
                'voxel_resolution': self.config.voxel_resolution,
                'validate_scene': self.config.validate_scene
            }
        })

        return validation

    def align_objects_spatial(self, objects: List[Dict]) -> List[Dict]:
        """
        Ensure objects don't overlap and are spatially coherent.

        Args:
            objects: List of object definitions with positions

        Returns:
            Aligned objects with corrected positions
        """
        logger.info(f"Aligning {len(objects)} objects spatially...")

        aligned = self.context_aligner.align_objects(objects)

        logger.info(f"Spatial alignment complete. Collisions resolved: {aligned['collisions_fixed']}")

        return aligned['objects']

    def _calculate_coherence(self, result: Dict[str, Any]) -> float:
        """Calculate overall coherence score for the scene."""
        scores = []

        # Reference quality
        if result.get('references'):
            scores.append(min(1.0, len(result['references']) / 10))

        # Proportion realism
        if result.get('proportions', {}).get('realism_score'):
            scores.append(result['proportions']['realism_score'])

        # Geometry completeness
        if result.get('geometry_hints'):
            scores.append(0.8)  # Base score for having geometry guidance

        # Lighting quality
        if result.get('lighting_config'):
            scores.append(0.9)  # Base score for lighting config

        # Texture suggestions
        if result.get('texture_suggestions'):
            scores.append(0.85)  # Base score for texture data

        return sum(scores) / len(scores) if scores else 0.5

    def enrich_agent_prompt(self, agent_role: str, base_prompt: str,
                           scene_data: Dict[str, Any]) -> str:
        """
        Enrich agent prompts with VoxelWeaver intelligence.

        Args:
            agent_role: Role of the agent (builder, texture, etc.)
            base_prompt: Original prompt for the agent
            scene_data: VoxelWeaver processed scene data

        Returns:
            Enriched prompt with references and guidance
        """
        enrichments = []

        if agent_role == "builder" and scene_data.get('geometry_hints'):
            enrichments.append("\n## VoxelWeaver Geometry Guidance:")
            enrichments.append(f"- Voxel resolution: {self.config.voxel_resolution}m")
            enrichments.append(f"- Real-world proportions: {scene_data['proportions']}")
            if scene_data.get('references'):
                enrichments.append(f"- {len(scene_data['references'])} external references found")

        elif agent_role == "texture" and scene_data.get('texture_suggestions'):
            enrichments.append("\n## VoxelWeaver Material Guidance:")
            enrichments.append("- PBR material suggestions from real projects:")
            for suggestion in scene_data.get('texture_suggestions', {}).get('materials', [])[:5]:
                enrichments.append(f"  * {suggestion}")

        elif agent_role == "render" and scene_data.get('lighting_config'):
            enrichments.append("\n## VoxelWeaver Lighting Guidance:")
            lighting = scene_data['lighting_config']
            enrichments.append(f"- Style: {lighting.get('style', 'realistic')}")
            enrichments.append(f"- Key light: {lighting.get('key_light', 'N/A')}")

        if enrichments:
            return base_prompt + "\n" + "\n".join(enrichments)

        return base_prompt
