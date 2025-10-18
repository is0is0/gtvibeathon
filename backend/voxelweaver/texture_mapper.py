"""
Texture Mapper Module
---------------------
Handles material and texture application for 3D objects.

This module creates PBR materials, procedural textures, and manages UV mapping
for realistic and stylized material rendering.
"""

import logging
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

logger = logging.getLogger(__name__)


class MaterialType(Enum):
    """Types of materials."""
    PBR = "pbr"  # Physically-based rendering
    PROCEDURAL = "procedural"  # Procedural textures
    SOLID = "solid"  # Solid color
    TEXTURE = "texture"  # Image texture
    EMISSION = "emission"  # Emissive material
    GLASS = "glass"  # Glass/transparent
    SUBSURFACE = "subsurface"  # Subsurface scattering
    METAL = "metal"  # Metallic


class TextureType(Enum):
    """Types of textures."""
    ALBEDO = "albedo"
    METALLIC = "metallic"
    ROUGHNESS = "roughness"
    NORMAL = "normal"
    DISPLACEMENT = "displacement"
    AMBIENT_OCCLUSION = "ao"
    EMISSION = "emission"


@dataclass
class MaterialProperties:
    """Properties for a PBR material."""
    base_color: Tuple[float, float, float, float] = (0.8, 0.8, 0.8, 1.0)
    metallic: float = 0.0
    roughness: float = 0.5
    specular: float = 0.5
    ior: float = 1.45  # Index of refraction
    transmission: float = 0.0
    emission_color: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    emission_strength: float = 0.0
    alpha: float = 1.0
    subsurface_weight: float = 0.0
    subsurface_radius: Tuple[float, float, float] = (1.0, 0.2, 0.1)
    normal_strength: float = 1.0
    clearcoat: float = 0.0
    clearcoat_roughness: float = 0.03
    sheen: float = 0.0
    sheen_tint: float = 0.5


@dataclass
class ProceduralTexture:
    """Procedural texture node configuration."""
    texture_type: str  # noise, voronoi, wave, magic, etc.
    scale: float = 5.0
    detail: float = 2.0
    roughness: float = 0.5
    distortion: float = 0.0
    color1: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    color2: Tuple[float, float, float] = (1.0, 1.0, 1.0)


@dataclass
class Material:
    """Complete material definition."""
    name: str
    material_type: MaterialType
    properties: MaterialProperties = field(default_factory=MaterialProperties)
    textures: Dict[str, str] = field(default_factory=dict)  # texture_type -> path
    procedural: Optional[ProceduralTexture] = None
    uv_mapping: str = "UV"  # UV, CUBE, SPHERE, CYLINDER
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'name': self.name,
            'type': self.material_type.value,
            'properties': {
                'base_color': list(self.properties.base_color),
                'metallic': self.properties.metallic,
                'roughness': self.properties.roughness,
                'specular': self.properties.specular,
                'ior': self.properties.ior,
                'transmission': self.properties.transmission,
                'emission_color': list(self.properties.emission_color),
                'emission_strength': self.properties.emission_strength,
                'alpha': self.properties.alpha,
                'subsurface_weight': self.properties.subsurface_weight,
                'subsurface_radius': list(self.properties.subsurface_radius),
                'normal_strength': self.properties.normal_strength,
                'clearcoat': self.properties.clearcoat,
                'clearcoat_roughness': self.properties.clearcoat_roughness,
                'sheen': self.properties.sheen,
                'sheen_tint': self.properties.sheen_tint
            },
            'textures': self.textures,
            'procedural': self._procedural_to_dict(),
            'uv_mapping': self.uv_mapping,
            'metadata': self.metadata
        }

    def _procedural_to_dict(self) -> Optional[Dict[str, Any]]:
        """Convert procedural texture to dict."""
        if not self.procedural:
            return None

        return {
            'type': self.procedural.texture_type,
            'scale': self.procedural.scale,
            'detail': self.procedural.detail,
            'roughness': self.procedural.roughness,
            'distortion': self.procedural.distortion,
            'color1': list(self.procedural.color1),
            'color2': list(self.procedural.color2)
        }


