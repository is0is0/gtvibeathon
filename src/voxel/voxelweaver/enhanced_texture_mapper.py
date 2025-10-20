"""
Enhanced Texture Mapper - Advanced texture mapping with intricate material generation.
Integrates with AdvancedTextureCatalog for comprehensive material creation.
"""

import logging
import random
import math
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass
from enum import Enum

from .advanced_texture_catalog import (
    AdvancedTextureCatalog, MaterialPreset, MaterialCategory,
    TextureType, TextureMap
)

logger = logging.getLogger(__name__)


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


class MaterialComplexity(str, Enum):
    """Material complexity levels."""
    SIMPLE = "simple"  # Basic materials with minimal maps
    MODERATE = "moderate"  # Standard materials with common maps
    ADVANCED = "advanced"  # Complex materials with multiple maps
    PRODUCTION = "production"  # Film-quality materials with all maps


@dataclass
class MaterialSuggestion:
    """Enhanced material suggestion with detailed mapping."""
    object_type: str
    material_name: str
    category: MaterialCategory
    preset: MaterialPreset
    environment_adaptation: float
    complexity_level: MaterialComplexity
    required_maps: List[TextureType]
    optional_maps: List[TextureType]
    shader_setup: List[str]
    quality_score: float
    cost_estimate: float  # Rendering cost estimate
    generation_time: float  # Estimated generation time in seconds
    custom_parameters: Dict[str, Any] = None

    def __post_init__(self):
        if self.custom_parameters is None:
            self.custom_parameters = {}


