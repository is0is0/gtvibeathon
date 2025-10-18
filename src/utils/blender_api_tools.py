"""
Blender API Tools - Utility Functions for Blender Python API Integration
=========================================================================

This module provides a comprehensive wrapper around Blender's Python API (bpy)
for safe, cross-platform integration with Blender operations including:
- Subprocess-based Blender script execution
- Object import/export operations
- Material and texture creation
- Camera and lighting setup
- Scene rendering and batch processing

Author: VoxelWeaver Team
Version: 1.0.0
"""

import subprocess
import sys
import json
import tempfile
import platform
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple, Union
from dataclasses import dataclass, field
import logging
from enum import Enum

from utils.logger import get_logger

logger = get_logger(__name__)


class BlenderEngine(Enum):
    """Render engine options."""
    CYCLES = "CYCLES"
    EEVEE = "BLENDER_EEVEE"
    WORKBENCH = "BLENDER_WORKBENCH"


class ExportFormat(Enum):
    """Supported export formats."""
    FBX = ".fbx"
    OBJ = ".obj"
    GLB = ".glb"
    GLTF = ".gltf"
    STL = ".stl"
    PLY = ".ply"
    BLEND = ".blend"


@dataclass
class BlenderExecutionResult:
    """Result of Blender script execution."""
    success: bool
    stdout: str
    stderr: str
    return_code: int
    output_data: Optional[Dict[str, Any]] = None
    execution_time: float = 0.0
    error_message: Optional[str] = None


@dataclass
class CameraConfig:
    """Camera configuration parameters."""
    location: Tuple[float, float, float] = (7.5, -7.5, 5.5)
    rotation: Tuple[float, float, float] = (1.1, 0.0, 0.785)
    lens: float = 50.0
    sensor_width: float = 36.0
    clip_start: float = 0.1
    clip_end: float = 100.0
    type: str = "PERSP"  # PERSP, ORTHO, PANO


@dataclass
class LightConfig:
    """Light configuration parameters."""
    type: str = "POINT"  # POINT, SUN, SPOT, AREA
    location: Tuple[float, float, float] = (5.0, 5.0, 5.0)
    energy: float = 1000.0
    color: Tuple[float, float, float] = (1.0, 1.0, 1.0)
    size: float = 0.1
    angle: Optional[float] = None  # For SPOT lights
    use_shadow: bool = True


@dataclass
class RenderConfig:
    """Render configuration parameters."""
    engine: BlenderEngine = BlenderEngine.CYCLES
    resolution_x: int = 1920
    resolution_y: int = 1080
    samples: int = 128
    use_denoising: bool = True
    file_format: str = "PNG"
    color_mode: str = "RGBA"
    output_path: Optional[str] = None
    transparent: bool = False
    device: str = "GPU"  # CPU or GPU


@dataclass
class MaterialConfig:
    """Material configuration parameters."""
    name: str = "Material"
    base_color: Tuple[float, float, float, float] = (0.8, 0.8, 0.8, 1.0)
    metallic: float = 0.0
    roughness: float = 0.5
    emission: Tuple[float, float, float, float] = (0.0, 0.0, 0.0, 1.0)
    emission_strength: float = 0.0
    alpha: float = 1.0
    use_nodes: bool = True


