"""
Advanced Texture Catalog - Comprehensive texture mapping system.
Provides intricate texture generation with multiple map types for realistic materials.
"""

import logging
import random
import math
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

logger = logging.getLogger(__name__)


class TextureType(str, Enum):
    """Types of texture maps."""
    DIFFUSE = "diffuse"  # Color/albedo
    NORMAL = "normal"  # Surface bumps
    SPECULAR = "specular"  # Shininess
    ROUGHNESS = "roughness"  # Surface roughness
    METALLIC = "metallic"  # Metallic vs non-metallic
    DISPLACEMENT = "displacement"  # Physical geometry alteration
    OPACITY = "opacity"  # Transparency
    EMISSION = "emission"  # Glowing surfaces
    AO = "ao"  # Ambient occlusion
    HEIGHT = "height"  # Height information
    DETAIL = "detail"  # Fine surface details
    MASK = "mask"  # Mixing masks


class MaterialCategory(str, Enum):
    """Material categories for organization."""
    ORGANIC = "organic"  # Wood, leather, fabric, skin
    METALLIC = "metallic"  # Steel, aluminum, gold, copper
    MINERAL = "mineral"  # Stone, concrete, ceramic, glass
    LIQUID = "liquid"  # Water, oil, blood, paint
    FABRIC = "fabric"  # Cotton, silk, denim, wool
    PLASTIC = "plastic"  # Hard plastic, rubber, vinyl
    NATURAL = "natural"  # Grass, leaves, bark, fur
    SYNTHETIC = "synthetic"  # Carbon fiber, neoprene, foam
    EMISSIVE = "emissive"  # Neon, LED, plasma, fire
    TRANSPARENT = "transparent"  # Glass, crystal, water, ice


class EnvironmentType(str, Enum):
    """Environment types for material adaptation."""
    INDOOR = "indoor"
    OUTDOOR = "outdoor"
    STUDIO = "studio"
    NIGHT = "night"
    UNDERWATER = "underwater"
    SPACE = "space"
    INDUSTRIAL = "industrial"
    NATURAL = "natural"
    URBAN = "urban"
    FANTASY = "fantasy"


@dataclass
class TextureMap:
    """A single texture map with properties."""
    map_type: TextureType
    resolution: Tuple[int, int]  # Width, height
    file_format: str  # PNG, EXR, HDR, etc.
    color_space: str  # sRGB, Linear, Raw
    compression: str  # None, LZ4, ZIP
    tiling: Tuple[float, float]  # U, V tiling
    offset: Tuple[float, float]  # U, V offset
    rotation: float  # Rotation in degrees
    blend_mode: str  # Multiply, Overlay, Screen, etc.
    intensity: float  # 0.0 to 1.0
    contrast: float  # 0.0 to 2.0
    brightness: float  # -1.0 to 1.0
    saturation: float  # 0.0 to 2.0
    procedural: bool  # Generated vs imported
    generation_method: Optional[str] = None
    parameters: Dict[str, Any] = None

    def __post_init__(self):
        if self.parameters is None:
            self.parameters = {}


@dataclass
class MaterialPreset:
    """A complete material preset with all texture maps."""
    name: str
    category: MaterialCategory
    description: str
    base_color: Tuple[float, float, float, float]  # RGBA
    roughness: float  # 0.0 to 1.0
    metallic: float  # 0.0 to 1.0
    specular: float  # 0.0 to 1.0
    emission_strength: float  # 0.0 to 10.0
    transmission: float  # 0.0 to 1.0 (for glass)
    ior: float  # Index of refraction
    subsurface: float  # 0.0 to 1.0
    anisotropy: float  # 0.0 to 1.0
    sheen: float  # 0.0 to 1.0
    clearcoat: float  # 0.0 to 1.0
    clearcoat_roughness: float  # 0.0 to 1.0
    texture_maps: Dict[TextureType, TextureMap]
    shader_nodes: List[str]  # Custom shader node setup
    environment_adaptation: Dict[str, float]  # How it adapts to different environments
    quality_level: str  # low, medium, high, production
    complexity_score: float  # 0.0 to 1.0


