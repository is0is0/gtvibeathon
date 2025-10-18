"""
HDRI Manager
============
Intelligent HDRI selection and blending system for dynamic lighting.

Features:
- Search HDRIs from AssetRegistry by tags, categories, mood
- Blend multiple HDRIs for unique lighting
- Time-of-day based HDRI selection
- Mood-based automatic selection
- HDRI strength and rotation optimization
"""

import os
import math
import random
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass

from subsystems.asset_registry import AssetRegistry, AssetType, Asset
from utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class HDRIBlendLayer:
    """Configuration for a single HDRI layer in a blend."""
    hdri_asset: Asset
    strength: float = 1.0  # 0.0 to 1.0
    rotation: float = 0.0  # In radians
    color_tint: Tuple[float, float, float] = (1.0, 1.0, 1.0)
    saturation: float = 1.0


class HDRIManager:
    """
    Manages HDRI selection, blending, and optimization for scene lighting.

    Can intelligently select HDRIs based on:
    - Scene mood (cozy, dramatic, energetic, etc.)
    - Time of day (sunrise, noon, sunset, night)
    - Environment (indoor, outdoor, urban, nature)
    - Style (realistic, stylized, cinematic)
    """

    # Mood to HDRI tag mapping
    MOOD_TAG_MAP = {
        'cozy': ['indoor', 'warm', 'soft', 'studio'],
        'dramatic': ['sunset', 'dark', 'dramatic', 'clouds'],
        'energetic': ['sunny', 'bright', 'daylight', 'clear'],
        'peaceful': ['nature', 'forest', 'peaceful', 'soft'],
        'mysterious': ['night', 'dark', 'foggy', 'atmospheric'],
        'futuristic': ['urban', 'city', 'night', 'neon'],
        'natural': ['outdoor', 'daylight', 'nature', 'clear'],
        'romantic': ['sunset', 'warm', 'soft', 'pink'],
    }

    # Time of day to HDRI preferences
    TIME_OF_DAY_TAGS = {
        'sunrise': ['sunrise', 'dawn', 'morning', 'warm'],
        'morning': ['morning', 'daylight', 'clear', 'bright'],
        'noon': ['noon', 'daylight', 'sunny', 'bright'],
        'afternoon': ['afternoon', 'daylight', 'warm'],
        'sunset': ['sunset', 'dusk', 'evening', 'warm'],
        'evening': ['evening', 'dusk', 'soft'],
        'night': ['night', 'dark', 'moon', 'stars'],
    }

    # Environment to HDRI categories
    ENVIRONMENT_CATEGORIES = {
        'indoor': ['indoor', 'studio', 'interior'],
        'outdoor': ['outdoor', 'nature', 'landscape'],
        'urban': ['urban', 'city', 'street'],
        'nature': ['forest', 'beach', 'mountain', 'field'],
        'studio': ['studio', 'neutral'],
    }

    def __init__(self, registry_path: Optional[str] = None):
        """
        Initialize HDRI manager.

        Args:
            registry_path: Path to AssetRegistry (optional, will search for HDRIs)
        """
        self.registry = None
        self.available_hdris: List[Asset] = []

        if registry_path:
            try:
                self.registry = AssetRegistry(registry_path)
                self.available_hdris = self.registry.list_assets(asset_type=AssetType.HDRI)
                logger.info(f"Loaded {len(self.available_hdris)} HDRIs from registry")
            except Exception as e:
                logger.warning(f"Could not load AssetRegistry: {e}")
        else:
            logger.info("No registry path provided, HDRI search will be limited")

    def search_hdris(
        self,
        tags: Optional[List[str]] = None,
        categories: Optional[List[str]] = None,
        query: Optional[str] = None,
        limit: int = 10,
    ) -> List[Asset]:
        """
        Search for HDRIs matching criteria.

        Args:
            tags: List of tags to match
            categories: List of categories to match
            query: Text query for name/description
            limit: Maximum number of results

        Returns:
            List of matching HDRI assets
        """
        if not self.registry:
            logger.warning("No registry available for HDRI search")
            return []

        results = self.registry.search_assets(
            query=query or "",
            asset_type=AssetType.HDRI,
            tags=tags,
            category=categories[0] if categories else None,
        )

        # Filter by additional criteria
        if tags:
            results = [
                asset for asset in results
                if any(tag in asset.tags for tag in tags)
            ]

        return results[:limit]

    def select_by_mood(self, mood: str, limit: int = 3) -> List[Asset]:
        """
        Select HDRIs matching a mood.

        Args:
            mood: Mood descriptor (cozy, dramatic, energetic, etc.)
            limit: Maximum number of HDRIs to return

        Returns:
            List of matching HDRI assets
        """
        logger.info(f"Selecting HDRIs for mood: {mood}")

        # Get tags for this mood
        tags = self.MOOD_TAG_MAP.get(mood.lower(), [mood.lower()])

        # Search with mood tags
        results = self.search_hdris(tags=tags, limit=limit * 2)

        # Score and rank results
        scored_results = []
        for asset in results:
            score = self._calculate_mood_score(asset, tags)
            scored_results.append((score, asset))

        # Sort by score and return top results
        scored_results.sort(reverse=True, key=lambda x: x[0])
        selected = [asset for score, asset in scored_results[:limit]]

        logger.info(f"Selected {len(selected)} HDRIs for mood '{mood}'")
        return selected

    def select_by_time_of_day(self, time_of_day: str, limit: int = 3) -> List[Asset]:
        """
        Select HDRIs matching a time of day.

        Args:
            time_of_day: Time descriptor (sunrise, noon, sunset, night, etc.)
            limit: Maximum number of HDRIs

        Returns:
            List of matching HDRI assets
        """
        logger.info(f"Selecting HDRIs for time: {time_of_day}")

        tags = self.TIME_OF_DAY_TAGS.get(time_of_day.lower(), [time_of_day.lower()])
        results = self.search_hdris(tags=tags, limit=limit * 2)

        # Score by relevance
        scored_results = []
        for asset in results:
            score = self._calculate_time_score(asset, tags)
            scored_results.append((score, asset))

        scored_results.sort(reverse=True, key=lambda x: x[0])
        selected = [asset for score, asset in scored_results[:limit]]

        logger.info(f"Selected {len(selected)} HDRIs for time '{time_of_day}'")
        return selected

    def select_by_environment(self, environment: str, limit: int = 3) -> List[Asset]:
        """
        Select HDRIs matching an environment type.

        Args:
            environment: Environment type (indoor, outdoor, urban, nature, etc.)
            limit: Maximum number of HDRIs

        Returns:
            List of matching HDRI assets
        """
        logger.info(f"Selecting HDRIs for environment: {environment}")

        categories = self.ENVIRONMENT_CATEGORIES.get(environment.lower(), [environment.lower()])
        results = self.search_hdris(tags=categories, limit=limit)

        logger.info(f"Selected {len(results)} HDRIs for environment '{environment}'")
        return results

    def select_smart(
        self,
        scene_context: Dict[str, Any],
        limit: int = 3,
    ) -> List[Asset]:
        """
        Intelligently select HDRIs based on complete scene context.

        Args:
            scene_context: Scene data with interpreted prompt, mood, style, etc.
            limit: Maximum number of HDRIs

        Returns:
            List of best matching HDRI assets
        """
        logger.info("Smart HDRI selection based on scene context")

        # Extract context
        prompt = scene_context.get('interpreted_prompt', {})
        mood = prompt.get('mood', {})
        time_of_day = prompt.get('time_of_day', 'noon')
        environment = prompt.get('environment', 'outdoor')
        style = scene_context.get('style', 'realistic')

        # Collect candidate HDRIs from different criteria
        candidates = []

        # Search by mood (highest priority)
        if mood:
            primary_mood = max(mood.items(), key=lambda x: x[1])[0] if isinstance(mood, dict) else mood
            mood_hdris = self.select_by_mood(primary_mood, limit=limit)
            candidates.extend([(2.0, hdri) for hdri in mood_hdris])

        # Search by time of day
        time_hdris = self.select_by_time_of_day(time_of_day, limit=limit)
        candidates.extend([(1.5, hdri) for hdri in time_hdris])

        # Search by environment
        env_hdris = self.select_by_environment(environment, limit=limit)
        candidates.extend([(1.0, hdri) for hdri in env_hdris])

        # Deduplicate and rank
        seen = set()
        ranked_candidates = []

        for weight, asset in candidates:
            if asset.id not in seen:
                seen.add(asset.id)
                ranked_candidates.append((weight, asset))

        # Sort by weight and return top results
        ranked_candidates.sort(reverse=True, key=lambda x: x[0])
        selected = [asset for weight, asset in ranked_candidates[:limit]]

        logger.info(f"Smart selection: {len(selected)} HDRIs chosen")
        return selected

    def create_blend_configuration(
        self,
        hdris: List[Asset],
        blend_mode: str = 'layered',
    ) -> List[HDRIBlendLayer]:
        """
        Create a blending configuration for multiple HDRIs.

        Args:
            hdris: List of HDRI assets to blend
            blend_mode: Blending mode ('layered', 'balanced', 'dominant')

        Returns:
            List of HDRIBlendLayer configurations
        """
        logger.info(f"Creating HDRI blend configuration: {len(hdris)} HDRIs, mode={blend_mode}")

        if not hdris:
            return []

        if len(hdris) == 1:
            # Single HDRI, no blending needed
            return [HDRIBlendLayer(
                hdri_asset=hdris[0],
                strength=1.0,
                rotation=0.0,
            )]

        layers = []

        if blend_mode == 'layered':
            # Decreasing strength for each layer
            for i, hdri in enumerate(hdris):
                strength = 1.0 / (i + 1)  # 1.0, 0.5, 0.33, 0.25, ...
                rotation = (2 * math.pi * i) / len(hdris)  # Evenly distributed rotations

                layers.append(HDRIBlendLayer(
                    hdri_asset=hdri,
                    strength=strength,
                    rotation=rotation,
                ))

        elif blend_mode == 'balanced':
            # Equal strength for all layers
            strength = 1.0 / len(hdris)

            for i, hdri in enumerate(hdris):
                rotation = random.uniform(0, 2 * math.pi)  # Random rotation

                layers.append(HDRIBlendLayer(
                    hdri_asset=hdri,
                    strength=strength,
                    rotation=rotation,
                ))

        elif blend_mode == 'dominant':
            # First HDRI is dominant, others are subtle
            for i, hdri in enumerate(hdris):
                if i == 0:
                    strength = 0.7
                else:
                    strength = 0.3 / (len(hdris) - 1)

                rotation = (2 * math.pi * i) / len(hdris)

                layers.append(HDRIBlendLayer(
                    hdri_asset=hdri,
                    strength=strength,
                    rotation=rotation,
                ))

        logger.info(f"Created {len(layers)} blend layers")
        return layers

    def generate_blend_script(
        self,
        layers: List[HDRIBlendLayer],
        world_strength: float = 1.0,
    ) -> str:
        """
        Generate Blender Python script for HDRI blending.

        Args:
            layers: List of HDRI blend layers
            world_strength: Overall world lighting strength

        Returns:
            Blender Python script as string
        """
        if not layers:
            return "# No HDRIs to blend\n"

        logger.info(f"Generating blend script for {len(layers)} layers")

        script = """
# HDRI Blending Setup
import bpy
import math

# Setup world
world = bpy.context.scene.world
if not world:
    world = bpy.data.worlds.new("World")
    bpy.context.scene.world = world

world.use_nodes = True
nodes = world.node_tree.nodes
links = world.node_tree.links

# Clear existing nodes
nodes.clear()

# Create output node
output = nodes.new(type='ShaderNodeOutputWorld')
output.location = (1000, 0)

"""

        if len(layers) == 1:
            # Single HDRI (simple setup)
            layer = layers[0]
            script += f"""
# Single HDRI setup
tex_coord = nodes.new(type='ShaderNodeTexCoord')
tex_coord.location = (-800, 0)

mapping = nodes.new(type='ShaderNodeMapping')
mapping.location = (-600, 0)
mapping.inputs['Rotation'].default_value[2] = {layer.rotation}
links.new(tex_coord.outputs['Generated'], mapping.inputs['Vector'])

env_tex = nodes.new(type='ShaderNodeTexEnvironment')
env_tex.location = (-400, 0)
try:
    env_tex.image = bpy.data.images.load("{layer.hdri_asset.path}")
except:
    print("Warning: Could not load HDRI: {layer.hdri_asset.path}")

links.new(mapping.outputs['Vector'], env_tex.inputs['Vector'])

bg = nodes.new(type='ShaderNodeBackground')
bg.location = (600, 0)
bg.inputs['Strength'].default_value = {world_strength * layer.strength}
links.new(env_tex.outputs['Color'], bg.inputs['Color'])

links.new(bg.outputs['Background'], output.inputs['Surface'])
"""
        else:
            # Multiple HDRIs (blending)
            script += "# Multi-HDRI blending setup\n\n"

            # Create shared texture coordinate and mapping nodes for each layer
            for i, layer in enumerate(layers):
                y_offset = -i * 300

                script += f"""
# Layer {i + 1}: {layer.hdri_asset.name}
tex_coord_{i} = nodes.new(type='ShaderNodeTexCoord')
tex_coord_{i}.location = (-1200, {y_offset})

mapping_{i} = nodes.new(type='ShaderNodeMapping')
mapping_{i}.location = (-1000, {y_offset})
mapping_{i}.inputs['Rotation'].default_value[2] = {layer.rotation}
links.new(tex_coord_{i}.outputs['Generated'], mapping_{i}.inputs['Vector'])

env_tex_{i} = nodes.new(type='ShaderNodeTexEnvironment')
env_tex_{i}.location = (-800, {y_offset})
try:
    env_tex_{i}.image = bpy.data.images.load("{layer.hdri_asset.path}")
except:
    print("Warning: Could not load HDRI: {layer.hdri_asset.path}")
links.new(mapping_{i}.outputs['Vector'], env_tex_{i}.inputs['Vector'])

"""

                # Add color adjustment if needed
                if layer.color_tint != (1.0, 1.0, 1.0) or layer.saturation != 1.0:
                    script += f"""
# Color adjustments for layer {i + 1}
hue_sat_{i} = nodes.new(type='ShaderNodeHueSaturation')
hue_sat_{i}.location = (-600, {y_offset})
hue_sat_{i}.inputs['Saturation'].default_value = {layer.saturation}
hue_sat_{i}.inputs['Color'].default_value = {list(layer.color_tint) + [1.0]}
links.new(env_tex_{i}.outputs['Color'], hue_sat_{i}.inputs['Color'])

"""

            # Create mix nodes to blend layers
            script += "\n# Blend layers together\n"

            for i in range(len(layers) - 1):
                y_offset = -150 * i

                if i == 0:
                    # First mix
                    input1 = f"env_tex_0.outputs['Color']"
                    input2 = f"env_tex_1.outputs['Color']"
                else:
                    # Subsequent mixes
                    input1 = f"mix_{i - 1}.outputs['Color']"
                    input2 = f"env_tex_{i + 1}.outputs['Color']"

                # Calculate blend factor
                factor = layers[i + 1].strength / (layers[0].strength + layers[i + 1].strength)

                script += f"""
mix_{i} = nodes.new(type='ShaderNodeMixRGB')
mix_{i}.location = (-400 + {i * 200}, {y_offset})
mix_{i}.blend_type = 'MIX'
mix_{i}.inputs['Fac'].default_value = {factor}
links.new({input1}, mix_{i}.inputs['Color1'])
links.new({input2}, mix_{i}.inputs['Color2'])

"""

            # Final background node
            final_mix = f"mix_{len(layers) - 2}" if len(layers) > 1 else "env_tex_0"

            script += f"""
# Final background shader
bg = nodes.new(type='ShaderNodeBackground')
bg.location = (600, 0)
bg.inputs['Strength'].default_value = {world_strength}
links.new({final_mix}.outputs['Color'], bg.inputs['Color'])

links.new(bg.outputs['Background'], output.inputs['Surface'])
"""

        script += """
print("HDRI blending complete")
"""

        return script

    def _calculate_mood_score(self, asset: Asset, tags: List[str]) -> float:
        """Calculate relevance score for mood matching."""
        score = 0.0

        # Check tag matches
        asset_tags = [tag.lower() for tag in asset.tags]
        for tag in tags:
            if tag.lower() in asset_tags:
                score += 1.0

        # Bonus for exact name match
        for tag in tags:
            if tag.lower() in asset.name.lower():
                score += 0.5

        return score

    def _calculate_time_score(self, asset: Asset, tags: List[str]) -> float:
        """Calculate relevance score for time of day matching."""
        score = 0.0

        asset_tags = [tag.lower() for tag in asset.tags]
        asset_name = asset.name.lower()

        for tag in tags:
            # Tag match
            if tag.lower() in asset_tags:
                score += 1.5

            # Name match (higher weight)
            if tag.lower() in asset_name:
                score += 2.0

        return score