class BlenderAPIWrapper:
    """
    High-level wrapper for Blender Python API operations.

    This class provides a safe, cross-platform interface for executing
    Blender operations via subprocess. It handles script generation,
    execution, error handling, and result parsing.

    Attributes:
        blender_path: Path to Blender executable
        background: Run Blender in background mode (no UI)
        python_path: Additional Python paths for imports
        timeout: Execution timeout in seconds

    Example:
        >>> wrapper = BlenderAPIWrapper()
        >>> result = wrapper.execute_in_blender("bpy.ops.mesh.primitive_cube_add()")
        >>> if result.success:
        ...     print("Cube created successfully")
    """

    def __init__(
        self,
        blender_path: Optional[str] = None,
        background: bool = True,
        python_path: Optional[List[str]] = None,
        timeout: int = 300
    ):
        """
        Initialize Blender API wrapper.

        Args:
            blender_path: Path to Blender executable (auto-detected if None)
            background: Run in background mode without GUI
            python_path: Additional Python module paths
            timeout: Script execution timeout in seconds

        Raises:
            FileNotFoundError: If Blender executable not found
        """
        self.blender_path = blender_path or self._find_blender()
        self.background = background
        self.python_path = python_path or []
        self.timeout = timeout
        self._validate_blender()

        logger.info(f"BlenderAPIWrapper initialized with Blender at: {self.blender_path}")

    def _find_blender(self) -> str:
        """
        Auto-detect Blender installation path.

        Returns:
            Path to Blender executable

        Raises:
            FileNotFoundError: If Blender not found
        """
        system = platform.system()

        # Common installation paths
        search_paths = []

        if system == "Darwin":  # macOS
            search_paths = [
                "/Applications/Blender.app/Contents/MacOS/Blender",
                "/Applications/Blender 4.0/Blender.app/Contents/MacOS/Blender",
                "/Applications/Blender 3.6/Blender.app/Contents/MacOS/Blender",
                "~/Applications/Blender.app/Contents/MacOS/Blender"
            ]
        elif system == "Linux":
            search_paths = [
                "/usr/bin/blender",
                "/usr/local/bin/blender",
                "/snap/bin/blender",
                "~/blender/blender"
            ]
        elif system == "Windows":
            search_paths = [
                r"C:\Program Files\Blender Foundation\Blender 4.0\blender.exe",
                r"C:\Program Files\Blender Foundation\Blender 3.6\blender.exe",
                r"C:\Program Files\Blender Foundation\Blender\blender.exe",
            ]

        # Expand user paths
        search_paths = [Path(p).expanduser() for p in search_paths]

        # Find first existing path
        for path in search_paths:
            if path.exists():
                logger.debug(f"Found Blender at: {path}")
                return str(path)

        raise FileNotFoundError(
            f"Blender not found. Searched paths: {[str(p) for p in search_paths]}. "
            "Please install Blender or provide explicit path."
        )

    def _validate_blender(self) -> None:
        """
        Validate Blender installation and version.

        Raises:
            RuntimeError: If Blender is invalid or version incompatible
        """
        try:
            version_info = self.get_blender_version()
            logger.info(f"Blender version: {version_info['version_string']}")

            # Check minimum version (3.0.0)
            major, minor, _ = version_info['version_tuple']
            if (major, minor) < (3, 0):
                raise RuntimeError(
                    f"Blender version {version_info['version_string']} is too old. "
                    "Please upgrade to Blender 3.0 or newer."
                )
        except Exception as e:
            raise RuntimeError(f"Failed to validate Blender installation: {e}")

    def execute_in_blender(
        self,
        script: str,
        blend_file: Optional[str] = None,
        save_file: Optional[str] = None,
        return_json: bool = False
    ) -> BlenderExecutionResult:
        """
        Execute Python script in Blender subprocess.

        Args:
            script: Python code to execute in Blender
            blend_file: Optional .blend file to load before execution
            save_file: Optional path to save .blend file after execution
            return_json: If True, expect JSON output from script

        Returns:
            BlenderExecutionResult with execution details

        Example:
            >>> script = '''
            ... import bpy
            ... bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0))
            ... print("Cube created")
            ... '''
            >>> result = wrapper.execute_in_blender(script)
        """
        import time
        start_time = time.time()

        try:
            # Create temporary script file
            with tempfile.NamedTemporaryFile(
                mode='w',
                suffix='.py',
                delete=False,
                encoding='utf-8'
            ) as f:
                # Add Python path setup if needed
                if self.python_path:
                    f.write("import sys\n")
                    for path in self.python_path:
                        f.write(f"sys.path.append('{path}')\n")
                    f.write("\n")

                # Write user script
                f.write(script)

                # Add save command if requested
                if save_file:
                    f.write(f"\nimport bpy\n")
                    f.write(f"bpy.ops.wm.save_as_mainfile(filepath='{save_file}')\n")

                script_path = f.name

            # Build Blender command
            cmd = [self.blender_path]

            if self.background:
                cmd.extend(['--background'])

            if blend_file:
                cmd.append(blend_file)

            cmd.extend(['--python', script_path])

            logger.debug(f"Executing Blender command: {' '.join(cmd)}")

            # Execute
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout
            )

            execution_time = time.time() - start_time

            # Parse output
            output_data = None
            if return_json and result.stdout:
                try:
                    # Look for JSON in stdout
                    for line in result.stdout.split('\n'):
                        if line.strip().startswith('{'):
                            output_data = json.loads(line)
                            break
                except json.JSONDecodeError as e:
                    logger.warning(f"Failed to parse JSON output: {e}")

            # Cleanup temp file
            Path(script_path).unlink(missing_ok=True)

            success = result.returncode == 0
            error_message = None

            if not success:
                error_message = f"Blender exited with code {result.returncode}"
                if result.stderr:
                    error_message += f": {result.stderr}"

            logger.info(
                f"Blender execution {'succeeded' if success else 'failed'} "
                f"in {execution_time:.2f}s"
            )

            return BlenderExecutionResult(
                success=success,
                stdout=result.stdout,
                stderr=result.stderr,
                return_code=result.returncode,
                output_data=output_data,
                execution_time=execution_time,
                error_message=error_message
            )

        except subprocess.TimeoutExpired:
            execution_time = time.time() - start_time
            logger.error(f"Blender execution timed out after {self.timeout}s")
            return BlenderExecutionResult(
                success=False,
                stdout="",
                stderr="",
                return_code=-1,
                execution_time=execution_time,
                error_message=f"Execution timed out after {self.timeout}s"
            )
        except Exception as e:
            execution_time = time.time() - start_time
            logger.exception(f"Blender execution failed: {e}")
            return BlenderExecutionResult(
                success=False,
                stdout="",
                stderr=str(e),
                return_code=-1,
                execution_time=execution_time,
                error_message=str(e)
            )

    def get_blender_version(self) -> Dict[str, Any]:
        """
        Get Blender version information.

        Returns:
            Dictionary with version info (version_string, version_tuple, etc.)

        Example:
            >>> version = wrapper.get_blender_version()
            >>> print(version['version_string'])  # "4.0.2"
        """
        script = """
import bpy
import json

version_info = {
    'version_string': bpy.app.version_string,
    'version_tuple': list(bpy.app.version),
    'build_date': bpy.app.build_date.decode('utf-8'),
    'build_hash': bpy.app.build_hash.decode('utf-8'),
}

print(json.dumps(version_info))
"""
        result = self.execute_in_blender(script, return_json=True)

        if result.success and result.output_data:
            return result.output_data

        raise RuntimeError(f"Failed to get Blender version: {result.error_message}")

    def import_object(
        self,
        file_path: str,
        location: Tuple[float, float, float] = (0, 0, 0),
        rotation: Tuple[float, float, float] = (0, 0, 0),
        scale: Tuple[float, float, float] = (1, 1, 1)
    ) -> BlenderExecutionResult:
        """
        Import 3D object into Blender scene.

        Args:
            file_path: Path to 3D model file (.obj, .fbx, .gltf, etc.)
            location: Import location (x, y, z)
            rotation: Import rotation in radians (x, y, z)
            scale: Import scale (x, y, z)

        Returns:
            BlenderExecutionResult

        Example:
            >>> result = wrapper.import_object("model.obj", location=(0, 0, 1))
        """
        file_path = Path(file_path).absolute()
        ext = file_path.suffix.lower()

        # Build import script based on file type
        if ext == '.obj':
            import_cmd = f"bpy.ops.import_scene.obj(filepath='{file_path}')"
        elif ext == '.fbx':
            import_cmd = f"bpy.ops.import_scene.fbx(filepath='{file_path}')"
        elif ext in ['.gltf', '.glb']:
            import_cmd = f"bpy.ops.import_scene.gltf(filepath='{file_path}')"
        elif ext == '.stl':
            import_cmd = f"bpy.ops.import_mesh.stl(filepath='{file_path}')"
        elif ext == '.ply':
            import_cmd = f"bpy.ops.import_mesh.ply(filepath='{file_path}')"
        else:
            raise ValueError(f"Unsupported file format: {ext}")

        script = f"""
import bpy
import math

# Import object
{import_cmd}

# Get imported objects
imported_objects = bpy.context.selected_objects

# Transform imported objects
for obj in imported_objects:
    obj.location = {location}
    obj.rotation_euler = {rotation}
    obj.scale = {scale}

print(f"Imported {{len(imported_objects)}} objects from {file_path}")
"""
        return self.execute_in_blender(script)

    def export_scene(
        self,
        output_path: str,
        format: Union[str, ExportFormat] = ExportFormat.FBX,
        selection_only: bool = False,
        apply_modifiers: bool = True
    ) -> BlenderExecutionResult:
        """
        Export scene or selection to file.

        Args:
            output_path: Output file path
            format: Export format (ExportFormat or string)
            selection_only: Export only selected objects
            apply_modifiers: Apply modifiers before export

        Returns:
            BlenderExecutionResult

        Example:
            >>> result = wrapper.export_scene("output.fbx", format=ExportFormat.FBX)
        """
        if isinstance(format, str):
            format = ExportFormat(format.lower() if format.startswith('.') else f'.{format.lower()}')

        output_path = Path(output_path).absolute()

        # Build export command based on format
        if format == ExportFormat.OBJ:
            export_cmd = f"""
bpy.ops.export_scene.obj(
    filepath='{output_path}',
    use_selection={selection_only},
    use_mesh_modifiers={apply_modifiers}
)
"""
        elif format == ExportFormat.FBX:
            export_cmd = f"""
bpy.ops.export_scene.fbx(
    filepath='{output_path}',
    use_selection={selection_only},
    use_mesh_modifiers={apply_modifiers}
)
"""
        elif format in [ExportFormat.GLB, ExportFormat.GLTF]:
            export_cmd = f"""
bpy.ops.export_scene.gltf(
    filepath='{output_path}',
    use_selection={selection_only},
    export_apply={apply_modifiers}
)
"""
        elif format == ExportFormat.STL:
            export_cmd = f"""
bpy.ops.export_mesh.stl(
    filepath='{output_path}',
    use_selection={selection_only},
    use_mesh_modifiers={apply_modifiers}
)
"""
        elif format == ExportFormat.BLEND:
            export_cmd = f"bpy.ops.wm.save_as_mainfile(filepath='{output_path}')"
        else:
            raise ValueError(f"Unsupported export format: {format}")

        script = f"""
import bpy

{export_cmd}

print(f"Exported to {output_path}")
"""
        return self.execute_in_blender(script)

    def create_material(
        self,
        config: MaterialConfig,
        target_object: Optional[str] = None
    ) -> BlenderExecutionResult:
        """
        Create and configure material.

        Args:
            config: Material configuration
            target_object: Optional object name to apply material to

        Returns:
            BlenderExecutionResult

        Example:
            >>> mat_config = MaterialConfig(
            ...     name="GoldMaterial",
            ...     base_color=(1.0, 0.8, 0.3, 1.0),
            ...     metallic=1.0,
            ...     roughness=0.2
            ... )
            >>> result = wrapper.create_material(mat_config)
        """
        script = f"""
import bpy

# Create material
mat = bpy.data.materials.new(name="{config.name}")
mat.use_nodes = {config.use_nodes}

if mat.use_nodes:
    # Get nodes
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    # Clear default nodes
    nodes.clear()

    # Create Principled BSDF
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.location = (0, 0)

    # Configure BSDF
    bsdf.inputs['Base Color'].default_value = {config.base_color}
    bsdf.inputs['Metallic'].default_value = {config.metallic}
    bsdf.inputs['Roughness'].default_value = {config.roughness}
    bsdf.inputs['Emission'].default_value = {config.emission}
    bsdf.inputs['Emission Strength'].default_value = {config.emission_strength}
    bsdf.inputs['Alpha'].default_value = {config.alpha}

    # Create output node
    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (300, 0)

    # Link nodes
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

# Apply to object if specified
target_obj = "{target_object}" if "{target_object}" else None
if target_obj:
    obj = bpy.data.objects.get(target_obj)
    if obj:
        obj.data.materials.clear()
        obj.data.materials.append(mat)
        print(f"Material '{config.name}' applied to {{target_obj}}")
    else:
        print(f"Warning: Object {{target_obj}} not found")
else:
    print(f"Material '{config.name}' created")
"""
        return self.execute_in_blender(script)

    def setup_camera(self, config: CameraConfig) -> BlenderExecutionResult:
        """
        Setup or update camera in scene.

        Args:
            config: Camera configuration

        Returns:
            BlenderExecutionResult

        Example:
            >>> cam_config = CameraConfig(
            ...     location=(10, -10, 10),
            ...     rotation=(1.1, 0, 0.785)
            ... )
            >>> result = wrapper.setup_camera(cam_config)
        """
        script = f"""
import bpy

# Get or create camera
if 'Camera' in bpy.data.cameras:
    camera = bpy.data.cameras['Camera']
    cam_obj = bpy.data.objects['Camera']
else:
    camera = bpy.data.cameras.new('Camera')
    cam_obj = bpy.data.objects.new('Camera', camera)
    bpy.context.scene.collection.objects.link(cam_obj)

# Configure camera
cam_obj.location = {config.location}
cam_obj.rotation_euler = {config.rotation}
camera.lens = {config.lens}
camera.sensor_width = {config.sensor_width}
camera.clip_start = {config.clip_start}
camera.clip_end = {config.clip_end}
camera.type = '{config.type}'

# Set as active camera
bpy.context.scene.camera = cam_obj

print(f"Camera configured at {{cam_obj.location}}")
"""
        return self.execute_in_blender(script)

    def setup_lighting(self, lights: List[LightConfig]) -> BlenderExecutionResult:
        """
        Setup lighting in scene.

        Args:
            lights: List of light configurations

        Returns:
            BlenderExecutionResult

        Example:
            >>> lights = [
            ...     LightConfig(type="SUN", energy=2.0),
            ...     LightConfig(type="POINT", location=(5, 5, 5), energy=1000)
            ... ]
            >>> result = wrapper.setup_lighting(lights)
        """
        lights_config = []
        for i, light in enumerate(lights):
            lights_config.append(f"""
# Light {i}
light_data_{i} = bpy.data.lights.new(name='Light_{i}', type='{light.type}')
light_obj_{i} = bpy.data.objects.new('Light_{i}', light_data_{i})
bpy.context.scene.collection.objects.link(light_obj_{i})

light_obj_{i}.location = {light.location}
light_data_{i}.energy = {light.energy}
light_data_{i}.color = {light.color}
light_data_{i}.use_shadow = {light.use_shadow}

if '{light.type}' in ['POINT', 'SPOT', 'AREA']:
    light_data_{i}.shadow_soft_size = {light.size}

if '{light.type}' == 'SPOT' and {light.angle is not None}:
    light_data_{i}.spot_size = {light.angle}

print(f"Created {{'{light.type}'}} light at {light.location}")
""")

        script = f"""
import bpy

# Remove existing lights
for obj in bpy.data.objects:
    if obj.type == 'LIGHT':
        bpy.data.objects.remove(obj, do_unlink=True)

{''.join(lights_config)}

print(f"Setup {len(lights)} lights")
"""
        return self.execute_in_blender(script)

    def render_scene(
        self,
        config: RenderConfig,
        blend_file: Optional[str] = None
    ) -> BlenderExecutionResult:
        """
        Render current scene with specified settings.

        Args:
            config: Render configuration
            blend_file: Optional .blend file to render

        Returns:
            BlenderExecutionResult

        Example:
            >>> render_config = RenderConfig(
            ...     engine=BlenderEngine.CYCLES,
            ...     samples=256,
            ...     resolution_x=1920,
            ...     resolution_y=1080,
            ...     output_path="/tmp/render.png"
            ... )
            >>> result = wrapper.render_scene(render_config)
        """
        output_path = config.output_path or "/tmp/render.png"

        script = f"""
import bpy

scene = bpy.context.scene

# Render engine
scene.render.engine = '{config.engine.value}'

# Resolution
scene.render.resolution_x = {config.resolution_x}
scene.render.resolution_y = {config.resolution_y}
scene.render.resolution_percentage = 100

# Samples
if scene.render.engine == 'CYCLES':
    scene.cycles.samples = {config.samples}
    scene.cycles.use_denoising = {config.use_denoising}
    scene.cycles.device = '{config.device}'
elif scene.render.engine == 'BLENDER_EEVEE':
    scene.eevee.taa_render_samples = {config.samples}

# Output
scene.render.filepath = '{output_path}'
scene.render.image_settings.file_format = '{config.file_format}'
scene.render.image_settings.color_mode = '{config.color_mode}'
scene.render.film_transparent = {config.transparent}

# Render
bpy.ops.render.render(write_still=True)

print(f"Render complete: {output_path}")
"""
        return self.execute_in_blender(script, blend_file=blend_file)

    def batch_operations(
        self,
        operations: List[str],
        blend_file: Optional[str] = None
    ) -> BlenderExecutionResult:
        """
        Execute multiple operations in batch.

        Args:
            operations: List of Python code snippets to execute
            blend_file: Optional .blend file to work with

        Returns:
            BlenderExecutionResult

        Example:
            >>> ops = [
            ...     "bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0))",
            ...     "bpy.ops.mesh.primitive_sphere_add(location=(3, 0, 0))",
            ...     "bpy.ops.mesh.primitive_cylinder_add(location=(6, 0, 0))"
            ... ]
            >>> result = wrapper.batch_operations(ops)
        """
        script = f"""
import bpy

operations = {operations}

for i, op in enumerate(operations):
    try:
        exec(op)
        print(f"Operation {{i+1}}/{{len(operations)}} completed")
    except Exception as e:
        print(f"Operation {{i+1}} failed: {{e}}")

print(f"Batch operations complete: {{len(operations)}} operations")
"""
        return self.execute_in_blender(script, blend_file=blend_file)


