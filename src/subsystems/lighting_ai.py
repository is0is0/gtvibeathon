"""
Lighting AI
----------
Intelligent lighting system for dynamic scene illumination.

Automatically configures lighting based on scene context, style, and mood.
Supports realistic HDRI lighting, stylized setups, and custom configurations.
"""

import math
import random
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class LightConfig:
    """Configuration for a single light."""
    name: str
    type: str  # 'SUN', 'POINT', 'SPOT', 'AREA'
    location: Tuple[float, float, float] = (0.0, 0.0, 5.0)
    rotation: Tuple[float, float, float] = (0.0, 0.0, 0.0)  # Euler angles in radians
    energy: float = 1.0  # Light strength
    color: Tuple[float, float, float] = (1.0, 1.0, 1.0)  # RGB
    size: float = 0.5  # For AREA lights
    angle: float = math.pi / 4  # For SPOT lights (in radians)
    shadow_soft_size: float = 0.1  # Soft shadow size


@dataclass
class WorldConfig:
    """Configuration for world/environment lighting."""
    use_nodes: bool = True
    strength: float = 1.0
    color: Tuple[float, float, float] = (0.5, 0.5, 0.5)
    hdri_path: Optional[str] = None
    hdri_rotation: float = 0.0  # In radians
    use_sky_texture: bool = False
    sky_turbidity: float = 2.0
    ambient_occlusion: bool = True


