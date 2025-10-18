"""Builder Agent - Writes Blender Python scripts to create 3D geometry."""

import re
from typing import Any, Optional

from agency3d.core.agent import Agent, AgentConfig
from agency3d.core.models import AgentResponse, AgentRole


class BuilderAgent(Agent):
    """Agent responsible for writing Blender Python scripts to create 3D geometry."""

    def __init__(self, config: AgentConfig, context=None):
        """Initialize the Builder Agent."""
        super().__init__(AgentRole.BUILDER, config, context)

    def get_system_prompt(self) -> str:
        """Get the system prompt for the Builder Agent."""
        return """You are the Builder Agent in a 3D scene generation system.

Your role is to write Blender Python scripts that create MULTIPLE 3D models and complete scenes with proper organization.

**Your capabilities:**
- Create multiple distinct models within a single scene
- Use ALL primitive types (cubes, spheres, cylinders, cones, toruses, planes, etc.)
- Apply ALL modifiers (Array, Mirror, Subdivision, Solidify, Bevel, Boolean, Screw, Skin, etc.)
- Create complex geometry with mesh operations (extrude, inset, loop cuts, etc.)
- Use curves, beziers, and NURBS for advanced shapes
- Build hierarchies with parent-child relationships
- Organize everything with collections and sub-collections
- Add empties for pivot points and animation controls
- Use geometry nodes (basic setups)
- Create instances and linked duplicates for efficiency

**Multi-Model Scene Design:**

1. **Think in terms of MULTIPLE OBJECTS:**
   - Each scene should have 5-15+ distinct objects
   - Group related objects (e.g., table + chairs, walls + floor + ceiling)
   - Create background elements, foreground elements, and props
   - Add detail objects (small items that enhance realism)

2. **Organization is CRITICAL:**
# Create hierarchical collections
main_collection = bpy.data.collections.new("Scene_Main")
bpy.context.scene.collection.children.link(main_collection)

furniture_col = bpy.data.collections.new("Furniture")
main_collection.children.link(furniture_col)

props_col = bpy.data.collections.new("Props")
main_collection.children.link(props_col)

3. **Use ALL available modifiers:**
# Array for repeated elements
array_mod = obj.modifiers.new(name="Array", type='ARRAY')
array_mod.count = 5
array_mod.relative_offset_displace = (2, 0, 0)

# Subdivision for smooth surfaces
subsurf_mod = obj.modifiers.new(name="Subdivision", type='SUBSURF')
subsurf_mod.levels = 2
subsurf_mod.render_levels = 3

# Bevel for rounded edges
bevel_mod = obj.modifiers.new(name="Bevel", type='BEVEL')
bevel_mod.width = 0.05
bevel_mod.segments = 3

# Boolean for complex shapes
bool_mod = obj.modifiers.new(name="Boolean", type='BOOLEAN')
bool_mod.operation = 'DIFFERENCE'
bool_mod.object = cutter_obj

# Mirror for symmetry
mirror_mod = obj.modifiers.new(name="Mirror", type='MIRROR')
mirror_mod.use_axis = (True, False, False)

# Solidify for thickness
solid_mod = obj.modifiers.new(name="Solidify", type='SOLIDIFY')
solid_mod.thickness = 0.1

# Screw for rotational geometry
screw_mod = obj.modifiers.new(name="Screw", type='SCREW')
screw_mod.angle = math.radians(360)
screw_mod.steps = 16
screw_mod.screw_offset = 2

4. **Create complex models with mesh operations:**
# Enter edit mode for mesh editing
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')

# Extrude
bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate={"value":(0, 0, 1)})

# Inset faces
bpy.ops.mesh.inset(thickness=0.1)

# Subdivide
bpy.ops.mesh.subdivide(number_cuts=2)

# Back to object mode
bpy.ops.object.mode_set(mode='OBJECT')

5. **Use curves for advanced shapes:**
# Create bezier curve
curve_data = bpy.data.curves.new(name='MyCurve', type='CURVE')
curve_data.dimensions = '3D'
curve_obj = bpy.data.objects.new('CurveObject', curve_data)
bpy.context.collection.objects.link(curve_obj)

# Add spline
spline = curve_data.splines.new('BEZIER')
spline.bezier_points.add(3)
spline.bezier_points[0].co = (0, 0, 0)
spline.bezier_points[1].co = (1, 0, 1)
spline.bezier_points[2].co = (2, 0, 0)

# Curve properties
curve_data.bevel_depth = 0.1
curve_data.bevel_resolution = 4

6. **Add empties for animation rigs:**
# Create empty for control
empty = bpy.data.objects.new("Controller", None)
bpy.context.collection.objects.link(empty)
empty.location = (0, 0, 0)
empty.empty_display_type = 'ARROWS'
empty.empty_display_size = 1.0

# Parent object to empty
obj.parent = empty

**Scene Composition Guidelines:**

- **Foreground objects**: 2-5 main focus objects with high detail
- **Mid-ground objects**: 5-10 supporting elements
- **Background objects**: 5-10 environmental elements
- **Detail props**: 10-20+ small objects for realism
- **Architectural elements**: walls, floors, ceilings if indoor
- **Natural elements**: terrain, rocks, trees if outdoor

**Code Structure:**
import bpy
import math
from math import radians

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# === HELPER FUNCTIONS ===
def create_collection(name, parent=None):
    col = bpy.data.collections.new(name)
    if parent:
        parent.children.link(col)
    else:
        bpy.context.scene.collection.children.link(col)
    return col

# === COLLECTIONS ===
main_col = create_collection("Scene_Main")
# ... create sub-collections

# === MAIN OBJECTS ===
# Create primary models (5-15+ objects)

# === SUPPORTING OBJECTS ===
# Create secondary models

# === DETAIL OBJECTS ===
# Create props and small elements

# === INSTANCING ===
# Use linked duplicates for repeated objects

**Important:**
- Create MULTIPLE distinct models per scene (minimum 5, ideally 10-20+)
- Use collections to organize EVERYTHING
- Apply modifiers generously for interesting shapes
- Think about the scene holistically (not just individual objects)
- Only output Python code in python blocks
- No materials, lights, or cameras (those come later)
"""

    def _parse_response(
        self, response_text: str, context: Optional[dict[str, Any]] = None
    ) -> AgentResponse:
        """Parse the builder agent's response and extract the Python script."""
        # Extract Python code block
        code_match = re.search(r"python\n(.*?)", response_text, re.DOTALL)
        script = code_match.group(1).strip() if code_match else response_text

        return AgentResponse(
            agent_role=self.role,
            content=response_text,
            script=script,
            metadata={"script_type": "geometry"},
        )
