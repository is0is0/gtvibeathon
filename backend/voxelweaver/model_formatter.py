"""
Model Formatter Module
----------------------
Handles 3D model format conversion and optimization.

This module converts between different 3D file formats, optimizes meshes,
and validates model data for compatibility with VoxelWeaver.
"""

import logging
import json
import struct
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass
from enum import Enum
import numpy as np

logger = logging.getLogger(__name__)


class ModelFormat(Enum):
    """Supported 3D model formats."""
    OBJ = "obj"  # Wavefront OBJ
    FBX = "fbx"  # Autodesk FBX
    GLTF = "gltf"  # glTF 2.0 (JSON)
    GLB = "glb"  # glTF 2.0 (binary)
    STL = "stl"  # STL (ASCII/Binary)
    PLY = "ply"  # Stanford PLY
    DAE = "dae"  # COLLADA
    BLEND = "blend"  # Blender native


class OptimizationLevel(Enum):
    """Mesh optimization levels."""
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    AGGRESSIVE = "aggressive"


@dataclass
class ModelData:
    """Container for 3D model data."""
    vertices: np.ndarray  # Nx3 vertex positions
    faces: np.ndarray  # Mx3 or Mx4 face indices
    normals: Optional[np.ndarray] = None  # Nx3 vertex normals
    uv_coords: Optional[np.ndarray] = None  # Nx2 UV coordinates
    colors: Optional[np.ndarray] = None  # Nx3 or Nx4 vertex colors
    material_indices: Optional[np.ndarray] = None  # Per-face material index
    materials: List[Dict[str, Any]] = None  # Material definitions
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        """Initialize default values."""
        if self.materials is None:
            self.materials = []
        if self.metadata is None:
            self.metadata = {}

    @property
    def vertex_count(self) -> int:
        """Get number of vertices."""
        return len(self.vertices) if self.vertices is not None else 0

    @property
    def face_count(self) -> int:
        """Get number of faces."""
        return len(self.faces) if self.faces is not None else 0

    @property
    def bounds(self) -> Tuple[np.ndarray, np.ndarray]:
        """Get bounding box (min, max)."""
        if self.vertices is None or len(self.vertices) == 0:
            return np.zeros(3), np.zeros(3)
        return self.vertices.min(axis=0), self.vertices.max(axis=0)


@dataclass
class ConversionResult:
    """Result of a format conversion."""
    success: bool
    output_path: Optional[Path]
    source_format: str
    target_format: str
    statistics: Dict[str, Any]
    errors: List[str]
    warnings: List[str]


