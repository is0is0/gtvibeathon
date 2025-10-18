"""
Blender Bridge Module
--------------------
Integrates with Blender Python API for scene export and rendering.

This module handles exporting VoxelWeaver scenes to Blender files in various
formats (.blend, .glb, .fbx, .obj) with full material and lighting support.
"""

import logging
import subprocess
import json
import tempfile
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass
from enum import Enum
import platform

logger = logging.getLogger(__name__)


class ExportFormat(Enum):
    """Supported export formats."""
    BLEND = "blend"  # Native Blender format
    GLB = "glb"  # glTF 2.0 binary
    GLTF = "gltf"  # glTF 2.0 separate
    FBX = "fbx"  # Autodesk FBX
    OBJ = "obj"  # Wavefront OBJ
    STL = "stl"  # STL for 3D printing
    USD = "usd"  # Universal Scene Description


class BlenderVersion:
    """Blender version information."""
    def __init__(self, major: int, minor: int, patch: int = 0):
        self.major = major
        self.minor = minor
        self.patch = patch

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"

    def __ge__(self, other: 'BlenderVersion') -> bool:
        return (self.major, self.minor, self.patch) >= (other.major, other.minor, other.patch)


@dataclass
class ExportSettings:
    """Settings for export operations."""
    format: ExportFormat
    include_materials: bool = True
    include_lighting: bool = True
    include_cameras: bool = True
    apply_modifiers: bool = True
    export_animations: bool = False
    optimize_mesh: bool = True
    compression: bool = False
    scale: float = 1.0
    forward_axis: str = 'Y'  # Y or Z
    up_axis: str = 'Z'  # Y or Z