# Convenience functions

def get_blender_version(blender_path: Optional[str] = None) -> Dict[str, Any]:
    """Get Blender version information."""
    wrapper = BlenderAPIWrapper(blender_path=blender_path)
    return wrapper.get_blender_version()


def execute_in_blender(
    script: str,
    blender_path: Optional[str] = None,
    **kwargs
) -> BlenderExecutionResult:
    """Execute script in Blender (convenience function)."""
    wrapper = BlenderAPIWrapper(blender_path=blender_path)
    return wrapper.execute_in_blender(script, **kwargs)


# Example usage
if __name__ == "__main__":
    # Initialize wrapper
    wrapper = BlenderAPIWrapper()

    # Get version
    version = wrapper.get_blender_version()
    print(f"Blender version: {version['version_string']}")

    # Create simple scene
    script = """
import bpy

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create objects
bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0))
bpy.ops.mesh.primitive_uv_sphere_add(location=(3, 0, 0))
bpy.ops.mesh.primitive_cylinder_add(location=(-3, 0, 0))

print("Scene created with 3 objects")
"""

    result = wrapper.execute_in_blender(script)
    print(f"Execution: {'Success' if result.success else 'Failed'}")
    print(f"Time: {result.execution_time:.2f}s")

    # Setup camera
    cam_config = CameraConfig(location=(10, -10, 8))
    wrapper.setup_camera(cam_config)

    # Setup lighting
    lights = [
        LightConfig(type="SUN", energy=2.0),
        LightConfig(type="POINT", location=(5, -5, 5), energy=1000)
    ]
    wrapper.setup_lighting(lights)

    # Create material
    mat_config = MaterialConfig(
        name="BlueMetal",
        base_color=(0.2, 0.4, 0.8, 1.0),
        metallic=0.9,
        roughness=0.1
    )
    wrapper.create_material(mat_config, target_object="Cube")

    print("Blender API tools demonstration complete")
