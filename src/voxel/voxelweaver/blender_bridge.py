"""
Blender Bridge - Integration utilities for Blender Python API.
Provides helpers for translating VoxelWeaver data into Blender operations.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple

logger = logging.getLogger(__name__)


class BlenderBridge:
    """
    Utilities for bridging VoxelWeaver data structures to Blender operations.
    Generates code snippets and data formats compatible with Blender Python API.
    """

    def __init__(self):
        """Initialize Blender bridge."""
        logger.info("BlenderBridge initialized")

    def generate_object_creation_code(
        self,
        geometry_hints: Dict[str, Any]
    ) -> str:
        """
        Generate Blender Python code for creating objects based on geometry hints.

        Args:
            geometry_hints: Geometry hints from GeometryHandler

        Returns:
            Python code string for Blender
        """
        code_lines = [
            "import bpy",
            "import math",
            "",
            "# Clear existing objects",
            "bpy.ops.object.select_all(action='SELECT')",
            "bpy.ops.object.delete()",
            ""
        ]

        hints = geometry_hints.get("geometry_hints", [])

        for hint in hints:
            obj_name = hint.get("object_name", "object")
            primitive = hint.get("base_primitive", "cube")
            modifiers = hint.get("modifiers", [])
            subdiv_level = hint.get("subdivision_level", 0)

            # Add object creation code
            code_lines.append(f"# Create {obj_name}")
            code_lines.extend(self._generate_primitive_code(primitive, obj_name))

            # Add modifiers
            if modifiers:
                for modifier in modifiers:
                    code_lines.extend(self._generate_modifier_code(modifier, obj_name, subdiv_level))

            code_lines.append("")

        return "\n".join(code_lines)

    def generate_material_code(
        self,
        material_suggestions: Dict[str, Any]
    ) -> str:
        """
        Generate Blender Python code for materials.

        Args:
            material_suggestions: Material suggestions from TextureMapper

        Returns:
            Python code string for materials
        """
        code_lines = [
            "import bpy",
            "",
            "# Material setup",
            ""
        ]

        materials = material_suggestions.get("materials", [])

        for mat in materials:
            mat_name = mat.get("material_name", "Material")
            obj_type = mat.get("object_type", "object")
            base_color = mat.get("base_color", (0.8, 0.8, 0.8))
            roughness = mat.get("roughness", 0.5)
            metallic = mat.get("metallic", 0.0)
            transmission = mat.get("transmission", 0.0)

            code_lines.append(f"# Material for {obj_type}")
            code_lines.append(f"mat = bpy.data.materials.new(name='{mat_name}')")
            code_lines.append("mat.use_nodes = True")
            code_lines.append("nodes = mat.node_tree.nodes")
            code_lines.append("links = mat.node_tree.links")
            code_lines.append("nodes.clear()")
            code_lines.append("")

            # Principled BSDF
            code_lines.append("# Principled BSDF")
            code_lines.append("bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')")
            code_lines.append(f"bsdf.inputs['Base Color'].default_value = {base_color + (1.0,)}")
            code_lines.append(f"bsdf.inputs['Roughness'].default_value = {roughness}")
            code_lines.append(f"bsdf.inputs['Metallic'].default_value = {metallic}")

            if transmission > 0:
                code_lines.append(f"bsdf.inputs['Transmission'].default_value = {transmission}")

            code_lines.append("")

            # Output
            code_lines.append("# Material output")
            code_lines.append("output = nodes.new(type='ShaderNodeOutputMaterial')")
            code_lines.append("links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])")
            code_lines.append("")

        return "\n".join(code_lines)

    def generate_lighting_code(
        self,
        lighting_config: Dict[str, Any]
    ) -> str:
        """
        Generate Blender Python code for lighting.

        Args:
            lighting_config: Lighting configuration from LightingEngine

        Returns:
            Python code string for lights
        """
        code_lines = [
            "import bpy",
            "import math",
            "",
            "# Lighting setup",
            ""
        ]

        lights = lighting_config.get("lights", [])

        for light in lights:
            light_name = light.get("name", "Light")
            light_type = light.get("type", "point").upper()
            energy = light.get("energy", 1000)
            color = light.get("color", (1.0, 1.0, 1.0))
            position = light.get("position", (0, 0, 5))
            size = light.get("size", 1.0)

            code_lines.append(f"# {light_name} light")
            code_lines.append(f"light_data = bpy.data.lights.new(name='{light_name}', type='{light_type}')")
            code_lines.append(f"light_data.energy = {energy}")
            code_lines.append(f"light_data.color = {color}")

            if light_type == "AREA":
                code_lines.append(f"light_data.size = {size}")

            code_lines.append(f"light_obj = bpy.data.objects.new(name='{light_name}', object_data=light_data)")
            code_lines.append(f"light_obj.location = {position}")
            code_lines.append("bpy.context.collection.objects.link(light_obj)")
            code_lines.append("")

        # Ambient lighting
        ambient = lighting_config.get("ambient", {})
        if ambient.get("enabled"):
            strength = ambient.get("strength", 1.0)
            color = ambient.get("color", (1.0, 1.0, 1.0))

            code_lines.append("# Ambient/World lighting")
            code_lines.append("world = bpy.data.worlds.get('World')")
            code_lines.append("if world:")
            code_lines.append("    world.use_nodes = True")
            code_lines.append("    bg = world.node_tree.nodes.get('Background')")
            code_lines.append("    if bg:")
            code_lines.append(f"        bg.inputs['Color'].default_value = {color + (1.0,)}")
            code_lines.append(f"        bg.inputs['Strength'].default_value = {strength}")
            code_lines.append("")

        return "\n".join(code_lines)

    def generate_positioning_code(
        self,
        aligned_objects: List[Dict[str, Any]]
    ) -> str:
        """
        Generate code for positioning objects.

        Args:
            aligned_objects: Objects from ContextAligner

        Returns:
            Python code for positioning
        """
        code_lines = [
            "import bpy",
            "",
            "# Position objects",
            ""
        ]

        for obj_data in aligned_objects:
            obj_name = obj_data.get("name", "object")
            position = obj_data.get("position", (0, 0, 0))
            rotation = obj_data.get("rotation", (0, 0, 0))
            scale = obj_data.get("scale", (1, 1, 1))

            code_lines.append(f"# Position {obj_name}")
            code_lines.append(f"obj = bpy.data.objects.get('{obj_name}')")
            code_lines.append("if obj:")
            code_lines.append(f"    obj.location = {position}")
            code_lines.append(f"    obj.rotation_euler = {rotation}")
            code_lines.append(f"    obj.scale = {scale}")
            code_lines.append("")

        return "\n".join(code_lines)

    def _generate_primitive_code(self, primitive: str, obj_name: str) -> List[str]:
        """Generate code for creating a primitive object."""
        primitive_ops = {
            "cube": f"bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0))",
            "uv_sphere": f"bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(0, 0, 0))",
            "ico_sphere": f"bpy.ops.mesh.primitive_ico_sphere_add(radius=1, location=(0, 0, 0))",
            "cylinder": f"bpy.ops.mesh.primitive_cylinder_add(radius=1, depth=2, location=(0, 0, 0))",
            "cone": f"bpy.ops.mesh.primitive_cone_add(radius1=1, depth=2, location=(0, 0, 0))",
            "torus": f"bpy.ops.mesh.primitive_torus_add(major_radius=1, minor_radius=0.25, location=(0, 0, 0))",
            "plane": f"bpy.ops.mesh.primitive_plane_add(size=2, location=(0, 0, 0))",
        }

        op = primitive_ops.get(primitive, primitive_ops["cube"])

        return [
            op,
            f"obj = bpy.context.active_object",
            f"obj.name = '{obj_name}'"
        ]

    def _generate_modifier_code(
        self,
        modifier: str,
        obj_name: str,
        subdiv_level: int = 0
    ) -> List[str]:
        """Generate code for adding a modifier."""
        code = []

        if modifier == "subdivision_surface":
            code.append(f"# Subdivision Surface for {obj_name}")
            code.append(f"obj = bpy.data.objects.get('{obj_name}')")
            code.append("if obj:")
            code.append("    mod = obj.modifiers.new('Subdivision', 'SUBSURF')")
            code.append(f"    mod.levels = {subdiv_level}")
            code.append(f"    mod.render_levels = {subdiv_level + 1}")

        elif modifier == "bevel":
            code.append(f"# Bevel for {obj_name}")
            code.append(f"obj = bpy.data.objects.get('{obj_name}')")
            code.append("if obj:")
            code.append("    mod = obj.modifiers.new('Bevel', 'BEVEL')")
            code.append("    mod.width = 0.05")
            code.append("    mod.segments = 3")

        elif modifier == "array":
            code.append(f"# Array for {obj_name}")
            code.append(f"obj = bpy.data.objects.get('{obj_name}')")
            code.append("if obj:")
            code.append("    mod = obj.modifiers.new('Array', 'ARRAY')")
            code.append("    mod.count = 3")

        elif modifier == "mirror":
            code.append(f"# Mirror for {obj_name}")
            code.append(f"obj = bpy.data.objects.get('{obj_name}')")
            code.append("if obj:")
            code.append("    mod = obj.modifiers.new('Mirror', 'MIRROR')")
            code.append("    mod.use_axis[0] = True")

        return code

    def format_voxelweaver_data(
        self,
        voxelweaver_result: Dict[str, Any]
    ) -> str:
        """
        Format VoxelWeaver results into a Blender-ready data structure.

        Args:
            voxelweaver_result: Complete VoxelWeaver processing result

        Returns:
            Formatted string for documentation or debugging
        """
        lines = [
            "=== VoxelWeaver Scene Data ===",
            "",
            f"Coherence Score: {voxelweaver_result.get('coherence_score', 0):.2f}",
            f"External References: {len(voxelweaver_result.get('references', []))}",
            "",
        ]

        # Proportions
        proportions = voxelweaver_result.get('proportions', {})
        if proportions:
            lines.append("Proportions:")
            lines.append(f"  Realism Score: {proportions.get('realism_score', 0):.2f}")
            lines.append(f"  Objects Analyzed: {proportions.get('objects_analyzed', 0)}")
            lines.append("")

        # Geometry
        geometry = voxelweaver_result.get('geometry_hints', {})
        if geometry:
            lines.append("Geometry:")
            lines.append(f"  Objects: {geometry.get('objects_count', 0)}")
            lines.append(f"  Total Vertices (est): {geometry.get('total_vertex_estimate', 0):,}")
            lines.append(f"  Complexity: {geometry.get('scene_complexity', 'unknown')}")
            lines.append("")

        # Lighting
        lighting = voxelweaver_result.get('lighting_config', {})
        if lighting:
            lines.append("Lighting:")
            lines.append(f"  Setup: {lighting.get('setup_name', 'unknown')}")
            lines.append(f"  Lights: {len(lighting.get('lights', []))}")
            lines.append(f"  Environment: {lighting.get('environment', 'unknown')}")
            lines.append("")

        # Materials
        textures = voxelweaver_result.get('texture_suggestions', {})
        if textures:
            lines.append("Materials:")
            lines.append(f"  Suggestions: {textures.get('suggestions_count', 0)}")
            lines.append("")

        return "\n".join(lines)

    def validate_blender_compatibility(self, scene_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check if scene data is compatible with Blender.

        Args:
            scene_data: Scene configuration

        Returns:
            Compatibility report
        """
        issues = []
        warnings = []

        # Check geometry hints
        geometry = scene_data.get("geometry_hints", {})
        if geometry:
            total_verts = geometry.get("total_vertex_estimate", 0)
            if total_verts > 10000000:
                warnings.append(f"Very high vertex count ({total_verts:,}) may cause Blender performance issues")

        # Check materials
        materials = scene_data.get("texture_suggestions", {}).get("materials", [])
        for mat in materials:
            if mat.get("transmission", 0) > 0 and mat.get("material_type") != "glass":
                warnings.append(f"Material {mat.get('material_name')} has transmission but isn't glass type")

        # Check lights
        lights = scene_data.get("lighting_config", {}).get("lights", [])
        if not lights:
            issues.append("No lights defined - scene will be dark")

        is_compatible = len(issues) == 0

        return {
            "compatible": is_compatible,
            "issues": issues,
            "warnings": warnings,
            "blender_version_required": "3.0+"
        }