# Example usage and testing
if __name__ == "__main__":
    from utils.logger import setup_logging
    import json

    setup_logging(level="INFO", console=True)

    print("\n" + "="*80)
    print("HDRI MANAGER - TEST SUITE")
    print("="*80 + "\n")

    # Initialize manager (assumes HDRIs downloaded via download_polyhaven_hdris.py)
    manager = HDRIManager("data/voxel_assets.db")

    # Test 1: Search HDRIs
    print("Test 1: Search HDRIs by tags")
    print("-" * 40)
    outdoor_hdris = manager.search_hdris(tags=['outdoor', 'daylight'], limit=5)
    print(f"Found {len(outdoor_hdris)} outdoor HDRIs:")
    for hdri in outdoor_hdris:
        print(f"  - {hdri.name}: {hdri.tags[:3]}...")

    # Test 2: Select by mood
    print("\nTest 2: Select HDRIs by mood")
    print("-" * 40)
    cozy_hdris = manager.select_by_mood('cozy', limit=3)
    print(f"Cozy mood HDRIs ({len(cozy_hdris)}):")
    for hdri in cozy_hdris:
        print(f"  - {hdri.name}")

    # Test 3: Select by time of day
    print("\nTest 3: Select HDRIs by time of day")
    print("-" * 40)
    sunset_hdris = manager.select_by_time_of_day('sunset', limit=3)
    print(f"Sunset HDRIs ({len(sunset_hdris)}):")
    for hdri in sunset_hdris:
        print(f"  - {hdri.name}")

    # Test 4: Smart selection
    print("\nTest 4: Smart HDRI selection")
    print("-" * 40)
    scene_context = {
        'interpreted_prompt': {
            'mood': {'cozy': 0.8, 'warm': 0.6},
            'time_of_day': 'sunset',
            'environment': 'indoor',
        },
        'style': 'realistic'
    }
    smart_hdris = manager.select_smart(scene_context, limit=2)
    print(f"Smart selection ({len(smart_hdris)}):")
    for hdri in smart_hdris:
        print(f"  - {hdri.name}")

    # Test 5: Create blend configuration
    print("\nTest 5: HDRI blending configuration")
    print("-" * 40)
    if len(smart_hdris) >= 2:
        layers = manager.create_blend_configuration(smart_hdris[:2], blend_mode='layered')
        print(f"Created {len(layers)} blend layers:")
        for i, layer in enumerate(layers):
            print(f"  Layer {i + 1}: {layer.hdri_asset.name}")
            print(f"    Strength: {layer.strength:.2f}")
            print(f"    Rotation: {math.degrees(layer.rotation):.1f}°")

        # Generate blend script
        script = manager.generate_blend_script(layers, world_strength=1.0)
        print(f"\nGenerated blend script ({len(script)} chars)")
        print("First 300 chars:")
        print(script[:300] + "...")

    print("\n" + "="*80)
    print("TEST SUITE COMPLETE")
    print("="*80 + "\n")