class EnhancedTextureMapper:
    """
    Enhanced texture mapper with advanced material generation capabilities.
    Provides intricate texture mapping with comprehensive material catalogs.
    """

    def __init__(self):
        """Initialize enhanced texture mapper."""
        self.catalog = AdvancedTextureCatalog()
        self.environment_weights = self._initialize_environment_weights()
        self.object_material_mapping = self._initialize_object_mapping()
        logger.info("EnhancedTextureMapper initialized")

    def _initialize_environment_weights(self) -> Dict[EnvironmentType, Dict[MaterialCategory, float]]:
        """Initialize environment-specific material weights."""
        return {
            EnvironmentType.INDOOR: {
                MaterialCategory.ORGANIC: 1.0,
                MaterialCategory.METALLIC: 0.8,
                MaterialCategory.MINERAL: 0.9,
                MaterialCategory.FABRIC: 1.2,
                MaterialCategory.PLASTIC: 1.0,
                MaterialCategory.EMISSIVE: 0.6,
                MaterialCategory.TRANSPARENT: 0.8
            },
            EnvironmentType.OUTDOOR: {
                MaterialCategory.ORGANIC: 1.2,
                MaterialCategory.METALLIC: 1.0,
                MaterialCategory.MINERAL: 1.3,
                MaterialCategory.FABRIC: 0.7,
                MaterialCategory.PLASTIC: 0.8,
                MaterialCategory.EMISSIVE: 0.4,
                MaterialCategory.TRANSPARENT: 0.6
            },
            EnvironmentType.STUDIO: {
                MaterialCategory.ORGANIC: 0.9,
                MaterialCategory.METALLIC: 1.1,
                MaterialCategory.MINERAL: 1.0,
                MaterialCategory.FABRIC: 1.0,
                MaterialCategory.PLASTIC: 1.1,
                MaterialCategory.EMISSIVE: 0.8,
                MaterialCategory.TRANSPARENT: 1.2
            },
            EnvironmentType.NIGHT: {
                MaterialCategory.ORGANIC: 0.6,
                MaterialCategory.METALLIC: 0.8,
                MaterialCategory.MINERAL: 0.7,
                MaterialCategory.FABRIC: 0.5,
                MaterialCategory.PLASTIC: 0.7,
                MaterialCategory.EMISSIVE: 1.5,
                MaterialCategory.TRANSPARENT: 0.9
            }
        }

    def _initialize_object_mapping(self) -> Dict[str, List[MaterialCategory]]:
        """Initialize object type to material category mapping."""
        return {
            "furniture": [MaterialCategory.ORGANIC, MaterialCategory.METALLIC, MaterialCategory.FABRIC],
            "building": [MaterialCategory.MINERAL, MaterialCategory.METALLIC, MaterialCategory.PLASTIC],
            "vehicle": [MaterialCategory.METALLIC, MaterialCategory.PLASTIC, MaterialCategory.SYNTHETIC],
            "clothing": [MaterialCategory.FABRIC, MaterialCategory.ORGANIC, MaterialCategory.SYNTHETIC],
            "electronics": [MaterialCategory.METALLIC, MaterialCategory.PLASTIC, MaterialCategory.EMISSIVE],
            "nature": [MaterialCategory.ORGANIC, MaterialCategory.NATURAL, MaterialCategory.MINERAL],
            "decoration": [MaterialCategory.ORGANIC, MaterialCategory.MINERAL, MaterialCategory.EMISSIVE],
            "weapon": [MaterialCategory.METALLIC, MaterialCategory.ORGANIC, MaterialCategory.SYNTHETIC],
            "container": [MaterialCategory.MINERAL, MaterialCategory.METALLIC, MaterialCategory.PLASTIC],
            "lighting": [MaterialCategory.EMISSIVE, MaterialCategory.METALLIC, MaterialCategory.TRANSPARENT]
        }

    def suggest_materials_advanced(
        self,
        concept: str,
        environment: EnvironmentType = EnvironmentType.INDOOR,
        complexity: MaterialComplexity = MaterialComplexity.MODERATE,
        object_types: List[str] = None
    ) -> List[MaterialSuggestion]:
        """
        Suggest advanced materials with intricate mapping.

        Args:
            concept: Scene concept description
            environment: Target environment
            complexity: Material complexity level
            object_types: Specific object types to focus on

        Returns:
            List of detailed material suggestions
        """
        logger.info(f"Generating advanced material suggestions for {environment.value} environment")

        suggestions = []
        
        # Extract object types from concept if not provided
        if not object_types:
            object_types = self._extract_object_types(concept)
        
        # Get environment weights
        env_weights = self.environment_weights.get(environment, {})
        
        for obj_type in object_types:
            # Get relevant material categories for this object type
            categories = self.object_material_mapping.get(obj_type, [MaterialCategory.ORGANIC])
            
            for category in categories:
                # Get environment weight for this category
                weight = env_weights.get(category, 1.0)
                
                # Get materials in this category
                materials = self.catalog.get_materials_by_category(category)
                
                # Filter by complexity if specified
                if complexity != MaterialComplexity.SIMPLE:
                    materials = [m for m in materials if self._matches_complexity(m, complexity)]
                
                # Score and rank materials
                for material in materials:
                    score = self._calculate_material_score(material, obj_type, environment, concept)
                    score *= weight  # Apply environment weight
                    
                    if score > 0.5:  # Only include materials with decent scores
                        suggestion = self._create_material_suggestion(
                            obj_type, material, environment, complexity, score
                        )
                        suggestions.append(suggestion)
        
        # Sort by quality score and return top suggestions
        suggestions.sort(key=lambda x: x.quality_score, reverse=True)
        return suggestions[:10]  # Return top 10 suggestions

    def _extract_object_types(self, concept: str) -> List[str]:
        """Extract object types from concept description."""
        concept_lower = concept.lower()
        object_types = []
        
        # Simple keyword matching (in production, this would use NLP)
        if any(word in concept_lower for word in ["chair", "table", "sofa", "desk", "bed"]):
            object_types.append("furniture")
        if any(word in concept_lower for word in ["building", "house", "wall", "roof"]):
            object_types.append("building")
        if any(word in concept_lower for word in ["car", "truck", "vehicle", "bike"]):
            object_types.append("vehicle")
        if any(word in concept_lower for word in ["clothing", "shirt", "pants", "dress"]):
            object_types.append("clothing")
        if any(word in concept_lower for word in ["computer", "phone", "screen", "device"]):
            object_types.append("electronics")
        if any(word in concept_lower for word in ["tree", "grass", "plant", "flower"]):
            object_types.append("nature")
        if any(word in concept_lower for word in ["lamp", "light", "bulb", "neon"]):
            object_types.append("lighting")
        
        return object_types if object_types else ["furniture"]  # Default fallback

    def _matches_complexity(self, material: MaterialPreset, complexity: MaterialComplexity) -> bool:
        """Check if material matches complexity level."""
        complexity_thresholds = {
            MaterialComplexity.SIMPLE: 0.3,
            MaterialComplexity.MODERATE: 0.5,
            MaterialComplexity.ADVANCED: 0.7,
            MaterialComplexity.PRODUCTION: 0.8
        }
        
        threshold = complexity_thresholds.get(complexity, 0.5)
        return material.complexity_score >= threshold

    def _calculate_material_score(
        self,
        material: MaterialPreset,
        object_type: str,
        environment: EnvironmentType,
        concept: str
    ) -> float:
        """Calculate material relevance score."""
        score = 0.0
        
        # Base score from material quality
        score += material.complexity_score * 0.3
        
        # Environment adaptation score
        env_adaptation = material.environment_adaptation.get(environment.value, 0.5)
        score += env_adaptation * 0.4
        
        # Object type relevance (simplified)
        if object_type in ["furniture", "building"] and material.category in [MaterialCategory.ORGANIC, MaterialCategory.MINERAL]:
            score += 0.3
        elif object_type in ["vehicle", "electronics"] and material.category in [MaterialCategory.METALLIC, MaterialCategory.PLASTIC]:
            score += 0.3
        elif object_type in ["lighting"] and material.category == MaterialCategory.EMISSIVE:
            score += 0.5
        
        # Concept relevance (simplified keyword matching)
        concept_lower = concept.lower()
        if material.category == MaterialCategory.ORGANIC and any(word in concept_lower for word in ["wood", "natural", "organic"]):
            score += 0.2
        elif material.category == MaterialCategory.METALLIC and any(word in concept_lower for word in ["metal", "steel", "chrome"]):
            score += 0.2
        elif material.category == MaterialCategory.EMISSIVE and any(word in concept_lower for word in ["neon", "glow", "light", "bright"]):
            score += 0.3
        
        return min(1.0, score)

    def _create_material_suggestion(
        self,
        object_type: str,
        material: MaterialPreset,
        environment: EnvironmentType,
        complexity: MaterialComplexity,
        score: float
    ) -> MaterialSuggestion:
        """Create a material suggestion from a preset."""
        
        # Determine required and optional maps based on complexity
        required_maps, optional_maps = self._get_map_requirements(material, complexity)
        
        # Calculate cost and time estimates
        cost_estimate = self._calculate_rendering_cost(material, complexity)
        generation_time = self._calculate_generation_time(material, complexity)
        
        return MaterialSuggestion(
            object_type=object_type,
            material_name=material.name,
            category=material.category,
            preset=material,
            environment_adaptation=material.environment_adaptation.get(environment.value, 0.5),
            complexity_level=complexity,
            required_maps=required_maps,
            optional_maps=optional_maps,
            shader_setup=material.shader_nodes,
            quality_score=score,
            cost_estimate=cost_estimate,
            generation_time=generation_time,
            custom_parameters=self._get_custom_parameters(material, environment)
        )

    def _get_map_requirements(
        self,
        material: MaterialPreset,
        complexity: MaterialComplexity
    ) -> Tuple[List[TextureType], List[TextureType]]:
        """Get required and optional texture maps based on complexity."""
        
        # Base maps that are always required
        base_required = [TextureType.DIFFUSE]
        
        # Maps required for different complexity levels
        complexity_requirements = {
            MaterialComplexity.SIMPLE: [TextureType.DIFFUSE],
            MaterialComplexity.MODERATE: [TextureType.DIFFUSE, TextureType.NORMAL, TextureType.ROUGHNESS],
            MaterialComplexity.ADVANCED: [TextureType.DIFFUSE, TextureType.NORMAL, TextureType.ROUGHNESS, 
                                        TextureType.METALLIC, TextureType.AO],
            MaterialComplexity.PRODUCTION: [TextureType.DIFFUSE, TextureType.NORMAL, TextureType.ROUGHNESS,
                                          TextureType.METALLIC, TextureType.AO, TextureType.SPECULAR,
                                          TextureType.DISPLACEMENT, TextureType.EMISSION]
        }
        
        required = complexity_requirements.get(complexity, [TextureType.DIFFUSE])
        
        # Add material-specific requirements
        if material.category == MaterialCategory.METALLIC:
            required.append(TextureType.METALLIC)
        if material.category == MaterialCategory.EMISSIVE:
            required.append(TextureType.EMISSION)
        if material.category == MaterialCategory.TRANSPARENT:
            required.append(TextureType.OPACITY)
        
        # Optional maps
        optional = [map_type for map_type in TextureType 
                   if map_type not in required and map_type in material.texture_maps]
        
        return required, optional

    def _calculate_rendering_cost(self, material: MaterialPreset, complexity: MaterialComplexity) -> float:
        """Calculate estimated rendering cost for material."""
        base_cost = 1.0
        
        # Cost multipliers based on complexity
        complexity_multipliers = {
            MaterialComplexity.SIMPLE: 1.0,
            MaterialComplexity.MODERATE: 1.5,
            MaterialComplexity.ADVANCED: 2.0,
            MaterialComplexity.PRODUCTION: 3.0
        }
        
        # Material-specific cost adjustments
        if material.category == MaterialCategory.EMISSIVE:
            base_cost *= 1.5  # Emissive materials are more expensive
        if material.category == MaterialCategory.TRANSPARENT:
            base_cost *= 1.3  # Transparency requires more samples
        if material.complexity_score > 0.8:
            base_cost *= 1.2  # Complex materials are more expensive
        
        return base_cost * complexity_multipliers.get(complexity, 1.0)

    def _calculate_generation_time(self, material: MaterialPreset, complexity: MaterialComplexity) -> float:
        """Calculate estimated generation time for material."""
        base_time = 5.0  # Base 5 seconds
        
        # Time multipliers based on complexity
        complexity_multipliers = {
            MaterialComplexity.SIMPLE: 1.0,
            MaterialComplexity.MODERATE: 1.5,
            MaterialComplexity.ADVANCED: 2.0,
            MaterialComplexity.PRODUCTION: 3.0
        }
        
        # Material-specific time adjustments
        if material.category == MaterialCategory.ORGANIC:
            base_time *= 1.3  # Organic materials take longer to generate
        if material.category == MaterialCategory.EMISSIVE:
            base_time *= 1.2  # Emissive materials require special handling
        if len(material.texture_maps) > 5:
            base_time *= 1.2  # More maps take longer
        
        return base_time * complexity_multipliers.get(complexity, 1.0)

    def _get_custom_parameters(self, material: MaterialPreset, environment: EnvironmentType) -> Dict[str, Any]:
        """Get custom parameters for material adaptation."""
        params = {}
        
        # Environment-specific adjustments
        if environment == EnvironmentType.NIGHT:
            params["emission_boost"] = 1.5
            params["contrast_boost"] = 1.2
        elif environment == EnvironmentType.OUTDOOR:
            params["weathering_factor"] = 0.3
            params["uv_scale"] = 0.8
        elif environment == EnvironmentType.STUDIO:
            params["polish_factor"] = 1.2
            params["reflection_boost"] = 1.1
        
        # Material-specific parameters
        if material.category == MaterialCategory.ORGANIC:
            params["grain_variation"] = 0.2
            params["age_factor"] = 0.5
        elif material.category == MaterialCategory.METALLIC:
            params["scratch_density"] = 0.3
            params["polish_level"] = 0.8
        
        return params

    def generate_material_blend_code(
        self,
        suggestion: MaterialSuggestion,
        object_name: str = "Object"
    ) -> str:
        """Generate Blender Python code for material suggestion."""
        
        material = suggestion.preset
        
        code_lines = [
            "import bpy",
            "import bmesh",
            "from mathutils import Vector",
            "",
            f"# Create material: {material.name}",
            f"# Object: {object_name}",
            f"# Environment: {suggestion.environment_adaptation:.2f} adaptation",
            f"# Complexity: {suggestion.complexity_level.value}",
            "",
            f"mat = bpy.data.materials.new(name='{material.name}')",
            "mat.use_nodes = True",
            "",
            "# Clear default nodes",
            "mat.node_tree.nodes.clear()",
            "",
            "# Add Principled BSDF",
            "bsdf = mat.node_tree.nodes.new('ShaderNodeBsdfPrincipled')",
            "bsdf.location = (0, 0)",
            "",
            "# Add Material Output",
            "output = mat.node_tree.nodes.new('ShaderNodeOutputMaterial')",
            "output.location = (400, 0)",
            "",
            "# Connect BSDF to Output",
            "mat.node_tree.links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])",
            ""
        ]
        
        # Add texture nodes for required maps
        for map_type in suggestion.required_maps:
            if map_type in material.texture_maps:
                texture_map = material.texture_maps[map_type]
                code_lines.extend(self._generate_texture_node_code(map_type, texture_map, material))
        
        # Set material properties
        code_lines.extend([
            "",
            "# Set material properties",
            f"bsdf.inputs['Base Color'].default_value = {material.base_color}",
            f"bsdf.inputs['Roughness'].default_value = {material.roughness}",
            f"bsdf.inputs['Metallic'].default_value = {material.metallic}",
            f"bsdf.inputs['Specular'].default_value = {material.specular}",
            f"bsdf.inputs['Emission Strength'].default_value = {material.emission_strength}",
            f"bsdf.inputs['Transmission Weight'].default_value = {material.transmission}",
            f"bsdf.inputs['IOR'].default_value = {material.ior}",
            f"bsdf.inputs['Subsurface Weight'].default_value = {material.subsurface}",
            f"bsdf.inputs['Anisotropic'].default_value = {material.anisotropy}",
            f"bsdf.inputs['Sheen Weight'].default_value = {material.sheen}",
            f"bsdf.inputs['Clearcoat Weight'].default_value = {material.clearcoat}",
            f"bsdf.inputs['Clearcoat Roughness'].default_value = {material.clearcoat_roughness}",
            ""
        ])
        
        # Add custom parameters
        if suggestion.custom_parameters:
            code_lines.extend([
                "# Custom parameters",
                f"# {suggestion.custom_parameters}",
                ""
            ])
        
        # Add material assignment
        code_lines.extend([
            "# Assign material to object",
            f"if '{object_name}' in bpy.data.objects:",
            f"    obj = bpy.data.objects['{object_name}']",
            "    if obj.data.materials:",
            "        obj.data.materials[0] = mat",
            "    else:",
            "        obj.data.materials.append(mat)",
            "",
            "print(f'✅ Material created: {material.name}')",
            "print(f'   Quality Score: {suggestion.quality_score:.2f}')",
            "print(f'   Cost Estimate: {suggestion.cost_estimate:.2f}')",
            "print(f'   Generation Time: {suggestion.generation_time:.1f}s')"
        ])
        
        return "\n".join(code_lines)

    def _generate_texture_node_code(
        self,
        map_type: TextureType,
        texture_map: TextureMap,
        material: MaterialPreset
    ) -> List[str]:
        """Generate Blender code for a specific texture map."""
        
        code_lines = []
        
        if map_type == TextureType.DIFFUSE:
            code_lines.extend([
                "# Diffuse/Base Color Map",
                "diffuse_tex = mat.node_tree.nodes.new('ShaderNodeTexImage')",
                "diffuse_tex.location = (-400, 200)",
                "diffuse_tex.name = 'Diffuse Texture'",
                "",
                "# Mapping node for UV coordinates",
                "mapping = mat.node_tree.nodes.new('ShaderNodeMapping')",
                "mapping.location = (-600, 200)",
                "mapping.inputs['Scale'].default_value = (4.0, 4.0, 1.0)",
                "",
                "# Texture Coordinate node",
                "tex_coord = mat.node_tree.nodes.new('ShaderNodeTexCoord')",
                "tex_coord.location = (-800, 200)",
                "",
                "# Connect nodes",
                "mat.node_tree.links.new(tex_coord.outputs['UV'], mapping.inputs['Vector'])",
                "mat.node_tree.links.new(mapping.outputs['Vector'], diffuse_tex.inputs['Vector'])",
                "mat.node_tree.links.new(diffuse_tex.outputs['Color'], bsdf.inputs['Base Color'])",
                ""
            ])
        
        elif map_type == TextureType.NORMAL:
            code_lines.extend([
                "# Normal Map",
                "normal_tex = mat.node_tree.nodes.new('ShaderNodeTexImage')",
                "normal_tex.location = (-400, 0)",
                "normal_tex.name = 'Normal Texture'",
                "normal_tex.image.colorspace_settings.name = 'Non-Color'",
                "",
                "# Normal Map node",
                "normal_map = mat.node_tree.nodes.new('ShaderNodeNormalMap')",
                "normal_map.location = (-200, 0)",
                "normal_map.inputs['Strength'].default_value = 1.0",
                "",
                "# Connect nodes",
                "mat.node_tree.links.new(normal_tex.outputs['Color'], normal_map.inputs['Color'])",
                "mat.node_tree.links.new(normal_map.outputs['Normal'], bsdf.inputs['Normal'])",
                ""
            ])
        
        elif map_type == TextureType.ROUGHNESS:
            code_lines.extend([
                "# Roughness Map",
                "roughness_tex = mat.node_tree.nodes.new('ShaderNodeTexImage')",
                "roughness_tex.location = (-400, -200)",
                "roughness_tex.name = 'Roughness Texture'",
                "roughness_tex.image.colorspace_settings.name = 'Non-Color'",
                "",
                "# Connect to Roughness",
                "mat.node_tree.links.new(roughness_tex.outputs['Color'], bsdf.inputs['Roughness'])",
                ""
            ])
        
        elif map_type == TextureType.METALLIC:
            code_lines.extend([
                "# Metallic Map",
                "metallic_tex = mat.node_tree.nodes.new('ShaderNodeTexImage')",
                "metallic_tex.location = (-400, -400)",
                "metallic_tex.name = 'Metallic Texture'",
                "metallic_tex.image.colorspace_settings.name = 'Non-Color'",
                "",
                "# Connect to Metallic",
                "mat.node_tree.links.new(metallic_tex.outputs['Color'], bsdf.inputs['Metallic'])",
                ""
            ])
        
        elif map_type == TextureType.EMISSION:
            code_lines.extend([
                "# Emission Map",
                "emission_tex = mat.node_tree.nodes.new('ShaderNodeTexImage')",
                "emission_tex.location = (-400, 400)",
                "emission_tex.name = 'Emission Texture'",
                "",
                "# Connect to Emission",
                "mat.node_tree.links.new(emission_tex.outputs['Color'], bsdf.inputs['Emission Color'])",
                ""
            ])
        
        return code_lines

    def get_catalog_statistics(self) -> Dict[str, Any]:
        """Get comprehensive catalog statistics."""
        catalog_summary = self.catalog.get_catalog_summary()
        
        # Add enhanced statistics
        enhanced_stats = {
            "catalog_summary": catalog_summary,
            "environment_support": len(EnvironmentType),
            "complexity_levels": len(MaterialComplexity),
            "texture_map_types": len(TextureType),
            "average_complexity": sum(p.complexity_score for p in self.catalog.material_presets.values()) / len(self.catalog.material_presets),
            "production_ready_materials": len([p for p in self.catalog.material_presets.values() if p.quality_level == "production"]),
            "emissive_materials": len([p for p in self.catalog.material_presets.values() if p.category == MaterialCategory.EMISSIVE]),
            "transparent_materials": len([p for p in self.catalog.material_presets.values() if p.category == MaterialCategory.TRANSPARENT])
        }
        
        return enhanced_stats
