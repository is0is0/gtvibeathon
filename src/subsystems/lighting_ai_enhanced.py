"""
Enhanced Lighting AI with HDRI Intelligence
===========================================
Extends the base LightingAI with HDRI Manager integration for intelligent
HDRI selection and blending based on scene context.

This wrapper adds:
- Automatic HDRI selection from AssetRegistry
- Multi-HDRI blending for unique atmospheres
- Smart mood-based lighting
- Time-of-day aware HDRI selection
"""

from typing import Dict, List, Any, Optional, Tuple
from subsystems.lighting_ai import LightingAI, LightConfig, WorldConfig
from subsystems.hdri_manager import HDRIManager, HDRIBlendLayer
from utils.logger import get_logger

logger = get_logger(__name__)


class LightingAIEnhanced(LightingAI):
    """
    Enhanced lighting AI with intelligent HDRI selection and blending.

    Inherits all functionality from LightingAI and adds:
    - AssetRegistry integration for HDRI access
    - Automatic HDRI selection based on scene context
    - Multi-HDRI blending for unique lighting
    - Smarter mood and time-of-day matching
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize enhanced lighting AI.

        Args:
            config: Configuration dictionary with optional:
                - registry_path: Path to AssetRegistry
                - enable_hdri_blending: Enable multi-HDRI blending (default: True)
                - max_hdri_layers: Maximum HDRIs to blend (default: 2)
                - hdri_blend_mode: Blending mode ('layered', 'balanced', 'dominant')
        """
        super().__init__(config)

        # HDRI Manager configuration
        registry_path = self.config.get('registry_path', 'data/voxel_assets.db')
        self.hdri_manager = HDRIManager(registry_path)

        self.enable_hdri_blending = self.config.get('enable_hdri_blending', True)
        self.max_hdri_layers = self.config.get('max_hdri_layers', 2)
        self.hdri_blend_mode = self.config.get('hdri_blend_mode', 'layered')

        logger.info(
            f"Enhanced Lighting AI initialized "
            f"(HDRI blending: {self.enable_hdri_blending}, "
            f"max layers: {self.max_hdri_layers})"
        )

    def apply(self, scene_data: Dict[str, Any], style: str = "realistic") -> Dict[str, Any]:
        """
        Apply intelligent lighting with automatic HDRI selection.

        This override adds HDRI intelligence before calling the base apply method.

        Args:
            scene_data: Scene data with objects
            style: Visual style for lighting

        Returns:
            Scene data with enhanced lighting configuration
        """
        logger.info(f"Applying enhanced lighting (style: {style})")

        # Intelligently select HDRIs based on scene context
        hdri_config = self._select_scene_hdris(scene_data, style)

        # Store HDRI configuration in scene data for base class to use
        if hdri_config:
            scene_data['hdri_configuration'] = hdri_config

        # Call base apply method
        result = super().apply(scene_data, style)

        # Add enhanced HDRI information to lighting config
        if hdri_config:
            result['lighting']['hdri_blend'] = {
                'enabled': True,
                'num_layers': len(hdri_config['layers']),
                'mode': hdri_config['blend_mode'],
                'hdris': [layer.hdri_asset.name for layer in hdri_config['layers']],
            }

        logger.info(f"Enhanced lighting applied with {len(hdri_config.get('layers', []))} HDRI layers")

        return result

    def _select_scene_hdris(
        self,
        scene_data: Dict[str, Any],
        style: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Intelligently select and configure HDRIs for the scene.

        Args:
            scene_data: Scene data with interpreted prompt
            style: Visual style

        Returns:
            HDRI configuration with blend layers, or None
        """
        logger.info("Selecting HDRIs for scene")

        # Check if HDRIs are available
        if not self.hdri_manager.available_hdris:
            logger.warning("No HDRIs available in registry")
            return None

        # Determine if we should use HDRIs for this style
        mode = self._style_to_mode(style)
        if not self.LIGHTING_MODES.get(mode, {}).get('use_hdri', False):
            logger.info(f"Style '{style}' (mode: {mode}) doesn't use HDRIs")
            return None

        # Use smart selection based on scene context
        num_layers = self.max_hdri_layers if self.enable_hdri_blending else 1
        selected_hdris = self.hdri_manager.select_smart(scene_data, limit=num_layers)

        if not selected_hdris:
            logger.warning("No HDRIs matched scene context")
            return None

        # Create blend configuration
        blend_mode = self.hdri_blend_mode
        layers = self.hdri_manager.create_blend_configuration(selected_hdris, blend_mode)

        # Adjust layer parameters based on mood
        layers = self._adjust_layers_for_mood(layers, scene_data)

        config = {
            'layers': layers,
            'blend_mode': blend_mode,
            'num_layers': len(layers),
        }

        logger.info(
            f"Selected {len(layers)} HDRI(s): "
            f"{', '.join([l.hdri_asset.name for l in layers])}"
        )

        return config

    def _adjust_layers_for_mood(
        self,
        layers: List[HDRIBlendLayer],
        scene_data: Dict[str, Any],
    ) -> List[HDRIBlendLayer]:
        """
        Adjust HDRI layer parameters based on scene mood.

        Args:
            layers: List of HDRI blend layers
            scene_data: Scene data with mood information

        Returns:
            Adjusted layers
        """
        prompt = scene_data.get('interpreted_prompt', {})
        mood = prompt.get('mood', {})

        if not mood or not isinstance(mood, dict):
            return layers

        # Extract primary mood
        if mood:
            primary_mood = max(mood.items(), key=lambda x: x[1])[0]
        else:
            return layers

        logger.debug(f"Adjusting HDRI layers for mood: {primary_mood}")

        # Mood-based adjustments
        for layer in layers:
            if primary_mood == 'cozy':
                # Warmer tint, slightly increased strength
                layer.color_tint = (1.0, 0.95, 0.85)
                layer.strength *= 1.1
                layer.saturation = 1.1

            elif primary_mood == 'dramatic':
                # Higher contrast, cooler tint
                layer.color_tint = (0.95, 0.95, 1.0)
                layer.strength *= 1.3
                layer.saturation = 1.2

            elif primary_mood == 'peaceful':
                # Softer, desaturated
                layer.strength *= 0.9
                layer.saturation = 0.8

            elif primary_mood == 'energetic':
                # Brighter, more saturated
                layer.strength *= 1.2
                layer.saturation = 1.3

            elif primary_mood == 'mysterious':
                # Darker, cooler
                layer.color_tint = (0.8, 0.85, 1.0)
                layer.strength *= 0.7
                layer.saturation = 0.9

        return layers

    def _setup_realistic_lighting(
        self,
        scene_context: Dict[str, Any],
        mood: Dict[str, Any]
    ) -> Tuple[List[LightConfig], WorldConfig]:
        """
        Override realistic lighting setup to use selected HDRIs.

        Args:
            scene_context: Scene analysis data
            mood: Mood descriptors

        Returns:
            Lights and world configuration with HDRI blend
        """
        logger.debug("Setting up realistic lighting with HDRI selection")

        # Get base lighting setup
        lights, world = super()._setup_realistic_lighting(scene_context, mood)

        # Check if HDRI configuration exists
        hdri_config = scene_context.get('hdri_configuration')

        if hdri_config and hdri_config['layers']:
            # Use selected HDRIs instead of default
            layers = hdri_config['layers']

            if len(layers) == 1:
                # Single HDRI
                world.hdri_path = layers[0].hdri_asset.path
                world.hdri_rotation = layers[0].rotation
                world.strength = layers[0].strength
            else:
                # Multiple HDRIs - use blend script
                # Store layers in world config for script generation
                world.hdri_blend_layers = layers
                world.hdri_path = None  # Will be handled by blend script

            logger.info(f"Using {len(layers)} HDRI(s) for realistic lighting")

        return lights, world

    def _generate_blender_lighting_script(
        self,
        lights: List[LightConfig],
        world: WorldConfig
    ) -> str:
        """
        Override script generation to include HDRI blending.

        Args:
            lights: List of light configurations
            world: World configuration

        Returns:
            Enhanced Blender Python script
        """
        # Check if we have HDRI blend layers
        if hasattr(world, 'hdri_blend_layers') and world.hdri_blend_layers:
            # Generate blend script
            logger.debug("Generating HDRI blend script")

            # Get base lighting script (without world setup)
            base_script = self._generate_base_lights_script(lights)

            # Generate HDRI blend script
            blend_script = self.hdri_manager.generate_blend_script(
                world.hdri_blend_layers,
                world_strength=world.strength
            )

            # Combine scripts
            return base_script + "\n" + blend_script

        else:
            # Use base script generation
            return super()._generate_blender_lighting_script(lights, world)

    def _generate_base_lights_script(self, lights: List[LightConfig]) -> str:
        """
        Generate script for just the lights (without world setup).

        Args:
            lights: List of light configurations

        Returns:
            Blender Python script for lights only
        """
        script = """
# Lighting Setup
import bpy
import math

# Clear existing lights
for obj in bpy.data.objects:
    if obj.type == 'LIGHT':
        bpy.data.objects.remove(obj, do_unlink=True)

"""

        # Add lights
        for light in lights:
            script += f"""
# Create {light.name} ({light.type})
light_data = bpy.data.lights.new(name='{light.name}', type='{light.type}')
light_data.energy = {light.energy}
light_data.color = {light.color}
light_data.shadow_soft_size = {light.shadow_soft_size}

"""
            if light.type == 'AREA':
                script += f"light_data.size = {light.size}\n"
            elif light.type == 'SPOT':
                script += f"light_data.spot_size = {light.angle}\n"

            script += f"""
light_obj = bpy.data.objects.new(name='{light.name}', object_data=light_data)
bpy.context.collection.objects.link(light_obj)
light_obj.location = {light.location}
light_obj.rotation_euler = {light.rotation}

"""

        return script

    def get_hdri_info(self) -> Dict[str, Any]:
        """
        Get information about available HDRIs.

        Returns:
            Dictionary with HDRI statistics and capabilities
        """
        return {
            'total_hdris': len(self.hdri_manager.available_hdris),
            'blending_enabled': self.enable_hdri_blending,
            'max_layers': self.max_hdri_layers,
            'blend_mode': self.hdri_blend_mode,
            'mood_mappings': list(self.hdri_manager.MOOD_TAG_MAP.keys()),
            'time_of_day_options': list(self.hdri_manager.TIME_OF_DAY_TAGS.keys()),
            'environment_types': list(self.hdri_manager.ENVIRONMENT_CATEGORIES.keys()),
        }


# Example usage and testing
if __name__ == "__main__":
    from utils.logger import setup_logging
    import json

    setup_logging(level="INFO", console=True)

    print("\n" + "="*80)
    print("ENHANCED LIGHTING AI - TEST SUITE")
    print("="*80 + "\n")

    # Initialize enhanced lighting AI
    config = {
        'registry_path': 'data/voxel_assets.db',
        'enable_hdri_blending': True,
        'max_hdri_layers': 2,
        'hdri_blend_mode': 'layered',
    }

    lighting_ai = LightingAIEnhanced(config)

    # Test 1: Get HDRI info
    print("Test 1: HDRI Capabilities")
    print("-" * 40)
    info = lighting_ai.get_hdri_info()
    print(f"Total HDRIs: {info['total_hdris']}")
    print(f"Blending enabled: {info['blending_enabled']}")
    print(f"Max layers: {info['max_layers']}")
    print(f"Supported moods: {', '.join(info['mood_mappings'][:5])}...")

    # Test 2: Apply lighting with HDRI selection
    print("\nTest 2: Apply Enhanced Lighting")
    print("-" * 40)

    test_scene = {
        'objects': [
            {
                'name': 'cube',
                'vertices': [
                    [-1, -1, 0], [1, -1, 0], [1, 1, 0], [-1, 1, 0],
                    [-1, -1, 2], [1, -1, 2], [1, 1, 2], [-1, 1, 2]
                ]
            }
        ],
        'interpreted_prompt': {
            'mood': {'cozy': 0.8, 'warm': 0.6},
            'time_of_day': 'sunset',
            'environment': 'indoor',
        },
        'style': 'realistic'
    }

    result = lighting_ai.apply(test_scene, style='realistic')
    print(f"Lighting mode: {result['lighting']['mode']}")
    print(f"Number of lights: {len(result['lighting']['lights'])}")

    if 'hdri_blend' in result['lighting']:
        blend_info = result['lighting']['hdri_blend']
        print(f"HDRI blending: {blend_info['enabled']}")
        print(f"HDRI layers: {blend_info['num_layers']}")
        print(f"HDRIs used: {', '.join(blend_info['hdris'])}")

    # Test 3: Generate script
    print("\nTest 3: Generated Blender Script")
    print("-" * 40)
    script = result['lighting']['blender_script']
    print(f"Script length: {len(script)} characters")
    print("First 400 characters:")
    print(script[:400] + "...")

    # Test 4: Different moods
    print("\nTest 4: Different Mood Lighting")
    print("-" * 40)

    moods_to_test = ['dramatic', 'peaceful', 'energetic']

    for mood_name in moods_to_test:
        test_scene_mood = {
            'objects': test_scene['objects'],
            'interpreted_prompt': {
                'mood': {mood_name: 1.0},
                'time_of_day': 'noon',
                'environment': 'outdoor',
            },
            'style': 'realistic'
        }

        result_mood = lighting_ai.apply(test_scene_mood, style='realistic')

        if 'hdri_blend' in result_mood['lighting']:
            blend = result_mood['lighting']['hdri_blend']
            print(f"{mood_name.capitalize()}: {blend['num_layers']} HDRIs - {', '.join(blend['hdris'])}")

    print("\n" + "="*80)
    print("TEST SUITE COMPLETE")
    print("="*80 + "\n")
