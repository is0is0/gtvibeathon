"""
Geometry Handler Module
-----------------------
Generates or imports voxel-based 3D geometries.

This module handles:
- Voxel-based geometry generation from prompts
- Importing and converting external 3D models to voxel meshes
- Procedural geometry generation when no reference is available
- Mesh optimization and cleanup
"""

import logging
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class GeometryType(Enum):
    """Types of geometry that can be generated."""
    PRIMITIVE = "primitive"  # Basic shapes (cube, sphere, cylinder)
    VOXEL = "voxel"  # Voxel-based mesh
    IMPORTED = "imported"  # Imported from file
    PROCEDURAL = "procedural"  # Procedurally generated


@dataclass
class BoundingBox:
    """3D bounding box representation."""
    min_point: Tuple[float, float, float]
    max_point: Tuple[float, float, float]

    @property
    def size(self) -> Tuple[float, float, float]:
        """Get bounding box dimensions."""
        return (
            self.max_point[0] - self.min_point[0],
            self.max_point[1] - self.min_point[1],
            self.max_point[2] - self.min_point[2]
        )

    @property
    def center(self) -> Tuple[float, float, float]:
        """Get bounding box center."""
        return (
            (self.min_point[0] + self.max_point[0]) / 2,
            (self.min_point[1] + self.max_point[1]) / 2,
            (self.min_point[2] + self.max_point[2]) / 2
        )

    @property
    def volume(self) -> float:
        """Get bounding box volume."""
        size = self.size
        return size[0] * size[1] * size[2]


@dataclass
class GeometryObject:
    """Represents a 3D geometry object."""
    name: str
    geometry_type: GeometryType
    vertices: np.ndarray  # Nx3 array of vertex positions
    faces: np.ndarray  # Mx3 or Mx4 array of face indices
    normals: Optional[np.ndarray] = None  # Nx3 array of vertex normals
    uv_coords: Optional[np.ndarray] = None  # Nx2 array of UV coordinates
    metadata: Dict[str, Any] = None
    bounding_box: Optional[BoundingBox] = None

    def __post_init__(self):
        """Calculate bounding box if not provided."""
        if self.metadata is None:
            self.metadata = {}

        if self.bounding_box is None and len(self.vertices) > 0:
            min_point = tuple(self.vertices.min(axis=0))
            max_point = tuple(self.vertices.max(axis=0))
            self.bounding_box = BoundingBox(min_point, max_point)


