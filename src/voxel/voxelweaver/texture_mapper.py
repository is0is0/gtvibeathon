"""
Texture Mapper - Intelligent material and texture suggestion system.
Suggests appropriate materials based on object type and external references.
"""

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class MaterialType(str, Enum):
    """Types of materials."""
    PBR = "pbr"  # Physically Based Rendering
    PROCEDURAL = "procedural"  # Procedurally generated
    IMAGE_BASED = "image_based"  # Uses image textures
    SHADER_MIX = "shader_mix"  # Mix of shaders
    EMISSION = "emission"  # Emissive materials
    GLASS = "glass"  # Transparent/refractive
    METAL = "metal"  # Metallic materials


@dataclass
class MaterialSuggestion:
    """A suggested material configuration."""
    object_type: str
    material_name: str
    material_type: MaterialType
    base_color: tuple  # RGB
    roughness: float  # 0-1
    metallic: float  # 0-1
    specular: float  # 0-1
    transmission: float = 0.0  # For glass
    emission_strength: float = 0.0  # For emissive
    normal_strength: float = 1.0
    texture_hints: List[str] = None
    shader_nodes: List[str] = None
    quality_score: float = 0.8

    def __post_init__(self):
        if self.texture_hints is None:
            self.texture_hints = []
        if self.shader_nodes is None:
            self.shader_nodes = []


