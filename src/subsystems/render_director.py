"""
Render Director
--------------
Comprehensive rendering orchestration system for Blender.

Handles camera setup, rendering configuration, multiple camera angles,
preview vs final renders, and export to various formats (PNG, EXR, GLTF).
"""

import math
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum
from utils.logger import get_logger

logger = get_logger(__name__)


class RenderEngine(str, Enum):
    """Supported render engines."""
    CYCLES = "CYCLES"
    EEVEE = "BLENDER_EEVEE"
    WORKBENCH = "BLENDER_WORKBENCH"


class ExportFormat(str, Enum):
    """Supported export formats."""
    PNG = "PNG"
    JPEG = "JPEG"
    EXR = "OPEN_EXR"
    TIFF = "TIFF"
    GLTF = "GLTF"
    GLB = "GLB"
    FBX = "FBX"
    OBJ = "OBJ"


class RenderQuality(str, Enum):
    """Render quality presets."""
    DRAFT = "draft"          # Fast preview, low samples
    PREVIEW = "preview"      # Medium quality for testing
    FINAL = "final"          # High quality for final output
    ULTRA = "ultra"          # Maximum quality, very slow


@dataclass
class CameraConfig:
    """Configuration for a camera."""
    name: str
    location: Tuple[float, float, float] = (7.0, -7.0, 5.0)
    rotation: Tuple[float, float, float] = (math.radians(60), 0, math.radians(45))
    lens: float = 50.0                    # Focal length in mm
    sensor_width: float = 36.0            # Sensor width in mm
    clip_start: float = 0.1
    clip_end: float = 100.0
    dof_enabled: bool = False             # Depth of field
    dof_focus_distance: float = 10.0
    dof_aperture: float = 2.8             # F-stop value


@dataclass
class RenderSettings:
    """Configuration for render settings."""
    engine: RenderEngine = RenderEngine.CYCLES
    quality: RenderQuality = RenderQuality.PREVIEW
    resolution: Tuple[int, int] = (1920, 1080)
    samples: Optional[int] = None         # Auto-determined from quality if None
    use_denoising: bool = True
    transparent_background: bool = False
    color_mode: str = "RGBA"              # RGB or RGBA
    file_format: ExportFormat = ExportFormat.PNG
    color_depth: str = "8"                # 8, 16, or 32 bits
    compression: int = 15                 # 0-100 for JPEG/PNG