class LightingAI:
    """
    AI-driven lighting analysis and setup system.

    Intelligently configures scene lighting based on:
    - Scene content and geometry
    - Visual style (realistic, stylized, etc.)
    - Mood and atmosphere
    - Time of day / environment context
    """

    # Lighting mode presets
    LIGHTING_MODES = {
        'realistic': {
            'description': 'HDRI environment lighting with natural shadows',
            'use_hdri': True,
            'use_sun': True,
            'ambient_strength': 0.3,
            'shadow_quality': 'high'
        },
        'stylized': {
            'description': 'Gradient/theatrical lighting with colored accents',
            'use_hdri': False,
            'use_three_point': True,
            'ambient_strength': 0.5,
            'color_variation': True
        },
        'studio': {
            'description': 'Professional three-point lighting setup',
            'use_hdri': False,
            'use_three_point': True,
            'ambient_strength': 0.2,
            'background_color': (0.8, 0.8, 0.8)
        },
        'cinematic': {
            'description': 'Dramatic high-contrast lighting',
            'use_hdri': False,
            'use_dramatic': True,
            'ambient_strength': 0.1,
            'high_contrast': True
        },
        'natural': {
            'description': 'Daylight simulation with sun',
            'use_hdri': False,
            'use_sun': True,
            'use_sky': True,
            'ambient_strength': 0.4
        },
        'custom': {
            'description': 'User-defined lighting configuration',
            'use_custom': True
        }
    }

    # Time of day lighting configurations
    TIME_OF_DAY_CONFIGS = {
        'sunrise': {
            'sun_color': (1.0, 0.8, 0.6),
            'sun_angle': (15.0, 0.0),  # degrees
            'ambient_color': (0.8, 0.7, 0.6),
            'strength_multiplier': 0.8
        },
        'noon': {
            'sun_color': (1.0, 1.0, 0.95),
            'sun_angle': (90.0, 0.0),
            'ambient_color': (0.7, 0.8, 1.0),
            'strength_multiplier': 1.2
        },
        'sunset': {
            'sun_color': (1.0, 0.6, 0.3),
            'sun_angle': (10.0, 0.0),
            'ambient_color': (1.0, 0.7, 0.5),
            'strength_multiplier': 0.9
        },
        'night': {
            'sun_color': (0.3, 0.3, 0.5),
            'sun_angle': (0.0, 0.0),
            'ambient_color': (0.1, 0.1, 0.2),
            'strength_multiplier': 0.1
        }
    }

    # Color temperature presets (in Kelvin, converted to RGB)
    COLOR_TEMPERATURES = {
        'candle': (1.0, 0.58, 0.33),      # 1850K
        'tungsten': (1.0, 0.78, 0.54),     # 2700K
        'warm_white': (1.0, 0.91, 0.82),   # 3500K
        'daylight': (1.0, 1.0, 0.98),      # 5500K
        'overcast': (0.78, 0.85, 1.0),     # 6500K
        'cool_white': (0.75, 0.82, 1.0),   # 7000K
        'moonlight': (0.6, 0.7, 1.0)       # 4100K
    }

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize lighting AI system.

        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.default_mode = self.config.get('default_mode', 'realistic')
        self.use_hdri = self.config.get('use_hdri', True)
        self.hdri_path = self.config.get('hdri_path', None)
        self.shadow_quality = self.config.get('shadow_quality', 'high')

        # Scene analysis cache
        self.scene_bounds = None
        self.scene_center = None
        self.num_objects = 0

        logger.info(f"Lighting AI initialized (mode: {self.default_mode}, HDRI: {self.use_hdri})")

    def apply(self, scene_data: Dict[str, Any], style: str = "realistic") -> Dict[str, Any]:
        """
        Apply intelligent lighting to scene.

        Args:
            scene_data: Scene data with objects
            style: Visual style for lighting

        Returns:
            Scene data with lighting configuration
        """
        logger.info(f"Applying lighting (style: {style})")

        # Analyze scene first
        analysis = self.analyze_scene(scene_data)

        # Determine lighting mode from style
        mode = self._style_to_mode(style)

        # Get mood-based adjustments
        mood = scene_data.get('interpreted_prompt', {}).get('mood', {})

        # Setup lighting based on mode
        lighting_config = self.setup_lighting(mode, analysis, mood)

        # Add lighting to scene data
        scene_data['lighting'] = lighting_config

        logger.info(f"Lighting applied: {len(lighting_config['lights'])} lights, mode: {mode}")

        return scene_data

    def analyze_scene(self, scene_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze scene geometry for intelligent light placement.

        Args:
            scene_data: Scene data with objects

        Returns:
            Analysis results including bounds, center, and recommendations
        """
        logger.info("Analyzing scene geometry for lighting")

        objects = scene_data.get('objects', [])
        self.num_objects = len(objects)

        if not objects:
            logger.warning("No objects in scene, using default bounds")
            return self._get_default_analysis()

        # Calculate scene bounds
        min_bounds = [float('inf'), float('inf'), float('inf')]
        max_bounds = [float('-inf'), float('-inf'), float('-inf')]

        for obj in objects:
            # Try to get bounds from object data
            vertices = obj.get('vertices', [])
            if vertices and len(vertices) > 0:
                for v in vertices:
                    for i in range(3):
                        min_bounds[i] = min(min_bounds[i], v[i])
                        max_bounds[i] = max(max_bounds[i], v[i])

        # If no vertices found, use default bounds
        if min_bounds[0] == float('inf'):
            logger.debug("No vertex data found, using default bounds")
            return self._get_default_analysis()

        # Calculate center and size
        center = [
            (min_bounds[i] + max_bounds[i]) / 2
            for i in range(3)
        ]
        size = [
            max_bounds[i] - min_bounds[i]
            for i in range(3)
        ]
        max_dimension = max(size)

        self.scene_bounds = (min_bounds, max_bounds)
        self.scene_center = center

        analysis = {
            'bounds': {'min': min_bounds, 'max': max_bounds},
            'center': center,
            'size': size,
            'max_dimension': max_dimension,
            'num_objects': self.num_objects,
            'recommended_light_distance': max_dimension * 2.0,
            'recommended_light_energy': max(1.0, max_dimension / 10.0)
        }

        logger.debug(f"Scene analysis: center={center}, size={size}, objects={self.num_objects}")

        return analysis

    def suggest_lighting_setup(
        self,
        scene_data: Dict[str, Any],
        style: str = "realistic"
    ) -> Dict[str, Any]:
        """
        Suggest optimal lighting setup for scene.

        Args:
            scene_data: Scene data
            style: Visual style

        Returns:
            Suggested lighting configuration
        """
        logger.info(f"Suggesting lighting setup for style: {style}")

        # Analyze scene
        analysis = self.analyze_scene(scene_data)

        # Get mood
        mood = scene_data.get('interpreted_prompt', {}).get('mood', {})

        # Determine mode
        mode = self._style_to_mode(style)

        # Get lighting preferences from prompt
        lighting_pref = scene_data.get('interpreted_prompt', {}).get('lighting', 'natural')

        suggestion = {
            'mode': mode,
            'style': style,
            'lighting_preference': lighting_pref,
            'mood': mood,
            'recommended_settings': self.LIGHTING_MODES[mode],
            'color_temperature': self._get_color_temperature(lighting_pref, mood)
        }

        logger.info(f"Suggested setup: mode={mode}, color_temp={suggestion['color_temperature']}")

        return suggestion

    def setup_lighting(
        self,
        mode: str,
        scene_context: Dict[str, Any],
        mood: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Setup lighting for scene based on mode and context.

        Args:
            mode: Lighting mode ('realistic', 'stylized', 'studio', etc.)
            scene_context: Scene analysis data
            mood: Optional mood descriptors

        Returns:
            Complete lighting configuration including lights and world settings
        """
        logger.info(f"Setting up lighting: mode={mode}")

        mood = mood or {}

        # Validate mode
        if mode not in self.LIGHTING_MODES:
            logger.warning(f"Unknown lighting mode '{mode}', using 'realistic'")
            mode = 'realistic'

        # Get mode configuration
        mode_config = self.LIGHTING_MODES[mode]

        # Initialize lighting configuration
        lights = []
        world_config = self._create_default_world_config()

        # Setup based on mode
        if mode == 'realistic':
            lights, world_config = self._setup_realistic_lighting(scene_context, mood)
        elif mode == 'stylized':
            lights, world_config = self._setup_stylized_lighting(scene_context, mood)
        elif mode == 'studio':
            lights, world_config = self._setup_studio_lighting(scene_context, mood)
        elif mode == 'cinematic':
            lights, world_config = self._setup_cinematic_lighting(scene_context, mood)
        elif mode == 'natural':
            lights, world_config = self._setup_natural_lighting(scene_context, mood)
        elif mode == 'custom':
            lights, world_config = self._setup_custom_lighting(scene_context, mood)

        # Generate Blender scripts
        lighting_config = {
            'mode': mode,
            'style': mode_config['description'],
            'lights': [self._light_to_dict(light) for light in lights],
            'world': self._world_to_dict(world_config),
            'blender_script': self._generate_blender_lighting_script(lights, world_config)
        }

        logger.info(f"Lighting setup complete: {len(lights)} lights")

        return lighting_config

    def auto_place_lights(
        self,
        scene_data: Dict[str, Any],
        num_lights: int = 3
    ) -> List[LightConfig]:
        """
        Automatically place lights around scene.

        Args:
            scene_data: Scene data
            num_lights: Number of lights to place

        Returns:
            List of light configurations
        """
        logger.info(f"Auto-placing {num_lights} lights")

        analysis = self.analyze_scene(scene_data)
        center = analysis['center']
        distance = analysis['recommended_light_distance']
        energy = analysis['recommended_light_energy']

        lights = []

        for i in range(num_lights):
            angle = (2 * math.pi * i) / num_lights

            location = (
                center[0] + distance * math.cos(angle),
                center[1] + distance * math.sin(angle),
                center[2] + distance * 0.5
            )

            light = LightConfig(
                name=f'Light_{i+1}',
                type='POINT',
                location=location,
                energy=energy,
                color=(1.0, 1.0, 1.0)
            )
            lights.append(light)

        logger.debug(f"Placed {len(lights)} lights around scene")

        return lights

    def calculate_exposure(self, scene_data: Dict[str, Any]) -> float:
        """
        Calculate optimal exposure for scene.

        Args:
            scene_data: Scene data with lighting

        Returns:
            Exposure value
        """
        logger.debug("Calculating optimal exposure")

        # Simple heuristic based on number of lights and their energy
        lights = scene_data.get('lighting', {}).get('lights', [])

        if not lights:
            return 1.0

        total_energy = sum(light.get('energy', 1.0) for light in lights)
        avg_energy = total_energy / len(lights)

        # Exposure inversely proportional to average energy
        exposure = max(0.1, min(2.0, 1.0 / avg_energy))

        logger.debug(f"Calculated exposure: {exposure:.2f}")

        return exposure

    def optimize_shadows(
        self,
        scene_data: Dict[str, Any],
        quality: str = 'balanced'
    ) -> Dict[str, Any]:
        """
        Optimize shadow settings for performance vs quality.

        Args:
            scene_data: Scene data
            quality: Quality preset ('draft', 'balanced', 'final')

        Returns:
            Shadow optimization settings
        """
        logger.info(f"Optimizing shadows (quality: {quality})")

        quality_presets = {
            'draft': {
                'use_shadows': True,
                'shadow_method': 'NOSHADOW',
                'shadow_buffer_size': 512,
                'shadow_samples': 1
            },
            'balanced': {
                'use_shadows': True,
                'shadow_method': 'RAY_SHADOW',
                'shadow_buffer_size': 2048,
                'shadow_samples': 4,
                'soft_shadows': True
            },
            'final': {
                'use_shadows': True,
                'shadow_method': 'RAY_SHADOW',
                'shadow_buffer_size': 4096,
                'shadow_samples': 16,
                'soft_shadows': True,
                'shadow_transparency': True
            }
        }

        settings = quality_presets.get(quality, quality_presets['balanced'])

        logger.debug(f"Shadow settings: {settings}")

        return settings

    # Private helper methods

    def _setup_realistic_lighting(
        self,
        scene_context: Dict[str, Any],
        mood: Dict[str, Any]
    ) -> Tuple[List[LightConfig], WorldConfig]:
        """Setup realistic HDRI-based lighting."""
        logger.debug("Setting up realistic lighting")

        center = scene_context['center']
        distance = scene_context['recommended_light_distance']

        lights = []

        # Add sun light
        sun = LightConfig(
            name='Sun',
            type='SUN',
            location=(center[0] + distance, center[1] + distance, center[2] + distance),
            rotation=(math.radians(45), 0, math.radians(45)),
            energy=5.0,
            color=(1.0, 1.0, 0.98),
            shadow_soft_size=0.1
        )
        lights.append(sun)

        # World configuration with HDRI
        world = WorldConfig(
            use_nodes=True,
            strength=1.0,
            hdri_path=self.hdri_path,
            ambient_occlusion=True
        )

        return lights, world

    def _setup_stylized_lighting(
        self,
        scene_context: Dict[str, Any],
        mood: Dict[str, Any]
    ) -> Tuple[List[LightConfig], WorldConfig]:
        """Setup stylized/theatrical lighting."""
        logger.debug("Setting up stylized lighting")

        center = scene_context['center']
        distance = scene_context['recommended_light_distance']

        lights = []

        # Colorful spotlights
        colors = [
            (1.0, 0.3, 0.3),  # Red
            (0.3, 0.3, 1.0),  # Blue
            (0.3, 1.0, 0.3),  # Green
        ]

        for i, color in enumerate(colors):
            angle = (2 * math.pi * i) / len(colors)

            location = (
                center[0] + distance * math.cos(angle),
                center[1] + distance * math.sin(angle),
                center[2] + distance * 0.7
            )

            # Calculate rotation to point at center
            rotation = (
                math.radians(45),
                0,
                angle + math.pi
            )

            light = LightConfig(
                name=f'Spot_{i+1}',
                type='SPOT',
                location=location,
                rotation=rotation,
                energy=100.0,
                color=color,
                angle=math.radians(60),
                shadow_soft_size=0.5
            )
            lights.append(light)

        # Gradient background
        world = WorldConfig(
            use_nodes=True,
            strength=0.5,
            color=(0.2, 0.2, 0.3),
            ambient_occlusion=False
        )

        return lights, world

    def _setup_studio_lighting(
        self,
        scene_context: Dict[str, Any],
        mood: Dict[str, Any]
    ) -> Tuple[List[LightConfig], WorldConfig]:
        """Setup three-point studio lighting."""
        logger.debug("Setting up studio lighting")

        center = scene_context['center']
        distance = scene_context['recommended_light_distance']

        lights = []

        # Key light (main light, 45 degrees)
        key_light = LightConfig(
            name='Key_Light',
            type='AREA',
            location=(center[0] + distance * 0.7, center[1] - distance * 0.7, center[2] + distance),
            rotation=(math.radians(45), 0, math.radians(-45)),
            energy=200.0,
            color=(1.0, 1.0, 1.0),
            size=2.0
        )
        lights.append(key_light)

        # Fill light (softer, opposite side)
        fill_light = LightConfig(
            name='Fill_Light',
            type='AREA',
            location=(center[0] - distance * 0.7, center[1] + distance * 0.5, center[2] + distance * 0.8),
            rotation=(math.radians(30), 0, math.radians(135)),
            energy=100.0,
            color=(1.0, 1.0, 1.0),
            size=3.0
        )
        lights.append(fill_light)

        # Back light (rim light)
        back_light = LightConfig(
            name='Back_Light',
            type='POINT',
            location=(center[0], center[1] + distance, center[2] + distance * 0.5),
            energy=150.0,
            color=(1.0, 0.95, 0.9)
        )
        lights.append(back_light)

        # Neutral background
        world = WorldConfig(
            use_nodes=True,
            strength=0.2,
            color=(0.8, 0.8, 0.8),
            ambient_occlusion=True
        )

        return lights, world

    def _setup_cinematic_lighting(
        self,
        scene_context: Dict[str, Any],
        mood: Dict[str, Any]
    ) -> Tuple[List[LightConfig], WorldConfig]:
        """Setup dramatic cinematic lighting."""
        logger.debug("Setting up cinematic lighting")

        center = scene_context['center']
        distance = scene_context['recommended_light_distance']

        lights = []

        # Strong key light (high contrast)
        key_light = LightConfig(
            name='Dramatic_Key',
            type='SPOT',
            location=(center[0] + distance, center[1] - distance * 0.5, center[2] + distance * 1.5),
            rotation=(math.radians(60), 0, math.radians(-30)),
            energy=500.0,
            color=(1.0, 0.9, 0.8),
            angle=math.radians(40),
            shadow_soft_size=0.3
        )
        lights.append(key_light)

        # Subtle rim light
        rim_light = LightConfig(
            name='Rim_Light',
            type='POINT',
            location=(center[0] - distance * 0.5, center[1] + distance, center[2] + distance),
            energy=100.0,
            color=(0.8, 0.9, 1.0)
        )
        lights.append(rim_light)

        # Dark background
        world = WorldConfig(
            use_nodes=True,
            strength=0.05,
            color=(0.05, 0.05, 0.1),
            ambient_occlusion=True
        )

        return lights, world

    def _setup_natural_lighting(
        self,
        scene_context: Dict[str, Any],
        mood: Dict[str, Any]
    ) -> Tuple[List[LightConfig], WorldConfig]:
        """Setup natural daylight simulation."""
        logger.debug("Setting up natural lighting")

        center = scene_context['center']
        distance = scene_context['recommended_light_distance']

        lights = []

        # Sun with sky texture
        sun = LightConfig(
            name='Sun',
            type='SUN',
            location=(center[0], center[1], center[2] + distance * 2),
            rotation=(math.radians(60), 0, 0),
            energy=3.0,
            color=(1.0, 1.0, 0.98),
            shadow_soft_size=0.05
        )
        lights.append(sun)

        # Sky texture background
        world = WorldConfig(
            use_nodes=True,
            strength=1.0,
            use_sky_texture=True,
            sky_turbidity=2.0,
            ambient_occlusion=True
        )

        return lights, world

    def _setup_custom_lighting(
        self,
        scene_context: Dict[str, Any],
        mood: Dict[str, Any]
    ) -> Tuple[List[LightConfig], WorldConfig]:
        """Setup custom user-defined lighting."""
        logger.debug("Setting up custom lighting")

        # Use config values or defaults
        custom_config = self.config.get('custom_lighting', {})

        center = scene_context['center']
        distance = scene_context['recommended_light_distance']

        lights = []

        # Default to single point light if no custom config
        light = LightConfig(
            name='Custom_Light',
            type=custom_config.get('type', 'POINT'),
            location=custom_config.get('location', (center[0], center[1], center[2] + distance)),
            energy=custom_config.get('energy', 100.0),
            color=tuple(custom_config.get('color', [1.0, 1.0, 1.0]))
        )
        lights.append(light)

        world = WorldConfig(
            use_nodes=True,
            strength=custom_config.get('ambient_strength', 0.5),
            color=tuple(custom_config.get('ambient_color', [0.5, 0.5, 0.5]))
        )

        return lights, world

    def _style_to_mode(self, style: str) -> str:
        """Convert visual style to lighting mode."""
        style_mapping = {
            'realistic': 'realistic',
            'photorealistic': 'realistic',
            'stylized': 'stylized',
            'modern': 'studio',
            'minimalist': 'studio',
            'vintage': 'cinematic',
            'fantasy': 'stylized',
            'futuristic': 'stylized',
            'industrial': 'cinematic'
        }

        return style_mapping.get(style, 'realistic')

    def _get_color_temperature(
        self,
        lighting_pref: str,
        mood: Dict[str, Any]
    ) -> str:
        """Get color temperature based on preferences and mood."""
        # Map lighting preferences to color temperature
        pref_mapping = {
            'warm': 'tungsten',
            'cool': 'cool_white',
            'natural': 'daylight',
            'dramatic': 'tungsten',
            'soft': 'warm_white'
        }

        # Check mood for temperature hints
        if 'cozy' in mood:
            return 'tungsten'
        elif 'energetic' in mood:
            return 'daylight'
        elif 'peaceful' in mood:
            return 'warm_white'

        return pref_mapping.get(lighting_pref, 'daylight')

    def _get_default_analysis(self) -> Dict[str, Any]:
        """Get default scene analysis for empty scenes."""
        return {
            'bounds': {'min': [-5, -5, 0], 'max': [5, 5, 5]},
            'center': [0, 0, 2.5],
            'size': [10, 10, 5],
            'max_dimension': 10,
            'num_objects': 0,
            'recommended_light_distance': 20.0,
            'recommended_light_energy': 1.0
        }

    def _create_default_world_config(self) -> WorldConfig:
        """Create default world configuration."""
        return WorldConfig(
            use_nodes=True,
            strength=1.0,
            color=(0.5, 0.5, 0.5),
            ambient_occlusion=True
        )

    def _light_to_dict(self, light: LightConfig) -> Dict[str, Any]:
        """Convert LightConfig to dictionary."""
        return {
            'name': light.name,
            'type': light.type,
            'location': list(light.location),
            'rotation': list(light.rotation),
            'energy': light.energy,
            'color': list(light.color),
            'size': light.size,
            'angle': light.angle,
            'shadow_soft_size': light.shadow_soft_size
        }

    def _world_to_dict(self, world: WorldConfig) -> Dict[str, Any]:
        """Convert WorldConfig to dictionary."""
        return {
            'use_nodes': world.use_nodes,
            'strength': world.strength,
            'color': list(world.color),
            'hdri_path': world.hdri_path,
            'hdri_rotation': world.hdri_rotation,
            'use_sky_texture': world.use_sky_texture,
            'sky_turbidity': world.sky_turbidity,
            'ambient_occlusion': world.ambient_occlusion
        }

    def _generate_blender_lighting_script(
        self,
        lights: List[LightConfig],
        world: WorldConfig
    ) -> str:
        """Generate Blender Python script for lighting setup."""
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

        # Setup world
        script += f"""
# Setup World/Environment
world = bpy.context.scene.world
if not world:
    world = bpy.data.worlds.new("World")
    bpy.context.scene.world = world

world.use_nodes = {world.use_nodes}

if world.use_nodes:
    nodes = world.node_tree.nodes
    links = world.node_tree.links

    # Clear existing nodes
    nodes.clear()

    # Create Background shader
    bg = nodes.new(type='ShaderNodeBackground')
    bg.location = (0, 0)
    bg.inputs['Strength'].default_value = {world.strength}
    bg.inputs['Color'].default_value = {list(world.color) + [1.0]}

    # Create World Output
    output = nodes.new(type='ShaderNodeOutputWorld')
    output.location = (300, 0)

    # Link Background to output
    links.new(bg.outputs['Background'], output.inputs['Surface'])
"""

        # Add HDRI if specified
        if world.hdri_path:
            script += f"""
    # Add HDRI Environment Texture
    tex_coord = nodes.new(type='ShaderNodeTexCoord')
    tex_coord.location = (-600, 0)

    mapping = nodes.new(type='ShaderNodeMapping')
    mapping.location = (-400, 0)
    mapping.inputs['Rotation'].default_value[2] = {world.hdri_rotation}
    links.new(tex_coord.outputs['Generated'], mapping.inputs['Vector'])

    env_tex = nodes.new(type='ShaderNodeTexEnvironment')
    env_tex.location = (-200, 0)
    try:
        env_tex.image = bpy.data.images.load("{world.hdri_path}")
    except:
        print("Warning: Could not load HDRI texture")
    links.new(mapping.outputs['Vector'], env_tex.inputs['Vector'])
    links.new(env_tex.outputs['Color'], bg.inputs['Color'])
"""

        # Add sky texture if specified
        if world.use_sky_texture:
            script += f"""
    # Add Sky Texture
    sky_tex = nodes.new(type='ShaderNodeTexSky')
    sky_tex.location = (-200, 0)
    sky_tex.sky_type = 'NISHITA'
    sky_tex.turbidity = {world.sky_turbidity}
    links.new(sky_tex.outputs['Color'], bg.inputs['Color'])
"""

        script += """
print("Lighting setup complete")
"""

        return script


# Example usage and testing
if __name__ == "__main__":
    from utils.logger import setup_logging

    # Setup logging
    setup_logging(level="DEBUG", console=True)

    # Create lighting AI
    lighting_ai = LightingAI()

    print("\n" + "="*80)
    print("LIGHTING AI - TEST SUITE")
    print("="*80 + "\n")

    # Test 1: Lighting modes
    print("\n" + "="*80)
    print("Test 1: Available Lighting Modes")
    print("="*80 + "\n")

    for mode, config in lighting_ai.LIGHTING_MODES.items():
        print(f"{mode.upper()}:")
        print(f"  {config['description']}")

    # Test 2: Scene analysis
    print("\n" + "="*80)
    print("Test 2: Scene Analysis")
    print("="*80 + "\n")

    test_scene = {
        'objects': [
            {
                'name': 'cube',
                'vertices': [
                    [-1, -1, 0], [1, -1, 0], [1, 1, 0], [-1, 1, 0],
                    [-1, -1, 2], [1, -1, 2], [1, 1, 2], [-1, 1, 2]
                ]
            }
        ]
    }

    analysis = lighting_ai.analyze_scene(test_scene)
    print(f"Scene Center: {analysis['center']}")
    print(f"Scene Size: {analysis['size']}")
    print(f"Recommended Light Distance: {analysis['recommended_light_distance']:.2f}")

    # Test 3: Setup different lighting modes
    print("\n" + "="*80)
    print("Test 3: Setup Lighting Modes")
    print("="*80 + "\n")

    for mode in ['realistic', 'stylized', 'studio']:
        print(f"\n{mode.upper()} MODE:")
        config = lighting_ai.setup_lighting(mode, analysis, {})
        print(f"  Lights: {len(config['lights'])}")
        for light in config['lights']:
            print(f"    - {light['name']} ({light['type']}): energy={light['energy']}")

    # Test 4: Apply to scene
    print("\n" + "="*80)
    print("Test 4: Apply Lighting to Scene")
    print("="*80 + "\n")

    test_scene['interpreted_prompt'] = {
        'lighting': 'warm',
        'mood': {'cozy': 0.8}
    }

    result = lighting_ai.apply(test_scene, style='realistic')
    print(f"Lighting applied: {result['lighting']['mode']}")
    print(f"Number of lights: {len(result['lighting']['lights'])}")
    print(f"World strength: {result['lighting']['world']['strength']}")

    # Test 5: Generate Blender script
    print("\n" + "="*80)
    print("Test 5: Generate Blender Script")
    print("="*80 + "\n")

    script = result['lighting']['blender_script']
    print("Generated Blender script (first 500 chars):")
    print(script[:500])

    print("\n" + "="*80)
    print("TEST SUITE COMPLETE")
    print("="*80 + "\n")
