"""
Lighting Engine Module
----------------------
Handles scene lighting and illumination for realistic and stylized renders.

This module provides comprehensive lighting solutions including HDRI environments,
three-point lighting setups, volumetric effects, and style-specific lighting.
"""

import logging
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

logger = logging.getLogger(__name__)


class LightType(Enum):
    """Types of lights available."""
    POINT = "point"  # Omnidirectional point light
    SUN = "sun"  # Directional light (infinite distance)
    SPOT = "spot"  # Spotlight with cone
    AREA = "area"  # Area light (rectangular/circular)
    HDRI = "hdri"  # HDRI environment map


class LightingStyle(Enum):
    """Lighting style presets."""
    REALISTIC = "realistic"  # Photorealistic lighting
    STYLIZED = "stylized"  # Artistic/stylized lighting
    CINEMATIC = "cinematic"  # Cinematic three-point lighting
    STUDIO = "studio"  # Studio product photography
    DRAMATIC = "dramatic"  # High contrast dramatic lighting
    AMBIENT = "ambient"  # Soft ambient lighting
    NATURAL = "natural"  # Natural outdoor lighting


@dataclass
class Light:
    """Represents a light source."""
    name: str
    light_type: LightType
    position: Tuple[float, float, float]
    rotation: Tuple[float, float, float]  # Euler angles in radians
    color: Tuple[float, float, float]  # RGB 0-1
    energy: float  # Light intensity
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'name': self.name,
            'type': self.light_type.value,
            'position': list(self.position),
            'rotation': list(self.rotation),
            'color': list(self.color),
            'energy': self.energy,
            'metadata': self.metadata
        }


@dataclass
class LightingSetup:
    """Complete lighting setup for a scene."""
    lights: List[Light]
    hdri_path: Optional[str]
    hdri_strength: float
    ambient_color: Tuple[float, float, float]
    ambient_strength: float
    volumetric_enabled: bool
    volumetric_density: float
    style: LightingStyle

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'lights': [light.to_dict() for light in self.lights],
            'hdri': {
                'path': self.hdri_path,
                'strength': self.hdri_strength
            },
            'ambient': {
                'color': list(self.ambient_color),
                'strength': self.ambient_strength
            },
            'volumetric': {
                'enabled': self.volumetric_enabled,
                'density': self.volumetric_density
            },
            'style': self.style.value
        }