class TextureMapper:
    """
    Handles material and texture application for 3D objects.

    This class creates and applies materials to objects, supporting PBR
    workflows, procedural textures, and various material types.

    Example:
        >>> mapper = TextureMapper()
        >>> scene = {"objects": [...]}
        >>> textured_scene = mapper.apply(scene, style="realistic")
        >>> print(f"Applied materials to {len(textured_scene['objects'])} objects")
    """

    def __init__(
        self,
        texture_library: Optional[Path] = None,
        default_uv_method: str = "UV"
    ):
        """
        Initialize texture mapper.

        Args:
            texture_library: Path to texture library directory
            default_uv_method: Default UV mapping method
        """
        self.texture_library = texture_library or Path("assets/textures")
        self.default_uv_method = default_uv_method

        # Material presets
        self.material_presets = self._initialize_material_presets()

        logger.info("TextureMapper initialized")

    def _initialize_material_presets(self) -> Dict[str, MaterialProperties]:
        """
        Initialize material property presets.

        Returns:
            Dictionary of material presets
        """
        return {
            # Metals
            "steel": MaterialProperties(
                base_color=(0.6, 0.6, 0.65, 1.0),
                metallic=1.0,
                roughness=0.3
            ),
            "gold": MaterialProperties(
                base_color=(1.0, 0.766, 0.336, 1.0),
                metallic=1.0,
                roughness=0.2
            ),
            "copper": MaterialProperties(
                base_color=(0.955, 0.637, 0.538, 1.0),
                metallic=1.0,
                roughness=0.25
            ),
            "aluminum": MaterialProperties(
                base_color=(0.913, 0.921, 0.925, 1.0),
                metallic=1.0,
                roughness=0.4
            ),

            # Non-metals
            "wood": MaterialProperties(
                base_color=(0.4, 0.25, 0.15, 1.0),
                metallic=0.0,
                roughness=0.7
            ),
            "plastic": MaterialProperties(
                base_color=(0.8, 0.8, 0.8, 1.0),
                metallic=0.0,
                roughness=0.3,
                specular=0.5
            ),
            "rubber": MaterialProperties(
                base_color=(0.2, 0.2, 0.2, 1.0),
                metallic=0.0,
                roughness=0.9
            ),
            "fabric": MaterialProperties(
                base_color=(0.6, 0.6, 0.7, 1.0),
                metallic=0.0,
                roughness=0.8,
                sheen=0.5
            ),
            "leather": MaterialProperties(
                base_color=(0.3, 0.2, 0.15, 1.0),
                metallic=0.0,
                roughness=0.6,
                sheen=0.2
            ),
            "ceramic": MaterialProperties(
                base_color=(0.9, 0.9, 0.85, 1.0),
                metallic=0.0,
                roughness=0.2,
                clearcoat=0.5
            ),

            # Special materials
            "glass": MaterialProperties(
                base_color=(1.0, 1.0, 1.0, 1.0),
                metallic=0.0,
                roughness=0.0,
                transmission=1.0,
                ior=1.45
            ),
            "glass_frosted": MaterialProperties(
                base_color=(1.0, 1.0, 1.0, 1.0),
                metallic=0.0,
                roughness=0.3,
                transmission=1.0,
                ior=1.45
            ),
            "water": MaterialProperties(
                base_color=(0.3, 0.5, 0.7, 1.0),
                metallic=0.0,
                roughness=0.0,
                transmission=0.9,
                ior=1.33
            ),
            "skin": MaterialProperties(
                base_color=(0.95, 0.75, 0.65, 1.0),
                metallic=0.0,
                roughness=0.4,
                subsurface_weight=0.3,
                subsurface_radius=(1.0, 0.5, 0.3)
            ),
            "wax": MaterialProperties(
                base_color=(0.95, 0.9, 0.85, 1.0),
                metallic=0.0,
                roughness=0.2,
                subsurface_weight=0.5,
                subsurface_radius=(0.5, 0.3, 0.2)
            )
        }

    def apply(
        self,
        scene: Dict[str, Any],
        style: str = "realistic",
        custom_materials: Optional[Dict[str, Material]] = None
    ) -> Dict[str, Any]:
        """
        Apply materials to scene objects.

        This is the main entry point for material application. It analyzes
        objects and assigns appropriate materials.

        Args:
            scene: Scene data with objects
            style: Material style ('realistic', 'stylized', 'flat', etc.)
            custom_materials: Optional custom material definitions

        Returns:
            Scene with material data

        Example:
            >>> mapper = TextureMapper()
            >>> scene = {"objects": [{"name": "table", ...}]}
            >>> textured = mapper.apply(scene, style="realistic")
        """
        logger.info(f"Applying materials to scene (style: {style})")

        textured_scene = scene.copy()
        objects = textured_scene.get('objects', [])

        # Apply materials to each object
        for obj in objects:
            material = self._assign_material(obj, style, custom_materials)
            obj['material'] = material.to_dict()

            # Generate/check UV mapping
            if 'uv_coords' not in obj:
                obj['uv_coords'] = self._generate_uv_coords(obj, material.uv_mapping)

        # Add material metadata
        textured_scene['metadata'] = textured_scene.get('metadata', {})
        textured_scene['metadata']['material_style'] = style
        textured_scene['metadata']['material_count'] = len(objects)

        logger.info(f"Applied materials to {len(objects)} objects")

        return textured_scene

    def _assign_material(
        self,
        obj: Dict[str, Any],
        style: str,
        custom_materials: Optional[Dict[str, Material]]
    ) -> Material:
        """
        Assign material to an object.

        Args:
            obj: Object to assign material to
            style: Material style
            custom_materials: Custom material definitions

        Returns:
            Material instance
        """
        object_name = obj.get('name', 'object')
        category = obj.get('category', obj.get('type', 'generic'))

        # Check for custom material
        if custom_materials and object_name in custom_materials:
            return custom_materials[object_name]

        # Determine material based on object type and style
        if style == "realistic":
            return self._create_realistic_material(object_name, category)
        elif style == "stylized":
            return self._create_stylized_material(object_name, category)
        elif style == "flat":
            return self._create_flat_material(object_name)
        else:
            return self._create_default_material(object_name)

    def _create_realistic_material(
        self,
        name: str,
        category: str
    ) -> Material:
        """
        Create realistic PBR material.

        Args:
            name: Object name
            category: Object category

        Returns:
            Material instance
        """
        name_lower = name.lower()

        # Determine material type from name
        material_key = None
        for preset_name in self.material_presets.keys():
            if preset_name in name_lower:
                material_key = preset_name
                break

        # Fallback based on category
        if not material_key:
            category_defaults = {
                'furniture': 'wood',
                'lighting': 'plastic',
                'decoration': 'ceramic',
                'appliance': 'steel',
                'architectural': 'concrete'
            }
            material_key = category_defaults.get(category, 'plastic')

        properties = self.material_presets.get(material_key, MaterialProperties())

        # Check for textures
        textures = self._find_textures(name, material_key)

        return Material(
            name=f"{name}_material",
            material_type=MaterialType.PBR,
            properties=properties,
            textures=textures,
            uv_mapping=self.default_uv_method,
            metadata={'category': category, 'preset': material_key}
        )

    def _create_stylized_material(
        self,
        name: str,
        category: str
    ) -> Material:
        """
        Create stylized material with procedural textures.

        Args:
            name: Object name
            category: Object category

        Returns:
            Material instance
        """
        # Use procedural textures for stylized look
        procedural = ProceduralTexture(
            texture_type='noise',
            scale=np.random.uniform(3.0, 8.0),
            detail=2.0,
            roughness=0.5,
            color1=(np.random.random(), np.random.random(), np.random.random()),
            color2=(np.random.random(), np.random.random(), np.random.random())
        )

        properties = MaterialProperties(
            base_color=(0.8, 0.8, 0.8, 1.0),
            metallic=0.0,
            roughness=0.6
        )

        return Material(
            name=f"{name}_stylized",
            material_type=MaterialType.PROCEDURAL,
            properties=properties,
            procedural=procedural,
            uv_mapping="CUBE",
            metadata={'category': category, 'style': 'stylized'}
        )

    def _create_flat_material(self, name: str) -> Material:
        """
        Create flat solid color material.

        Args:
            name: Object name

        Returns:
            Material instance
        """
        # Random pleasant color
        hue = np.random.random()
        saturation = 0.6
        value = 0.8

        # HSV to RGB
        c = value * saturation
        x = c * (1 - abs((hue * 6) % 2 - 1))
        m = value - c

        if hue < 1/6:
            rgb = (c, x, 0)
        elif hue < 2/6:
            rgb = (x, c, 0)
        elif hue < 3/6:
            rgb = (0, c, x)
        elif hue < 4/6:
            rgb = (0, x, c)
        elif hue < 5/6:
            rgb = (x, 0, c)
        else:
            rgb = (c, 0, x)

        base_color = tuple(r + m for r in rgb) + (1.0,)

        properties = MaterialProperties(
            base_color=base_color,
            metallic=0.0,
            roughness=0.8,
            specular=0.2
        )

        return Material(
            name=f"{name}_flat",
            material_type=MaterialType.SOLID,
            properties=properties,
            uv_mapping=self.default_uv_method,
            metadata={'style': 'flat'}
        )

    def _create_default_material(self, name: str) -> Material:
        """
        Create default fallback material.

        Args:
            name: Object name

        Returns:
            Material instance
        """
        return Material(
            name=f"{name}_default",
            material_type=MaterialType.PBR,
            properties=MaterialProperties(),
            uv_mapping=self.default_uv_method,
            metadata={}
        )

    def _find_textures(
        self,
        object_name: str,
        material_key: str
    ) -> Dict[str, str]:
        """
        Find texture files for a material.

        Args:
            object_name: Object name
            material_key: Material preset key

        Returns:
            Dictionary mapping texture types to file paths
        """
        textures = {}

        if not self.texture_library.exists():
            return textures

        # Look for texture files
        material_dir = self.texture_library / material_key

        if material_dir.exists():
            texture_map = {
                'albedo': ['albedo', 'diffuse', 'color', 'base_color'],
                'metallic': ['metallic', 'metal'],
                'roughness': ['roughness', 'rough'],
                'normal': ['normal', 'nrm'],
                'ao': ['ao', 'ambient_occlusion'],
                'displacement': ['displacement', 'height', 'disp']
            }

            for tex_type, variations in texture_map.items():
                for variation in variations:
                    for ext in ['.png', '.jpg', '.exr']:
                        tex_file = material_dir / f"{variation}{ext}"
                        if tex_file.exists():
                            textures[tex_type] = str(tex_file)
                            break
                    if tex_type in textures:
                        break

        return textures

    def _generate_uv_coords(
        self,
        obj: Dict[str, Any],
        mapping_method: str
    ) -> List[List[float]]:
        """
        Generate UV coordinates for an object.

        Args:
            obj: Object data
            mapping_method: UV mapping method

        Returns:
            UV coordinates array
        """
        vertices = obj.get('vertices', [])

        if vertices is None or (isinstance(vertices, (list, np.ndarray)) and len(vertices) == 0):
            return []

        if not isinstance(vertices, np.ndarray):
            vertices = np.array(vertices)

        # Generate UVs based on method
        if mapping_method == "UV":
            return self._generate_planar_uv(vertices)
        elif mapping_method == "CUBE":
            return self._generate_cube_uv(vertices)
        elif mapping_method == "SPHERE":
            return self._generate_spherical_uv(vertices)
        elif mapping_method == "CYLINDER":
            return self._generate_cylindrical_uv(vertices)
        else:
            return self._generate_planar_uv(vertices)

    def _generate_planar_uv(self, vertices: np.ndarray) -> List[List[float]]:
        """Generate planar UV mapping."""
        if len(vertices) == 0:
            return []

        # Project to XY plane
        min_x, min_y = vertices[:, 0].min(), vertices[:, 1].min()
        max_x, max_y = vertices[:, 0].max(), vertices[:, 1].max()

        range_x = max_x - min_x if max_x != min_x else 1.0
        range_y = max_y - min_y if max_y != min_y else 1.0

        uvs = []
        for vertex in vertices:
            u = (vertex[0] - min_x) / range_x
            v = (vertex[1] - min_y) / range_y
            uvs.append([u, v])

        return uvs

    def _generate_cube_uv(self, vertices: np.ndarray) -> List[List[float]]:
        """Generate cubic UV mapping."""
        # Simple box projection
        return self._generate_planar_uv(vertices)

    def _generate_spherical_uv(self, vertices: np.ndarray) -> List[List[float]]:
        """Generate spherical UV mapping."""
        if len(vertices) == 0:
            return []

        uvs = []
        for vertex in vertices:
            x, y, z = vertex[0], vertex[1], vertex[2]

            # Convert to spherical coordinates
            theta = np.arctan2(y, x)
            phi = np.arctan2(np.sqrt(x*x + y*y), z)

            u = 0.5 + theta / (2 * np.pi)
            v = phi / np.pi

            uvs.append([u, v])

        return uvs

    def _generate_cylindrical_uv(self, vertices: np.ndarray) -> List[List[float]]:
        """Generate cylindrical UV mapping."""
        if len(vertices) == 0:
            return []

        min_z, max_z = vertices[:, 2].min(), vertices[:, 2].max()
        range_z = max_z - min_z if max_z != min_z else 1.0

        uvs = []
        for vertex in vertices:
            x, y, z = vertex[0], vertex[1], vertex[2]

            # Cylindrical projection
            theta = np.arctan2(y, x)
            u = 0.5 + theta / (2 * np.pi)
            v = (z - min_z) / range_z

            uvs.append([u, v])

        return uvs

    def create_emission_material(
        self,
        name: str,
        color: Tuple[float, float, float],
        strength: float = 10.0
    ) -> Material:
        """
        Create emissive material for light sources.

        Args:
            name: Material name
            color: Emission color (RGB)
            strength: Emission strength

        Returns:
            Material instance

        Example:
            >>> mapper = TextureMapper()
            >>> light_mat = mapper.create_emission_material(
            ...     "light_bulb",
            ...     color=(1.0, 0.9, 0.7),
            ...     strength=50.0
            ... )
        """
        properties = MaterialProperties(
            base_color=(1.0, 1.0, 1.0, 1.0),
            emission_color=color,
            emission_strength=strength
        )

        return Material(
            name=name,
            material_type=MaterialType.EMISSION,
            properties=properties,
            metadata={'emissive': True}
        )


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    mapper = TextureMapper()

    # Create test scene
    test_scene = {
        "objects": [
            {
                "name": "wooden_table",
                "category": "furniture",
                "vertices": np.random.rand(100, 3)
            },
            {
                "name": "steel_chair",
                "category": "furniture",
                "vertices": np.random.rand(80, 3)
            },
            {
                "name": "glass_vase",
                "category": "decoration",
                "vertices": np.random.rand(60, 3)
            }
        ]
    }

    # Test different styles
    for style in ["realistic", "stylized", "flat"]:
        print(f"\n{'='*60}")
        print(f"Testing {style.upper()} materials")
        print('='*60)

        textured = mapper.apply(test_scene, style=style)

        for obj in textured['objects']:
            mat = obj['material']
            print(f"\n{obj['name']}:")
            print(f"  Material: {mat['name']}")
            print(f"  Type: {mat['type']}")
            print(f"  Base Color: {mat['properties']['base_color']}")
            print(f"  Metallic: {mat['properties']['metallic']}")
            print(f"  Roughness: {mat['properties']['roughness']}")
            print(f"  UV Mapping: {mat['uv_mapping']}")

    # Test emission material
    print("\n" + "="*60)
    print("Testing EMISSION material")
    print("="*60)

    emission_mat = mapper.create_emission_material(
        "light_bulb",
        color=(1.0, 0.9, 0.7),
        strength=50.0
    )

    print(f"\n{emission_mat.name}:")
    print(f"  Type: {emission_mat.material_type.value}")
    print(f"  Emission Color: {emission_mat.properties.emission_color}")
    print(f"  Emission Strength: {emission_mat.properties.emission_strength}")