class ModelFormatter:
    """
    Handles 3D model format conversion and optimization.

    This class provides utilities for converting between different 3D
    file formats, optimizing meshes, and validating model data.

    Example:
        >>> formatter = ModelFormatter()
        >>> result = formatter.convert(
        ...     "input.obj",
        ...     "output.glb",
        ...     optimize=True
        ... )
        >>> print(f"Conversion successful: {result.success}")
    """

    def __init__(
        self,
        default_optimization: OptimizationLevel = OptimizationLevel.MEDIUM
    ):
        """
        Initialize model formatter.

        Args:
            default_optimization: Default optimization level
        """
        self.default_optimization = default_optimization

        # Format capabilities
        self.format_capabilities = {
            ModelFormat.OBJ: {
                'read': True,
                'write': True,
                'materials': True,
                'animations': False,
                'binary': False
            },
            ModelFormat.FBX: {
                'read': True,
                'write': True,
                'materials': True,
                'animations': True,
                'binary': True
            },
            ModelFormat.GLTF: {
                'read': True,
                'write': True,
                'materials': True,
                'animations': True,
                'binary': False
            },
            ModelFormat.GLB: {
                'read': True,
                'write': True,
                'materials': True,
                'animations': True,
                'binary': True
            },
            ModelFormat.STL: {
                'read': True,
                'write': True,
                'materials': False,
                'animations': False,
                'binary': True
            }
        }

        logger.info(f"ModelFormatter initialized (default optimization: {default_optimization.value})")

    def convert(
        self,
        input_path: Path,
        output_path: Path,
        optimize: bool = True,
        optimization_level: Optional[OptimizationLevel] = None,
        preserve_materials: bool = True
    ) -> ConversionResult:
        """
        Convert 3D model from one format to another.

        This is the main entry point for format conversion. It reads the
        input file, optionally optimizes it, and writes to the target format.

        Args:
            input_path: Path to input model file
            output_path: Path to output model file
            optimize: Whether to optimize the mesh
            optimization_level: Optimization level (uses default if None)
            preserve_materials: Whether to preserve materials

        Returns:
            ConversionResult with status and statistics

        Example:
            >>> formatter = ModelFormatter()
            >>> result = formatter.convert(
            ...     Path("model.obj"),
            ...     Path("model.glb"),
            ...     optimize=True
            ... )
        """
        logger.info(f"Converting {input_path} -> {output_path}")

        errors = []
        warnings = []

        # Validate input file
        if not input_path.exists():
            errors.append(f"Input file not found: {input_path}")
            return ConversionResult(
                success=False,
                output_path=None,
                source_format=input_path.suffix[1:],
                target_format=output_path.suffix[1:],
                statistics={},
                errors=errors,
                warnings=warnings
            )

        # Detect formats
        source_format = self._detect_format(input_path)
        target_format = self._detect_format(output_path)

        if not source_format or not target_format:
            errors.append("Could not detect file format")
            return ConversionResult(
                success=False,
                output_path=None,
                source_format=input_path.suffix[1:],
                target_format=output_path.suffix[1:],
                statistics={},
                errors=errors,
                warnings=warnings
            )

        # Validate format support
        validation = self._validate_conversion(source_format, target_format)
        if not validation['supported']:
            errors.append(validation['reason'])
            return ConversionResult(
                success=False,
                output_path=None,
                source_format=source_format.value,
                target_format=target_format.value,
                statistics={},
                errors=errors,
                warnings=warnings
            )

        try:
            # Read input model
            model_data = self._read_model(input_path, source_format)

            # Optimize if requested
            if optimize:
                opt_level = optimization_level or self.default_optimization
                model_data = self._optimize_mesh(model_data, opt_level)

            # Write output model
            self._write_model(output_path, model_data, target_format, preserve_materials)

            # Collect statistics
            statistics = {
                'input_vertices': model_data.metadata.get('original_vertex_count', model_data.vertex_count),
                'output_vertices': model_data.vertex_count,
                'input_faces': model_data.metadata.get('original_face_count', model_data.face_count),
                'output_faces': model_data.face_count,
                'materials': len(model_data.materials),
                'optimization_level': opt_level.value if optimize else 'none',
                'file_size': output_path.stat().st_size if output_path.exists() else 0
            }

            logger.info(f"Conversion completed: {statistics['output_vertices']} vertices, {statistics['output_faces']} faces")

            return ConversionResult(
                success=True,
                output_path=output_path,
                source_format=source_format.value,
                target_format=target_format.value,
                statistics=statistics,
                errors=errors,
                warnings=warnings
            )

        except Exception as e:
            logger.error(f"Conversion failed: {e}", exc_info=True)
            errors.append(str(e))

            return ConversionResult(
                success=False,
                output_path=None,
                source_format=source_format.value,
                target_format=target_format.value,
                statistics={},
                errors=errors,
                warnings=warnings
            )

    def _detect_format(self, file_path: Path) -> Optional[ModelFormat]:
        """
        Detect model format from file extension.

        Args:
            file_path: Path to model file

        Returns:
            ModelFormat or None
        """
        extension = file_path.suffix.lower().lstrip('.')

        for fmt in ModelFormat:
            if fmt.value == extension:
                return fmt

        logger.warning(f"Unknown format: {extension}")
        return None

    def _validate_conversion(
        self,
        source: ModelFormat,
        target: ModelFormat
    ) -> Dict[str, Any]:
        """
        Validate if conversion is supported.

        Args:
            source: Source format
            target: Target format

        Returns:
            Validation result
        """
        source_caps = self.format_capabilities.get(source, {})
        target_caps = self.format_capabilities.get(target, {})

        if not source_caps.get('read', False):
            return {
                'supported': False,
                'reason': f"Cannot read {source.value} format"
            }

        if not target_caps.get('write', False):
            return {
                'supported': False,
                'reason': f"Cannot write {target.value} format"
            }

        return {'supported': True, 'reason': ''}

    def _read_model(
        self,
        file_path: Path,
        format: ModelFormat
    ) -> ModelData:
        """
        Read model from file.

        Args:
            file_path: Path to model file
            format: Model format

        Returns:
            ModelData instance
        """
        logger.info(f"Reading {format.value} file: {file_path}")

        if format == ModelFormat.OBJ:
            return self._read_obj(file_path)
        elif format == ModelFormat.STL:
            return self._read_stl(file_path)
        elif format == ModelFormat.GLTF or format == ModelFormat.GLB:
            return self._read_gltf(file_path)
        else:
            # For unsupported formats, return empty model
            logger.warning(f"Reading {format.value} not fully implemented")
            return ModelData(
                vertices=np.array([[0, 0, 0]]),
                faces=np.array([[0, 0, 0]]),
                metadata={'format': format.value}
            )

    def _read_obj(self, file_path: Path) -> ModelData:
        """Read Wavefront OBJ file."""
        vertices = []
        normals = []
        uvs = []
        faces = []

        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue

                parts = line.split()
                if not parts:
                    continue

                if parts[0] == 'v':  # Vertex
                    vertices.append([float(x) for x in parts[1:4]])

                elif parts[0] == 'vn':  # Normal
                    normals.append([float(x) for x in parts[1:4]])

                elif parts[0] == 'vt':  # UV coordinate
                    uvs.append([float(x) for x in parts[1:3]])

                elif parts[0] == 'f':  # Face
                    face = []
                    for vertex in parts[1:]:
                        # Parse face format: v/vt/vn or v//vn or v/vt or v
                        indices = vertex.split('/')
                        v_idx = int(indices[0]) - 1  # OBJ is 1-indexed
                        face.append(v_idx)
                    faces.append(face)

        return ModelData(
            vertices=np.array(vertices, dtype=np.float32),
            faces=np.array(faces, dtype=np.int32),
            normals=np.array(normals, dtype=np.float32) if normals else None,
            uv_coords=np.array(uvs, dtype=np.float32) if uvs else None,
            metadata={'format': 'obj', 'source': str(file_path)}
        )

    def _read_stl(self, file_path: Path) -> ModelData:
        """Read STL file (binary or ASCII)."""
        # Try binary first
        try:
            with open(file_path, 'rb') as f:
                # Skip header
                f.read(80)

                # Read triangle count
                triangle_count = struct.unpack('I', f.read(4))[0]

                vertices = []
                faces = []
                vertex_map = {}
                vertex_index = 0

                for i in range(triangle_count):
                    # Skip normal
                    f.read(12)

                    # Read 3 vertices
                    face = []
                    for j in range(3):
                        v = struct.unpack('fff', f.read(12))

                        # Deduplicate vertices
                        v_key = tuple(round(x, 6) for x in v)
                        if v_key not in vertex_map:
                            vertex_map[v_key] = vertex_index
                            vertices.append(v)
                            vertex_index += 1

                        face.append(vertex_map[v_key])

                    faces.append(face)

                    # Skip attribute byte count
                    f.read(2)

                return ModelData(
                    vertices=np.array(vertices, dtype=np.float32),
                    faces=np.array(faces, dtype=np.int32),
                    metadata={'format': 'stl', 'source': str(file_path)}
                )

        except Exception as e:
            logger.warning(f"Failed to read as binary STL: {e}")
            # Could implement ASCII STL reading here
            raise

    def _read_gltf(self, file_path: Path) -> ModelData:
        """Read glTF/GLB file (simplified)."""
        # This is a simplified implementation
        # Full glTF support would require a proper parser

        logger.warning("glTF reading is simplified")

        return ModelData(
            vertices=np.array([[0, 0, 0]], dtype=np.float32),
            faces=np.array([[0, 0, 0]], dtype=np.int32),
            metadata={'format': 'gltf', 'source': str(file_path)}
        )

    def _write_model(
        self,
        file_path: Path,
        model_data: ModelData,
        format: ModelFormat,
        preserve_materials: bool
    ) -> None:
        """
        Write model to file.

        Args:
            file_path: Output file path
            model_data: Model data to write
            format: Target format
            preserve_materials: Whether to preserve materials
        """
        logger.info(f"Writing {format.value} file: {file_path}")

        # Create output directory
        file_path.parent.mkdir(parents=True, exist_ok=True)

        if format == ModelFormat.OBJ:
            self._write_obj(file_path, model_data, preserve_materials)
        elif format == ModelFormat.STL:
            self._write_stl(file_path, model_data)
        elif format == ModelFormat.GLTF:
            self._write_gltf(file_path, model_data, preserve_materials)
        else:
            logger.warning(f"Writing {format.value} not fully implemented")

    def _write_obj(
        self,
        file_path: Path,
        model_data: ModelData,
        preserve_materials: bool
    ) -> None:
        """Write Wavefront OBJ file."""
        with open(file_path, 'w') as f:
            f.write(f"# Exported by VoxelWeaver ModelFormatter\n")
            f.write(f"# Vertices: {model_data.vertex_count}\n")
            f.write(f"# Faces: {model_data.face_count}\n\n")

            # Write vertices
            for vertex in model_data.vertices:
                f.write(f"v {vertex[0]:.6f} {vertex[1]:.6f} {vertex[2]:.6f}\n")

            f.write("\n")

            # Write normals
            if model_data.normals is not None:
                for normal in model_data.normals:
                    f.write(f"vn {normal[0]:.6f} {normal[1]:.6f} {normal[2]:.6f}\n")
                f.write("\n")

            # Write UV coordinates
            if model_data.uv_coords is not None:
                for uv in model_data.uv_coords:
                    f.write(f"vt {uv[0]:.6f} {uv[1]:.6f}\n")
                f.write("\n")

            # Write faces (OBJ is 1-indexed)
            for face in model_data.faces:
                f.write("f")
                for vertex_idx in face:
                    f.write(f" {vertex_idx + 1}")
                f.write("\n")

        logger.info(f"Wrote OBJ file: {file_path}")

    def _write_stl(self, file_path: Path, model_data: ModelData) -> None:
        """Write binary STL file."""
        with open(file_path, 'wb') as f:
            # Write header (80 bytes)
            header = b"VoxelWeaver ModelFormatter STL Export"
            f.write(header.ljust(80, b'\0'))

            # Write triangle count
            f.write(struct.pack('I', model_data.face_count))

            # Write triangles
            for face in model_data.faces:
                # Calculate face normal
                v0 = model_data.vertices[face[0]]
                v1 = model_data.vertices[face[1]]
                v2 = model_data.vertices[face[2]]

                edge1 = v1 - v0
                edge2 = v2 - v0
                normal = np.cross(edge1, edge2)
                norm = np.linalg.norm(normal)
                if norm > 0:
                    normal = normal / norm
                else:
                    normal = np.array([0, 0, 1])

                # Write normal
                f.write(struct.pack('fff', *normal))

                # Write vertices
                for vertex_idx in face[:3]:  # STL only supports triangles
                    vertex = model_data.vertices[vertex_idx]
                    f.write(struct.pack('fff', *vertex))

                # Write attribute byte count (unused)
                f.write(struct.pack('H', 0))

        logger.info(f"Wrote STL file: {file_path}")

    def _write_gltf(
        self,
        file_path: Path,
        model_data: ModelData,
        preserve_materials: bool
    ) -> None:
        """Write glTF file (simplified)."""
        # Simplified glTF export
        logger.warning("glTF writing is simplified")

        gltf = {
            "asset": {"version": "2.0", "generator": "VoxelWeaver ModelFormatter"},
            "scene": 0,
            "scenes": [{"nodes": [0]}],
            "nodes": [{"mesh": 0}],
            "meshes": [{
                "primitives": [{
                    "attributes": {"POSITION": 0},
                    "mode": 4  # TRIANGLES
                }]
            }]
        }

        with open(file_path, 'w') as f:
            json.dump(gltf, f, indent=2)

        logger.info(f"Wrote glTF file: {file_path}")

    def _optimize_mesh(
        self,
        model_data: ModelData,
        level: OptimizationLevel
    ) -> ModelData:
        """
        Optimize mesh geometry.

        Args:
            model_data: Model to optimize
            level: Optimization level

        Returns:
            Optimized model data
        """
        logger.info(f"Optimizing mesh (level: {level.value})")

        # Store original counts
        model_data.metadata['original_vertex_count'] = model_data.vertex_count
        model_data.metadata['original_face_count'] = model_data.face_count

        if level == OptimizationLevel.NONE:
            return model_data

        # Apply optimizations based on level
        if level.value in ['low', 'medium', 'high', 'aggressive']:
            # Remove duplicate vertices
            model_data = self._remove_duplicate_vertices(model_data)

        if level.value in ['medium', 'high', 'aggressive']:
            # Remove degenerate faces
            model_data = self._remove_degenerate_faces(model_data)

        if level.value in ['high', 'aggressive']:
            # Simplify mesh
            reduction_ratio = 0.7 if level == OptimizationLevel.HIGH else 0.5
            # model_data = self._simplify_mesh(model_data, reduction_ratio)

        logger.info(f"Optimization complete: {model_data.vertex_count} vertices, {model_data.face_count} faces")

        return model_data

    def _remove_duplicate_vertices(self, model_data: ModelData) -> ModelData:
        """Remove duplicate vertices and update face indices."""
        vertices = model_data.vertices
        faces = model_data.faces

        # Find unique vertices
        unique_vertices, inverse_indices = np.unique(
            vertices,
            axis=0,
            return_inverse=True
        )

        # Update face indices
        new_faces = inverse_indices[faces]

        logger.info(f"Removed {len(vertices) - len(unique_vertices)} duplicate vertices")

        model_data.vertices = unique_vertices
        model_data.faces = new_faces

        return model_data

    def _remove_degenerate_faces(self, model_data: ModelData) -> ModelData:
        """Remove faces with duplicate vertices."""
        faces = model_data.faces
        valid_faces = []

        for face in faces:
            # Check if face has duplicate vertices
            if len(face) == len(set(face)):
                valid_faces.append(face)

        removed = len(faces) - len(valid_faces)
        if removed > 0:
            logger.info(f"Removed {removed} degenerate faces")
            model_data.faces = np.array(valid_faces, dtype=np.int32)

        return model_data

    def validate_model(self, file_path: Path) -> Dict[str, Any]:
        """
        Validate a 3D model file.

        Args:
            file_path: Path to model file

        Returns:
            Validation report

        Example:
            >>> formatter = ModelFormatter()
            >>> report = formatter.validate_model(Path("model.obj"))
            >>> if report['valid']:
            ...     print("Model is valid")
        """
        logger.info(f"Validating model: {file_path}")

        report = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'statistics': {}
        }

        # Check file exists
        if not file_path.exists():
            report['valid'] = False
            report['errors'].append("File not found")
            return report

        # Detect format
        format = self._detect_format(file_path)
        if not format:
            report['valid'] = False
            report['errors'].append("Unknown file format")
            return report

        try:
            # Read model
            model_data = self._read_model(file_path, format)

            # Validate geometry
            if model_data.vertex_count == 0:
                report['errors'].append("No vertices found")
                report['valid'] = False

            if model_data.face_count == 0:
                report['errors'].append("No faces found")
                report['valid'] = False

            # Check for invalid face indices
            if model_data.face_count > 0:
                max_index = model_data.faces.max()
                if max_index >= model_data.vertex_count:
                    report['errors'].append(f"Invalid face index: {max_index} >= {model_data.vertex_count}")
                    report['valid'] = False

            # Collect statistics
            report['statistics'] = {
                'format': format.value,
                'vertices': model_data.vertex_count,
                'faces': model_data.face_count,
                'has_normals': model_data.normals is not None,
                'has_uvs': model_data.uv_coords is not None,
                'materials': len(model_data.materials),
                'file_size': file_path.stat().st_size
            }

        except Exception as e:
            report['valid'] = False
            report['errors'].append(f"Failed to read model: {e}")

        logger.info(f"Validation complete: {'valid' if report['valid'] else 'invalid'}")

        return report


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    formatter = ModelFormatter(default_optimization=OptimizationLevel.MEDIUM)

    # Create test model data
    test_vertices = np.array([
        [0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0],
        [0, 0, 1], [1, 0, 1], [1, 1, 1], [0, 1, 1]
    ], dtype=np.float32)

    test_faces = np.array([
        [0, 1, 2, 3], [4, 7, 6, 5],
        [0, 4, 5, 1], [2, 6, 7, 3],
        [0, 3, 7, 4], [1, 5, 6, 2]
    ], dtype=np.int32)

    test_model = ModelData(
        vertices=test_vertices,
        faces=test_faces,
        metadata={'test': True}
    )

    # Test writing different formats
    output_dir = Path("output/model_formatter")
    output_dir.mkdir(parents=True, exist_ok=True)

    for format_name in ["obj", "stl"]:
        print(f"\n{'='*60}")
        print(f"Testing {format_name.upper()} export")
        print('='*60)

        output_path = output_dir / f"test_model.{format_name}"

        try:
            format_enum = ModelFormat(format_name)
            formatter._write_model(output_path, test_model, format_enum, True)
            print(f"✓ Wrote {format_name.upper()} file: {output_path}")

            # Validate
            report = formatter.validate_model(output_path)
            print(f"\nValidation: {'✓ Valid' if report['valid'] else '✗ Invalid'}")
            print(f"Statistics: {report['statistics']}")

            if report['errors']:
                print(f"Errors: {report['errors']}")

        except Exception as e:
            print(f"✗ Failed: {e}")

    print(f"\n{'='*60}")
    print("Testing optimization")
    print('='*60)

    for level in [OptimizationLevel.NONE, OptimizationLevel.MEDIUM, OptimizationLevel.HIGH]:
        optimized = formatter._optimize_mesh(test_model, level)
        print(f"\n{level.value.upper()}:")
        print(f"  Vertices: {optimized.vertex_count}")
        print(f"  Faces: {optimized.face_count}")
