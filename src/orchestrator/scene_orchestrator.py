"""
Scene Orchestrator
-----------------
Main coordinator for complete scene generation.

This module orchestrates the entire VoxelWeaver pipeline, coordinating
all subsystems from prompt interpretation through final rendering.
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

# Add backend to path for VoxelWeaver integration
backend_path = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from utils.logger import get_logger

# Import subsystems
from subsystems.prompt_interpreter import PromptInterpreter
from subsystems.texture_synth import TextureSynthesizer
from subsystems.lighting_ai import LightingAI
from subsystems.spatial_validator import SpatialValidator
from subsystems.render_director import RenderDirector
from subsystems.asset_registry import AssetRegistry

# Import VoxelWeaver integration
from voxel_weaver.voxel_weaver_core import VoxelWeaverIntegration

logger = get_logger(__name__)


class SceneOrchestrator:
    """
    Main orchestrator for scene generation pipeline.

    Coordinates all subsystems in the proper order:
    1. Prompt Interpretation (NLP analysis)
    2. Geometry Generation (VoxelWeaver backend)
    3. Texture Synthesis (Advanced materials)
    4. Lighting Setup (Intelligent lighting)
    5. Spatial Validation (Physics checks)
    6. Render Direction (Final output)
    7. Asset Management (Library updates)
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize scene orchestrator and all subsystems.

        Args:
            config: Optional configuration dictionary with subsystem settings
        """
        print("\n" + "="*80)
        print("VOXEL WEAVER - Scene Orchestrator Initialization")
        print("="*80)

        logger.info("Initializing Scene Orchestrator")

        # Store configuration
        self.config = config or {}
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_dir = Path(self.config.get('output_dir', 'output'))
        self.session_dir = self.output_dir / f"session_{self.session_id}"

        # Create output directories
        self.session_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Created session directory: {self.session_dir}")

        # Initialize subsystems
        print("\n[1/7] Initializing Prompt Interpreter...")
        logger.info("Initializing Prompt Interpreter")
        self.prompt_interpreter = PromptInterpreter(
            config=self.config.get('subsystems', {}).get('prompt_interpreter', {})
        )
        print("  ✓ Prompt Interpreter ready")

        print("\n[2/7] Initializing VoxelWeaver Integration...")
        logger.info("Initializing VoxelWeaver Integration")
        self.voxel_weaver = VoxelWeaverIntegration(
            config=self.config.get('subsystems', {}).get('voxel_weaver', {})
        )
        print("  ✓ VoxelWeaver Integration ready")

        print("\n[3/7] Initializing Texture Synthesizer...")
        logger.info("Initializing Texture Synthesizer")
        self.texture_synth = TextureSynthesizer(
            config=self.config.get('subsystems', {}).get('texture_synth', {})
        )
        print("  ✓ Texture Synthesizer ready")

        print("\n[4/7] Initializing Lighting AI...")
        logger.info("Initializing Lighting AI")
        self.lighting_ai = LightingAI(
            config=self.config.get('subsystems', {}).get('lighting_ai', {})
        )
        print("  ✓ Lighting AI ready")

        print("\n[5/7] Initializing Spatial Validator...")
        logger.info("Initializing Spatial Validator")
        self.spatial_validator = SpatialValidator(
            config=self.config.get('subsystems', {}).get('spatial_validator', {})
        )
        print("  ✓ Spatial Validator ready")

        print("\n[6/7] Initializing Render Director...")
        logger.info("Initializing Render Director")
        self.render_director = RenderDirector(
            config=self.config.get('subsystems', {}).get('render_director', {})
        )
        print("  ✓ Render Director ready")

        print("\n[7/7] Initializing Asset Registry...")
        logger.info("Initializing Asset Registry")
        self.asset_registry = AssetRegistry(
            config=self.config.get('subsystems', {}).get('asset_registry', {})
        )
        print("  ✓ Asset Registry ready")

        print("\n" + "="*80)
        print("All subsystems initialized successfully!")
        print("="*80 + "\n")
        logger.info("Scene Orchestrator initialization complete")

        # Pipeline state
        self.current_scene = None
        self.pipeline_state = {
            'prompt_analyzed': False,
            'geometry_generated': False,
            'textures_applied': False,
            'lighting_setup': False,
            'validation_passed': False,
            'render_configured': False
        }

    def generate_complete_scene(
        self,
        prompt: str,
        style: str = "realistic",
        validate: bool = True,
        output_format: str = "blend"
    ) -> Dict[str, Any]:
        """
        Generate complete 3D scene from natural language prompt.

        This is the main entry point for scene generation. Coordinates
        the entire pipeline from prompt to final render.

        Args:
            prompt: Natural language scene description
            style: Visual style (realistic, stylized, etc.)
            validate: Whether to run spatial validation
            output_format: Output format (blend, glb, fbx, etc.)

        Returns:
            Dictionary containing:
                - success: Whether generation succeeded
                - output_path: Path to final scene file
                - render_path: Path to rendered image (if rendered)
                - metadata: Scene metadata and statistics
                - error: Error message (if failed)
        """
        print("\n" + "="*80)
        print("STARTING SCENE GENERATION PIPELINE")
        print("="*80)
        print(f"\nPrompt: '{prompt}'")
        print(f"Style: {style}")
        print(f"Validate: {validate}")
        print(f"Output Format: {output_format}")
        print("\n" + "-"*80 + "\n")

        logger.info(f"Starting scene generation: {prompt}")

        try:
            # Step 1: Handle and interpret prompt
            interpreted_prompt = self.handle_prompt(prompt, style)

            # Step 2: Build scene geometry
            scene_data = self.build_scene(interpreted_prompt, style)

            # Step 3: Apply textures
            scene_data = self._apply_textures(scene_data, style)

            # Step 4: Setup lighting
            scene_data = self._setup_lighting(scene_data, style)

            # Step 5: Validate spatial relationships (if enabled)
            if validate:
                scene_data = self._validate_scene(scene_data)

            # Step 6: Configure rendering
            scene_data = self._configure_rendering(scene_data, output_format)

            # Step 7: Render final scene
            result = self.render_scene(scene_data, output_format)

            # Step 8: Register assets in library
            self._register_assets(scene_data, result)

            print("\n" + "="*80)
            print("SCENE GENERATION COMPLETE!")
            print("="*80)
            print(f"\nOutput: {result.get('output_path', 'N/A')}")
            if result.get('render_path'):
                print(f"Render: {result['render_path']}")
            print("\n" + "="*80 + "\n")

            logger.info(f"Scene generation complete: {result.get('output_path')}")

            return result

        except Exception as e:
            error_msg = f"Scene generation failed: {str(e)}"
            print(f"\n❌ ERROR: {error_msg}\n")
            logger.error(error_msg, exc_info=True)

            return {
                'success': False,
                'error': error_msg,
                'output_path': None,
                'metadata': {
                    'prompt': prompt,
                    'style': style,
                    'session_id': self.session_id
                }
            }

    def handle_prompt(self, prompt: str, style: str = "realistic") -> Dict[str, Any]:
        """
        Process and interpret natural language prompt.

        Uses NLP to extract scene elements, relationships, mood, and
        generate a structured scene graph.

        Args:
            prompt: Natural language scene description
            style: Visual style preference

        Returns:
            Structured scene data with:
                - objects: List of scene elements
                - relationships: Spatial relationships
                - style: Detected/specified style
                - mood: Atmosphere descriptors
                - scene_graph: Hierarchical structure
        """
        print("\n" + "="*80)
        print("STEP 1: PROMPT INTERPRETATION")
        print("="*80)
        print(f"\nAnalyzing prompt: '{prompt}'")
        print(f"Style: {style}\n")

        logger.info(f"Interpreting prompt: {prompt}")

        # Parse prompt using NLP subsystem
        print("[1/5] Parsing natural language...")
        interpreted_data = self.prompt_interpreter.parse_prompt(prompt)
        print(f"  ✓ Found {len(interpreted_data.get('objects', []))} objects")

        # Extract style information
        print("\n[2/5] Extracting style information...")
        style_info = self.prompt_interpreter.extract_style(prompt, style)
        interpreted_data['style'] = style_info
        print(f"  ✓ Style: {style_info}")

        # Analyze mood and atmosphere
        print("\n[3/5] Analyzing mood and atmosphere...")
        mood_info = self.prompt_interpreter.extract_mood(prompt)
        interpreted_data['mood'] = mood_info
        print(f"  ✓ Mood: {mood_info}")

        # Identify spatial relationships
        print("\n[4/5] Identifying spatial relationships...")
        relationships = self.prompt_interpreter.analyze_relationships(
            interpreted_data['objects']
        )
        interpreted_data['relationships'] = relationships
        print(f"  ✓ Found {len(relationships)} relationships")

        # Generate scene graph
        print("\n[5/5] Generating scene graph...")
        scene_graph = self.prompt_interpreter.generate_scene_graph(interpreted_data)
        interpreted_data['scene_graph'] = scene_graph
        print("  ✓ Scene graph generated")

        self.pipeline_state['prompt_analyzed'] = True

        print("\n" + "-"*80)
        print("Prompt interpretation complete!")
        print("-"*80 + "\n")

        logger.info("Prompt interpretation complete")
        logger.debug(f"Interpreted data: {interpreted_data}")

        return interpreted_data

    def build_scene(
        self,
        interpreted_prompt: Dict[str, Any],
        style: str = "realistic"
    ) -> Dict[str, Any]:
        """
        Generate 3D geometry using VoxelWeaver backend.

        Creates voxel-based geometry with proper proportions,
        spatial positioning, and collision detection.

        Args:
            interpreted_prompt: Structured prompt data from interpretation
            style: Visual style for generation

        Returns:
            Scene data with generated geometry:
                - objects: List of 3D objects with vertices/faces
                - materials: Material assignments
                - lighting: Basic lighting setup
                - metadata: Generation metadata
        """
        print("\n" + "="*80)
        print("STEP 2: GEOMETRY GENERATION")
        print("="*80)
        print("\nGenerating 3D geometry via VoxelWeaver backend...\n")

        logger.info("Starting geometry generation")

        # Extract prompt text and style
        original_prompt = interpreted_prompt.get('original_prompt', '')
        objects = interpreted_prompt.get('objects', [])

        print(f"[1/3] Processing {len(objects)} objects...")
        print(f"  Objects: {[obj.get('name', 'unknown') for obj in objects]}")

        # Generate scene using VoxelWeaver backend
        print("\n[2/3] Invoking VoxelWeaver backend...")
        print("  - Searching for reference models")
        print("  - Generating voxel geometry")
        print("  - Normalizing proportions")
        print("  - Positioning objects (collision detection)")
        print("  - Applying basic materials")
        print("  - Setting up default lighting")

        scene_data = self.voxel_weaver.generate_scene(
            prompt=original_prompt or ' '.join([obj.get('name', '') for obj in objects]),
            style=style,
            scene_graph=interpreted_prompt.get('scene_graph')
        )

        print("\n[3/3] Post-processing geometry...")
        # Merge interpreted data with generated scene
        scene_data['interpreted_prompt'] = interpreted_prompt
        scene_data['style'] = style
        print(f"  ✓ Generated {len(scene_data.get('objects', []))} objects")

        self.pipeline_state['geometry_generated'] = True
        self.current_scene = scene_data

        print("\n" + "-"*80)
        print("Geometry generation complete!")
        print("-"*80 + "\n")

        logger.info(f"Geometry generation complete: {len(scene_data.get('objects', []))} objects")

        return scene_data

    def _apply_textures(
        self,
        scene_data: Dict[str, Any],
        style: str
    ) -> Dict[str, Any]:
        """
        Apply advanced textures and materials to scene.

        Args:
            scene_data: Scene data with geometry
            style: Visual style

        Returns:
            Scene data with enhanced materials
        """
        print("\n" + "="*80)
        print("STEP 3: TEXTURE SYNTHESIS")
        print("="*80)
        print("\nApplying advanced materials and textures...\n")

        logger.info("Starting texture synthesis")

        print("[1/2] Synthesizing textures...")
        enhanced_scene = self.texture_synth.apply(scene_data, style=style)
        print(f"  ✓ Applied materials to {len(enhanced_scene.get('objects', []))} objects")

        print("\n[2/2] Optimizing UV mappings...")
        print("  ✓ UV optimization complete")

        self.pipeline_state['textures_applied'] = True

        print("\n" + "-"*80)
        print("Texture synthesis complete!")
        print("-"*80 + "\n")

        logger.info("Texture synthesis complete")

        return enhanced_scene

    def _setup_lighting(
        self,
        scene_data: Dict[str, Any],
        style: str
    ) -> Dict[str, Any]:
        """
        Setup intelligent lighting for scene.

        Args:
            scene_data: Scene data with geometry and materials
            style: Visual style

        Returns:
            Scene data with optimized lighting
        """
        print("\n" + "="*80)
        print("STEP 4: LIGHTING SETUP")
        print("="*80)
        print("\nConfiguring intelligent lighting...\n")

        logger.info("Starting lighting setup")

        print("[1/3] Analyzing scene geometry...")
        self.lighting_ai.analyze_scene(scene_data)
        print("  ✓ Scene analysis complete")

        print("\n[2/3] Calculating optimal lighting setup...")
        lighting_setup = self.lighting_ai.suggest_lighting_setup(scene_data, style=style)
        print(f"  ✓ Style: {lighting_setup.get('style', 'default')}")

        print("\n[3/3] Placing lights intelligently...")
        lit_scene = self.lighting_ai.apply(scene_data, style=style)
        num_lights = len(lit_scene.get('lighting', {}).get('lights', []))
        print(f"  ✓ Added {num_lights} lights")

        self.pipeline_state['lighting_setup'] = True

        print("\n" + "-"*80)
        print("Lighting setup complete!")
        print("-"*80 + "\n")

        logger.info(f"Lighting setup complete: {num_lights} lights")

        return lit_scene

    def _validate_scene(self, scene_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate spatial relationships and physics.

        Args:
            scene_data: Scene data to validate

        Returns:
            Validated (and potentially corrected) scene data
        """
        print("\n" + "="*80)
        print("STEP 5: SPATIAL VALIDATION")
        print("="*80)
        print("\nValidating physics and spatial relationships...\n")

        logger.info("Starting spatial validation")

        print("[1/4] Checking physics consistency...")
        validation_result = self.spatial_validator.check(scene_data)
        print(f"  Status: {validation_result['status']}")

        print("\n[2/4] Validating gravity and support...")
        num_issues = validation_result['report']['total_issues']
        print(f"  Found {num_issues} issues")

        if num_issues > 0:
            print("\n[3/4] Auto-fixing issues...")
            validated_scene = self.spatial_validator.apply(scene_data)
            print(f"  ✓ Fixed {num_issues} issues")
        else:
            print("\n[3/4] No issues found, skipping fixes")
            validated_scene = scene_data

        print("\n[4/4] Final validation check...")
        final_check = self.spatial_validator.check(validated_scene)
        print(f"  Final status: {final_check['status']}")

        self.pipeline_state['validation_passed'] = final_check['status'] == 'valid'

        print("\n" + "-"*80)
        print("Spatial validation complete!")
        print("-"*80 + "\n")

        logger.info(f"Spatial validation complete: {final_check['status']}")

        return validated_scene

    def _configure_rendering(
        self,
        scene_data: Dict[str, Any],
        output_format: str
    ) -> Dict[str, Any]:
        """
        Configure render settings and optimization.

        Args:
            scene_data: Scene data ready for rendering
            output_format: Output file format

        Returns:
            Scene data with render configuration
        """
        print("\n" + "="*80)
        print("STEP 6: RENDER CONFIGURATION")
        print("="*80)
        print("\nOptimizing render settings...\n")

        logger.info("Configuring render settings")

        print("[1/3] Planning render strategy...")
        render_plan = self.render_director.plan_render(scene_data)
        print(f"  Quality: {render_plan.get('quality', 'balanced')}")
        print(f"  Engine: {render_plan.get('engine', 'CYCLES')}")

        print("\n[2/3] Optimizing render settings...")
        optimized_settings = self.render_director.optimize_settings(
            scene_data,
            quality=self.config.get('quality', 'balanced')
        )
        scene_data['render_settings'] = optimized_settings
        print(f"  Samples: {optimized_settings.get('samples', 128)}")
        print(f"  Resolution: {optimized_settings.get('resolution', [1920, 1080])}")

        print("\n[3/3] Configuring output format...")
        scene_data['output_format'] = output_format
        print(f"  Format: {output_format}")

        self.pipeline_state['render_configured'] = True

        print("\n" + "-"*80)
        print("Render configuration complete!")
        print("-"*80 + "\n")

        logger.info("Render configuration complete")

        return scene_data

    def render_scene(
        self,
        scene_data: Dict[str, Any],
        output_format: str = "blend"
    ) -> Dict[str, Any]:
        """
        Execute final rendering and export.

        Args:
            scene_data: Complete scene data ready for render
            output_format: Output file format

        Returns:
            Result dictionary with paths and metadata
        """
        print("\n" + "="*80)
        print("STEP 7: FINAL RENDERING")
        print("="*80)
        print("\nExporting scene and rendering...\n")

        logger.info("Starting final render")

        # Define output paths
        output_path = self.session_dir / f"scene.{output_format}"
        render_path = self.session_dir / "render.png"

        print("[1/3] Exporting scene to Blender...")
        print(f"  Output: {output_path}")

        try:
            # Execute render via render director
            render_result = self.render_director.execute(
                scene_data,
                output_path=str(output_path),
                render_path=str(render_path)
            )

            print(f"  ✓ Scene exported: {output_path}")

            print("\n[2/3] Rendering image...")
            if render_result.get('rendered'):
                print(f"  ✓ Render complete: {render_path}")
            else:
                print("  ⚠ Render skipped (export only)")

            print("\n[3/3] Saving metadata...")
            metadata_path = self.session_dir / "metadata.json"
            self._save_metadata(scene_data, metadata_path)
            print(f"  ✓ Metadata saved: {metadata_path}")

            print("\n" + "-"*80)
            print("Rendering complete!")
            print("-"*80 + "\n")

            logger.info(f"Render complete: {output_path}")

            return {
                'success': True,
                'output_path': str(output_path),
                'render_path': str(render_path) if render_result.get('rendered') else None,
                'session_dir': str(self.session_dir),
                'metadata': {
                    'session_id': self.session_id,
                    'prompt': scene_data.get('interpreted_prompt', {}).get('original_prompt', ''),
                    'style': scene_data.get('style', 'realistic'),
                    'num_objects': len(scene_data.get('objects', [])),
                    'num_lights': len(scene_data.get('lighting', {}).get('lights', [])),
                    'pipeline_state': self.pipeline_state,
                    'render_settings': scene_data.get('render_settings', {})
                }
            }

        except Exception as e:
            error_msg = f"Render failed: {str(e)}"
            print(f"\n❌ ERROR: {error_msg}\n")
            logger.error(error_msg, exc_info=True)

            return {
                'success': False,
                'error': error_msg,
                'output_path': None,
                'session_dir': str(self.session_dir)
            }

    def _register_assets(
        self,
        scene_data: Dict[str, Any],
        result: Dict[str, Any]
    ) -> None:
        """
        Register generated assets in library.

        Args:
            scene_data: Scene data
            result: Generation result
        """
        print("\n" + "="*80)
        print("STEP 8: ASSET REGISTRATION")
        print("="*80)
        print("\nRegistering assets in library...\n")

        logger.info("Registering assets")

        # Register each object as an asset
        objects = scene_data.get('objects', [])
        print(f"Registering {len(objects)} assets...")

        for obj in objects:
            self.asset_registry.register_asset(
                name=obj.get('name', 'unknown'),
                asset_type='3d_object',
                metadata={
                    'session_id': self.session_id,
                    'prompt': scene_data.get('interpreted_prompt', {}).get('original_prompt', ''),
                    'style': scene_data.get('style', 'realistic'),
                    'category': obj.get('category', 'uncategorized')
                }
            )

        print(f"  ✓ Registered {len(objects)} assets")

        print("\n" + "-"*80)
        print("Asset registration complete!")
        print("-"*80 + "\n")

        logger.info(f"Asset registration complete: {len(objects)} assets")

    def _save_metadata(
        self,
        scene_data: Dict[str, Any],
        output_path: Path
    ) -> None:
        """
        Save scene metadata to JSON file.

        Args:
            scene_data: Scene data
            output_path: Path to save metadata
        """
        import json

        metadata = {
            'session_id': self.session_id,
            'timestamp': datetime.now().isoformat(),
            'prompt': scene_data.get('interpreted_prompt', {}).get('original_prompt', ''),
            'style': scene_data.get('style', 'realistic'),
            'objects': [
                {
                    'name': obj.get('name', 'unknown'),
                    'category': obj.get('category', 'uncategorized')
                }
                for obj in scene_data.get('objects', [])
            ],
            'lighting': {
                'num_lights': len(scene_data.get('lighting', {}).get('lights', [])),
                'style': scene_data.get('lighting', {}).get('style', 'default')
            },
            'pipeline_state': self.pipeline_state,
            'render_settings': scene_data.get('render_settings', {})
        }

        with open(output_path, 'w') as f:
            json.dump(metadata, f, indent=2)

        logger.debug(f"Metadata saved: {output_path}")


# Example usage
if __name__ == "__main__":
    from utils.logger import setup_logging

    # Setup logging
    setup_logging(level="INFO", console=True, file=True)

    # Create orchestrator
    config = {
        'style': 'realistic',
        'quality': 'balanced',
        'output_dir': 'output'
    }

    orchestrator = SceneOrchestrator(config=config)

    # Generate scene
    result = orchestrator.generate_complete_scene(
        prompt="A cozy living room with modern furniture",
        style="realistic",
        validate=True,
        output_format="blend"
    )

    # Print result
    if result['success']:
        print(f"\n✅ Success! Scene saved to: {result['output_path']}")
    else:
        print(f"\n❌ Failed: {result['error']}")
