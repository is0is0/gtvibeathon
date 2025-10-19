"""
Lighting Engine - Intelligent lighting configuration for 3D scenes.
Analyzes scene concept and suggests appropriate lighting setups.
"""

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class LightingStyle(str, Enum):
    """Lighting style presets."""
    REALISTIC = "realistic"
    STYLIZED = "stylized"
    DRAMATIC = "dramatic"
    SOFT = "soft"
    HIGH_KEY = "high_key"
    LOW_KEY = "low_key"
    STUDIO = "studio"
    OUTDOOR = "outdoor"
    CINEMATIC = "cinematic"


class TimeOfDay(str, Enum):
    """Time of day for natural lighting."""
    DAWN = "dawn"
    MORNING = "morning"
    NOON = "noon"
    AFTERNOON = "afternoon"
    SUNSET = "sunset"
    DUSK = "dusk"
    NIGHT = "night"


@dataclass
class LightConfig:
    """Configuration for a single light source."""
    name: str
    light_type: str  # point, sun, spot, area
    energy: float  # Light intensity
    color: tuple  # RGB color (0-1 range)
    position: tuple  # x, y, z
    rotation: Optional[tuple] = None  # rx, ry, rz
    size: float = 1.0  # For area lights
    color_temperature: Optional[float] = None  # In Kelvin