class AdvancedTextureCatalog:
    """
    Advanced texture catalog system for intricate material generation.
    Provides comprehensive texture mapping with multiple map types.
    """

    def __init__(self):
        """Initialize advanced texture catalog."""
        self.material_presets = {}
        self.texture_generators = {}
        self.environment_adapters = {}
        self._initialize_catalog()
        logger.info("AdvancedTextureCatalog initialized")

    def _initialize_catalog(self):
        """Initialize the texture catalog with comprehensive presets."""
        
        # Organic Materials
        self._create_wood_materials()
        self._create_leather_materials()
        self._create_fabric_materials()
        self._create_skin_materials()
        
        # Metallic Materials
        self._create_steel_materials()
        self._create_aluminum_materials()
        self._create_gold_materials()
        self._create_copper_materials()
        
        # Mineral Materials
        self._create_stone_materials()
        self._create_concrete_materials()
        self._create_ceramic_materials()
        self._create_glass_materials()
        
        # Synthetic Materials
        self._create_plastic_materials()
        self._create_rubber_materials()
        self._create_carbon_fiber_materials()
        
        # Natural Materials
        self._create_grass_materials()
        self._create_bark_materials()
        self._create_water_materials()
        
        # Emissive Materials
        self._create_neon_materials()
        self._create_led_materials()
        self._create_plasma_materials()
        
        logger.info(f"Initialized {len(self.material_presets)} material presets")

    def _create_wood_materials(self):
        """Create comprehensive wood material presets."""
        
        # Oak Wood
        oak_textures = {
            TextureType.DIFFUSE: TextureMap(
                map_type=TextureType.DIFFUSE,
                resolution=(2048, 2048),
                file_format="PNG",
                color_space="sRGB",
                compression="None",
                tiling=(4.0, 4.0),
                offset=(0.0, 0.0),
                rotation=0.0,
                blend_mode="Multiply",
                intensity=1.0,
                contrast=1.2,
                brightness=0.1,
                saturation=0.9,
                procedural=True,
                generation_method="procedural_wood",
                parameters={
                    "wood_type": "oak",
                    "grain_density": 0.8,
                    "grain_contrast": 0.7,
                    "color_variation": 0.3,
                    "age_factor": 0.5
                }
            ),
            TextureType.NORMAL: TextureMap(
                map_type=TextureType.NORMAL,
                resolution=(2048, 2048),
                file_format="PNG",
                color_space="Linear",
                compression="None",
                tiling=(4.0, 4.0),
                offset=(0.0, 0.0),
                rotation=0.0,
                blend_mode="Normal",
                intensity=0.8,
                contrast=1.0,
                brightness=0.0,
                saturation=1.0,
                procedural=True,
                generation_method="procedural_normal",
                parameters={
                    "strength": 0.8,
                    "detail_level": 0.6,
                    "grain_bumps": True
                }
            ),
            TextureType.ROUGHNESS: TextureMap(
                map_type=TextureType.ROUGHNESS,
                resolution=(2048, 2048),
                file_format="PNG",
                color_space="Linear",
                compression="None",
                tiling=(4.0, 4.0),
                offset=(0.0, 0.0),
                rotation=0.0,
                blend_mode="Multiply",
                intensity=0.7,
                contrast=1.1,
                brightness=0.2,
                saturation=1.0,
                procedural=True,
                generation_method="procedural_roughness",
                parameters={
                    "base_roughness": 0.7,
                    "variation": 0.3,
                    "grain_roughness": 0.8
                }
            ),
            TextureType.METALLIC: TextureMap(
                map_type=TextureType.METALLIC,
                resolution=(2048, 2048),
                file_format="PNG",
                color_space="Linear",
                compression="None",
                tiling=(4.0, 4.0),
                offset=(0.0, 0.0),
                rotation=0.0,
                blend_mode="Multiply",
                intensity=0.0,
                contrast=1.0,
                brightness=0.0,
                saturation=1.0,
                procedural=True,
                generation_method="constant",
                parameters={"value": 0.0}
            ),
            TextureType.AO: TextureMap(
                map_type=TextureType.AO,
                resolution=(2048, 2048),
                file_format="PNG",
                color_space="Linear",
                compression="None",
                tiling=(4.0, 4.0),
                offset=(0.0, 0.0),
                rotation=0.0,
                blend_mode="Multiply",
                intensity=0.8,
                contrast=1.2,
                brightness=0.1,
                saturation=1.0,
                procedural=True,
                generation_method="procedural_ao",
                parameters={
                    "strength": 0.8,
                    "detail_ao": True,
                    "grain_ao": True
                }
            )
        }
        
        self.material_presets["oak_wood"] = MaterialPreset(
            name="Oak Wood",
            category=MaterialCategory.ORGANIC,
            description="Natural oak wood with visible grain and subtle color variation",
            base_color=(0.6, 0.4, 0.2, 1.0),
            roughness=0.7,
            metallic=0.0,
            specular=0.5,
            emission_strength=0.0,
            transmission=0.0,
            ior=1.5,
            subsurface=0.1,
            anisotropy=0.0,
            sheen=0.0,
            clearcoat=0.0,
            clearcoat_roughness=0.0,
            texture_maps=oak_textures,
            shader_nodes=["Principled BSDF", "Image Texture", "Normal Map", "Mapping"],
            environment_adaptation={
                "indoor": 1.0,
                "outdoor": 0.8,
                "studio": 1.2,
                "night": 0.6
            },
            quality_level="high",
            complexity_score=0.7
        )
        
        # Add more wood variants
        self._create_wood_variants()

    def _create_wood_variants(self):
        """Create variants of wood materials."""
        
        wood_variants = [
            {
                "name": "mahogany_wood",
                "base_color": (0.4, 0.2, 0.1, 1.0),
                "description": "Rich mahogany wood with deep red-brown tones",
                "grain_contrast": 0.9,
                "color_variation": 0.2
            },
            {
                "name": "pine_wood",
                "base_color": (0.8, 0.7, 0.5, 1.0),
                "description": "Light pine wood with subtle grain",
                "grain_contrast": 0.4,
                "color_variation": 0.1
            },
            {
                "name": "walnut_wood",
                "base_color": (0.3, 0.2, 0.1, 1.0),
                "description": "Dark walnut wood with strong grain pattern",
                "grain_contrast": 0.8,
                "color_variation": 0.4
            }
        ]
        
        for variant in wood_variants:
            # Create texture maps for each variant
            textures = self._generate_wood_textures(variant)
            
            self.material_presets[variant["name"]] = MaterialPreset(
                name=variant["name"].replace("_", " ").title(),
                category=MaterialCategory.ORGANIC,
                description=variant["description"],
                base_color=variant["base_color"],
                roughness=0.7,
                metallic=0.0,
                specular=0.5,
                emission_strength=0.0,
                transmission=0.0,
                ior=1.5,
                subsurface=0.1,
                anisotropy=0.0,
                sheen=0.0,
                clearcoat=0.0,
                clearcoat_roughness=0.0,
                texture_maps=textures,
                shader_nodes=["Principled BSDF", "Image Texture", "Normal Map", "Mapping"],
                environment_adaptation={
                    "indoor": 1.0,
                    "outdoor": 0.8,
                    "studio": 1.2,
                    "night": 0.6
                },
                quality_level="high",
                complexity_score=0.7
            )

    def _create_steel_materials(self):
        """Create comprehensive steel material presets."""
        
        # Stainless Steel
        steel_textures = {
            TextureType.DIFFUSE: TextureMap(
                map_type=TextureType.DIFFUSE,
                resolution=(2048, 2048),
                file_format="PNG",
                color_space="sRGB",
                compression="None",
                tiling=(8.0, 8.0),
                offset=(0.0, 0.0),
                rotation=0.0,
                blend_mode="Multiply",
                intensity=0.9,
                contrast=1.1,
                brightness=0.0,
                saturation=0.8,
                procedural=True,
                generation_method="procedural_metal",
                parameters={
                    "metal_type": "stainless_steel",
                    "scratches": True,
                    "wear_level": 0.3,
                    "polish_level": 0.8
                }
            ),
            TextureType.NORMAL: TextureMap(
                map_type=TextureType.NORMAL,
                resolution=(2048, 2048),
                file_format="PNG",
                color_space="Linear",
                compression="None",
                tiling=(8.0, 8.0),
                offset=(0.0, 0.0),
                rotation=0.0,
                blend_mode="Normal",
                intensity=0.6,
                contrast=1.0,
                brightness=0.0,
                saturation=1.0,
                procedural=True,
                generation_method="procedural_metal_normal",
                parameters={
                    "scratch_depth": 0.3,
                    "surface_detail": 0.5,
                    "brushed_pattern": True
                }
            ),
            TextureType.ROUGHNESS: TextureMap(
                map_type=TextureType.ROUGHNESS,
                resolution=(2048, 2048),
                file_format="PNG",
                color_space="Linear",
                compression="None",
                tiling=(8.0, 8.0),
                offset=(0.0, 0.0),
                rotation=0.0,
                blend_mode="Multiply",
                intensity=0.3,
                contrast=1.2,
                brightness=0.1,
                saturation=1.0,
                procedural=True,
                generation_method="procedural_metal_roughness",
                parameters={
                    "base_roughness": 0.3,
                    "scratch_roughness": 0.8,
                    "polish_variation": 0.2
                }
            ),
            TextureType.METALLIC: TextureMap(
                map_type=TextureType.METALLIC,
                resolution=(2048, 2048),
                file_format="PNG",
                color_space="Linear",
                compression="None",
                tiling=(8.0, 8.0),
                offset=(0.0, 0.0),
                rotation=0.0,
                blend_mode="Multiply",
                intensity=1.0,
                contrast=1.0,
                brightness=0.0,
                saturation=1.0,
                procedural=True,
                generation_method="constant",
                parameters={"value": 1.0}
            ),
            TextureType.SPECULAR: TextureMap(
                map_type=TextureType.SPECULAR,
                resolution=(2048, 2048),
                file_format="PNG",
                color_space="Linear",
                compression="None",
                tiling=(8.0, 8.0),
                offset=(0.0, 0.0),
                rotation=0.0,
                blend_mode="Multiply",
                intensity=0.9,
                contrast=1.1,
                brightness=0.0,
                saturation=1.0,
                procedural=True,
                generation_method="procedural_metal_specular",
                parameters={
                    "base_specular": 0.9,
                    "scratch_specular": 0.3,
                    "polish_specular": 1.0
                }
            )
        }
        
        self.material_presets["stainless_steel"] = MaterialPreset(
            name="Stainless Steel",
            category=MaterialCategory.METALLIC,
            description="Polished stainless steel with subtle scratches and wear",
            base_color=(0.7, 0.7, 0.7, 1.0),
            roughness=0.3,
            metallic=1.0,
            specular=0.9,
            emission_strength=0.0,
            transmission=0.0,
            ior=2.4,
            subsurface=0.0,
            anisotropy=0.0,
            sheen=0.0,
            clearcoat=0.0,
            clearcoat_roughness=0.0,
            texture_maps=steel_textures,
            shader_nodes=["Principled BSDF", "Image Texture", "Normal Map", "Mapping"],
            environment_adaptation={
                "indoor": 1.0,
                "outdoor": 0.9,
                "studio": 1.1,
                "night": 0.7
            },
            quality_level="production",
            complexity_score=0.8
        )

    def _create_glass_materials(self):
        """Create comprehensive glass material presets."""
        
        # Clear Glass
        glass_textures = {
            TextureType.DIFFUSE: TextureMap(
                map_type=TextureType.DIFFUSE,
                resolution=(1024, 1024),
                file_format="PNG",
                color_space="sRGB",
                compression="None",
                tiling=(1.0, 1.0),
                offset=(0.0, 0.0),
                rotation=0.0,
                blend_mode="Multiply",
                intensity=0.1,
                contrast=1.0,
                brightness=0.0,
                saturation=0.5,
                procedural=True,
                generation_method="procedural_glass",
                parameters={
                    "glass_type": "clear",
                    "tint_strength": 0.1,
                    "clarity": 0.95
                }
            ),
            TextureType.NORMAL: TextureMap(
                map_type=TextureType.NORMAL,
                resolution=(1024, 1024),
                file_format="PNG",
                color_space="Linear",
                compression="None",
                tiling=(1.0, 1.0),
                offset=(0.0, 0.0),
                rotation=0.0,
                blend_mode="Normal",
                intensity=0.2,
                contrast=1.0,
                brightness=0.0,
                saturation=1.0,
                procedural=True,
                generation_method="procedural_glass_normal",
                parameters={
                    "surface_imperfections": 0.2,
                    "micro_scratches": True,
                    "detail_level": 0.3
                }
            ),
            TextureType.ROUGHNESS: TextureMap(
                map_type=TextureType.ROUGHNESS,
                resolution=(1024, 1024),
                file_format="PNG",
                color_space="Linear",
                compression="None",
                tiling=(1.0, 1.0),
                offset=(0.0, 0.0),
                rotation=0.0,
                blend_mode="Multiply",
                intensity=0.1,
                contrast=1.0,
                brightness=0.0,
                saturation=1.0,
                procedural=True,
                generation_method="procedural_glass_roughness",
                parameters={
                    "base_roughness": 0.1,
                    "scratch_roughness": 0.3,
                    "polish_variation": 0.05
                }
            ),
            TextureType.METALLIC: TextureMap(
                map_type=TextureType.METALLIC,
                resolution=(1024, 1024),
                file_format="PNG",
                color_space="Linear",
                compression="None",
                tiling=(1.0, 1.0),
                offset=(0.0, 0.0),
                rotation=0.0,
                blend_mode="Multiply",
                intensity=0.0,
                contrast=1.0,
                brightness=0.0,
                saturation=1.0,
                procedural=True,
                generation_method="constant",
                parameters={"value": 0.0}
            ),
            TextureType.OPACITY: TextureMap(
                map_type=TextureType.OPACITY,
                resolution=(1024, 1024),
                file_format="PNG",
                color_space="Linear",
                compression="None",
                tiling=(1.0, 1.0),
                offset=(0.0, 0.0),
                rotation=0.0,
                blend_mode="Multiply",
                intensity=0.9,
                contrast=1.0,
                brightness=0.0,
                saturation=1.0,
                procedural=True,
                generation_method="procedural_glass_opacity",
                parameters={
                    "base_opacity": 0.9,
                    "edge_opacity": 1.0,
                    "thickness_variation": 0.1
                }
            )
        }
        
        self.material_presets["clear_glass"] = MaterialPreset(
            name="Clear Glass",
            category=MaterialCategory.TRANSPARENT,
            description="Crystal clear glass with subtle surface imperfections",
            base_color=(0.9, 0.9, 0.95, 0.9),
            roughness=0.1,
            metallic=0.0,
            specular=0.95,
            emission_strength=0.0,
            transmission=0.95,
            ior=1.5,
            subsurface=0.0,
            anisotropy=0.0,
            sheen=0.0,
            clearcoat=0.0,
            clearcoat_roughness=0.0,
            texture_maps=glass_textures,
            shader_nodes=["Principled BSDF", "Image Texture", "Normal Map", "Mapping", "Transparent BSDF"],
            environment_adaptation={
                "indoor": 1.0,
                "outdoor": 0.8,
                "studio": 1.2,
                "night": 0.6
            },
            quality_level="production",
            complexity_score=0.9
        )

    def _create_neon_materials(self):
        """Create emissive neon materials."""
        
        # Neon Blue
        neon_textures = {
            TextureType.DIFFUSE: TextureMap(
                map_type=TextureType.DIFFUSE,
                resolution=(1024, 1024),
                file_format="PNG",
                color_space="sRGB",
                compression="None",
                tiling=(1.0, 1.0),
                offset=(0.0, 0.0),
                rotation=0.0,
                blend_mode="Multiply",
                intensity=0.8,
                contrast=1.2,
                brightness=0.2,
                saturation=1.5,
                procedural=True,
                generation_method="procedural_neon",
                parameters={
                    "neon_color": (0.0, 0.5, 1.0),
                    "glow_intensity": 0.8,
                    "flicker": 0.1
                }
            ),
            TextureType.EMISSION: TextureMap(
                map_type=TextureType.EMISSION,
                resolution=(1024, 1024),
                file_format="PNG",
                color_space="Linear",
                compression="None",
                tiling=(1.0, 1.0),
                offset=(0.0, 0.0),
                rotation=0.0,
                blend_mode="Add",
                intensity=3.0,
                contrast=1.0,
                brightness=0.0,
                saturation=1.0,
                procedural=True,
                generation_method="procedural_neon_emission",
                parameters={
                    "emission_strength": 3.0,
                    "glow_falloff": 0.5,
                    "flicker_strength": 0.2
                }
            ),
            TextureType.ROUGHNESS: TextureMap(
                map_type=TextureType.ROUGHNESS,
                resolution=(1024, 1024),
                file_format="PNG",
                color_space="Linear",
                compression="None",
                tiling=(1.0, 1.0),
                offset=(0.0, 0.0),
                rotation=0.0,
                blend_mode="Multiply",
                intensity=0.2,
                contrast=1.0,
                brightness=0.0,
                saturation=1.0,
                procedural=True,
                generation_method="constant",
                parameters={"value": 0.2}
            ),
            TextureType.METALLIC: TextureMap(
                map_type=TextureType.METALLIC,
                resolution=(1024, 1024),
                file_format="PNG",
                color_space="Linear",
                compression="None",
                tiling=(1.0, 1.0),
                offset=(0.0, 0.0),
                rotation=0.0,
                blend_mode="Multiply",
                intensity=0.0,
                contrast=1.0,
                brightness=0.0,
                saturation=1.0,
                procedural=True,
                generation_method="constant",
                parameters={"value": 0.0}
            )
        }
        
        self.material_presets["neon_blue"] = MaterialPreset(
            name="Neon Blue",
            category=MaterialCategory.EMISSIVE,
            description="Bright blue neon with intense glow and subtle flicker",
            base_color=(0.0, 0.5, 1.0, 1.0),
            roughness=0.2,
            metallic=0.0,
            specular=0.8,
            emission_strength=3.0,
            transmission=0.0,
            ior=1.5,
            subsurface=0.0,
            anisotropy=0.0,
            sheen=0.0,
            clearcoat=0.0,
            clearcoat_roughness=0.0,
            texture_maps=neon_textures,
            shader_nodes=["Principled BSDF", "Emission", "Image Texture", "Mapping"],
            environment_adaptation={
                "indoor": 1.0,
                "outdoor": 1.2,
                "studio": 0.8,
                "night": 1.5
            },
            quality_level="high",
            complexity_score=0.6
        )

    def _generate_wood_textures(self, variant: Dict) -> Dict[TextureType, TextureMap]:
        """Generate texture maps for wood variants."""
        return {
            TextureType.DIFFUSE: TextureMap(
                map_type=TextureType.DIFFUSE,
                resolution=(2048, 2048),
                file_format="PNG",
                color_space="sRGB",
                compression="None",
                tiling=(4.0, 4.0),
                offset=(0.0, 0.0),
                rotation=0.0,
                blend_mode="Multiply",
                intensity=1.0,
                contrast=1.2,
                brightness=0.1,
                saturation=0.9,
                procedural=True,
                generation_method="procedural_wood",
                parameters={
                    "wood_type": variant["name"].split("_")[0],
                    "grain_density": 0.8,
                    "grain_contrast": variant["grain_contrast"],
                    "color_variation": variant["color_variation"],
                    "age_factor": 0.5
                }
            ),
            TextureType.NORMAL: TextureMap(
                map_type=TextureType.NORMAL,
                resolution=(2048, 2048),
                file_format="PNG",
                color_space="Linear",
                compression="None",
                tiling=(4.0, 4.0),
                offset=(0.0, 0.0),
                rotation=0.0,
                blend_mode="Normal",
                intensity=0.8,
                contrast=1.0,
                brightness=0.0,
                saturation=1.0,
                procedural=True,
                generation_method="procedural_normal",
                parameters={
                    "strength": 0.8,
                    "detail_level": 0.6,
                    "grain_bumps": True
                }
            ),
            TextureType.ROUGHNESS: TextureMap(
                map_type=TextureType.ROUGHNESS,
                resolution=(2048, 2048),
                file_format="PNG",
                color_space="Linear",
                compression="None",
                tiling=(4.0, 4.0),
                offset=(0.0, 0.0),
                rotation=0.0,
                blend_mode="Multiply",
                intensity=0.7,
                contrast=1.1,
                brightness=0.2,
                saturation=1.0,
                procedural=True,
                generation_method="procedural_roughness",
                parameters={
                    "base_roughness": 0.7,
                    "variation": 0.3,
                    "grain_roughness": 0.8
                }
            ),
            TextureType.METALLIC: TextureMap(
                map_type=TextureType.METALLIC,
                resolution=(2048, 2048),
                file_format="PNG",
                color_space="Linear",
                compression="None",
                tiling=(4.0, 4.0),
                offset=(0.0, 0.0),
                rotation=0.0,
                blend_mode="Multiply",
                intensity=0.0,
                contrast=1.0,
                brightness=0.0,
                saturation=1.0,
                procedural=True,
                generation_method="constant",
                parameters={"value": 0.0}
            )
        }

    def get_material_preset(self, name: str) -> Optional[MaterialPreset]:
        """Get a material preset by name."""
        return self.material_presets.get(name)

    def get_materials_by_category(self, category: MaterialCategory) -> List[MaterialPreset]:
        """Get all materials in a category."""
        return [preset for preset in self.material_presets.values() 
                if preset.category == category]

    def get_materials_by_environment(self, environment: str) -> List[MaterialPreset]:
        """Get materials optimized for a specific environment."""
        optimized = []
        for preset in self.material_presets.values():
            if environment in preset.environment_adaptation:
                if preset.environment_adaptation[environment] > 0.8:
                    optimized.append(preset)
        return optimized

    def generate_custom_material(
        self,
        base_preset: str,
        modifications: Dict[str, Any]
    ) -> MaterialPreset:
        """Generate a custom material based on a preset with modifications."""
        
        base = self.get_material_preset(base_preset)
        if not base:
            raise ValueError(f"Base preset '{base_preset}' not found")
        
        # Create modified preset
        modified = MaterialPreset(
            name=f"{base.name} (Custom)",
            category=base.category,
            description=f"Custom variant of {base.description}",
            base_color=modifications.get("base_color", base.base_color),
            roughness=modifications.get("roughness", base.roughness),
            metallic=modifications.get("metallic", base.metallic),
            specular=modifications.get("specular", base.specular),
            emission_strength=modifications.get("emission_strength", base.emission_strength),
            transmission=modifications.get("transmission", base.transmission),
            ior=modifications.get("ior", base.ior),
            subsurface=modifications.get("subsurface", base.subsurface),
            anisotropy=modifications.get("anisotropy", base.anisotropy),
            sheen=modifications.get("sheen", base.sheen),
            clearcoat=modifications.get("clearcoat", base.clearcoat),
            clearcoat_roughness=modifications.get("clearcoat_roughness", base.clearcoat_roughness),
            texture_maps=base.texture_maps.copy(),
            shader_nodes=base.shader_nodes.copy(),
            environment_adaptation=base.environment_adaptation.copy(),
            quality_level=modifications.get("quality_level", base.quality_level),
            complexity_score=modifications.get("complexity_score", base.complexity_score)
        )
        
        return modified

    def generate_blender_material_code(self, preset: MaterialPreset) -> str:
        """Generate Blender Python code for a material preset."""
        
        code_lines = [
            "import bpy",
            "import bmesh",
            "from mathutils import Vector",
            "",
            f"# Create material: {preset.name}",
            f"mat = bpy.data.materials.new(name='{preset.name}')",
            "mat.use_nodes = True",
            "",
            "# Get the Principled BSDF node",
            "bsdf = mat.node_tree.nodes['Principled BSDF']",
            "",
            "# Set base properties",
            f"bsdf.inputs['Base Color'].default_value = {preset.base_color}",
            f"bsdf.inputs['Roughness'].default_value = {preset.roughness}",
            f"bsdf.inputs['Metallic'].default_value = {preset.metallic}",
            f"bsdf.inputs['Specular'].default_value = {preset.specular}",
            f"bsdf.inputs['Emission Strength'].default_value = {preset.emission_strength}",
            f"bsdf.inputs['Transmission Weight'].default_value = {preset.transmission}",
            f"bsdf.inputs['IOR'].default_value = {preset.ior}",
            f"bsdf.inputs['Subsurface Weight'].default_value = {preset.subsurface}",
            f"bsdf.inputs['Anisotropic'].default_value = {preset.anisotropy}",
            f"bsdf.inputs['Sheen Weight'].default_value = {preset.sheen}",
            f"bsdf.inputs['Clearcoat Weight'].default_value = {preset.clearcoat}",
            f"bsdf.inputs['Clearcoat Roughness'].default_value = {preset.clearcoat_roughness}",
            ""
        ]
        
        # Add texture map nodes
        for map_type, texture_map in preset.texture_maps.items():
            if texture_map.procedural:
                code_lines.extend(self._generate_procedural_texture_code(map_type, texture_map))
            else:
                code_lines.extend(self._generate_image_texture_code(map_type, texture_map))
        
        # Add custom shader nodes
        for node in preset.shader_nodes:
            if node not in ["Principled BSDF", "Image Texture", "Normal Map", "Mapping"]:
                code_lines.append(f"# Add {node} node")
                code_lines.append(f"# {node}_node = mat.node_tree.nodes.new('{node}')")
        
        code_lines.extend([
            "",
            "print(f'✅ Material created: {preset.name}')",
            "print(f'   Category: {preset.category.value}')",
            "print(f'   Quality: {preset.quality_level}')",
            "print(f'   Complexity: {preset.complexity_score:.2f}')"
        ])
        
        return "\n".join(code_lines)

    def _generate_procedural_texture_code(self, map_type: TextureType, texture_map: TextureMap) -> List[str]:
        """Generate Blender code for procedural textures."""
        
        code_lines = [
            f"# {map_type.value.title()} Map (Procedural)",
            f"# Generation method: {texture_map.generation_method}",
            f"# Parameters: {texture_map.parameters}",
            ""
        ]
        
        if map_type == TextureType.DIFFUSE:
            code_lines.extend([
                "# Add Image Texture node for diffuse",
                "diffuse_tex = mat.node_tree.nodes.new('ShaderNodeTexImage')",
                "diffuse_tex.name = 'Diffuse Texture'",
                "# Connect to Base Color",
                "mat.node_tree.links.new(diffuse_tex.outputs['Color'], bsdf.inputs['Base Color'])",
                ""
            ])
        elif map_type == TextureType.NORMAL:
            code_lines.extend([
                "# Add Normal Map node",
                "normal_map = mat.node_tree.nodes.new('ShaderNodeNormalMap')",
                "normal_tex = mat.node_tree.nodes.new('ShaderNodeTexImage')",
                "normal_tex.name = 'Normal Texture'",
                "# Connect normal map",
                "mat.node_tree.links.new(normal_tex.outputs['Color'], normal_map.inputs['Color'])",
                "mat.node_tree.links.new(normal_map.outputs['Normal'], bsdf.inputs['Normal'])",
                ""
            ])
        elif map_type == TextureType.ROUGHNESS:
            code_lines.extend([
                "# Add Roughness Map",
                "roughness_tex = mat.node_tree.nodes.new('ShaderNodeTexImage')",
                "roughness_tex.name = 'Roughness Texture'",
                "# Connect to Roughness",
                "mat.node_tree.links.new(roughness_tex.outputs['Color'], bsdf.inputs['Roughness'])",
                ""
            ])
        elif map_type == TextureType.METALLIC:
            code_lines.extend([
                "# Add Metallic Map",
                "metallic_tex = mat.node_tree.nodes.new('ShaderNodeTexImage')",
                "metallic_tex.name = 'Metallic Texture'",
                "# Connect to Metallic",
                "mat.node_tree.links.new(metallic_tex.outputs['Color'], bsdf.inputs['Metallic'])",
                ""
            ])
        elif map_type == TextureType.EMISSION:
            code_lines.extend([
                "# Add Emission Map",
                "emission_tex = mat.node_tree.nodes.new('ShaderNodeTexImage')",
                "emission_tex.name = 'Emission Texture'",
                "# Connect to Emission",
                "mat.node_tree.links.new(emission_tex.outputs['Color'], bsdf.inputs['Emission Color'])",
                ""
            ])
        
        return code_lines

    def _generate_image_texture_code(self, map_type: TextureType, texture_map: TextureMap) -> List[str]:
        """Generate Blender code for image textures."""
        
        return [
            f"# {map_type.value.title()} Map (Image Texture)",
            f"# File: {texture_map.file_format}",
            f"# Resolution: {texture_map.resolution}",
            f"# Tiling: {texture_map.tiling}",
            f"# Intensity: {texture_map.intensity}",
            ""
        ]

    def get_catalog_summary(self) -> Dict[str, Any]:
        """Get a summary of the texture catalog."""
        
        categories = {}
        for preset in self.material_presets.values():
            if preset.category not in categories:
                categories[preset.category] = []
            categories[preset.category].append(preset.name)
        
        return {
            "total_materials": len(self.material_presets),
            "categories": {cat.value: len(materials) for cat, materials in categories.items()},
            "quality_levels": {
                "low": len([p for p in self.material_presets.values() if p.quality_level == "low"]),
                "medium": len([p for p in self.material_presets.values() if p.quality_level == "medium"]),
                "high": len([p for p in self.material_presets.values() if p.quality_level == "high"]),
                "production": len([p for p in self.material_presets.values() if p.quality_level == "production"])
            },
            "complexity_distribution": {
                "simple": len([p for p in self.material_presets.values() if p.complexity_score < 0.3]),
                "moderate": len([p for p in self.material_presets.values() if 0.3 <= p.complexity_score < 0.7]),
                "complex": len([p for p in self.material_presets.values() if p.complexity_score >= 0.7])
            }
        }

    def _create_leather_materials(self):
        """Create leather material presets."""
        pass

    def _create_fabric_materials(self):
        """Create fabric material presets."""
        pass

    def _create_skin_materials(self):
        """Create skin material presets."""
        pass

    def _create_aluminum_materials(self):
        """Create aluminum material presets."""
        pass

    def _create_gold_materials(self):
        """Create gold material presets."""
        pass

    def _create_copper_materials(self):
        """Create copper material presets."""
        pass

    def _create_stone_materials(self):
        """Create stone material presets."""
        pass

    def _create_concrete_materials(self):
        """Create concrete material presets."""
        pass

    def _create_ceramic_materials(self):
        """Create ceramic material presets."""
        pass

    def _create_plastic_materials(self):
        """Create plastic material presets."""
        pass

    def _create_rubber_materials(self):
        """Create rubber material presets."""
        pass

    def _create_carbon_fiber_materials(self):
        """Create carbon fiber material presets."""
        pass

    def _create_grass_materials(self):
        """Create grass material presets."""
        pass

    def _create_bark_materials(self):
        """Create bark material presets."""
        pass

    def _create_water_materials(self):
        """Create water material presets."""
        pass

    def _create_led_materials(self):
        """Create LED material presets."""
        pass

    def _create_plasma_materials(self):
        """Create plasma material presets."""
        pass