class RenderDirector:
    """
    Orchestrates rendering pipeline with advanced camera and render management.

    Features:
    - Multiple camera angles and configurations
    - Preview vs final render modes
    - Support for PNG, EXR, GLTF, and other export formats
    - Automatic quality presets
    - Render optimization
    """

    # Quality preset configurations
    QUALITY_PRESETS = {
        RenderQuality.DRAFT: {
            'samples': 32,
            'use_denoising': False,
            'resolution_percentage': 50,
            'description': 'Fast preview render'
        },
        RenderQuality.PREVIEW: {
            'samples': 128,
            'use_denoising': True,
            'resolution_percentage': 75,
            'description': 'Medium quality testing'
        },
        RenderQuality.FINAL: {
            'samples': 256,
            'use_denoising': True,
            'resolution_percentage': 100,
            'description': 'High quality final render'
        },
        RenderQuality.ULTRA: {
            'samples': 1024,
            'use_denoising': True,
            'resolution_percentage': 100,
            'description': 'Maximum quality (very slow)'
        }
    }

    # Predefined camera angles for multi-angle rendering
    CAMERA_PRESETS = {
        'front': {
            'location': (0, -10, 3),
            'rotation': (math.radians(80), 0, 0),
            'description': 'Front view'
        },
        'back': {
            'location': (0, 10, 3),
            'rotation': (math.radians(80), 0, math.radians(180)),
            'description': 'Back view'
        },
        'left': {
            'location': (-10, 0, 3),
            'rotation': (math.radians(80), 0, math.radians(-90)),
            'description': 'Left side view'
        },
        'right': {
            'location': (10, 0, 3),
            'rotation': (math.radians(80), 0, math.radians(90)),
            'description': 'Right side view'
        },
        'top': {
            'location': (0, 0, 15),
            'rotation': (0, 0, 0),
            'description': 'Top-down view'
        },
        'perspective': {
            'location': (7, -7, 5),
            'rotation': (math.radians(60), 0, math.radians(45)),
            'description': 'Three-quarter perspective'
        },
        'closeup': {
            'location': (3, -3, 2),
            'rotation': (math.radians(70), 0, math.radians(45)),
            'description': 'Close-up view'
        },
        'wide': {
            'location': (15, -15, 10),
            'rotation': (math.radians(55), 0, math.radians(45)),
            'description': 'Wide establishing shot'
        }
    }

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize Render Director.

        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.default_engine = RenderEngine(
            self.config.get('default_engine', RenderEngine.CYCLES.value)
        )
        self.default_quality = RenderQuality(
            self.config.get('default_quality', RenderQuality.PREVIEW.value)
        )
        self.default_resolution = tuple(
            self.config.get('default_resolution', (1920, 1080))
        )

        # Track cameras created
        self.cameras: List[CameraConfig] = []
        self.active_camera: Optional[str] = None

        logger.info(
            f"Render Director initialized (engine: {self.default_engine.value}, "
            f"quality: {self.default_quality.value})"
        )

    def setup_camera(
        self,
        scene_context: Dict[str, Any],
        camera_name: str = "Camera",
        preset: Optional[str] = None,
        **kwargs
    ) -> CameraConfig:
        """
        Setup camera for scene rendering.

        Args:
            scene_context: Scene data with bounds and objects
            camera_name: Name for the camera
            preset: Optional camera preset name ('front', 'perspective', etc.)
            **kwargs: Override camera configuration parameters

        Returns:
            Camera configuration
        """
        logger.info(f"Setting up camera: {camera_name}" + (f" (preset: {preset})" if preset else ""))

        # Get scene bounds for intelligent camera placement
        bounds = scene_context.get('bounds', {})
        center = scene_context.get('center', [0, 0, 0])
        max_dimension = scene_context.get('max_dimension', 10.0)

        # Use preset if specified
        if preset and preset in self.CAMERA_PRESETS:
            preset_config = self.CAMERA_PRESETS[preset]
            location = preset_config['location']
            rotation = preset_config['rotation']
            logger.debug(f"Using preset '{preset}': {preset_config['description']}")
        else:
            # Default intelligent placement based on scene bounds
            distance = max_dimension * 2.0
            location = kwargs.get('location', (
                center[0] + distance * 0.7,
                center[1] - distance * 0.7,
                center[2] + distance * 0.5
            ))
            rotation = kwargs.get('rotation', (math.radians(60), 0, math.radians(45)))

        # Create camera configuration
        camera_config = CameraConfig(
            name=camera_name,
            location=kwargs.get('location', location),
            rotation=kwargs.get('rotation', rotation),
            lens=kwargs.get('lens', 50.0),
            sensor_width=kwargs.get('sensor_width', 36.0),
            clip_start=kwargs.get('clip_start', 0.1),
            clip_end=kwargs.get('clip_end', max(100.0, max_dimension * 10)),
            dof_enabled=kwargs.get('dof_enabled', False),
            dof_focus_distance=kwargs.get('dof_focus_distance', max_dimension),
            dof_aperture=kwargs.get('dof_aperture', 2.8)
        )

        self.cameras.append(camera_config)
        self.active_camera = camera_name

        logger.info(
            f"Camera configured: {camera_name} at {camera_config.location}, "
            f"lens={camera_config.lens}mm"
        )

        return camera_config

    def setup_multi_angle_cameras(
        self,
        scene_context: Dict[str, Any],
        angles: List[str] = ['perspective', 'front', 'top']
    ) -> List[CameraConfig]:
        """
        Setup multiple cameras for different viewing angles.

        Args:
            scene_context: Scene data
            angles: List of camera preset names

        Returns:
            List of camera configurations
        """
        logger.info(f"Setting up {len(angles)} camera angles")

        cameras = []
        for i, angle in enumerate(angles):
            camera_name = f"Camera_{angle.capitalize()}"
            camera = self.setup_camera(
                scene_context,
                camera_name=camera_name,
                preset=angle
            )
            cameras.append(camera)

        logger.info(f"Multi-angle setup complete: {len(cameras)} cameras")
        return cameras

    def render_scene(
        self,
        output_path: str,
        scene_context: Optional[Dict[str, Any]] = None,
        resolution: Tuple[int, int] = (1920, 1080),
        quality: Optional[RenderQuality] = None,
        engine: Optional[RenderEngine] = None,
        file_format: Optional[ExportFormat] = None,
        camera_name: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Render scene to output file.

        Args:
            output_path: Path to save rendered image
            scene_context: Optional scene data for context-aware rendering
            resolution: Output resolution (width, height)
            quality: Render quality preset
            engine: Render engine to use
            file_format: Output file format
            camera_name: Specific camera to use (or active camera)
            **kwargs: Additional render settings

        Returns:
            Render result with metadata
        """
        # Use defaults if not specified
        quality = quality or self.default_quality
        engine = engine or self.default_engine
        file_format = file_format or ExportFormat.PNG

        logger.info(
            f"Rendering scene: {Path(output_path).name} "
            f"[{resolution[0]}x{resolution[1]}, {quality.value}, {engine.value}]"
        )

        # Get quality preset settings
        quality_settings = self.QUALITY_PRESETS[quality]
        samples = kwargs.get('samples', quality_settings['samples'])
        use_denoising = kwargs.get('use_denoising', quality_settings['use_denoising'])

        # Adjust resolution if percentage specified
        res_percentage = quality_settings.get('resolution_percentage', 100)
        if res_percentage != 100:
            resolution = (
                int(resolution[0] * res_percentage / 100),
                int(resolution[1] * res_percentage / 100)
            )
            logger.debug(f"Resolution adjusted to {resolution} ({res_percentage}%)")

        # Create render settings
        render_settings = RenderSettings(
            engine=engine,
            quality=quality,
            resolution=resolution,
            samples=samples,
            use_denoising=use_denoising,
            transparent_background=kwargs.get('transparent_background', False),
            file_format=file_format,
            color_depth=kwargs.get('color_depth', '8'),
            compression=kwargs.get('compression', 15)
        )

        # Determine which camera to use
        camera_to_use = camera_name or self.active_camera or "Camera"

        # Generate Blender script
        render_script = self._generate_render_script(
            output_path,
            render_settings,
            camera_to_use,
            scene_context
        )

        result = {
            'output_path': output_path,
            'resolution': resolution,
            'quality': quality.value,
            'engine': engine.value,
            'format': file_format.value,
            'samples': samples,
            'camera': camera_to_use,
            'script': render_script,
            'settings': {
                'use_denoising': use_denoising,
                'transparent_background': render_settings.transparent_background,
                'color_depth': render_settings.color_depth
            }
        }

        logger.info(f"Render configuration complete: {samples} samples, denoising={use_denoising}")

        return result

    def render_multi_angle(
        self,
        output_dir: str,
        cameras: Optional[List[str]] = None,
        quality: Optional[RenderQuality] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Render scene from multiple camera angles.

        Args:
            output_dir: Directory to save renders
            cameras: List of camera names (or use all if None)
            quality: Render quality
            **kwargs: Additional render settings

        Returns:
            List of render results
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Use all cameras if none specified
        camera_names = cameras or [cam.name for cam in self.cameras]

        logger.info(f"Rendering {len(camera_names)} angles to {output_dir}")

        results = []
        for camera_name in camera_names:
            # Generate output filename
            output_file = output_path / f"render_{camera_name.lower()}.png"

            # Render from this camera
            result = self.render_scene(
                str(output_file),
                camera_name=camera_name,
                quality=quality,
                **kwargs
            )
            results.append(result)

        logger.info(f"Multi-angle render complete: {len(results)} renders")
        return results

    def export_scene(
        self,
        output_path: str,
        export_format: ExportFormat,
        scene_context: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Export scene to various formats (GLTF, FBX, OBJ, etc.).

        Args:
            output_path: Path to save exported file
            export_format: Export format
            scene_context: Optional scene data
            **kwargs: Format-specific export options

        Returns:
            Export result with metadata
        """
        logger.info(f"Exporting scene to {export_format.value}: {Path(output_path).name}")

        # Generate export script based on format
        if export_format in [ExportFormat.GLTF, ExportFormat.GLB]:
            export_script = self._generate_gltf_export_script(output_path, export_format, kwargs)
        elif export_format == ExportFormat.FBX:
            export_script = self._generate_fbx_export_script(output_path, kwargs)
        elif export_format == ExportFormat.OBJ:
            export_script = self._generate_obj_export_script(output_path, kwargs)
        else:
            logger.error(f"Unsupported export format: {export_format}")
            raise ValueError(f"Unsupported export format: {export_format}")

        result = {
            'output_path': output_path,
            'format': export_format.value,
            'script': export_script
        }

        logger.info(f"Export configuration complete: {export_format.value}")

        return result

    def plan_render(self, scene_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Plan rendering strategy based on scene data.

        Analyzes scene and suggests optimal render settings,
        camera placement, and quality settings.

        Args:
            scene_data: Scene data with objects and metadata

        Returns:
            Render plan with recommendations
        """
        logger.info("Planning render strategy")

        # Analyze scene complexity
        num_objects = len(scene_data.get('objects', []))
        has_complex_materials = scene_data.get('has_complex_materials', False)
        has_transparency = scene_data.get('has_transparency', False)
        scene_type = scene_data.get('type', 'general')

        # Determine recommended quality
        if num_objects > 50 or has_complex_materials:
            recommended_quality = RenderQuality.PREVIEW
            logger.debug("Complex scene detected, recommending PREVIEW quality")
        else:
            recommended_quality = RenderQuality.FINAL
            logger.debug("Simple scene, recommending FINAL quality")

        # Determine recommended engine
        if has_transparency or scene_type == 'stylized':
            recommended_engine = RenderEngine.EEVEE
            logger.debug("Transparency/stylized detected, recommending EEVEE")
        else:
            recommended_engine = RenderEngine.CYCLES
            logger.debug("Photorealistic scene, recommending CYCLES")

        # Suggest camera angles based on scene type
        if scene_type == 'product':
            recommended_angles = ['perspective', 'front', 'top', 'closeup']
        elif scene_type == 'environment':
            recommended_angles = ['perspective', 'wide', 'front']
        else:
            recommended_angles = ['perspective', 'front', 'top']

        plan = {
            'recommended_quality': recommended_quality.value,
            'recommended_engine': recommended_engine.value,
            'recommended_angles': recommended_angles,
            'estimated_render_time': self._estimate_render_time(
                num_objects,
                recommended_quality,
                recommended_engine
            ),
            'scene_complexity': {
                'num_objects': num_objects,
                'has_complex_materials': has_complex_materials,
                'has_transparency': has_transparency
            }
        }

        logger.info(
            f"Render plan: {recommended_quality.value} quality, "
            f"{recommended_engine.value} engine, "
            f"{len(recommended_angles)} angles"
        )

        return plan

    def generate_camera_script(self, camera: CameraConfig) -> str:
        """
        Generate Blender Python script to create and configure camera.

        Args:
            camera: Camera configuration

        Returns:
            Blender Python script
        """
        script = f"""
# Camera Setup: {camera.name}
import bpy
import math

# Create or get camera
if '{camera.name}' in bpy.data.objects:
    camera = bpy.data.objects['{camera.name}']
else:
    camera_data = bpy.data.cameras.new(name='{camera.name}')
    camera = bpy.data.objects.new('{camera.name}', camera_data)
    bpy.context.scene.collection.objects.link(camera)

# Position and rotation
camera.location = {camera.location}
camera.rotation_euler = {camera.rotation}

# Camera properties
camera.data.lens = {camera.lens}  # Focal length in mm
camera.data.sensor_width = {camera.sensor_width}
camera.data.clip_start = {camera.clip_start}
camera.data.clip_end = {camera.clip_end}

# Depth of field
camera.data.dof.use_dof = {str(camera.dof_enabled)}
"""

        if camera.dof_enabled:
            script += f"""
camera.data.dof.focus_distance = {camera.dof_focus_distance}
camera.data.dof.aperture_fstop = {camera.dof_aperture}
"""

        script += f"""
# Set as active camera
bpy.context.scene.camera = camera

print(f"Camera '{camera.name}' configured at {camera.location}")
"""

        return script

    # Private helper methods

    def _generate_render_script(
        self,
        output_path: str,
        settings: RenderSettings,
        camera_name: str,
        scene_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate Blender Python script for rendering."""

        # Normalize path for cross-platform compatibility
        output_path = str(Path(output_path).as_posix())

        script = f"""
# Render Setup
import bpy

# Set active camera
if '{camera_name}' in bpy.data.objects:
    bpy.context.scene.camera = bpy.data.objects['{camera_name}']

# Render engine
bpy.context.scene.render.engine = '{settings.engine.value}'

# Resolution
bpy.context.scene.render.resolution_x = {settings.resolution[0]}
bpy.context.scene.render.resolution_y = {settings.resolution[1]}
bpy.context.scene.render.resolution_percentage = 100

# Output settings
bpy.context.scene.render.filepath = '{output_path}'
bpy.context.scene.render.image_settings.file_format = '{settings.file_format.value}'
bpy.context.scene.render.image_settings.color_mode = '{settings.color_mode}'
bpy.context.scene.render.image_settings.color_depth = '{settings.color_depth}'
"""

        # Engine-specific settings
        if settings.engine == RenderEngine.CYCLES:
            script += f"""
# Cycles settings
bpy.context.scene.cycles.samples = {settings.samples}
bpy.context.scene.cycles.use_denoising = {str(settings.use_denoising)}
bpy.context.scene.cycles.denoiser = 'OPTIX'  # Use GPU denoiser if available
"""
        elif settings.engine == RenderEngine.EEVEE:
            script += f"""
# EEVEE settings
bpy.context.scene.eevee.taa_render_samples = {settings.samples}
bpy.context.scene.eevee.use_gtao = True  # Ambient occlusion
bpy.context.scene.eevee.use_bloom = True  # Bloom effect
bpy.context.scene.eevee.use_ssr = True   # Screen space reflections
"""

        # Transparent background
        if settings.transparent_background:
            script += """
# Transparent background
bpy.context.scene.render.film_transparent = True
"""

        # Format-specific settings
        if settings.file_format == ExportFormat.PNG:
            script += f"""
# PNG compression
bpy.context.scene.render.image_settings.compression = {settings.compression}
"""
        elif settings.file_format == ExportFormat.JPEG:
            script += f"""
# JPEG quality
bpy.context.scene.render.image_settings.quality = {settings.compression}
"""
        elif settings.file_format == ExportFormat.EXR:
            script += """
# OpenEXR settings (high dynamic range)
bpy.context.scene.render.image_settings.color_depth = '32'
bpy.context.scene.render.image_settings.exr_codec = 'ZIP'  # Compression
"""

        script += """
# Render the scene
print(f"Rendering to: {bpy.context.scene.render.filepath}")
bpy.ops.render.render(write_still=True)
print("Render complete!")
"""

        return script

    def _generate_gltf_export_script(
        self,
        output_path: str,
        export_format: ExportFormat,
        options: Dict[str, Any]
    ) -> str:
        """Generate GLTF/GLB export script."""

        output_path = str(Path(output_path).as_posix())
        is_glb = export_format == ExportFormat.GLB

        script = f"""
# GLTF Export
import bpy

# Export settings
export_format = '{"GLB" if is_glb else "GLTF_SEPARATE"}'
export_path = '{output_path}'

# Select all objects for export
bpy.ops.object.select_all(action='SELECT')

# Export to GLTF/GLB
bpy.ops.export_scene.gltf(
    filepath=export_path,
    export_format=export_format,
    export_textures={str(options.get('export_textures', True))},
    export_normals={str(options.get('export_normals', True))},
    export_materials={str(options.get('export_materials', 'EXPORT'))},
    export_colors={str(options.get('export_colors', True))},
    export_cameras={str(options.get('export_cameras', False))},
    export_lights={str(options.get('export_lights', False))},
    export_apply={str(options.get('export_apply', False))}
)

print(f"Exported to: {{export_path}}")
"""

        return script

    def _generate_fbx_export_script(
        self,
        output_path: str,
        options: Dict[str, Any]
    ) -> str:
        """Generate FBX export script."""

        output_path = str(Path(output_path).as_posix())

        script = f"""
# FBX Export
import bpy

export_path = '{output_path}'

# Select all objects
bpy.ops.object.select_all(action='SELECT')

# Export to FBX
bpy.ops.export_scene.fbx(
    filepath=export_path,
    use_selection={str(options.get('use_selection', False))},
    use_active_collection={str(options.get('use_active_collection', False))},
    object_types={{'MESH', 'ARMATURE', 'CAMERA', 'LIGHT'}},
    use_mesh_modifiers={str(options.get('apply_modifiers', True))},
    mesh_smooth_type='{options.get('smooth_type', 'FACE')}',
    use_custom_props={str(options.get('custom_props', False))}
)

print(f"Exported to: {{export_path}}")
"""

        return script

    def _generate_obj_export_script(
        self,
        output_path: str,
        options: Dict[str, Any]
    ) -> str:
        """Generate OBJ export script."""

        output_path = str(Path(output_path).as_posix())

        script = f"""
# OBJ Export
import bpy

export_path = '{output_path}'

# Select all mesh objects
bpy.ops.object.select_all(action='DESELECT')
for obj in bpy.data.objects:
    if obj.type == 'MESH':
        obj.select_set(True)

# Export to OBJ
bpy.ops.export_scene.obj(
    filepath=export_path,
    use_selection={str(options.get('use_selection', True))},
    use_materials={str(options.get('export_materials', True))},
    use_triangles={str(options.get('use_triangles', False))},
    use_normals={str(options.get('export_normals', True))},
    use_uvs={str(options.get('export_uvs', True))},
    use_mesh_modifiers={str(options.get('apply_modifiers', True))}
)

print(f"Exported to: {{export_path}}")
"""

        return script

    def _estimate_render_time(
        self,
        num_objects: int,
        quality: RenderQuality,
        engine: RenderEngine
    ) -> str:
        """Estimate render time based on scene complexity."""

        # Very rough estimation
        base_time = 5  # seconds

        # Factor in objects (logarithmic scale)
        object_factor = math.log(max(1, num_objects)) * 2

        # Quality multipliers
        quality_multipliers = {
            RenderQuality.DRAFT: 0.5,
            RenderQuality.PREVIEW: 1.0,
            RenderQuality.FINAL: 3.0,
            RenderQuality.ULTRA: 10.0
        }

        # Engine multipliers
        engine_multipliers = {
            RenderEngine.WORKBENCH: 0.1,
            RenderEngine.EEVEE: 0.3,
            RenderEngine.CYCLES: 1.0
        }

        estimated_seconds = (
            base_time * object_factor *
            quality_multipliers[quality] *
            engine_multipliers[engine]
        )

        # Format as human-readable
        if estimated_seconds < 60:
            return f"~{int(estimated_seconds)}s"
        elif estimated_seconds < 3600:
            return f"~{int(estimated_seconds / 60)}m"
        else:
            hours = int(estimated_seconds / 3600)
            minutes = int((estimated_seconds % 3600) / 60)
            return f"~{hours}h {minutes}m"


# Example usage and testing
if __name__ == "__main__":
    from utils.logger import setup_logging

    # Setup logging
    setup_logging(level="DEBUG", console=True)

    # Create render director
    director = RenderDirector()

    print("\n" + "="*80)
    print("RENDER DIRECTOR - TEST SUITE")
    print("="*80 + "\n")

    # Test scene context
    test_scene = {
        'center': [0, 0, 2],
        'bounds': {'min': [-5, -5, 0], 'max': [5, 5, 4]},
        'max_dimension': 10,
        'objects': [
            {'name': 'cube1'},
            {'name': 'sphere1'},
            {'name': 'cylinder1'}
        ]
    }

    # Test 1: Plan render strategy
    print("\n" + "="*80)
    print("Test 1: Plan Render Strategy")
    print("="*80 + "\n")

    plan = director.plan_render(test_scene)
    print(f"Recommended Quality: {plan['recommended_quality']}")
    print(f"Recommended Engine: {plan['recommended_engine']}")
    print(f"Recommended Angles: {', '.join(plan['recommended_angles'])}")
    print(f"Estimated Time: {plan['estimated_render_time']}")

    # Test 2: Setup single camera
    print("\n" + "="*80)
    print("Test 2: Setup Single Camera")
    print("="*80 + "\n")

    camera = director.setup_camera(test_scene, preset='perspective')
    print(f"Camera: {camera.name}")
    print(f"Location: {camera.location}")
    print(f"Lens: {camera.lens}mm")

    # Test 3: Setup multi-angle cameras
    print("\n" + "="*80)
    print("Test 3: Setup Multi-Angle Cameras")
    print("="*80 + "\n")

    cameras = director.setup_multi_angle_cameras(test_scene, ['front', 'top', 'perspective'])
    for cam in cameras:
        print(f"  - {cam.name} at {cam.location}")

    # Test 4: Render configuration
    print("\n" + "="*80)
    print("Test 4: Render Configuration")
    print("="*80 + "\n")

    render_result = director.render_scene(
        "output/test_render.png",
        scene_context=test_scene,
        quality=RenderQuality.PREVIEW,
        resolution=(1920, 1080)
    )
    print(f"Output: {render_result['output_path']}")
    print(f"Resolution: {render_result['resolution']}")
    print(f"Samples: {render_result['samples']}")
    print(f"Engine: {render_result['engine']}")

    # Test 5: Export configuration
    print("\n" + "="*80)
    print("Test 5: Export Configuration")
    print("="*80 + "\n")

    export_result = director.export_scene(
        "output/scene.gltf",
        ExportFormat.GLTF,
        scene_context=test_scene
    )
    print(f"Export to: {export_result['output_path']}")
    print(f"Format: {export_result['format']}")

    # Test 6: Generate camera script
    print("\n" + "="*80)
    print("Test 6: Generate Camera Script")
    print("="*80 + "\n")

    camera_script = director.generate_camera_script(cameras[0])
    print("Generated Blender script (first 300 chars):")
    print(camera_script[:300])

    print("\n" + "="*80)
    print("TEST SUITE COMPLETE")
    print("="*80 + "\n")