class LightingEngine:
    """
    Analyzes scene concepts and generates appropriate lighting configurations.
    """

    # Color temperature presets (in Kelvin)
    COLOR_TEMPS = {
        "candle": 1850,
        "warm_incandescent": 2700,
        "tungsten": 3200,
        "sunrise": 3500,
        "sunset": 3500,
        "fluorescent": 4000,
        "daylight": 5500,
        "overcast": 6500,
        "blue_sky": 10000,
    }

    # Standard lighting setups
    LIGHTING_SETUPS = {
        "three_point": {
            "description": "Classic three-point lighting (key, fill, rim)",
            "lights": [
                {"name": "key", "type": "area", "energy": 1000, "angle": 45, "height": 2.5},
                {"name": "fill", "type": "area", "energy": 400, "angle": -45, "height": 1.5},
                {"name": "rim", "type": "area", "energy": 600, "angle": 180, "height": 2.0},
            ]
        },
        "studio": {
            "description": "Studio photography lighting",
            "lights": [
                {"name": "key", "type": "area", "energy": 1200, "angle": 30, "height": 2.5},
                {"name": "fill", "type": "area", "energy": 600, "angle": -30, "height": 2.0},
                {"name": "back", "type": "spot", "energy": 800, "angle": 150, "height": 3.0},
            ]
        },
        "natural": {
            "description": "Natural outdoor lighting",
            "lights": [
                {"name": "sun", "type": "sun", "energy": 5, "angle": 45, "height": 10},
                {"name": "sky", "type": "area", "energy": 200, "angle": 0, "height": 5},
            ]
        },
        "dramatic": {
            "description": "High contrast dramatic lighting",
            "lights": [
                {"name": "key", "type": "spot", "energy": 1500, "angle": 60, "height": 3.0},
                {"name": "rim", "type": "spot", "energy": 1000, "angle": 150, "height": 2.5},
            ]
        },
    }

    def __init__(self, style: str = "realistic"):
        """
        Initialize lighting engine.

        Args:
            style: Default lighting style
        """
        self.style = style
        logger.info(f"LightingEngine initialized with style={style}")

    def configure_from_concept(self, concept: str) -> Dict[str, Any]:
        """
        Generate lighting configuration from scene concept.

        Args:
            concept: Scene concept description

        Returns:
            Lighting configuration dictionary
        """
        logger.info("Analyzing concept for lighting configuration...")

        concept_lower = concept.lower()

        # Detect environment type
        environment = self._detect_environment(concept_lower)

        # Detect time of day
        time_of_day = self._detect_time_of_day(concept_lower)

        # Detect mood
        mood = self._detect_mood(concept_lower)

        # Select appropriate setup
        setup_name = self._select_setup(environment, time_of_day, mood)

        # Generate light configurations
        lights = self._generate_lights(setup_name, time_of_day, mood)

        # Add ambient/environment lighting
        ambient = self._configure_ambient(environment, time_of_day)

        config = {
            "style": self.style,
            "environment": environment,
            "time_of_day": time_of_day,
            "mood": mood,
            "setup_name": setup_name,
            "lights": [self._light_to_dict(light) for light in lights],
            "ambient": ambient,
            "recommendations": self._generate_recommendations(environment, time_of_day)
        }

        logger.info(f"Generated lighting config: {setup_name} with {len(lights)} lights")

        return config

    def _detect_environment(self, concept: str) -> str:
        """Detect whether scene is indoor, outdoor, or studio."""
        if any(word in concept for word in ["outdoor", "forest", "field", "park", "street", "sky"]):
            return "outdoor"
        elif any(word in concept for word in ["studio", "photography", "product", "white background"]):
            return "studio"
        elif any(word in concept for word in ["room", "indoor", "interior", "building", "house"]):
            return "indoor"
        else:
            return "neutral"

    def _detect_time_of_day(self, concept: str) -> Optional[str]:
        """Detect time of day from concept."""
        for time in TimeOfDay:
            if time.value in concept:
                return time.value

        # Check synonyms
        if any(word in concept for word in ["sunrise", "dawn", "early morning"]):
            return TimeOfDay.DAWN.value
        elif any(word in concept for word in ["sunset", "dusk", "evening"]):
            return TimeOfDay.SUNSET.value
        elif any(word in concept for word in ["night", "dark", "midnight"]):
            return TimeOfDay.NIGHT.value
        elif "noon" in concept or "midday" in concept:
            return TimeOfDay.NOON.value

        return None

    def _detect_mood(self, concept: str) -> str:
        """Detect mood/atmosphere from concept."""
        if any(word in concept for word in ["dramatic", "intense", "dark", "moody"]):
            return "dramatic"
        elif any(word in concept for word in ["soft", "gentle", "calm", "peaceful"]):
            return "soft"
        elif any(word in concept for word in ["bright", "cheerful", "light", "airy"]):
            return "bright"
        elif any(word in concept for word in ["warm", "cozy", "inviting"]):
            return "warm"
        elif any(word in concept for word in ["cool", "clinical", "modern"]):
            return "cool"
        else:
            return "neutral"

    def _select_setup(self, environment: str, time_of_day: Optional[str], mood: str) -> str:
        """Select appropriate lighting setup."""
        if environment == "studio":
            return "studio"
        elif environment == "outdoor":
            return "natural"
        elif mood == "dramatic":
            return "dramatic"
        else:
            return "three_point"

    def _generate_lights(
        self,
        setup_name: str,
        time_of_day: Optional[str],
        mood: str
    ) -> List[LightConfig]:
        """Generate light configurations based on setup."""
        setup = self.LIGHTING_SETUPS.get(setup_name, self.LIGHTING_SETUPS["three_point"])

        lights = []
        distance = 5.0  # Distance from origin

        for light_data in setup["lights"]:
            # Calculate position based on angle
            import math
            angle_rad = math.radians(light_data["angle"])
            x = distance * math.cos(angle_rad)
            y = distance * math.sin(angle_rad)
            z = light_data["height"]

            # Determine color based on time of day
            color = self._get_light_color(light_data["name"], time_of_day, mood)

            # Get color temperature
            color_temp = self._get_color_temperature(time_of_day, light_data["name"])

            light = LightConfig(
                name=light_data["name"],
                light_type=light_data["type"],
                energy=light_data["energy"],
                color=color,
                position=(x, y, z),
                rotation=(-45, 0, angle_rad),
                size=2.0 if light_data["type"] == "area" else 1.0,
                color_temperature=color_temp
            )

            lights.append(light)

        return lights

    def _get_light_color(self, light_name: str, time_of_day: Optional[str], mood: str) -> tuple:
        """Get color for a light based on context."""
        # Base colors
        if time_of_day == "sunset" or time_of_day == "sunrise":
            return (1.0, 0.8, 0.6)  # Warm orange
        elif time_of_day == "night":
            return (0.7, 0.8, 1.0)  # Cool blue
        elif mood == "warm":
            return (1.0, 0.95, 0.9)  # Warm white
        elif mood == "cool":
            return (0.9, 0.95, 1.0)  # Cool white
        else:
            return (1.0, 1.0, 1.0)  # Neutral white

    def _get_color_temperature(self, time_of_day: Optional[str], light_name: str) -> Optional[float]:
        """Get color temperature in Kelvin."""
        if time_of_day == "sunset" or time_of_day == "sunrise":
            return self.COLOR_TEMPS["sunset"]
        elif time_of_day == "noon":
            return self.COLOR_TEMPS["daylight"]
        elif time_of_day == "night":
            return self.COLOR_TEMPS["blue_sky"]
        elif light_name == "key":
            return self.COLOR_TEMPS["daylight"]
        else:
            return None

    def _configure_ambient(self, environment: str, time_of_day: Optional[str]) -> Dict[str, Any]:
        """Configure ambient/world lighting."""
        if environment == "outdoor":
            strength = 0.5 if time_of_day == "night" else 1.0
            color = (0.5, 0.6, 0.8) if time_of_day == "night" else (0.8, 0.9, 1.0)
        elif environment == "studio":
            strength = 0.3
            color = (1.0, 1.0, 1.0)
        else:
            strength = 0.2
            color = (0.9, 0.9, 0.9)

        return {
            "enabled": True,
            "strength": strength,
            "color": color,
            "type": "sky" if environment == "outdoor" else "solid"
        }

    def _generate_recommendations(self, environment: str, time_of_day: Optional[str]) -> List[str]:
        """Generate lighting recommendations."""
        recommendations = []

        if environment == "outdoor" and not time_of_day:
            recommendations.append("Consider specifying time of day for more accurate outdoor lighting")

        if environment == "studio":
            recommendations.append("Studio lighting works best with HDR environment for reflections")

        if time_of_day == "night":
            recommendations.append("Add volumetric fog for atmospheric night scenes")

        recommendations.append("Enable shadow for all lights for realism")
        recommendations.append("Use area lights for soft shadows")

        return recommendations

    def _light_to_dict(self, light: LightConfig) -> Dict[str, Any]:
        """Convert LightConfig to dictionary."""
        return {
            "name": light.name,
            "type": light.light_type,
            "energy": light.energy,
            "color": light.color,
            "position": light.position,
            "rotation": light.rotation,
            "size": light.size,
            "color_temperature": light.color_temperature
        }

    def adjust_for_style(self, config: Dict[str, Any], style: LightingStyle) -> Dict[str, Any]:
        """Adjust lighting configuration for specific style."""
        if style == LightingStyle.DRAMATIC:
            # Increase contrast
            for light in config["lights"]:
                if light["name"] == "key":
                    light["energy"] *= 1.5
                elif light["name"] == "fill":
                    light["energy"] *= 0.5

        elif style == LightingStyle.SOFT:
            # Reduce contrast, soften
            for light in config["lights"]:
                if light["type"] != "area":
                    light["type"] = "area"
                light["size"] = 3.0

        elif style == LightingStyle.HIGH_KEY:
            # Bright overall
            for light in config["lights"]:
                light["energy"] *= 1.3
            config["ambient"]["strength"] *= 1.5

        elif style == LightingStyle.LOW_KEY:
            # Dark overall
            for light in config["lights"]:
                if light["name"] != "key":
                    light["energy"] *= 0.5
            config["ambient"]["strength"] *= 0.3

        return config