class GeometryHandler:
    """
    Handles voxel-based 3D geometry generation and import.

    This class is responsible for creating, importing, and converting
    3D geometries into voxel-compatible meshes for Blender.

    Example:
        >>> handler = GeometryHandler(voxel_resolution=0.1)
        >>> objects = handler.generate_from_prompt(
        ...     "A table with four legs",
        ...     references={}
        ... )
        >>> print(f"Generated {len(objects)} objects")
    """

    def __init__(self, voxel_resolution: float = 0.1):
        """
        Initialize the geometry handler.

        Args:
            voxel_resolution: Voxel grid resolution in Blender units (default: 0.1m)
        """
        self.voxel_resolution = voxel_resolution
        self.primitive_library = self._initialize_primitive_library()
        logger.info(f"GeometryHandler initialized with voxel resolution: {voxel_resolution}")

    def _initialize_primitive_library(self) -> Dict[str, Dict[str, Any]]:
        """
        Initialize library of primitive shapes.

        Returns:
            Dictionary of primitive shape definitions
        """
        return {
            "cube": {
                "type": "cube",
                "default_size": (1.0, 1.0, 1.0),
                "vertices_count": 8,
                "faces_count": 6
            },
            "sphere": {
                "type": "sphere",
                "default_radius": 0.5,
                "segments": 32,
                "rings": 16
            },
            "cylinder": {
                "type": "cylinder",
                "default_radius": 0.5,
                "default_height": 1.0,
                "segments": 32
            },
            "plane": {
                "type": "plane",
                "default_size": (2.0, 2.0),
                "subdivisions": 1
            },
            "cone": {
                "type": "cone",
                "default_radius": 0.5,
                "default_height": 1.0,
                "segments": 32
            },
            "torus": {
                "type": "torus",
                "major_radius": 0.75,
                "minor_radius": 0.25,
                "major_segments": 48,
                "minor_segments": 12
            }
        }

    def generate_from_prompt(
        self,
        prompt: str,
        references: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Generate geometry objects from a natural language prompt.

        This is the main entry point for geometry generation. It analyzes
        the prompt and creates appropriate geometry objects.

        Args:
            prompt: Natural language scene description
            references: Reference data from SearchScraper

        Returns:
            List of geometry object dictionaries

        Example:
            >>> handler = GeometryHandler()
            >>> objects = handler.generate_from_prompt(
            ...     "A modern living room with a sofa and coffee table",
            ...     references={}
            ... )
        """
        logger.info(f"Generating geometry from prompt: {prompt}")

        # Parse prompt to extract objects
        object_descriptions = self._parse_prompt(prompt)
        logger.info(f"Identified {len(object_descriptions)} objects to generate")

        # Generate geometry for each object
        geometry_objects = []
        for desc in object_descriptions:
            try:
                # Check if we have a reference model
                if self._has_reference_model(desc, references):
                    geom = self._import_reference_model(desc, references)
                else:
                    # Generate procedurally
                    geom = self._generate_procedural(desc)

                geometry_objects.append(geom)
                logger.info(f"Generated geometry for: {desc['name']}")

            except Exception as e:
                logger.error(f"Failed to generate geometry for {desc.get('name', 'unknown')}: {e}")
                # Create fallback primitive
                geom = self._create_fallback_primitive(desc)
                geometry_objects.append(geom)

        return geometry_objects

    def _parse_prompt(self, prompt: str) -> List[Dict[str, str]]:
        """
        Parse prompt to extract object descriptions.

        Args:
            prompt: Scene description

        Returns:
            List of object description dictionaries

        Example:
            >>> handler = GeometryHandler()
            >>> objects = handler._parse_prompt("A table with four chairs")
            >>> print(objects)
            [{'name': 'table', 'type': 'furniture', ...}, ...]
        """
        # Simple keyword-based parsing (can be enhanced with NLP)
        object_keywords = {
            "furniture": ["table", "chair", "sofa", "couch", "desk", "bed", "shelf", "cabinet"],
            "lighting": ["lamp", "light", "chandelier", "sconce"],
            "decoration": ["vase", "plant", "picture", "frame", "rug", "pillow"],
            "appliance": ["tv", "television", "monitor", "computer", "refrigerator"],
            "architectural": ["wall", "floor", "ceiling", "door", "window"]
        }

        prompt_lower = prompt.lower()
        found_objects = []

        for category, keywords in object_keywords.items():
            for keyword in keywords:
                if keyword in prompt_lower:
                    found_objects.append({
                        "name": keyword,
                        "type": category,
                        "description": prompt
                    })

        # If no objects found, create a default placeholder
        if not found_objects:
            found_objects.append({
                "name": "scene_element",
                "type": "generic",
                "description": prompt
            })

        return found_objects

    def _has_reference_model(
        self,
        description: Dict[str, str],
        references: Dict[str, Any]
    ) -> bool:
        """
        Check if a reference model exists for the object.

        Args:
            description: Object description
            references: Reference data

        Returns:
            True if reference model exists
        """
        if not references or 'models' not in references:
            return False

        object_name = description.get('name', '').lower()
        for model in references.get('models', []):
            if object_name in model.get('name', '').lower():
                return True

        return False

    def _import_reference_model(
        self,
        description: Dict[str, str],
        references: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Import and convert a reference model to voxel mesh.

        Args:
            description: Object description
            references: Reference data with model information

        Returns:
            Geometry object dictionary
        """
        logger.info(f"Importing reference model for: {description['name']}")

        # Find matching reference model
        object_name = description.get('name', '').lower()
        model_data = None

        for model in references.get('models', []):
            if object_name in model.get('name', '').lower():
                model_data = model
                break

        if not model_data:
            # Fallback to procedural
            return self._generate_procedural(description)

        # Create geometry object from reference
        # (In production, this would load actual model file)
        geometry = {
            "name": description['name'],
            "type": GeometryType.IMPORTED.value,
            "vertices": self._generate_placeholder_vertices(model_data),
            "faces": self._generate_placeholder_faces(model_data),
            "metadata": {
                "source": "reference",
                "reference_name": model_data.get('name'),
                "original_format": model_data.get('format', 'unknown')
            }
        }

        return geometry

    def _generate_procedural(self, description: Dict[str, str]) -> Dict[str, Any]:
        """
        Generate geometry procedurally based on object type.

        Args:
            description: Object description

        Returns:
            Geometry object dictionary
        """
        logger.info(f"Generating procedural geometry for: {description['name']}")

        object_type = description.get('type', 'generic')
        object_name = description.get('name', '')

        # Determine appropriate primitive or complex shape
        if object_type == "furniture":
            return self._generate_furniture(description)
        elif object_type == "lighting":
            return self._generate_lighting(description)
        elif object_type == "decoration":
            return self._generate_decoration(description)
        else:
            return self._create_fallback_primitive(description)

    def _generate_furniture(self, description: Dict[str, str]) -> Dict[str, Any]:
        """Generate furniture geometry."""
        name = description.get('name', 'furniture')

        # Simple furniture templates
        if "table" in name:
            return self._create_table()
        elif "chair" in name or "seat" in name:
            return self._create_chair()
        elif "sofa" in name or "couch" in name:
            return self._create_sofa()
        elif "bed" in name:
            return self._create_bed()
        else:
            return self._create_primitive_box(name, (1.0, 1.0, 0.8))

    def _generate_lighting(self, description: Dict[str, str]) -> Dict[str, Any]:
        """Generate lighting geometry."""
        name = description.get('name', 'light')

        if "lamp" in name:
            return self._create_lamp()
        else:
            # Simple light fixture
            return self._create_primitive_cylinder(name, 0.2, 0.5)

    def _generate_decoration(self, description: Dict[str, str]) -> Dict[str, Any]:
        """Generate decoration geometry."""
        name = description.get('name', 'decoration')

        if "vase" in name:
            return self._create_primitive_cylinder(name, 0.15, 0.4)
        elif "plant" in name:
            return self._create_primitive_sphere(name, 0.3)
        else:
            return self._create_primitive_box(name, (0.3, 0.3, 0.3))

    def _create_table(self) -> Dict[str, Any]:
        """Create a simple table geometry."""
        # Table top + 4 legs
        vertices, faces = self._create_box_vertices_faces((1.2, 0.8, 0.05))

        # Add legs (simplified - just add to metadata for now)
        return {
            "name": "table",
            "type": GeometryType.PROCEDURAL.value,
            "vertices": vertices,
            "faces": faces,
            "metadata": {
                "object_type": "furniture",
                "subtype": "table",
                "has_legs": True,
                "leg_count": 4
            }
        }

    def _create_chair(self) -> Dict[str, Any]:
        """Create a simple chair geometry."""
        vertices, faces = self._create_box_vertices_faces((0.5, 0.5, 0.5))

        return {
            "name": "chair",
            "type": GeometryType.PROCEDURAL.value,
            "vertices": vertices,
            "faces": faces,
            "metadata": {
                "object_type": "furniture",
                "subtype": "chair",
                "has_backrest": True
            }
        }

    def _create_sofa(self) -> Dict[str, Any]:
        """Create a simple sofa geometry."""
        vertices, faces = self._create_box_vertices_faces((2.0, 0.9, 0.8))

        return {
            "name": "sofa",
            "type": GeometryType.PROCEDURAL.value,
            "vertices": vertices,
            "faces": faces,
            "metadata": {
                "object_type": "furniture",
                "subtype": "sofa",
                "seating_capacity": 3
            }
        }

    def _create_bed(self) -> Dict[str, Any]:
        """Create a simple bed geometry."""
        vertices, faces = self._create_box_vertices_faces((2.0, 1.6, 0.6))

        return {
            "name": "bed",
            "type": GeometryType.PROCEDURAL.value,
            "vertices": vertices,
            "faces": faces,
            "metadata": {
                "object_type": "furniture",
                "subtype": "bed",
                "size": "double"
            }
        }

    def _create_lamp(self) -> Dict[str, Any]:
        """Create a simple lamp geometry."""
        # Lamp = base + stand + shade
        vertices, faces = self._create_cylinder_vertices_faces(0.15, 1.5, 16)

        return {
            "name": "lamp",
            "type": GeometryType.PROCEDURAL.value,
            "vertices": vertices,
            "faces": faces,
            "metadata": {
                "object_type": "lighting",
                "subtype": "floor_lamp",
                "light_source": True
            }
        }

    def _create_primitive_box(
        self,
        name: str,
        size: Tuple[float, float, float]
    ) -> Dict[str, Any]:
        """Create a box primitive."""
        vertices, faces = self._create_box_vertices_faces(size)

        return {
            "name": name,
            "type": GeometryType.PRIMITIVE.value,
            "vertices": vertices,
            "faces": faces,
            "metadata": {"primitive_type": "box", "size": size}
        }

    def _create_primitive_sphere(self, name: str, radius: float) -> Dict[str, Any]:
        """Create a sphere primitive."""
        vertices, faces = self._create_sphere_vertices_faces(radius, 16, 8)

        return {
            "name": name,
            "type": GeometryType.PRIMITIVE.value,
            "vertices": vertices,
            "faces": faces,
            "metadata": {"primitive_type": "sphere", "radius": radius}
        }

    def _create_primitive_cylinder(
        self,
        name: str,
        radius: float,
        height: float
    ) -> Dict[str, Any]:
        """Create a cylinder primitive."""
        vertices, faces = self._create_cylinder_vertices_faces(radius, height, 16)

        return {
            "name": name,
            "type": GeometryType.PRIMITIVE.value,
            "vertices": vertices,
            "faces": faces,
            "metadata": {"primitive_type": "cylinder", "radius": radius, "height": height}
        }

    def _create_fallback_primitive(self, description: Dict[str, str]) -> Dict[str, Any]:
        """Create a fallback primitive when generation fails."""
        logger.warning(f"Using fallback primitive for: {description.get('name', 'unknown')}")
        return self._create_primitive_box(
            description.get('name', 'object'),
            (1.0, 1.0, 1.0)
        )

    def _create_box_vertices_faces(
        self,
        size: Tuple[float, float, float]
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Create vertices and faces for a box.

        Args:
            size: Box dimensions (width, depth, height)

        Returns:
            Tuple of (vertices array, faces array)
        """
        w, d, h = [s / 2 for s in size]

        # 8 vertices of a box
        vertices = np.array([
            [-w, -d, -h], [w, -d, -h], [w, d, -h], [-w, d, -h],  # Bottom
            [-w, -d, h], [w, -d, h], [w, d, h], [-w, d, h]  # Top
        ], dtype=np.float32)

        # 6 faces (quads)
        faces = np.array([
            [0, 1, 2, 3],  # Bottom
            [4, 7, 6, 5],  # Top
            [0, 4, 5, 1],  # Front
            [2, 6, 7, 3],  # Back
            [0, 3, 7, 4],  # Left
            [1, 5, 6, 2]   # Right
        ], dtype=np.int32)

        return vertices, faces

    def _create_sphere_vertices_faces(
        self,
        radius: float,
        segments: int,
        rings: int
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Create vertices and faces for a UV sphere.

        Args:
            radius: Sphere radius
            segments: Number of horizontal segments
            rings: Number of vertical rings

        Returns:
            Tuple of (vertices array, faces array)
        """
        vertices = []
        faces = []

        # Generate vertices
        for ring in range(rings + 1):
            theta = np.pi * ring / rings
            sin_theta = np.sin(theta)
            cos_theta = np.cos(theta)

            for seg in range(segments):
                phi = 2 * np.pi * seg / segments
                sin_phi = np.sin(phi)
                cos_phi = np.cos(phi)

                x = radius * sin_theta * cos_phi
                y = radius * sin_theta * sin_phi
                z = radius * cos_theta

                vertices.append([x, y, z])

        # Generate faces
        for ring in range(rings):
            for seg in range(segments):
                v1 = ring * segments + seg
                v2 = ring * segments + (seg + 1) % segments
                v3 = (ring + 1) * segments + (seg + 1) % segments
                v4 = (ring + 1) * segments + seg

                faces.append([v1, v2, v3, v4])

        return np.array(vertices, dtype=np.float32), np.array(faces, dtype=np.int32)

    def _create_cylinder_vertices_faces(
        self,
        radius: float,
        height: float,
        segments: int
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Create vertices and faces for a cylinder.

        Args:
            radius: Cylinder radius
            height: Cylinder height
            segments: Number of circular segments

        Returns:
            Tuple of (vertices array, faces array)
        """
        vertices = []
        faces = []

        h_half = height / 2

        # Bottom center
        vertices.append([0, 0, -h_half])
        # Top center
        vertices.append([0, 0, h_half])

        # Generate side vertices
        for i in range(segments):
            angle = 2 * np.pi * i / segments
            x = radius * np.cos(angle)
            y = radius * np.sin(angle)

            # Bottom ring
            vertices.append([x, y, -h_half])
            # Top ring
            vertices.append([x, y, h_half])

        # Generate faces
        for i in range(segments):
            next_i = (i + 1) % segments

            # Bottom face (triangle)
            faces.append([0, 2 + i * 2, 2 + next_i * 2])

            # Top face (triangle)
            faces.append([1, 3 + next_i * 2, 3 + i * 2])

            # Side face (quad)
            faces.append([
                2 + i * 2,
                3 + i * 2,
                3 + next_i * 2,
                2 + next_i * 2
            ])

        return np.array(vertices, dtype=np.float32), np.array(faces, dtype=np.int32)

    def _generate_placeholder_vertices(self, model_data: Dict[str, Any]) -> np.ndarray:
        """Generate placeholder vertices for imported models."""
        # In production, this would load actual model data
        # For now, create a simple box
        return np.array([
            [-0.5, -0.5, -0.5], [0.5, -0.5, -0.5],
            [0.5, 0.5, -0.5], [-0.5, 0.5, -0.5],
            [-0.5, -0.5, 0.5], [0.5, -0.5, 0.5],
            [0.5, 0.5, 0.5], [-0.5, 0.5, 0.5]
        ], dtype=np.float32)

    def _generate_placeholder_faces(self, model_data: Dict[str, Any]) -> np.ndarray:
        """Generate placeholder faces for imported models."""
        return np.array([
            [0, 1, 2, 3], [4, 7, 6, 5],
            [0, 4, 5, 1], [2, 6, 7, 3],
            [0, 3, 7, 4], [1, 5, 6, 2]
        ], dtype=np.int32)

    def voxelize_mesh(
        self,
        vertices: np.ndarray,
        faces: np.ndarray
    ) -> Dict[str, Any]:
        """
        Convert mesh to voxel representation.

        Args:
            vertices: Mesh vertices
            faces: Mesh faces

        Returns:
            Voxelized geometry data
        """
        logger.info("Voxelizing mesh...")

        # Calculate bounding box
        min_point = vertices.min(axis=0)
        max_point = vertices.max(axis=0)

        # Create voxel grid
        grid_size = np.ceil((max_point - min_point) / self.voxel_resolution).astype(int)

        voxel_data = {
            "resolution": self.voxel_resolution,
            "grid_size": grid_size.tolist(),
            "origin": min_point.tolist(),
            "metadata": {
                "original_vertex_count": len(vertices),
                "original_face_count": len(faces)
            }
        }

        return voxel_data


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    handler = GeometryHandler(voxel_resolution=0.1)

    # Generate geometry from prompt
    objects = handler.generate_from_prompt(
        "A living room with a sofa, coffee table, and floor lamp",
        references={}
    )

    print(f"\nGenerated {len(objects)} objects:")
    for obj in objects:
        print(f"  - {obj['name']}: {obj['type']}")
        print(f"    Vertices: {len(obj['vertices'])}, Faces: {len(obj['faces'])}")
