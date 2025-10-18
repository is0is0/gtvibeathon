"""
Texture Synthesis
----------------
Advanced texture and material generation for 3D objects.

Generates procedural materials using Blender's shader system,
with support for PBR materials, AI texture synthesis, and
automatic UV mapping.
"""

import random
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from pathlib import Path
from utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class MaterialProperties:
    """Represents material properties for PBR rendering."""
    name: str
    base_color: Tuple[float, float, float, float] = (0.8, 0.8, 0.8, 1.0)  # RGBA
    metallic: float = 0.0  # 0.0 = dielectric, 1.0 = metallic
    roughness: float = 0.5  # 0.0 = smooth, 1.0 = rough
    specular: float = 0.5
    emission_strength: float = 0.0
    emission_color: Tuple[float, float, float, float] = (1.0, 1.0, 1.0, 1.0)
    alpha: float = 1.0  # Transparency
    ior: float = 1.45  # Index of refraction
    transmission: float = 0.0  # For glass materials
    subsurface: float = 0.0  # For skin, wax, etc.
    normal_strength: float = 1.0  # Bump map strength
    procedural_type: Optional[str] = None  # noise, voronoi, wave, etc.
    use_texture: bool = False
    texture_path: Optional[str] = None


class TextureSynthesizer:
    """
    Advanced texture synthesis and material generation system.

    Generates procedural materials using Blender's shader node system,
    supports PBR workflow, and provides placeholders for AI texture synthesis.
    """

    # Material presets for common materials
    MATERIAL_PRESETS = {
        'wood': MaterialProperties(
            name='Wood',
            base_color=(0.4, 0.25, 0.15, 1.0),
            metallic=0.0,
            roughness=0.8,
            procedural_type='wood',
            normal_strength=0.5
        ),
        'metal': MaterialProperties(
            name='Metal',
            base_color=(0.8, 0.8, 0.8, 1.0),
            metallic=1.0,
            roughness=0.2,
            specular=1.0,
            procedural_type='noise'
        ),
        'glass': MaterialProperties(
            name='Glass',
            base_color=(1.0, 1.0, 1.0, 1.0),
            metallic=0.0,
            roughness=0.0,
            transmission=1.0,
            ior=1.45,
            alpha=0.1
        ),
        'plastic': MaterialProperties(
            name='Plastic',
            base_color=(0.8, 0.2, 0.2, 1.0),
            metallic=0.0,
            roughness=0.3,
            specular=0.5
        ),
        'fabric': MaterialProperties(
            name='Fabric',
            base_color=(0.6, 0.6, 0.7, 1.0),
            metallic=0.0,
            roughness=0.9,
            procedural_type='noise',
            normal_strength=0.3
        ),
        'stone': MaterialProperties(
            name='Stone',
            base_color=(0.5, 0.5, 0.5, 1.0),
            metallic=0.0,
            roughness=0.9,
            procedural_type='voronoi',
            normal_strength=1.0
        ),
        'concrete': MaterialProperties(
            name='Concrete',
            base_color=(0.6, 0.6, 0.6, 1.0),
            metallic=0.0,
            roughness=0.85,
            procedural_type='noise',
            normal_strength=0.4
        ),
        'gold': MaterialProperties(
            name='Gold',
            base_color=(1.0, 0.766, 0.336, 1.0),
            metallic=1.0,
            roughness=0.1,
            specular=1.0
        ),
        'silver': MaterialProperties(
            name='Silver',
            base_color=(0.972, 0.960, 0.915, 1.0),
            metallic=1.0,
            roughness=0.15,
            specular=1.0
        ),
        'copper': MaterialProperties(
            name='Copper',
            base_color=(0.955, 0.637, 0.538, 1.0),
            metallic=1.0,
            roughness=0.2,
            specular=1.0
        ),
        'rubber': MaterialProperties(
            name='Rubber',
            base_color=(0.1, 0.1, 0.1, 1.0),
            metallic=0.0,
            roughness=0.95,
            specular=0.3
        ),
        'leather': MaterialProperties(
            name='Leather',
            base_color=(0.4, 0.3, 0.2, 1.0),
            metallic=0.0,
            roughness=0.7,
            procedural_type='noise',
            normal_strength=0.4
        ),
        'ceramic': MaterialProperties(
            name='Ceramic',
            base_color=(0.9, 0.9, 0.85, 1.0),
            metallic=0.0,
            roughness=0.1,
            specular=0.8
        ),
        'marble': MaterialProperties(
            name='Marble',
            base_color=(0.95, 0.95, 0.95, 1.0),
            metallic=0.0,
            roughness=0.3,
            procedural_type='marble',
            normal_strength=0.2
        ),
        'skin': MaterialProperties(
            name='Skin',
            base_color=(0.95, 0.76, 0.66, 1.0),
            metallic=0.0,
            roughness=0.4,
            subsurface=0.15,
            procedural_type='noise',
            normal_strength=0.1
        ),
        'emissive': MaterialProperties(
            name='Emissive',
            base_color=(1.0, 1.0, 1.0, 1.0),
            metallic=0.0,
            roughness=0.5,
            emission_strength=10.0,
            emission_color=(1.0, 0.8, 0.6, 1.0)
        )
    }

    # Category to material mapping
    CATEGORY_MATERIALS = {
        'furniture': ['wood', 'metal', 'fabric'],
        'electronics': ['plastic', 'metal', 'glass'],
        'nature': ['wood', 'stone', 'fabric'],
        'architecture': ['concrete', 'stone', 'wood', 'glass'],
        'vehicle': ['metal', 'plastic', 'rubber'],
        'decor': ['ceramic', 'glass', 'metal', 'wood'],
        'food': ['plastic', 'ceramic']
    }

    # Color variations for different styles
    STYLE_COLORS = {
        'realistic': {
            'saturation_range': (0.2, 0.6),
            'brightness_range': (0.3, 0.8)
        },
        'stylized': {
            'saturation_range': (0.6, 1.0),
            'brightness_range': (0.4, 1.0)
        },
        'modern': {
            'saturation_range': (0.0, 0.3),
            'brightness_range': (0.5, 0.9)
        },
        'vintage': {
            'saturation_range': (0.3, 0.5),
            'brightness_range': (0.2, 0.6)
        },
        'fantasy': {
            'saturation_range': (0.7, 1.0),
            'brightness_range': (0.5, 1.0)
        }
    }

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize texture synthesizer.

        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.resolution = self.config.get('resolution', '2k')
        self.enable_cache = self.config.get('enable_cache', True)
        self.cache_dir = Path(self.config.get('cache_dir', 'cache/textures'))

        # AI texture synthesis configuration (placeholder)
        self.use_ai_synthesis = self.config.get('use_ai_synthesis', False)
        self.ai_provider = self.config.get('ai_provider', None)  # e.g., 'stable-diffusion'

        # Create cache directory
        if self.enable_cache:
            self.cache_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Texture Synthesizer initialized (resolution: {self.resolution}, AI: {self.use_ai_synthesis})")

    def apply(self, scene_data: Dict[str, Any], style: str = "realistic") -> Dict[str, Any]:
        """
        Apply textures and materials to all objects in scene.

        Args:
            scene_data: Scene data with objects
            style: Visual style for material generation

        Returns:
            Scene data with materials applied
        """
        logger.info(f"Applying textures to scene (style: {style})")

        objects = scene_data.get('objects', [])
        if not objects:
            logger.warning("No objects found in scene data")
            return scene_data

        # Apply materials to each object
        for obj in objects:
            try:
                material = self._generate_material_for_object(obj, style)
                obj['material'] = material
                logger.debug(f"Applied material to {obj.get('name', 'unknown')}: {material['name']}")
            except Exception as e:
                logger.error(f"Failed to apply material to {obj.get('name', 'unknown')}: {e}")
                obj['material'] = self._get_default_material()

        logger.info(f"Applied materials to {len(objects)} objects")

        return scene_data

    def generate_texture(self, description: str) -> Dict[str, Any]:
        """
        Generate texture from natural language description.

        Args:
            description: Natural language texture description
                e.g., "rough wooden surface", "shiny metal", "red plastic"

        Returns:
            Dictionary containing material properties and texture data
        """
        logger.info(f"Generating texture from description: '{description}'")

        # Parse description for material type and properties
        material_type = self._parse_material_type(description)
        color = self._parse_color(description)
        roughness = self._parse_roughness(description)
        metallic = self._parse_metallic(description)

        # Get base material preset
        if material_type in self.MATERIAL_PRESETS:
            material = self.MATERIAL_PRESETS[material_type]
        else:
            logger.warning(f"Unknown material type '{material_type}', using default")
            material = self._get_default_material()

        # Override with parsed properties
        if color:
            material.base_color = color
        if roughness is not None:
            material.roughness = roughness
        if metallic is not None:
            material.metallic = metallic

        # AI texture synthesis (placeholder)
        if self.use_ai_synthesis:
            texture_data = self._generate_ai_texture(description)
            if texture_data:
                material.use_texture = True
                material.texture_path = texture_data['path']

        logger.info(f"Generated texture: {material.name} (type: {material_type})")

        return self._material_to_dict(material)

    def apply_texture_to_object(
        self,
        object_name: str,
        texture_data: Optional[Dict[str, Any]] = None,
        material_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Apply texture/material to a specific object.

        Args:
            object_name: Name of the object
            texture_data: Pre-generated texture data (optional)
            material_type: Material type if texture_data not provided

        Returns:
            Blender material data dictionary
        """
        logger.info(f"Applying texture to object: {object_name}")

        try:
            if texture_data:
                # Use provided texture data
                material_dict = texture_data
            elif material_type:
                # Generate from material type
                if material_type in self.MATERIAL_PRESETS:
                    material = self.MATERIAL_PRESETS[material_type]
                    material_dict = self._material_to_dict(material)
                else:
                    logger.warning(f"Unknown material type '{material_type}'")
                    material_dict = self._get_default_material()
            else:
                # No data provided, use default
                logger.warning(f"No texture data or material type provided for {object_name}")
                material_dict = self._get_default_material()

            # Generate Blender material script
            material_dict['blender_script'] = self._generate_blender_material_script(
                object_name,
                material_dict
            )

            logger.info(f"Texture applied to {object_name}: {material_dict['name']}")

            return material_dict

        except Exception as e:
            logger.error(f"Failed to apply texture to {object_name}: {e}", exc_info=True)
            return self._get_default_material()

    def synthesize_texture(self, object_name: str, material_type: str) -> Dict[str, Any]:
        """
        Synthesize texture for object (legacy method for compatibility).

        Args:
            object_name: Name of the object
            material_type: Material type

        Returns:
            Material dictionary
        """
        return self.apply_texture_to_object(object_name, material_type=material_type)

    def optimize_uvs(self, objects: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Optimize UV mappings for objects.

        Args:
            objects: List of objects with geometry

        Returns:
            Objects with optimized UV data
        """
        logger.info(f"Optimizing UV mappings for {len(objects)} objects")

        for obj in objects:
            # Generate UV mapping strategy
            obj['uv_mapping'] = {
                'type': 'smart_project',  # or 'cube_project', 'sphere_project', 'unwrap'
                'island_margin': 0.02,
                'angle_limit': 66.0
            }

            logger.debug(f"UV mapping configured for {obj.get('name', 'unknown')}")

        return objects

    def create_texture_atlas(self, objects: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Create texture atlas for multiple objects.

        Args:
            objects: List of objects to combine into atlas

        Returns:
            Atlas data and UV remapping information
        """
        logger.info(f"Creating texture atlas for {len(objects)} objects")

        atlas_data = {
            'resolution': self.resolution,
            'objects': [obj.get('name', 'unknown') for obj in objects],
            'layout': 'grid',  # or 'packed'
            'padding': 4
        }

        logger.debug(f"Texture atlas created: {atlas_data}")

        return atlas_data

    # Private helper methods

    def _generate_material_for_object(
        self,
        obj: Dict[str, Any],
        style: str
    ) -> Dict[str, Any]:
        """Generate material for a specific object based on its properties."""
        object_name = obj.get('name', 'unknown')
        category = obj.get('category', 'object')
        modifiers = obj.get('modifiers', [])
        attributes = obj.get('attributes', {})

        # Check if object has explicit material in attributes
        if 'material' in attributes and attributes['material']:
            material_type = attributes['material']
            logger.debug(f"Using explicit material for {object_name}: {material_type}")
        # Check modifiers for material hints
        elif modifiers:
            material_type = self._get_material_from_modifiers(modifiers)
            logger.debug(f"Material from modifiers for {object_name}: {material_type}")
        # Infer from category
        else:
            material_type = self._get_material_from_category(category)
            logger.debug(f"Material from category for {object_name}: {material_type}")

        # Get material preset
        if material_type in self.MATERIAL_PRESETS:
            material = MaterialProperties(**vars(self.MATERIAL_PRESETS[material_type]))
        else:
            logger.warning(f"Material type '{material_type}' not found, using default")
            material = self._get_default_material_props()

        # Apply style-based color adjustments
        material = self._apply_style_to_material(material, style)

        # Convert to dictionary
        return self._material_to_dict(material)

    def _get_material_from_modifiers(self, modifiers: List[str]) -> str:
        """Extract material type from modifier words."""
        # Material keywords
        material_keywords = {
            'wooden': 'wood',
            'wood': 'wood',
            'metal': 'metal',
            'metallic': 'metal',
            'glass': 'glass',
            'plastic': 'plastic',
            'fabric': 'fabric',
            'stone': 'stone',
            'concrete': 'concrete',
            'leather': 'leather',
            'rubber': 'rubber',
            'ceramic': 'ceramic',
            'marble': 'marble',
            'gold': 'gold',
            'golden': 'gold',
            'silver': 'silver',
            'copper': 'copper'
        }

        for modifier in modifiers:
            modifier_lower = modifier.lower()
            if modifier_lower in material_keywords:
                return material_keywords[modifier_lower]

        return 'plastic'  # Default

    def _get_material_from_category(self, category: str) -> str:
        """Get appropriate material type for object category."""
        if category in self.CATEGORY_MATERIALS:
            # Pick first material from category list
            return self.CATEGORY_MATERIALS[category][0]
        return 'plastic'  # Default

    def _apply_style_to_material(
        self,
        material: MaterialProperties,
        style: str
    ) -> MaterialProperties:
        """Apply style-specific adjustments to material."""
        if style not in self.STYLE_COLORS:
            return material

        style_config = self.STYLE_COLORS[style]

        # Adjust saturation and brightness
        r, g, b, a = material.base_color

        # Convert to HSV-like adjustments
        max_rgb = max(r, g, b)
        min_rgb = min(r, g, b)

        # Simple saturation adjustment
        sat_range = style_config['saturation_range']
        target_sat = random.uniform(*sat_range)

        # Simple brightness adjustment
        bright_range = style_config['brightness_range']
        target_bright = random.uniform(*bright_range)

        # Apply adjustments (simplified)
        r = max(0.0, min(1.0, r * target_bright))
        g = max(0.0, min(1.0, g * target_bright))
        b = max(0.0, min(1.0, b * target_bright))

        material.base_color = (r, g, b, a)

        return material

    def _parse_material_type(self, description: str) -> str:
        """Parse material type from description."""
        description_lower = description.lower()

        for material_type in self.MATERIAL_PRESETS.keys():
            if material_type in description_lower:
                return material_type

        return 'plastic'  # Default

    def _parse_color(self, description: str) -> Optional[Tuple[float, float, float, float]]:
        """Parse color from description."""
        description_lower = description.lower()

        # Basic color keywords
        colors = {
            'red': (0.8, 0.1, 0.1, 1.0),
            'green': (0.1, 0.8, 0.1, 1.0),
            'blue': (0.1, 0.1, 0.8, 1.0),
            'yellow': (0.8, 0.8, 0.1, 1.0),
            'orange': (0.8, 0.4, 0.1, 1.0),
            'purple': (0.6, 0.1, 0.8, 1.0),
            'white': (0.9, 0.9, 0.9, 1.0),
            'black': (0.1, 0.1, 0.1, 1.0),
            'gray': (0.5, 0.5, 0.5, 1.0),
            'grey': (0.5, 0.5, 0.5, 1.0),
            'brown': (0.4, 0.3, 0.2, 1.0),
            'pink': (0.9, 0.6, 0.7, 1.0)
        }

        for color_name, color_value in colors.items():
            if color_name in description_lower:
                return color_value

        return None

    def _parse_roughness(self, description: str) -> Optional[float]:
        """Parse roughness from description."""
        description_lower = description.lower()

        if any(word in description_lower for word in ['shiny', 'glossy', 'polished', 'smooth']):
            return 0.1
        elif any(word in description_lower for word in ['rough', 'matte', 'dull']):
            return 0.9

        return None

    def _parse_metallic(self, description: str) -> Optional[float]:
        """Parse metallic property from description."""
        description_lower = description.lower()

        if any(word in description_lower for word in ['metal', 'metallic', 'chrome']):
            return 1.0

        return None

    def _material_to_dict(self, material: MaterialProperties) -> Dict[str, Any]:
        """Convert MaterialProperties to dictionary."""
        return {
            'name': material.name,
            'base_color': list(material.base_color),
            'metallic': material.metallic,
            'roughness': material.roughness,
            'specular': material.specular,
            'emission_strength': material.emission_strength,
            'emission_color': list(material.emission_color),
            'alpha': material.alpha,
            'ior': material.ior,
            'transmission': material.transmission,
            'subsurface': material.subsurface,
            'normal_strength': material.normal_strength,
            'procedural_type': material.procedural_type,
            'use_texture': material.use_texture,
            'texture_path': material.texture_path
        }

    def _get_default_material(self) -> Dict[str, Any]:
        """Get default material as dictionary."""
        return self._material_to_dict(self._get_default_material_props())

    def _get_default_material_props(self) -> MaterialProperties:
        """Get default material properties."""
        return MaterialProperties(
            name='Default',
            base_color=(0.8, 0.8, 0.8, 1.0),
            metallic=0.0,
            roughness=0.5
        )

    def _generate_blender_material_script(
        self,
        object_name: str,
        material_data: Dict[str, Any]
    ) -> str:
        """
        Generate Blender Python script for creating material.

        Args:
            object_name: Name of the object to apply material to
            material_data: Material properties dictionary

        Returns:
            Blender Python script as string
        """
        material_name = material_data['name']

        script = f"""
# Material: {material_name} for {object_name}
import bpy

# Create material
mat = bpy.data.materials.new(name="{material_name}_{object_name}")
mat.use_nodes = True
nodes = mat.node_tree.nodes
links = mat.node_tree.links

# Clear default nodes
nodes.clear()

# Create Principled BSDF
bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
bsdf.location = (0, 0)

# Set material properties
bsdf.inputs['Base Color'].default_value = {material_data['base_color']}
bsdf.inputs['Metallic'].default_value = {material_data['metallic']}
bsdf.inputs['Roughness'].default_value = {material_data['roughness']}
bsdf.inputs['Specular'].default_value = {material_data['specular']}
bsdf.inputs['Emission'].default_value = {material_data['emission_color']}
bsdf.inputs['Emission Strength'].default_value = {material_data['emission_strength']}
bsdf.inputs['Alpha'].default_value = {material_data['alpha']}
bsdf.inputs['IOR'].default_value = {material_data['ior']}
bsdf.inputs['Transmission'].default_value = {material_data['transmission']}
bsdf.inputs['Subsurface'].default_value = {material_data['subsurface']}

# Create Material Output
output = nodes.new(type='ShaderNodeOutputMaterial')
output.location = (300, 0)

# Link BSDF to output
links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
"""

        # Add procedural texture if specified
        if material_data.get('procedural_type'):
            script += self._add_procedural_texture_script(
                material_data['procedural_type'],
                material_data.get('normal_strength', 1.0)
            )

        # Add texture if path specified
        if material_data.get('use_texture') and material_data.get('texture_path'):
            script += self._add_image_texture_script(material_data['texture_path'])

        # Apply material to object
        script += f"""
# Apply material to object
obj = bpy.data.objects.get("{object_name}")
if obj:
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)
    print(f"Material '{material_name}' applied to '{object_name}'")
else:
    print(f"Warning: Object '{object_name}' not found")
"""

        return script

    def _add_procedural_texture_script(
        self,
        texture_type: str,
        normal_strength: float
    ) -> str:
        """Add procedural texture nodes to material script."""
        script = f"""
# Add procedural texture
tex_coord = nodes.new(type='ShaderNodeTexCoord')
tex_coord.location = (-600, 0)

mapping = nodes.new(type='ShaderNodeMapping')
mapping.location = (-400, 0)
links.new(tex_coord.outputs['Generated'], mapping.inputs['Vector'])

"""

        if texture_type == 'noise':
            script += """
noise_tex = nodes.new(type='ShaderNodeTexNoise')
noise_tex.location = (-200, 0)
noise_tex.inputs['Scale'].default_value = 5.0
links.new(mapping.outputs['Vector'], noise_tex.inputs['Vector'])
links.new(noise_tex.outputs['Color'], bsdf.inputs['Base Color'])
"""
        elif texture_type == 'voronoi':
            script += """
voronoi_tex = nodes.new(type='ShaderNodeTexVoronoi')
voronoi_tex.location = (-200, 0)
voronoi_tex.inputs['Scale'].default_value = 5.0
links.new(mapping.outputs['Vector'], voronoi_tex.inputs['Vector'])
links.new(voronoi_tex.outputs['Color'], bsdf.inputs['Base Color'])
"""
        elif texture_type in ['wood', 'marble']:
            script += """
wave_tex = nodes.new(type='ShaderNodeTexWave')
wave_tex.location = (-200, 0)
wave_tex.inputs['Scale'].default_value = 5.0
wave_tex.wave_type = 'BANDS'
links.new(mapping.outputs['Vector'], wave_tex.inputs['Vector'])
links.new(wave_tex.outputs['Color'], bsdf.inputs['Base Color'])
"""

        # Add normal map
        if normal_strength > 0:
            script += f"""
# Add normal map
bump = nodes.new(type='ShaderNodeBump')
bump.location = (-200, -200)
bump.inputs['Strength'].default_value = {normal_strength}
links.new(bsdf.outputs['BSDF'], bump.inputs['Normal'])
"""

        return script

    def _add_image_texture_script(self, texture_path: str) -> str:
        """Add image texture node to material script."""
        return f"""
# Add image texture
img_tex = nodes.new(type='ShaderNodeTexImage')
img_tex.location = (-200, 100)
img_tex.image = bpy.data.images.load("{texture_path}")
links.new(img_tex.outputs['Color'], bsdf.inputs['Base Color'])
"""

    def _generate_ai_texture(self, description: str) -> Optional[Dict[str, Any]]:
        """
        Generate texture using AI (placeholder for future implementation).

        Args:
            description: Texture description

        Returns:
            Texture data with path to generated image, or None if failed
        """
        logger.info(f"AI texture synthesis requested: {description}")

        # Placeholder for AI texture generation
        # Future implementation could integrate:
        # - Stable Diffusion XL
        # - DALL-E
        # - Midjourney API
        # - Custom texture synthesis models

        if not self.use_ai_synthesis:
            logger.debug("AI synthesis disabled")
            return None

        logger.warning("AI texture synthesis not yet implemented (placeholder)")

        # Placeholder return structure
        return None

        # Future implementation example:
        # try:
        #     if self.ai_provider == 'stable-diffusion':
        #         image = generate_sdxl_texture(description)
        #         texture_path = self.cache_dir / f"{hash(description)}.png"
        #         image.save(texture_path)
        #         return {'path': str(texture_path), 'description': description}
        # except Exception as e:
        #     logger.error(f"AI texture generation failed: {e}")
        #     return None


# Example usage and testing
if __name__ == "__main__":
    from utils.logger import setup_logging

    # Setup logging
    setup_logging(level="DEBUG", console=True)

    # Create synthesizer
    synthesizer = TextureSynthesizer()

    print("\n" + "="*80)
    print("TEXTURE SYNTHESIZER - TEST SUITE")
    print("="*80 + "\n")

    # Test 1: Material presets
    print("\n" + "="*80)
    print("Test 1: Material Presets")
    print("="*80 + "\n")

    for material_name in ['wood', 'metal', 'glass', 'gold', 'marble']:
        material = synthesizer.MATERIAL_PRESETS[material_name]
        print(f"\n{material_name.upper()}:")
        print(f"  Base Color: {material.base_color}")
        print(f"  Metallic: {material.metallic}")
        print(f"  Roughness: {material.roughness}")
        print(f"  Procedural: {material.procedural_type}")

    # Test 2: Generate texture from description
    print("\n" + "="*80)
    print("Test 2: Generate Textures from Descriptions")
    print("="*80 + "\n")

    descriptions = [
        "rough wooden surface",
        "shiny red metal",
        "transparent glass",
        "matte black plastic",
        "polished gold"
    ]

    for desc in descriptions:
        texture = synthesizer.generate_texture(desc)
        print(f"\nDescription: '{desc}'")
        print(f"  Material: {texture['name']}")
        print(f"  Color: {texture['base_color']}")
        print(f"  Roughness: {texture['roughness']}")
        print(f"  Metallic: {texture['metallic']}")

    # Test 3: Apply to scene
    print("\n" + "="*80)
    print("Test 3: Apply Materials to Scene")
    print("="*80 + "\n")

    test_scene = {
        'objects': [
            {
                'name': 'table',
                'category': 'furniture',
                'modifiers': ['wooden']
            },
            {
                'name': 'phone',
                'category': 'electronics',
                'modifiers': []
            },
            {
                'name': 'vase',
                'category': 'decor',
                'attributes': {'material': 'ceramic'}
            }
        ]
    }

    result = synthesizer.apply(test_scene, style='realistic')

    print(f"\nApplied materials to {len(result['objects'])} objects:")
    for obj in result['objects']:
        mat = obj.get('material', {})
        print(f"\n  {obj['name']} ({obj['category']}):")
        print(f"    Material: {mat.get('name', 'N/A')}")
        print(f"    Color: {mat.get('base_color', 'N/A')}")

    # Test 4: Generate Blender script
    print("\n" + "="*80)
    print("Test 4: Generate Blender Material Script")
    print("="*80 + "\n")

    material_dict = synthesizer.apply_texture_to_object('TestCube', material_type='wood')
    print("Generated Blender script (first 500 chars):")
    print(material_dict.get('blender_script', '')[:500])

    print("\n" + "="*80)
    print("TEST SUITE COMPLETE")
    print("="*80 + "\n")