class BlenderBridge:
    """
    Handles Blender integration and scene export.

    This class exports VoxelWeaver scenes to Blender format and other
    3D file formats using Blender's Python API.

    Example:
        >>> bridge = BlenderBridge()
        >>> scene = {"objects": [...], "lighting": {...}}
        >>> result = bridge.export_scene(scene, format="glb")
        >>> print(f"Exported to: {result['path']}")
    """

    def __init__(
        self,
        blender_executable: Optional[Path] = None,
        temp_dir: Optional[Path] = None
    ):
        """
        Initialize Blender bridge.

        Args:
            blender_executable: Path to Blender executable
            temp_dir: Temporary directory for intermediate files
        """
        self.blender_path = blender_executable or self._find_blender()
        self.temp_dir = temp_dir or Path(tempfile.gettempdir()) / "voxelweaver"
        self.temp_dir.mkdir(parents=True, exist_ok=True)

        # Verify Blender is available
        self.blender_version = self._get_blender_version()

        logger.info(f"BlenderBridge initialized with Blender {self.blender_version}")

    def _find_blender(self) -> Path:
        """
        Find Blender executable on system.

        Returns:
            Path to Blender executable

        Raises:
            RuntimeError: If Blender is not found
        """
        system = platform.system()

        # Common Blender installation paths
        possible_paths = []

        if system == "Darwin":  # macOS
            possible_paths = [
                Path("/Applications/Blender.app/Contents/MacOS/Blender"),
                Path.home() / "Applications/Blender.app/Contents/MacOS/Blender"
            ]
        elif system == "Windows":
            possible_paths = [
                Path("C:/Program Files/Blender Foundation/Blender/blender.exe"),
                Path("C:/Program Files/Blender Foundation/Blender 4.0/blender.exe"),
                Path("C:/Program Files/Blender Foundation/Blender 3.6/blender.exe"),
            ]
        else:  # Linux
            possible_paths = [
                Path("/usr/bin/blender"),
                Path("/usr/local/bin/blender"),
                Path.home() / "blender/blender"
            ]

        # Check environment variable
        import os
        if "BLENDER_PATH" in os.environ:
            possible_paths.insert(0, Path(os.environ["BLENDER_PATH"]))

        # Try to find Blender
        for path in possible_paths:
            if path.exists():
                logger.info(f"Found Blender at: {path}")
                return path

        # Try 'blender' command in PATH
        try:
            result = subprocess.run(
                ["which", "blender"] if system != "Windows" else ["where", "blender"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                blender_path = Path(result.stdout.strip())
                logger.info(f"Found Blender in PATH: {blender_path}")
                return blender_path
        except Exception:
            pass

        raise RuntimeError(
            "Blender not found. Please install Blender or set BLENDER_PATH environment variable."
        )

    def _get_blender_version(self) -> BlenderVersion:
        """
        Get installed Blender version.

        Returns:
            BlenderVersion instance
        """
        try:
            result = subprocess.run(
                [str(self.blender_path), "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )

            # Parse version from output
            # Example: "Blender 4.0.2"
            output = result.stdout.strip()
            for line in output.split('\n'):
                if "Blender" in line:
                    parts = line.split()
                    for part in parts:
                        if part[0].isdigit():
                            version_parts = part.split('.')
                            major = int(version_parts[0])
                            minor = int(version_parts[1]) if len(version_parts) > 1 else 0
                            patch = int(version_parts[2]) if len(version_parts) > 2 else 0
                            return BlenderVersion(major, minor, patch)

        except Exception as e:
            logger.warning(f"Could not determine Blender version: {e}")

        return BlenderVersion(3, 6, 0)  # Default fallback

    def export_scene(
        self,
        scene: Dict[str, Any],
        format: str = "blend",
        output_dir: Optional[Path] = None,
        filename: Optional[str] = None,
        settings: Optional[ExportSettings] = None
    ) -> Dict[str, Any]:
        """
        Export scene to Blender file.

        This is the main entry point for scene export. It converts the
        VoxelWeaver scene to Blender format and exports to the target format.

        Args:
            scene: Scene data with objects, lighting, materials
            format: Export format ('blend', 'glb', 'fbx', 'obj')
            output_dir: Output directory (default: temp_dir)
            filename: Output filename (auto-generated if None)
            settings: Optional export settings

        Returns:
            Dictionary containing:
                - path: Path to exported file
                - format: Export format
                - metadata: Export metadata
                - success: Success status
                - errors: List of errors

        Example:
            >>> bridge = BlenderBridge()
            >>> result = bridge.export_scene(
            ...     scene_data,
            ...     format="glb",
            ...     output_dir=Path("output")
            ... )
        """
        logger.info(f"Exporting scene to {format} format")

        # Parse format
        try:
            export_format = ExportFormat(format.lower())
        except ValueError:
            logger.error(f"Unsupported export format: {format}")
            return {
                'success': False,
                'path': None,
                'errors': [f"Unsupported format: {format}"]
            }

        # Setup paths
        output_dir = output_dir or self.temp_dir
        output_dir.mkdir(parents=True, exist_ok=True)

        if not filename:
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"voxelweaver_scene_{timestamp}.{export_format.value}"

        output_path = output_dir / filename

        # Setup export settings
        if not settings:
            settings = ExportSettings(format=export_format)

        # Generate Blender Python script
        script_path = self._generate_blender_script(scene, output_path, settings)

        try:
            # Execute Blender script
            result = self._execute_blender_script(script_path)

            if result['returncode'] == 0:
                return {
                    'success': True,
                    'path': str(output_path),
                    'format': export_format.value,
                    'metadata': {
                        'object_count': len(scene.get('objects', [])),
                        'light_count': len(scene.get('lighting', {}).get('lights', [])),
                        'file_size': output_path.stat().st_size if output_path.exists() else 0
                    },
                    'errors': []
                }
            else:
                return {
                    'success': False,
                    'path': None,
                    'format': export_format.value,
                    'metadata': {},
                    'errors': [result.get('stderr', 'Unknown error')]
                }

        except Exception as e:
            logger.error(f"Export failed: {e}", exc_info=True)
            return {
                'success': False,
                'path': None,
                'format': export_format.value,
                'metadata': {},
                'errors': [str(e)]
            }

    def _generate_blender_script(
        self,
        scene: Dict[str, Any],
        output_path: Path,
        settings: ExportSettings
    ) -> Path:
        """
        Generate Blender Python script for scene export.

        Args:
            scene: Scene data
            output_path: Output file path
            settings: Export settings

        Returns:
            Path to generated script
        """
        logger.info("Generating Blender Python script")

        script_path = self.temp_dir / "export_script.py"

        # Generate script content
        script = self._create_export_script(scene, output_path, settings)

        # Write script
        with open(script_path, 'w') as f:
            f.write(script)

        logger.info(f"Script written to: {script_path}")
        return script_path

    def _create_export_script(
        self,
        scene: Dict[str, Any],
        output_path: Path,
        settings: ExportSettings
    ) -> str:
        """
        Create Blender Python script content.

        Args:
            scene: Scene data
            output_path: Output file path
            settings: Export settings

        Returns:
            Python script as string
        """
        objects = scene.get('objects', [])
        lighting = scene.get('lighting', {})

        script_lines = [
            "import bpy",
            "import math",
            "import json",
            "",
            "# Clear existing scene",
            "bpy.ops.object.select_all(action='SELECT')",
            "bpy.ops.object.delete(use_global=False)",
            "",
            "# Remove default lights and camera",
            "for obj in bpy.data.objects:",
            "    if obj.type in ['LIGHT', 'CAMERA']:",
            "        bpy.data.objects.remove(obj, do_unlink=True)",
            "",
            "# Create objects",
        ]

        # Add objects
        for obj in objects:
            script_lines.extend(self._create_object_code(obj, settings))

        # Add lighting
        if settings.include_lighting and lighting:
            script_lines.append("\n# Create lighting")
            script_lines.extend(self._create_lighting_code(lighting))

        # Add camera
        if settings.include_cameras:
            script_lines.append("\n# Create camera")
            script_lines.extend(self._create_camera_code(scene))

        # Export
        script_lines.append("\n# Export scene")
        script_lines.extend(self._create_export_code(output_path, settings))

        return '\n'.join(script_lines)

    def _create_object_code(
        self,
        obj: Dict[str, Any],
        settings: ExportSettings
    ) -> List[str]:
        """Generate Blender code for creating an object."""
        lines = [f"\n# Create object: {obj.get('name', 'object')}"]

        name = obj.get('name', 'object')
        position = obj.get('position', [0, 0, 0])
        rotation = obj.get('rotation', [0, 0, 0])

        # Create mesh from vertices and faces
        vertices_str = json.dumps(obj.get('vertices', []))
        faces_str = json.dumps(obj.get('faces', []))

        lines.extend([
            f"mesh_{name} = bpy.data.meshes.new('{name}')",
            f"vertices = {vertices_str}",
            f"faces = {faces_str}",
            f"mesh_{name}.from_pydata(vertices, [], faces)",
            f"mesh_{name}.update()",
            f"obj_{name} = bpy.data.objects.new('{name}', mesh_{name})",
            f"bpy.context.collection.objects.link(obj_{name})",
            f"obj_{name}.location = {position}",
            f"obj_{name}.rotation_euler = {rotation}",
        ])

        # Add material
        if settings.include_materials and 'material' in obj:
            lines.extend(self._create_material_code(obj, name))

        return lines

    def _create_material_code(
        self,
        obj: Dict[str, Any],
        obj_name: str
    ) -> List[str]:
        """Generate Blender code for creating materials."""
        material = obj.get('material', {})
        mat_name = material.get('name', f"{obj_name}_material")

        lines = [
            f"\n# Create material for {obj_name}",
            f"mat_{obj_name} = bpy.data.materials.new('{mat_name}')",
            f"mat_{obj_name}.use_nodes = True",
            f"nodes = mat_{obj_name}.node_tree.nodes",
            f"links = mat_{obj_name}.node_tree.links",
            "nodes.clear()",
            "",
            "# Create shader nodes",
            "output_node = nodes.new('ShaderNodeOutputMaterial')",
            "principled = nodes.new('ShaderNodeBsdfPrincipled')",
            "links.new(principled.outputs['BSDF'], output_node.inputs['Surface'])",
        ]

        # Set material properties
        props = material.get('properties', {})

        if 'base_color' in props:
            color = props['base_color']
            lines.append(f"principled.inputs['Base Color'].default_value = {color}")

        if 'metallic' in props:
            lines.append(f"principled.inputs['Metallic'].default_value = {props['metallic']}")

        if 'roughness' in props:
            lines.append(f"principled.inputs['Roughness'].default_value = {props['roughness']}")

        if 'emission_strength' in props and props['emission_strength'] > 0:
            emission_color = props.get('emission_color', [1, 1, 1])
            lines.append(f"principled.inputs['Emission'].default_value = {emission_color + [1.0]}")
            lines.append(f"principled.inputs['Emission Strength'].default_value = {props['emission_strength']}")

        if 'transmission' in props and props['transmission'] > 0:
            lines.append(f"principled.inputs['Transmission'].default_value = {props['transmission']}")
            lines.append(f"principled.inputs['IOR'].default_value = {props.get('ior', 1.45)}")

        # Assign material to object
        lines.extend([
            f"obj_{obj_name}.data.materials.append(mat_{obj_name})",
        ])

        return lines

    def _create_lighting_code(self, lighting: Dict[str, Any]) -> List[str]:
        """Generate Blender code for creating lights."""
        lines = []

        lights = lighting.get('lights', [])

        for i, light in enumerate(lights):
            light_name = light.get('name', f'Light_{i}')
            light_type = light.get('type', 'POINT').upper()
            position = light.get('position', [0, 5, 0])
            rotation = light.get('rotation', [0, 0, 0])
            color = light.get('color', [1, 1, 1])
            energy = light.get('energy', 100.0)

            lines.extend([
                f"\n# Create light: {light_name}",
                f"light_data_{i} = bpy.data.lights.new('{light_name}', '{light_type}')",
                f"light_data_{i}.color = {color}",
                f"light_data_{i}.energy = {energy}",
                f"light_obj_{i} = bpy.data.objects.new('{light_name}', light_data_{i})",
                f"bpy.context.collection.objects.link(light_obj_{i})",
                f"light_obj_{i}.location = {position}",
                f"light_obj_{i}.rotation_euler = {rotation}",
            ])

        # HDRI environment
        if lighting.get('hdri', {}).get('path'):
            hdri_path = lighting['hdri']['path']
            hdri_strength = lighting['hdri'].get('strength', 1.0)

            lines.extend([
                "\n# Setup HDRI environment",
                "world = bpy.context.scene.world",
                "world.use_nodes = True",
                "world_nodes = world.node_tree.nodes",
                "world_links = world.node_tree.links",
                "world_nodes.clear()",
                "",
                "env_texture = world_nodes.new('ShaderNodeTexEnvironment')",
                f"env_texture.image = bpy.data.images.load('{hdri_path}')",
                "background = world_nodes.new('ShaderNodeBackground')",
                f"background.inputs['Strength'].default_value = {hdri_strength}",
                "world_output = world_nodes.new('ShaderNodeOutputWorld')",
                "world_links.new(env_texture.outputs['Color'], background.inputs['Color'])",
                "world_links.new(background.outputs['Background'], world_output.inputs['Surface'])",
            ])

        return lines

    def _create_camera_code(self, scene: Dict[str, Any]) -> List[str]:
        """Generate Blender code for creating camera."""
        # Analyze scene to determine good camera position
        objects = scene.get('objects', [])

        if objects:
            # Calculate scene center
            positions = [obj.get('position', [0, 0, 0]) for obj in objects if 'position' in obj]
            if positions:
                import numpy as np
                center = np.array(positions).mean(axis=0).tolist()
                # Position camera to view scene
                camera_pos = [center[0], center[1] - 10, center[2] + 5]
            else:
                camera_pos = [0, -10, 5]
        else:
            camera_pos = [0, -10, 5]

        return [
            "camera_data = bpy.data.cameras.new('Camera')",
            "camera_obj = bpy.data.objects.new('Camera', camera_data)",
            "bpy.context.collection.objects.link(camera_obj)",
            f"camera_obj.location = {camera_pos}",
            "camera_obj.rotation_euler = [1.1, 0, 0]",
            "bpy.context.scene.camera = camera_obj",
        ]

    def _create_export_code(
        self,
        output_path: Path,
        settings: ExportSettings
    ) -> List[str]:
        """Generate Blender code for exporting scene."""
        lines = []

        output_str = str(output_path).replace('\\', '/')

        if settings.format == ExportFormat.BLEND:
            lines.append(f"bpy.ops.wm.save_as_mainfile(filepath='{output_str}')")

        elif settings.format == ExportFormat.GLB:
            lines.extend([
                "bpy.ops.export_scene.gltf(",
                f"    filepath='{output_str}',",
                "    export_format='GLB',",
                f"    export_materials={'EXPORT' if settings.include_materials else 'NONE'},",
                f"    export_lights={str(settings.include_lighting).lower()},",
                f"    export_cameras={str(settings.include_cameras).lower()}",
                ")"
            ])

        elif settings.format == ExportFormat.FBX:
            lines.extend([
                "bpy.ops.export_scene.fbx(",
                f"    filepath='{output_str}',",
                f"    use_selection=False,",
                f"    apply_scale_options='FBX_SCALE_ALL'",
                ")"
            ])

        elif settings.format == ExportFormat.OBJ:
            lines.extend([
                "bpy.ops.export_scene.obj(",
                f"    filepath='{output_str}',",
                f"    use_materials={str(settings.include_materials).lower()}",
                ")"
            ])

        lines.append("\nprint('Export completed successfully')")

        return lines

    def _execute_blender_script(self, script_path: Path) -> Dict[str, Any]:
        """
        Execute Blender Python script.

        Args:
            script_path: Path to script file

        Returns:
            Execution result dictionary
        """
        logger.info("Executing Blender script...")

        try:
            result = subprocess.run(
                [
                    str(self.blender_path),
                    "--background",
                    "--python", str(script_path)
                ],
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )

            logger.info(f"Blender execution completed with return code: {result.returncode}")

            if result.stdout:
                logger.debug(f"Blender stdout: {result.stdout}")

            if result.stderr:
                logger.debug(f"Blender stderr: {result.stderr}")

            return {
                'returncode': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr
            }

        except subprocess.TimeoutExpired:
            logger.error("Blender execution timed out")
            return {
                'returncode': -1,
                'stdout': '',
                'stderr': 'Execution timed out'
            }

        except Exception as e:
            logger.error(f"Blender execution failed: {e}")
            return {
                'returncode': -1,
                'stdout': '',
                'stderr': str(e)
            }


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    bridge = BlenderBridge()

    # Create test scene
    test_scene = {
        "objects": [
            {
                "name": "cube",
                "vertices": [
                    [-1, -1, -1], [1, -1, -1], [1, 1, -1], [-1, 1, -1],
                    [-1, -1, 1], [1, -1, 1], [1, 1, 1], [-1, 1, 1]
                ],
                "faces": [
                    [0, 1, 2, 3], [4, 7, 6, 5],
                    [0, 4, 5, 1], [2, 6, 7, 3],
                    [0, 3, 7, 4], [1, 5, 6, 2]
                ],
                "position": [0, 0, 0],
                "rotation": [0, 0, 0],
                "material": {
                    "name": "test_material",
                    "properties": {
                        "base_color": [0.8, 0.3, 0.3, 1.0],
                        "metallic": 0.5,
                        "roughness": 0.3
                    }
                }
            }
        ],
        "lighting": {
            "lights": [
                {
                    "name": "Sun",
                    "type": "SUN",
                    "position": [5, 5, 10],
                    "rotation": [-0.785, 0.785, 0],
                    "color": [1.0, 1.0, 1.0],
                    "energy": 5.0
                }
            ]
        }
    }

    # Export to different formats
    for format_type in ["blend", "glb", "obj"]:
        print(f"\n{'='*60}")
        print(f"Exporting to {format_type.upper()} format")
        print('='*60)

        result = bridge.export_scene(
            test_scene,
            format=format_type,
            output_dir=Path("output"),
            filename=f"test_scene.{format_type}"
        )

        if result['success']:
            print(f"✓ Export successful!")
            print(f"  File: {result['path']}")
            print(f"  Size: {result['metadata'].get('file_size', 0)} bytes")
        else:
            print(f"✗ Export failed:")
            for error in result['errors']:
                print(f"  - {error}")