class TextureMapper:
    """
    Suggests materials and textures based on object types and external references.
    """

    # Material presets for common objects
    MATERIAL_PRESETS = {
        # Metals
        "metal": {
            "base_color": (0.8, 0.8, 0.8),
            "roughness": 0.2,
            "metallic": 1.0,
            "specular": 0.5,
            "type": MaterialType.METAL
        },
        "gold": {
            "base_color": (1.0, 0.85, 0.0),
            "roughness": 0.1,
            "metallic": 1.0,
            "specular": 0.5,
            "type": MaterialType.METAL
        },
        "copper": {
            "base_color": (0.95, 0.64, 0.54),
            "roughness": 0.3,
            "metallic": 1.0,
            "specular": 0.5,
            "type": MaterialType.METAL
        },

        # Woods
        "wood": {
            "base_color": (0.4, 0.25, 0.15),
            "roughness": 0.8,
            "metallic": 0.0,
            "specular": 0.3,
            "type": MaterialType.PBR,
            "textures": ["wood_grain", "bump"]
        },

        # Fabrics
        "fabric": {
            "base_color": (0.7, 0.7, 0.7),
            "roughness": 0.9,
            "metallic": 0.0,
            "specular": 0.2,
            "type": MaterialType.PBR,
            "textures": ["cloth_weave", "normal"]
        },
        "leather": {
            "base_color": (0.3, 0.2, 0.15),
            "roughness": 0.6,
            "metallic": 0.0,
            "specular": 0.4,
            "type": MaterialType.PBR,
            "textures": ["leather_grain", "bump"]
        },

        # Glass
        "glass": {
            "base_color": (1.0, 1.0, 1.0),
            "roughness": 0.0,
            "metallic": 0.0,
            "specular": 0.5,
            "transmission": 0.95,
            "type": MaterialType.GLASS
        },

        # Plastics
        "plastic": {
            "base_color": (0.8, 0.2, 0.2),
            "roughness": 0.4,
            "metallic": 0.0,
            "specular": 0.5,
            "type": MaterialType.PBR
        },

        # Stone
        "stone": {
            "base_color": (0.5, 0.5, 0.5),
            "roughness": 0.9,
            "metallic": 0.0,
            "specular": 0.2,
            "type": MaterialType.PBR,
            "textures": ["stone_texture", "bump", "normal"]
        },
        "marble": {
            "base_color": (0.95, 0.95, 0.95),
            "roughness": 0.2,
            "metallic": 0.0,
            "specular": 0.5,
            "type": MaterialType.PBR,
            "textures": ["marble_veins", "bump"]
        },

        # Organic
        "skin": {
            "base_color": (0.95, 0.8, 0.7),
            "roughness": 0.4,
            "metallic": 0.0,
            "specular": 0.4,
            "type": MaterialType.PBR,
            "textures": ["skin_pores", "normal", "subsurface"]
        },
        "bark": {
            "base_color": (0.3, 0.2, 0.1),
            "roughness": 0.95,
            "metallic": 0.0,
            "specular": 0.1,
            "type": MaterialType.PROCEDURAL,
            "textures": ["bark_texture", "bump", "displacement"]
        },
        "leaves": {
            "base_color": (0.2, 0.6, 0.2),
            "roughness": 0.8,
            "metallic": 0.0,
            "specular": 0.3,
            "type": MaterialType.PBR,
            "textures": ["leaf_veins", "alpha"]
        },

        # Emissive
        "emission": {
            "base_color": (1.0, 1.0, 1.0),
            "roughness": 0.0,
            "metallic": 0.0,
            "specular": 0.0,
            "emission_strength": 5.0,
            "type": MaterialType.EMISSION
        },
    }

    # Object type to material mapping
    OBJECT_TO_MATERIAL = {
        "chair": ["wood", "metal", "fabric"],
        "table": ["wood", "glass", "metal"],
        "car": ["metal", "glass", "plastic", "rubber"],
        "tree": ["bark", "leaves"],
        "human": ["skin", "fabric"],
        "building": ["concrete", "glass", "metal"],
        "floor": ["wood", "tile", "carpet"],
        "wall": ["paint", "wallpaper", "concrete"],
        "cup": ["ceramic", "glass", "metal"],
        "window": ["glass"],
        "lamp": ["metal", "glass", "emission"],
        "bird": ["feathers", "glass", "metal"],  # Can be real or decorative
        "fabric": ["fabric", "cloth"],
    }

    def __init__(self):
        """Initialize texture mapper."""
        logger.info("TextureMapper initialized")

    def suggest_materials(
        self,
        concept: str,
        references: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Suggest materials based on concept and external references.

        Args:
            concept: Scene concept description
            references: External references from ReferenceSearcher

        Returns:
            Dictionary of material suggestions
        """
        logger.info("Generating material suggestions...")

        # Extract objects from concept
        objects = self._extract_objects(concept)

        # Generate suggestions for each object
        suggestions = []
        for obj_name in objects:
            obj_suggestions = self._suggest_for_object(obj_name, concept, references)
            suggestions.extend(obj_suggestions)

        # Extract material hints from references
        reference_materials = self._extract_reference_materials(references)

        result = {
            "suggestions_count": len(suggestions),
            "materials": [self._suggestion_to_dict(s) for s in suggestions],
            "reference_materials": reference_materials,
            "procedural_textures": self._list_procedural_textures(),
            "shader_recommendations": self._generate_shader_recommendations(suggestions)
        }

        logger.info(f"Generated {len(suggestions)} material suggestions")

        return result

    def _extract_objects(self, concept: str) -> List[str]:
        """Extract object names from concept."""
        concept_lower = concept.lower()
        found = []

        for obj_type in self.OBJECT_TO_MATERIAL.keys():
            if obj_type in concept_lower and obj_type not in found:
                found.append(obj_type)

        # Also check for material keywords
        for material in self.MATERIAL_PRESETS.keys():
            if material in concept_lower and material not in found:
                found.append(material)

        return found

    def _suggest_for_object(
        self,
        obj_name: str,
        concept: str,
        references: List[Dict[str, Any]]
    ) -> List[MaterialSuggestion]:
        """Generate material suggestions for a specific object."""
        suggestions = []

        # Get possible materials for this object
        possible_materials = self.OBJECT_TO_MATERIAL.get(obj_name, ["generic"])

        # Check references for material hints
        ref_hints = []
        for ref in references:
            if ref.get("object_type") == obj_name:
                ref_hints.extend(ref.get("material_hints", []))

        # Combine with possible materials
        all_materials = list(set(possible_materials + ref_hints))

        for mat_name in all_materials[:3]:  # Top 3 materials
            preset = self.MATERIAL_PRESETS.get(mat_name, self.MATERIAL_PRESETS.get("plastic"))

            # Adjust color based on concept
            base_color = self._adjust_color_from_concept(preset["base_color"], concept, obj_name)

            suggestion = MaterialSuggestion(
                object_type=obj_name,
                material_name=mat_name,
                material_type=preset["type"],
                base_color=base_color,
                roughness=preset["roughness"],
                metallic=preset["metallic"],
                specular=preset["specular"],
                transmission=preset.get("transmission", 0.0),
                emission_strength=preset.get("emission_strength", 0.0),
                texture_hints=preset.get("textures", []),
                shader_nodes=self._generate_shader_nodes(preset),
                quality_score=0.9 if mat_name in ref_hints else 0.7
            )

            suggestions.append(suggestion)

        return suggestions

    def _adjust_color_from_concept(
        self,
        base_color: tuple,
        concept: str,
        obj_name: str
    ) -> tuple:
        """Adjust base color based on concept description."""
        concept_lower = concept.lower()

        # Color keywords
        color_map = {
            "red": (0.8, 0.1, 0.1),
            "blue": (0.1, 0.3, 0.8),
            "green": (0.2, 0.8, 0.2),
            "yellow": (0.9, 0.9, 0.1),
            "orange": (1.0, 0.6, 0.0),
            "purple": (0.7, 0.2, 0.8),
            "pink": (1.0, 0.7, 0.8),
            "white": (0.95, 0.95, 0.95),
            "black": (0.05, 0.05, 0.05),
            "gray": (0.5, 0.5, 0.5),
            "brown": (0.4, 0.25, 0.15),
            "amber": (1.0, 0.75, 0.0),
            "sage": (0.6, 0.7, 0.5),
            "pastel": (0.9, 0.8, 0.85),
        }

        # Check if color is mentioned near object name
        for color_name, color_value in color_map.items():
            if color_name in concept_lower:
                # If color is mentioned in proximity to object
                return color_value

        return base_color

    def _generate_shader_nodes(self, preset: Dict[str, Any]) -> List[str]:
        """Generate list of shader nodes needed."""
        nodes = ["Principled BSDF"]

        if preset["type"] == MaterialType.GLASS:
            nodes.append("Glass BSDF")
        elif preset["type"] == MaterialType.EMISSION:
            nodes.append("Emission Shader")

        if preset.get("textures"):
            for texture in preset["textures"]:
                if "bump" in texture or "normal" in texture:
                    nodes.append("Bump Node")
                    nodes.append("Normal Map")
                elif "displacement" in texture:
                    nodes.append("Displacement Node")
                else:
                    nodes.append("Image Texture")

        nodes.append("Mix Shader")

        return list(set(nodes))

    def _extract_reference_materials(self, references: List[Dict[str, Any]]) -> List[str]:
        """Extract unique material hints from references."""
        materials = []

        for ref in references:
            hints = ref.get("material_hints", [])
            for hint in hints:
                if hint not in materials:
                    materials.append(hint)

        return materials

    def _list_procedural_textures(self) -> List[str]:
        """List common procedural textures in Blender."""
        return [
            "Noise Texture",
            "Voronoi Texture",
            "Wave Texture",
            "Musgrave Texture",
            "Magic Texture",
            "Gradient Texture",
            "Checker Texture",
            "Brick Texture",
        ]

    def _generate_shader_recommendations(
        self,
        suggestions: List[MaterialSuggestion]
    ) -> List[str]:
        """Generate shader setup recommendations."""
        recommendations = []

        # Count material types
        type_counts = {}
        for suggestion in suggestions:
            mat_type = suggestion.material_type.value
            type_counts[mat_type] = type_counts.get(mat_type, 0) + 1

        if type_counts.get("glass", 0) > 0:
            recommendations.append("Enable Bloom in Eevee or use Cycles for realistic glass rendering")
            recommendations.append("Set IOR to 1.45 for glass materials")

        if type_counts.get("metal", 0) > 0:
            recommendations.append("Use HDRI environment for realistic metal reflections")

        if type_counts.get("emission", 0) > 0:
            recommendations.append("Consider adding Bloom for glowing effects")

        recommendations.append("Use Principled BSDF for all PBR materials")
        recommendations.append("Connect Normal maps to Normal input for surface detail")

        return recommendations

    def _suggestion_to_dict(self, suggestion: MaterialSuggestion) -> Dict[str, Any]:
        """Convert MaterialSuggestion to dictionary."""
        return {
            "object_type": suggestion.object_type,
            "material_name": suggestion.material_name,
            "material_type": suggestion.material_type.value,
            "base_color": suggestion.base_color,
            "roughness": suggestion.roughness,
            "metallic": suggestion.metallic,
            "specular": suggestion.specular,
            "transmission": suggestion.transmission,
            "emission_strength": suggestion.emission_strength,
            "normal_strength": suggestion.normal_strength,
            "texture_hints": suggestion.texture_hints,
            "shader_nodes": suggestion.shader_nodes,
            "quality_score": suggestion.quality_score
        }

    def get_material_for_object(self, object_type: str) -> Optional[MaterialSuggestion]:
        """Get the best material suggestion for an object type."""
        possible = self.OBJECT_TO_MATERIAL.get(object_type.lower())
        if not possible:
            return None

        # Return first material as default
        mat_name = possible[0]
        preset = self.MATERIAL_PRESETS.get(mat_name)

        if not preset:
            return None

        return MaterialSuggestion(
            object_type=object_type,
            material_name=mat_name,
            material_type=preset["type"],
            base_color=preset["base_color"],
            roughness=preset["roughness"],
            metallic=preset["metallic"],
            specular=preset["specular"],
            transmission=preset.get("transmission", 0.0),
            emission_strength=preset.get("emission_strength", 0.0),
            texture_hints=preset.get("textures", []),
            shader_nodes=self._generate_shader_nodes(preset)
        )