class LightingEngine:
    """
    Handles scene lighting and illumination.

    This class creates and manages lighting setups for various styles,
    from realistic photographic lighting to stylized artistic effects.

    Example:
        >>> engine = LightingEngine()
        >>> scene = {"objects": [...]}
        >>> lit_scene = engine.apply(scene, style="realistic")
        >>> print(f"Added {len(lit_scene['lighting']['lights'])} lights")
    """

    def __init__(
        self,
        hdri_library: Optional[Path] = None,
        default_style: LightingStyle = LightingStyle.REALISTIC
    ):
        """
        Initialize lighting engine.

        Args:
            hdri_library: Path to HDRI library directory
            default_style: Default lighting style
        """
        self.hdri_library = hdri_library or Path("assets/hdri")
        self.default_style = default_style

        # Color temperature presets (in RGB 0-1)
        self.color_temperatures = {
            'warm': (1.0, 0.9, 0.7),
            'neutral': (1.0, 1.0, 1.0),
            'cool': (0.7, 0.9, 1.0),
            'daylight': (1.0, 0.98, 0.95),
            'tungsten': (1.0, 0.8, 0.4),
            'fluorescent': (0.9, 0.95, 1.0),
            'candlelight': (1.0, 0.7, 0.3)
        }

        logger.info(f"LightingEngine initialized with {default_style.value} style")

    def apply(
        self,
        scene: Dict[str, Any],
        style: Optional[str] = None,
        custom_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Apply lighting to a scene.

        This is the main entry point for lighting application. It analyzes
        the scene and creates an appropriate lighting setup.

        Args:
            scene: Scene data with objects
            style: Lighting style ('realistic', 'stylized', 'cinematic', etc.)
            custom_config: Optional custom lighting configuration

        Returns:
            Scene with lighting data added

        Example:
            >>> engine = LightingEngine()
            >>> scene = {"objects": [{"name": "table", ...}]}
            >>> lit_scene = engine.apply(scene, style="cinematic")
            >>> print(lit_scene['lighting']['lights'])
        """
        logger.info(f"Applying lighting to scene (style: {style})")

        # Parse style
        lighting_style = self._parse_style(style)

        # Analyze scene
        scene_analysis = self._analyze_scene(scene)

        # Create lighting setup based on style
        if custom_config:
            lighting_setup = self._create_custom_lighting(scene_analysis, custom_config)
        else:
            lighting_setup = self._create_style_lighting(scene_analysis, lighting_style)

        # Apply lighting to scene
        lit_scene = scene.copy()
        lit_scene['lighting'] = lighting_setup.to_dict()

        # Add lighting metadata
        lit_scene['metadata'] = lit_scene.get('metadata', {})
        lit_scene['metadata']['lighting_style'] = lighting_style.value
        lit_scene['metadata']['light_count'] = len(lighting_setup.lights)

        logger.info(f"Applied {len(lighting_setup.lights)} lights to scene")

        return lit_scene

    def _parse_style(self, style: Optional[str]) -> LightingStyle:
        """
        Parse lighting style string to enum.

        Args:
            style: Style string

        Returns:
            LightingStyle enum
        """
        if not style:
            return self.default_style

        style_lower = style.lower()
        for lighting_style in LightingStyle:
            if lighting_style.value == style_lower:
                return lighting_style

        logger.warning(f"Unknown lighting style '{style}', using default")
        return self.default_style

    def _analyze_scene(self, scene: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze scene to determine lighting requirements.

        Args:
            scene: Scene data

        Returns:
            Scene analysis data
        """
        objects = scene.get('objects', [])

        # Calculate scene bounds
        all_positions = []
        for obj in objects:
            if 'position' in obj:
                all_positions.append(obj['position'])
            elif 'bounding_box' in obj:
                all_positions.append(obj['bounding_box'].get('center', [0, 0, 0]))

        if all_positions:
            positions_array = np.array(all_positions)
            scene_center = positions_array.mean(axis=0)
            scene_bounds = {
                'min': positions_array.min(axis=0).tolist(),
                'max': positions_array.max(axis=0).tolist(),
                'center': scene_center.tolist()
            }
            scene_size = positions_array.max(axis=0) - positions_array.min(axis=0)
            scene_radius = float(np.linalg.norm(scene_size) / 2)
        else:
            scene_bounds = {
                'min': [-5, 0, -5],
                'max': [5, 5, 5],
                'center': [0, 2.5, 0]
            }
            scene_radius = 5.0

        return {
            'object_count': len(objects),
            'bounds': scene_bounds,
            'radius': scene_radius,
            'categories': self._extract_categories(objects)
        }

    def _extract_categories(self, objects: List[Dict[str, Any]]) -> Dict[str, int]:
        """Extract object category counts."""
        categories = {}
        for obj in objects:
            category = obj.get('category', obj.get('type', 'generic'))
            categories[category] = categories.get(category, 0) + 1
        return categories

    def _create_style_lighting(
        self,
        analysis: Dict[str, Any],
        style: LightingStyle
    ) -> LightingSetup:
        """
        Create lighting setup for a specific style.

        Args:
            analysis: Scene analysis
            style: Lighting style

        Returns:
            LightingSetup instance
        """
        logger.info(f"Creating {style.value} lighting setup")

        if style == LightingStyle.REALISTIC:
            return self._create_realistic_lighting(analysis)
        elif style == LightingStyle.STYLIZED:
            return self._create_stylized_lighting(analysis)
        elif style == LightingStyle.CINEMATIC:
            return self._create_cinematic_lighting(analysis)
        elif style == LightingStyle.STUDIO:
            return self._create_studio_lighting(analysis)
        elif style == LightingStyle.DRAMATIC:
            return self._create_dramatic_lighting(analysis)
        elif style == LightingStyle.AMBIENT:
            return self._create_ambient_lighting(analysis)
        elif style == LightingStyle.NATURAL:
            return self._create_natural_lighting(analysis)
        else:
            return self._create_realistic_lighting(analysis)

    def _create_realistic_lighting(self, analysis: Dict[str, Any]) -> LightingSetup:
        """Create realistic photographic lighting."""
        center = analysis['bounds']['center']
        radius = analysis['radius']

        lights = []

        # Sun light (key light)
        lights.append(Light(
            name="Sun",
            light_type=LightType.SUN,
            position=(radius * 2, radius * 3, radius * 2),
            rotation=(np.radians(-45), np.radians(45), 0),
            color=self.color_temperatures['daylight'],
            energy=5.0,
            metadata={'role': 'key'}
        ))

        # HDRI environment
        hdri_path = self._find_hdri('outdoor')

        return LightingSetup(
            lights=lights,
            hdri_path=hdri_path,
            hdri_strength=1.0,
            ambient_color=(0.1, 0.1, 0.15),
            ambient_strength=0.3,
            volumetric_enabled=True,
            volumetric_density=0.01,
            style=LightingStyle.REALISTIC
        )

    def _create_stylized_lighting(self, analysis: Dict[str, Any]) -> LightingSetup:
        """Create stylized artistic lighting."""
        center = analysis['bounds']['center']
        radius = analysis['radius']

        lights = []

        # Colorful key light
        lights.append(Light(
            name="KeyLight",
            light_type=LightType.AREA,
            position=(radius * 1.5, radius * 2, radius * 1.5),
            rotation=(np.radians(-45), np.radians(45), 0),
            color=(1.0, 0.8, 0.9),
            energy=150.0,
            metadata={'role': 'key', 'size': 2.0}
        ))

        # Rim light with color
        lights.append(Light(
            name="RimLight",
            light_type=LightType.POINT,
            position=(-radius * 1.5, radius, -radius * 1.5),
            rotation=(0, 0, 0),
            color=(0.6, 0.8, 1.0),
            energy=100.0,
            metadata={'role': 'rim'}
        ))

        return LightingSetup(
            lights=lights,
            hdri_path=None,
            hdri_strength=0.5,
            ambient_color=(0.2, 0.15, 0.25),
            ambient_strength=0.5,
            volumetric_enabled=True,
            volumetric_density=0.05,
            style=LightingStyle.STYLIZED
        )

    def _create_cinematic_lighting(self, analysis: Dict[str, Any]) -> LightingSetup:
        """Create three-point cinematic lighting."""
        center = analysis['bounds']['center']
        radius = analysis['radius']

        lights = []

        # Key light
        lights.append(Light(
            name="KeyLight",
            light_type=LightType.AREA,
            position=(radius * 2, radius * 2.5, radius * 2),
            rotation=(np.radians(-50), np.radians(45), 0),
            color=self.color_temperatures['warm'],
            energy=200.0,
            metadata={'role': 'key', 'size': 3.0}
        ))

        # Fill light
        lights.append(Light(
            name="FillLight",
            light_type=LightType.AREA,
            position=(-radius * 1.5, radius * 1.5, radius),
            rotation=(np.radians(-30), np.radians(-45), 0),
            color=self.color_temperatures['cool'],
            energy=80.0,
            metadata={'role': 'fill', 'size': 2.0}
        ))

        # Back/rim light
        lights.append(Light(
            name="RimLight",
            light_type=LightType.SPOT,
            position=(0, radius * 2, -radius * 2),
            rotation=(np.radians(-45), 0, 0),
            color=(1.0, 1.0, 1.0),
            energy=150.0,
            metadata={'role': 'rim', 'spot_size': np.radians(60), 'blend': 0.15}
        ))

        return LightingSetup(
            lights=lights,
            hdri_path=self._find_hdri('studio'),
            hdri_strength=0.3,
            ambient_color=(0.05, 0.05, 0.08),
            ambient_strength=0.2,
            volumetric_enabled=True,
            volumetric_density=0.02,
            style=LightingStyle.CINEMATIC
        )

    def _create_studio_lighting(self, analysis: Dict[str, Any]) -> LightingSetup:
        """Create studio product photography lighting."""
        center = analysis['bounds']['center']
        radius = analysis['radius']

        lights = []

        # Main light (large softbox)
        lights.append(Light(
            name="MainLight",
            light_type=LightType.AREA,
            position=(radius * 1.5, radius * 2, radius * 2),
            rotation=(np.radians(-45), np.radians(30), 0),
            color=(1.0, 1.0, 1.0),
            energy=250.0,
            metadata={'role': 'key', 'size': 4.0}
        ))

        # Fill light (large softbox)
        lights.append(Light(
            name="FillLight",
            light_type=LightType.AREA,
            position=(-radius * 1.5, radius * 1.5, radius),
            rotation=(np.radians(-30), np.radians(-30), 0),
            color=(1.0, 1.0, 1.0),
            energy=120.0,
            metadata={'role': 'fill', 'size': 3.0}
        ))

        # Top light
        lights.append(Light(
            name="TopLight",
            light_type=LightType.AREA,
            position=(0, radius * 3, 0),
            rotation=(np.radians(-90), 0, 0),
            color=(1.0, 1.0, 1.0),
            energy=100.0,
            metadata={'role': 'top', 'size': 3.0}
        ))

        return LightingSetup(
            lights=lights,
            hdri_path=self._find_hdri('studio'),
            hdri_strength=0.5,
            ambient_color=(0.1, 0.1, 0.1),
            ambient_strength=0.4,
            volumetric_enabled=False,
            volumetric_density=0.0,
            style=LightingStyle.STUDIO
        )

    def _create_dramatic_lighting(self, analysis: Dict[str, Any]) -> LightingSetup:
        """Create high-contrast dramatic lighting."""
        center = analysis['bounds']['center']
        radius = analysis['radius']

        lights = []

        # Strong directional key light
        lights.append(Light(
            name="KeyLight",
            light_type=LightType.SPOT,
            position=(radius * 2, radius * 3, radius),
            rotation=(np.radians(-60), np.radians(30), 0),
            color=(1.0, 0.95, 0.8),
            energy=500.0,
            metadata={'role': 'key', 'spot_size': np.radians(45), 'blend': 0.1}
        ))

        # Subtle rim light
        lights.append(Light(
            name="RimLight",
            light_type=LightType.POINT,
            position=(-radius, radius * 2, -radius * 2),
            rotation=(0, 0, 0),
            color=(0.8, 0.9, 1.0),
            energy=80.0,
            metadata={'role': 'rim'}
        ))

        return LightingSetup(
            lights=lights,
            hdri_path=None,
            hdri_strength=0.1,
            ambient_color=(0.01, 0.01, 0.02),
            ambient_strength=0.05,
            volumetric_enabled=True,
            volumetric_density=0.1,
            style=LightingStyle.DRAMATIC
        )

    def _create_ambient_lighting(self, analysis: Dict[str, Any]) -> LightingSetup:
        """Create soft ambient lighting."""
        center = analysis['bounds']['center']
        radius = analysis['radius']

        lights = []

        # Soft overhead light
        lights.append(Light(
            name="OverheadLight",
            light_type=LightType.AREA,
            position=(0, radius * 2.5, 0),
            rotation=(np.radians(-90), 0, 0),
            color=(1.0, 1.0, 1.0),
            energy=100.0,
            metadata={'role': 'ambient', 'size': 5.0}
        ))

        return LightingSetup(
            lights=lights,
            hdri_path=self._find_hdri('indoor'),
            hdri_strength=1.5,
            ambient_color=(0.2, 0.2, 0.25),
            ambient_strength=0.8,
            volumetric_enabled=False,
            volumetric_density=0.0,
            style=LightingStyle.AMBIENT
        )

    def _create_natural_lighting(self, analysis: Dict[str, Any]) -> LightingSetup:
        """Create natural outdoor lighting."""
        center = analysis['bounds']['center']
        radius = analysis['radius']

        lights = []

        # Sun
        lights.append(Light(
            name="Sun",
            light_type=LightType.SUN,
            position=(radius * 5, radius * 8, radius * 3),
            rotation=(np.radians(-30), np.radians(30), 0),
            color=self.color_temperatures['daylight'],
            energy=4.0,
            metadata={'role': 'sun'}
        ))

        return LightingSetup(
            lights=lights,
            hdri_path=self._find_hdri('outdoor'),
            hdri_strength=1.2,
            ambient_color=(0.4, 0.5, 0.6),
            ambient_strength=0.6,
            volumetric_enabled=True,
            volumetric_density=0.005,
            style=LightingStyle.NATURAL
        )

    def _create_custom_lighting(
        self,
        analysis: Dict[str, Any],
        config: Dict[str, Any]
    ) -> LightingSetup:
        """
        Create custom lighting from configuration.

        Args:
            analysis: Scene analysis
            config: Custom lighting configuration

        Returns:
            LightingSetup instance
        """
        logger.info("Creating custom lighting setup")

        lights = []

        # Parse custom lights
        for light_config in config.get('lights', []):
            light = Light(
                name=light_config.get('name', 'CustomLight'),
                light_type=LightType(light_config.get('type', 'point')),
                position=tuple(light_config.get('position', [0, 5, 0])),
                rotation=tuple(light_config.get('rotation', [0, 0, 0])),
                color=tuple(light_config.get('color', [1, 1, 1])),
                energy=light_config.get('energy', 100.0),
                metadata=light_config.get('metadata', {})
            )
            lights.append(light)

        return LightingSetup(
            lights=lights,
            hdri_path=config.get('hdri_path'),
            hdri_strength=config.get('hdri_strength', 1.0),
            ambient_color=tuple(config.get('ambient_color', [0.1, 0.1, 0.1])),
            ambient_strength=config.get('ambient_strength', 0.3),
            volumetric_enabled=config.get('volumetric_enabled', False),
            volumetric_density=config.get('volumetric_density', 0.01),
            style=LightingStyle(config.get('style', 'realistic'))
        )

    def _find_hdri(self, environment_type: str) -> Optional[str]:
        """
        Find an appropriate HDRI file.

        Args:
            environment_type: Type of environment ('studio', 'outdoor', 'indoor')

        Returns:
            Path to HDRI file or None
        """
        # In production, this would search the HDRI library
        # For now, return placeholder paths
        hdri_map = {
            'studio': 'studio_softbox.hdr',
            'outdoor': 'outdoor_sky.hdr',
            'indoor': 'indoor_ambient.hdr'
        }

        hdri_filename = hdri_map.get(environment_type, 'default.hdr')

        if self.hdri_library.exists():
            hdri_path = self.hdri_library / hdri_filename
            if hdri_path.exists():
                return str(hdri_path)

        logger.warning(f"HDRI file not found: {hdri_filename}")
        return None


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    engine = LightingEngine()

    # Create test scene
    test_scene = {
        "objects": [
            {
                "name": "table",
                "position": [0, 0.75, 0],
                "category": "furniture"
            },
            {
                "name": "chair",
                "position": [0, 0.85, 1.5],
                "category": "furniture"
            },
            {
                "name": "lamp",
                "position": [2, 1.5, 0],
                "category": "lighting"
            }
        ]
    }

    # Apply different lighting styles
    styles = ["realistic", "cinematic", "studio", "dramatic"]

    for style in styles:
        print(f"\n{'='*60}")
        print(f"Testing {style.upper()} lighting")
        print('='*60)

        lit_scene = engine.apply(test_scene, style=style)

        print(f"\nLighting setup:")
        print(f"  Style: {lit_scene['lighting']['style']}")
        print(f"  Lights: {len(lit_scene['lighting']['lights'])}")

        for light in lit_scene['lighting']['lights']:
            print(f"    - {light['name']} ({light['type']})")
            print(f"      Position: {light['position']}")
            print(f"      Energy: {light['energy']}")
            print(f"      Color: {light['color']}")

        print(f"\n  HDRI: {lit_scene['lighting']['hdri']['path']}")
        print(f"  HDRI Strength: {lit_scene['lighting']['hdri']['strength']}")
        print(f"  Volumetric: {lit_scene['lighting']['volumetric']['enabled']}")
