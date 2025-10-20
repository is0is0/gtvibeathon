"""
Model Formatter - 3D format conversion and export utilities.
Handles conversion between different 3D formats and Blender integration.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

logger = logging.getLogger(__name__)


class ExportFormat(str, Enum):
    """Supported 3D export formats."""
    BLEND = "blend"  # Blender native format
    GLB = "glb"  # glTF binary
    GLTF = "gltf"  # glTF text
    FBX = "fbx"  # Autodesk FBX
    OBJ = "obj"  # Wavefront OBJ
    DAE = "dae"  # Collada
    STL = "stl"  # STereoLithography
    PLY = "ply"  # Polygon File Format
    USD = "usd"  # Universal Scene Description
    ABC = "abc"  # Alembic


@dataclass
class ExportConfig:
    """Configuration for 3D model export."""
    format: ExportFormat
    include_materials: bool = True
    include_animations: bool = True
    include_lighting: bool = True
    include_camera: bool = True
    compression: bool = True  # For formats that support it
    quality: str = "high"  # low, medium, high, production
    scale_factor: float = 1.0
    output_path: Optional[str] = None


@dataclass
class ModelMetadata:
    """Metadata for a 3D model."""
    name: str
    format: ExportFormat
    file_size: int  # bytes
    vertex_count: int
    face_count: int
    material_count: int
    texture_count: int
    animation_count: int
    bounding_box: Tuple[float, float, float, float, float, float]  # min_x, min_y, min_z, max_x, max_y, max_z
    created_at: str
    modified_at: str


class ModelFormatter:
    """
    Handles 3D model format conversion and export.
    Provides utilities for converting between different 3D formats.
    """

    def __init__(self):
        """Initialize model formatter."""
        logger.info("ModelFormatter initialized")

    def generate_export_code(
        self,
        scene_data: Dict[str, Any],
        export_config: ExportConfig
    ) -> str:
        """
        Generate Blender Python code for exporting scene to specified format.

        Args:
            scene_data: Scene data with objects, materials, etc.
            export_config: Export configuration

        Returns:
            Python code string for Blender export
        """
        logger.info(f"Generating export code for {export_config.format} format")

        code_lines = [
            "import bpy",
            "import os",
            "from pathlib import Path",
            "",
            "# Export configuration",
            f"export_format = '{export_config.format}'",
            f"include_materials = {export_config.include_materials}",
            f"include_animations = {export_config.include_animations}",
            f"include_lighting = {export_config.include_lighting}",
            f"include_camera = {export_config.include_camera}",
            f"compression = {export_config.compression}",
            f"quality = '{export_config.quality}'",
            f"scale_factor = {export_config.scale_factor}",
            ""
        ]

        # Add format-specific export code
        if export_config.format == ExportFormat.BLEND:
            code_lines.extend(self._generate_blend_export_code(export_config))
        elif export_config.format == ExportFormat.GLB:
            code_lines.extend(self._generate_glb_export_code(export_config))
        elif export_config.format == ExportFormat.FBX:
            code_lines.extend(self._generate_fbx_export_code(export_config))
        elif export_config.format == ExportFormat.OBJ:
            code_lines.extend(self._generate_obj_export_code(export_config))
        elif export_config.format == ExportFormat.STL:
            code_lines.extend(self._generate_stl_export_code(export_config))
        else:
            code_lines.extend(self._generate_generic_export_code(export_config))

        return "\n".join(code_lines)

    def _generate_blend_export_code(self, config: ExportConfig) -> List[str]:
        """Generate Blender native format export code."""
        return [
            "# Export as Blender .blend file",
            "output_path = Path('output') / 'scene.blend'",
            "output_path.parent.mkdir(parents=True, exist_ok=True)",
            "",
            "# Save current scene",
            "bpy.ops.wm.save_as_mainfile(",
            "    filepath=str(output_path),",
            "    check_existing=False",
            ")",
            "",
            "print(f'✅ Scene saved as .blend: {output_path}')"
        ]

    def _generate_glb_export_code(self, config: ExportConfig) -> List[str]:
        """Generate glTF binary export code."""
        return [
            "# Export as glTF binary (.glb)",
            "output_path = Path('output') / 'scene.glb'",
            "output_path.parent.mkdir(parents=True, exist_ok=True)",
            "",
            "# Configure glTF export",
            "bpy.ops.export_scene.gltf(",
            "    filepath=str(output_path),",
            "    export_format='GLB',",
            f"    export_materials={'EXPORT' if config.include_materials else 'NONE'},",
            f"    export_animations={config.include_animations},",
            f"    export_lighting={config.include_lighting},",
            f"    export_cameras={config.include_camera},",
            f"    export_compression={config.compression},",
            f"    export_image_format='AUTO',",
            f"    export_texture_dir='textures',",
            ")",
            "",
            "print(f'✅ Scene exported as .glb: {output_path}')"
        ]

    def _generate_fbx_export_code(self, config: ExportConfig) -> List[str]:
        """Generate FBX export code."""
        return [
            "# Export as FBX",
            "output_path = Path('output') / 'scene.fbx'",
            "output_path.parent.mkdir(parents=True, exist_ok=True)",
            "",
            "# Configure FBX export",
            "bpy.ops.export_scene.fbx(",
            "    filepath=str(output_path),",
            f"    use_selection=False,",
            f"    use_active_collection=False,",
            f"    global_scale={config.scale_factor},",
            f"    apply_unit_scale=True,",
            f"    apply_scale_options='FBX_SCALE_NONE',",
            f"    use_space_transform=True,",
            f"    bake_space_transform=False,",
            f"    object_types={{'MESH', 'ARMATURE', 'LIGHT', 'CAMERA'}},",
            f"    use_mesh_modifiers=True,",
            f"    use_mesh_modifiers_render=True,",
            f"    use_materials={config.include_materials},",
            f"    use_armature_deform_only=False,",
            f"    add_leaf_bones=True,",
            f"    primary_bone_axis='Y',",
            f"    secondary_bone_axis='X',",
            f"    use_metadata=True,",
            ")",
            "",
            "print(f'✅ Scene exported as .fbx: {output_path}')"
        ]

    def _generate_obj_export_code(self, config: ExportConfig) -> List[str]:
        """Generate OBJ export code."""
        return [
            "# Export as OBJ",
            "output_path = Path('output') / 'scene.obj'",
            "output_path.parent.mkdir(parents=True, exist_ok=True)",
            "",
            "# Configure OBJ export",
            "bpy.ops.export_scene.obj(",
            "    filepath=str(output_path),",
            f"    use_selection=False,",
            f"    use_animation={config.include_animations},",
            f"    use_mesh_modifiers=True,",
            f"    use_edges=True,",
            f"    use_smooth_groups=False,",
            f"    use_smooth_groups_bitflags=False,",
            f"    use_normals=True,",
            f"    use_uvs=True,",
            f"    use_materials={config.include_materials},",
            f"    use_triangles=False,",
            f"    use_nurbs=False,",
            f"    use_vertex_groups=False,",
            f"    use_blen_objects=True,",
            f"    group_by_object=False,",
            f"    group_by_material=False,",
            f"    keep_vertex_order=False,",
            f"    global_scale={config.scale_factor},",
            f"    path_mode='AUTO',",
            ")",
            "",
            "print(f'✅ Scene exported as .obj: {output_path}')"
        ]

    def _generate_stl_export_code(self, config: ExportConfig) -> List[str]:
        """Generate STL export code."""
        return [
            "# Export as STL",
            "output_path = Path('output') / 'scene.stl'",
            "output_path.parent.mkdir(parents=True, exist_ok=True)",
            "",
            "# Configure STL export",
            "bpy.ops.export_mesh.stl(",
            "    filepath=str(output_path),",
            f"    use_selection=False,",
            f"    use_mesh_modifiers=True,",
            f"    use_scene_unit=False,",
            f"    use_smooth_groups=False,",
            f"    batch_mode='OFF',",
            f"    global_scale={config.scale_factor},",
            f"    ascii=False,",
            ")",
            "",
            "print(f'✅ Scene exported as .stl: {output_path}')"
        ]

    def _generate_generic_export_code(self, config: ExportConfig) -> List[str]:
        """Generate generic export code for unsupported formats."""
        return [
            f"# Export as {config.format.upper()}",
            "output_path = Path('output') / f'scene.{config.format}'",
            "output_path.parent.mkdir(parents=True, exist_ok=True)",
            "",
            "# Generic export (format-specific implementation needed)",
            "print(f'⚠️ {config.format.upper()} export not yet implemented')",
            "print(f'   Output path: {output_path}')",
            "print(f'   Please implement {config.format.upper()} export manually')"
        ]

    def analyze_model_requirements(
        self,
        scene_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze scene data to determine export requirements.

        Args:
            scene_data: Scene data with objects, materials, etc.

        Returns:
            Analysis results with export recommendations
        """
        logger.info("Analyzing model export requirements...")

        analysis = {
            'total_objects': len(scene_data.get('objects', [])),
            'total_materials': len(scene_data.get('materials', [])),
            'total_textures': len(scene_data.get('textures', [])),
            'has_animations': bool(scene_data.get('animations', [])),
            'has_lighting': bool(scene_data.get('lights', [])),
            'has_camera': bool(scene_data.get('camera')),
            'complexity_score': 0.0,
            'recommended_formats': [],
            'export_notes': []
        }

        # Calculate complexity score
        object_count = analysis['total_objects']
        material_count = analysis['total_materials']
        texture_count = analysis['total_textures']

        complexity = (object_count * 0.3 + material_count * 0.4 + texture_count * 0.3) / 100
        analysis['complexity_score'] = min(1.0, complexity)

        # Recommend formats based on scene characteristics
        if analysis['has_animations']:
            analysis['recommended_formats'].extend(['glb', 'fbx', 'dae'])
        else:
            analysis['recommended_formats'].extend(['obj', 'stl', 'ply'])

        if analysis['total_materials'] > 0:
            analysis['recommended_formats'].extend(['glb', 'gltf', 'fbx'])

        if analysis['complexity_score'] > 0.7:
            analysis['recommended_formats'].extend(['blend', 'abc', 'usd'])

        # Remove duplicates and limit
        analysis['recommended_formats'] = list(set(analysis['recommended_formats']))[:5]

        # Add export notes
        if analysis['complexity_score'] > 0.8:
            analysis['export_notes'].append("High complexity scene - consider using .blend or .abc format")
        
        if analysis['has_animations']:
            analysis['export_notes'].append("Scene contains animations - use .glb or .fbx format")
        
        if analysis['total_materials'] > 10:
            analysis['export_notes'].append("Many materials - ensure format supports PBR materials")

        logger.info(f"Model analysis complete. Complexity: {analysis['complexity_score']:.2f}")
        logger.info(f"Recommended formats: {analysis['recommended_formats']}")

        return analysis

    def create_export_config(
        self,
        format: ExportFormat,
        scene_data: Dict[str, Any],
        output_path: Optional[str] = None
    ) -> ExportConfig:
        """
        Create export configuration based on format and scene data.

        Args:
            format: Export format
            scene_data: Scene data
            output_path: Optional output path

        Returns:
            Configured export configuration
        """
        logger.info(f"Creating export config for {format} format")

        # Analyze scene requirements
        analysis = self.analyze_model_requirements(scene_data)

        # Set default values based on format
        include_materials = analysis['total_materials'] > 0
        include_animations = analysis['has_animations']
        include_lighting = analysis['has_lighting']
        include_camera = analysis['has_camera']

        # Format-specific optimizations
        if format == ExportFormat.STL:
            include_materials = False  # STL doesn't support materials
            include_animations = False
            include_lighting = False
            include_camera = False
        elif format == ExportFormat.OBJ:
            include_animations = False  # OBJ doesn't support animations
        elif format == ExportFormat.BLEND:
            # Blender format supports everything
            pass

        # Set quality based on complexity
        if analysis['complexity_score'] > 0.8:
            quality = "production"
        elif analysis['complexity_score'] > 0.5:
            quality = "high"
        else:
            quality = "medium"

        config = ExportConfig(
            format=format,
            include_materials=include_materials,
            include_animations=include_animations,
            include_lighting=include_lighting,
            include_camera=include_camera,
            compression=True,
            quality=quality,
            scale_factor=1.0,
            output_path=output_path
        )

        logger.info(f"Export config created: {format} with {quality} quality")
        return config

    def get_supported_formats(self) -> List[ExportFormat]:
        """Get list of supported export formats."""
        return list(ExportFormat)

    def get_format_info(self, format: ExportFormat) -> Dict[str, Any]:
        """
        Get information about a specific export format.

        Args:
            format: Export format

        Returns:
            Format information dictionary
        """
        format_info = {
            ExportFormat.BLEND: {
                'name': 'Blender Native',
                'extension': '.blend',
                'supports_materials': True,
                'supports_animations': True,
                'supports_lighting': True,
                'supports_camera': True,
                'compression': False,
                'description': 'Blender native format with full feature support'
            },
            ExportFormat.GLB: {
                'name': 'glTF Binary',
                'extension': '.glb',
                'supports_materials': True,
                'supports_animations': True,
                'supports_lighting': True,
                'supports_camera': True,
                'compression': True,
                'description': 'Universal 3D format for web and real-time applications'
            },
            ExportFormat.FBX: {
                'name': 'Autodesk FBX',
                'extension': '.fbx',
                'supports_materials': True,
                'supports_animations': True,
                'supports_lighting': True,
                'supports_camera': True,
                'compression': False,
                'description': 'Industry standard for 3D content exchange'
            },
            ExportFormat.OBJ: {
                'name': 'Wavefront OBJ',
                'extension': '.obj',
                'supports_materials': True,
                'supports_animations': False,
                'supports_lighting': False,
                'supports_camera': False,
                'compression': False,
                'description': 'Simple mesh format for static 3D models'
            },
            ExportFormat.STL: {
                'name': 'STereoLithography',
                'extension': '.stl',
                'supports_materials': False,
                'supports_animations': False,
                'supports_lighting': False,
                'supports_camera': False,
                'compression': False,
                'description': 'Simple mesh format for 3D printing'
            }
        }

        return format_info.get(format, {
            'name': format.value.upper(),
            'extension': f'.{format.value}',
            'supports_materials': False,
            'supports_animations': False,
            'supports_lighting': False,
            'supports_camera': False,
            'compression': False,
            'description': f'{format.value.upper()} format (implementation needed)'
        })
