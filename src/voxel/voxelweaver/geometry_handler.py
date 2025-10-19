"""
Geometry Handler - Provides intelligent geometry generation guidance.
Uses voxel-based analysis and procedural techniques for coherent 3D modeling.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class GeometryType(str, Enum):
    """Types of geometry generation approaches."""
    PRIMITIVE = "primitive"  # Basic shapes (cube, sphere, etc.)
    PROCEDURAL = "procedural"  # Generated algorithmically
    SCULPTED = "sculpted"  # Organic, subdivision-based
    PARAMETRIC = "parametric"  # Geometry nodes / modifiers
    IMPORTED = "imported"  # From external source
    HYBRID = "hybrid"  # Combination of approaches


class ComplexityLevel(str, Enum):
    """Geometry complexity levels."""
    SIMPLE = "simple"  # < 1K vertices
    MODERATE = "moderate"  # 1K - 10K vertices
    DETAILED = "detailed"  # 10K - 100K vertices
    HIGHLY_DETAILED = "highly_detailed"  # > 100K vertices


@dataclass
class GeometryHint:
    """Guidance for generating a specific piece of geometry."""
    object_name: str
    geometry_type: GeometryType
    complexity: ComplexityLevel
    base_primitive: Optional[str] = None  # cube, sphere, cylinder, etc.
    modifiers: List[str] = None  # subdivision, bevel, array, etc.
    subdivision_level: int = 0
    vertex_count_estimate: int = 0
    technique_notes: str = ""
    blender_code_hints: List[str] = None

    def __post_init__(self):
        if self.modifiers is None:
            self.modifiers = []
        if self.blender_code_hints is None:
            self.blender_code_hints = []


class GeometryHandler:
    """
    Provides intelligent geometry generation guidance based on object type,
    voxel resolution, and procedural techniques.
    """

    # Object type to base primitive mapping
    PRIMITIVE_MAPPING = {
        "cube": "cube",
        "box": "cube",
        "sphere": "uv_sphere",
        "ball": "uv_sphere",
        "cylinder": "cylinder",
        "tube": "cylinder",
        "cone": "cone",
        "torus": "torus",
        "ring": "torus",
        "plane": "plane",
        "floor": "plane",
        "ground": "plane",
    }

    # Object categories to geometry approach
    GEOMETRY_APPROACHES = {
        # Organic objects - use subdivision/sculpting
        "organic": {
            "objects": ["human", "animal", "tree", "plant", "creature", "character"],
            "type": GeometryType.SCULPTED,
            "complexity": ComplexityLevel.DETAILED,
            "modifiers": ["subdivision_surface", "smooth"],
        },

        # Mechanical - use parametric/boolean
        "mechanical": {
            "objects": ["car", "robot", "machine", "engine", "gear", "vehicle"],
            "type": GeometryType.PARAMETRIC,
            "complexity": ComplexityLevel.MODERATE,
            "modifiers": ["bevel", "array", "mirror", "boolean"],
        },

        # Architecture - use arrays/modifiers
        "architectural": {
            "objects": ["building", "house", "wall", "door", "window", "room"],
            "type": GeometryType.PARAMETRIC,
            "complexity": ComplexityLevel.MODERATE,
            "modifiers": ["array", "solidify", "bevel"],
        },

        # Simple objects - primitives
        "simple": {
            "objects": ["cube", "sphere", "cylinder", "cone", "plane"],
            "type": GeometryType.PRIMITIVE,
            "complexity": ComplexityLevel.SIMPLE,
            "modifiers": [],
        },

        # Furniture - hybrid approach
        "furniture": {
            "objects": ["chair", "table", "desk", "sofa", "bed", "shelf"],
            "type": GeometryType.HYBRID,
            "complexity": ComplexityLevel.MODERATE,
            "modifiers": ["bevel", "subdivision_surface"],
        },

        # Nature - procedural
        "nature": {
            "objects": ["terrain", "mountain", "rock", "water", "cloud"],
            "type": GeometryType.PROCEDURAL,
            "complexity": ComplexityLevel.DETAILED,
            "modifiers": ["displacement", "subdivision_surface"],
        },
    }

    # Vertex count estimates
    VERTEX_ESTIMATES = {
        ComplexityLevel.SIMPLE: 100,
        ComplexityLevel.MODERATE: 5000,
        ComplexityLevel.DETAILED: 50000,
        ComplexityLevel.HIGHLY_DETAILED: 200000,
    }

    def __init__(self, voxel_resolution: float = 0.1, use_procedural: bool = True):
        """
        Initialize geometry handler.

        Args:
            voxel_resolution: Size of voxels in meters (smaller = more detail)
            use_procedural: Whether to use procedural generation
        """
        self.voxel_resolution = voxel_resolution
        self.use_procedural = use_procedural
        logger.info(f"GeometryHandler initialized (voxel_res={voxel_resolution}m, procedural={use_procedural})")

    def analyze_requirements(
        self,
        concept: str,
        proportions: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze concept and generate geometry hints.

        Args:
            concept: Scene concept description
            proportions: Proportion analysis results

        Returns:
            Dictionary of geometry hints and recommendations
        """
        logger.info("Analyzing geometry requirements...")

        # Extract objects from concept
        objects = self._extract_objects(concept)

        # Generate hints for each object
        hints = []
        for obj_name in objects:
            hint = self._generate_hint(obj_name, concept, proportions)
            hints.append(hint)

        # Calculate total complexity
        total_vertices = sum(h.vertex_count_estimate for h in hints)
        complexity_rating = self._rate_scene_complexity(total_vertices)

        result = {
            "voxel_resolution": self.voxel_resolution,
            "objects_count": len(objects),
            "geometry_hints": [self._hint_to_dict(h) for h in hints],
            "total_vertex_estimate": total_vertices,
            "scene_complexity": complexity_rating,
            "procedural_enabled": self.use_procedural,
            "recommendations": self._generate_recommendations(hints, total_vertices)
        }

        logger.info(f"Geometry analysis complete. {len(hints)} objects, ~{total_vertices:,} vertices")

        return result

    def _extract_objects(self, concept: str) -> List[str]:
        """Extract object names from concept."""
        concept_lower = concept.lower()
        found = []

        # Check all known objects
        for category_data in self.GEOMETRY_APPROACHES.values():
            for obj in category_data["objects"]:
                if obj in concept_lower and obj not in found:
                    found.append(obj)

        # Check primitives
        for obj in self.PRIMITIVE_MAPPING.keys():
            if obj in concept_lower and obj not in found:
                found.append(obj)

        # If nothing found, look for common nouns
        if not found:
            import re
            words = re.findall(r'\b[a-z]{3,}\b', concept_lower)
            found = [w for w in words[:10] if w not in ['the', 'and', 'with']]

        return found

    def _generate_hint(
        self,
        obj_name: str,
        concept: str,
        proportions: Dict[str, Any]
    ) -> GeometryHint:
        """Generate geometry hint for a specific object."""

        # Determine category
        category = self._categorize_object(obj_name)

        # Get approach for this category
        approach = self.GEOMETRY_APPROACHES.get(category, self.GEOMETRY_APPROACHES["simple"])

        # Determine base primitive
        base_primitive = self.PRIMITIVE_MAPPING.get(obj_name)
        if not base_primitive:
            # Default based on category
            if category == "organic":
                base_primitive = "uv_sphere"
            elif category == "architectural":
                base_primitive = "cube"
            else:
                base_primitive = "cube"

        # Determine subdivision level based on complexity
        complexity = approach["complexity"]
        if complexity == ComplexityLevel.SIMPLE:
            subdiv_level = 0
        elif complexity == ComplexityLevel.MODERATE:
            subdiv_level = 1
        elif complexity == ComplexityLevel.DETAILED:
            subdiv_level = 2
        else:
            subdiv_level = 3

        # Estimate vertices
        base_verts = self._get_base_primitive_vertices(base_primitive)
        vertex_estimate = base_verts * (4 ** subdiv_level) if subdiv_level > 0 else base_verts

        # Generate technique notes
        notes = self._generate_technique_notes(obj_name, approach, base_primitive)

        # Generate Blender code hints
        code_hints = self._generate_code_hints(obj_name, base_primitive, approach["modifiers"])

        return GeometryHint(
            object_name=obj_name,
            geometry_type=approach["type"],
            complexity=complexity,
            base_primitive=base_primitive,
            modifiers=approach["modifiers"],
            subdivision_level=subdiv_level,
            vertex_count_estimate=vertex_estimate,
            technique_notes=notes,
            blender_code_hints=code_hints
        )

    def _categorize_object(self, obj_name: str) -> str:
        """Categorize an object into a geometry approach category."""
        for category, data in self.GEOMETRY_APPROACHES.items():
            if obj_name in data["objects"]:
                return category

        # Default categorization based on name
        if any(word in obj_name for word in ["tree", "plant", "animal", "character"]):
            return "organic"
        elif any(word in obj_name for word in ["machine", "robot", "car"]):
            return "mechanical"
        elif any(word in obj_name for word in ["building", "wall", "door"]):
            return "architectural"
        else:
            return "simple"

    def _get_base_primitive_vertices(self, primitive: str) -> int:
        """Get vertex count for base primitives."""
        counts = {
            "cube": 8,
            "uv_sphere": 482,  # Default 32x16 segments
            "ico_sphere": 42,  # Default 2 subdivisions
            "cylinder": 64,  # Default 32 vertices
            "cone": 33,
            "torus": 576,  # Default 48x12
            "plane": 4,
        }
        return counts.get(primitive, 100)

    def _generate_technique_notes(
        self,
        obj_name: str,
        approach: Dict[str, Any],
        primitive: str
    ) -> str:
        """Generate human-readable technique notes."""
        notes = f"Start with {primitive} primitive. "

        if approach["type"] == GeometryType.SCULPTED:
            notes += "Apply subdivision surface modifier and use smooth shading for organic form. "
        elif approach["type"] == GeometryType.PARAMETRIC:
            notes += "Use modifiers for parametric control. "
        elif approach["type"] == GeometryType.PROCEDURAL:
            notes += "Consider geometry nodes or displacement for procedural detail. "

        if approach["modifiers"]:
            notes += f"Recommended modifiers: {', '.join(approach['modifiers'])}. "

        return notes

    def _generate_code_hints(
        self,
        obj_name: str,
        primitive: str,
        modifiers: List[str]
    ) -> List[str]:
        """Generate Blender Python code hints."""
        hints = []

        # Primitive creation
        primitive_ops = {
            "cube": "bpy.ops.mesh.primitive_cube_add(size=2)",
            "uv_sphere": "bpy.ops.mesh.primitive_uv_sphere_add(radius=1, segments=32, ring_count=16)",
            "ico_sphere": "bpy.ops.mesh.primitive_ico_sphere_add(radius=1, subdivisions=2)",
            "cylinder": "bpy.ops.mesh.primitive_cylinder_add(radius=1, depth=2, vertices=32)",
            "cone": "bpy.ops.mesh.primitive_cone_add(radius1=1, depth=2, vertices=32)",
            "torus": "bpy.ops.mesh.primitive_torus_add(major_radius=1, minor_radius=0.25)",
            "plane": "bpy.ops.mesh.primitive_plane_add(size=2)",
        }

        if primitive in primitive_ops:
            hints.append(primitive_ops[primitive])

        # Modifier hints
        for mod in modifiers:
            if mod == "subdivision_surface":
                hints.append("obj.modifiers.new('Subsurf', 'SUBSURF'); obj.modifiers['Subsurf'].levels = 2")
            elif mod == "bevel":
                hints.append("obj.modifiers.new('Bevel', 'BEVEL'); obj.modifiers['Bevel'].width = 0.05")
            elif mod == "array":
                hints.append("obj.modifiers.new('Array', 'ARRAY'); obj.modifiers['Array'].count = 3")
            elif mod == "mirror":
                hints.append("obj.modifiers.new('Mirror', 'MIRROR'); obj.modifiers['Mirror'].use_axis[0] = True")

        return hints

    def _rate_scene_complexity(self, total_vertices: int) -> str:
        """Rate overall scene complexity."""
        if total_vertices < 10000:
            return "low"
        elif total_vertices < 100000:
            return "medium"
        elif total_vertices < 500000:
            return "high"
        else:
            return "very_high"

    def _generate_recommendations(self, hints: List[GeometryHint], total_verts: int) -> List[str]:
        """Generate recommendations based on analysis."""
        recommendations = []

        # Complexity warnings
        if total_verts > 1000000:
            recommendations.append(
                "Scene is very complex (>1M vertices). Consider using level-of-detail or instancing."
            )

        # Modifier suggestions
        modifier_counts = {}
        for hint in hints:
            for mod in hint.modifiers:
                modifier_counts[mod] = modifier_counts.get(mod, 0) + 1

        if modifier_counts.get("subdivision_surface", 0) > 5:
            recommendations.append(
                "Many subdivision modifiers detected. Ensure viewport subdivision is set lower than render."
            )

        # Voxel resolution suggestions
        if self.voxel_resolution < 0.01:
            recommendations.append(
                f"Very fine voxel resolution ({self.voxel_resolution}m). This will create extremely detailed geometry."
            )
        elif self.voxel_resolution > 0.5:
            recommendations.append(
                f"Coarse voxel resolution ({self.voxel_resolution}m). Consider lowering for more detail."
            )

        # Geometry type distribution
        type_counts = {}
        for hint in hints:
            type_counts[hint.geometry_type] = type_counts.get(hint.geometry_type, 0) + 1

        if type_counts.get(GeometryType.PROCEDURAL, 0) > 0 and not self.use_procedural:
            recommendations.append("Procedural geometry detected but procedural generation is disabled.")

        return recommendations

    def _hint_to_dict(self, hint: GeometryHint) -> Dict[str, Any]:
        """Convert GeometryHint to dictionary."""
        return {
            "object_name": hint.object_name,
            "geometry_type": hint.geometry_type.value,
            "complexity": hint.complexity.value,
            "base_primitive": hint.base_primitive,
            "modifiers": hint.modifiers,
            "subdivision_level": hint.subdivision_level,
            "vertex_count_estimate": hint.vertex_count_estimate,
            "technique_notes": hint.technique_notes,
            "blender_code_hints": hint.blender_code_hints
        }

    def get_voxel_grid_size(self, object_dimensions: Dict[str, float]) -> Tuple[int, int, int]:
        """
        Calculate voxel grid dimensions for an object.

        Args:
            object_dimensions: Dict with 'width', 'height', 'depth' in meters

        Returns:
            (x_voxels, y_voxels, z_voxels)
        """
        width = object_dimensions.get("width", 1.0)
        height = object_dimensions.get("height", 1.0)
        depth = object_dimensions.get("depth", 1.0)

        x_voxels = max(1, int(width / self.voxel_resolution))
        y_voxels = max(1, int(depth / self.voxel_resolution))
        z_voxels = max(1, int(height / self.voxel_resolution))

        return (x_voxels, y_voxels, z_voxels)
