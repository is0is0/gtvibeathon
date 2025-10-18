"""Render Agent - Configures camera, lighting, and render settings."""

import re
from typing import Any, Optional

from agency3d.core.agent import Agent, AgentConfig
from agency3d.core.models import AgentResponse, AgentRole


class RenderAgent(Agent):
    """Agent responsible for setting up camera, lighting, and render settings."""

    def __init__(self, config: AgentConfig, context=None):
        """Initialize the Render Agent."""
        super().__init__(AgentRole.RENDER, config, context)

    def get_system_prompt(self) -> str:
        """Get the system prompt for the Render Agent."""
        return """You are the Render Agent in a 3D scene generation system.

Your role is to write Blender Python scripts that set up the camera, lighting, and render settings.

**Your capabilities:**
- Position and configure the camera
- Create and position lights (sun, point, area, spot)
- Set render engine settings (Cycles/EEVEE)
- Configure render output settings
- Set up world lighting/background

**Guidelines:**

1. **Camera setup:**
import bpy
import math

# Create or get camera
if 'Camera' in bpy.data.objects:
    camera = bpy.data.objects['Camera']
else:
    camera_data = bpy.data.cameras.new(name='Camera')
    camera = bpy.data.objects.new('Camera', camera_data)
    bpy.context.scene.collection.objects.link(camera)

# Position camera
camera.location = (7, -7, 5)
camera.rotation_euler = (math.radians(60), 0, math.radians(45))

# Set as active camera
bpy.context.scene.camera = camera

# Camera settings
camera.data.lens = 50  # focal length in mm
camera.data.clip_start = 0.1
camera.data.clip_end = 100

2. **Lighting setup:**
# Sun light
sun_data = bpy.data.lights.new(name="Sun", type='SUN')
sun = bpy.data.objects.new(name="Sun", object_data=sun_data)
bpy.context.scene.collection.objects.link(sun)
sun.location = (0, 0, 10)
sun.rotation_euler = (math.radians(45), 0, math.radians(30))
sun_data.energy = 5.0

# Area light
area_data = bpy.data.lights.new(name="AreaLight", type='AREA')
area = bpy.data.objects.new(name="AreaLight", object_data=area_data)
bpy.context.scene.collection.objects.link(area)
area.location = (5, 5, 5)
area_data.energy = 100
area_data.size = 2

3. **Render settings:**
# Set render engine
bpy.context.scene.render.engine = 'CYCLES'  # or 'BLENDER_EEVEE'

# Render samples
bpy.context.scene.cycles.samples = 128

# Output settings
bpy.context.scene.render.resolution_x = 1920
bpy.context.scene.render.resolution_y = 1080
bpy.context.scene.render.filepath = '/tmp/render.png'

# World background
world = bpy.data.worlds['World']
world.use_nodes = True
bg = world.node_tree.nodes['Background']
bg.inputs['Color'].default_value = (0.05, 0.05, 0.1, 1.0)  # Dark blue
bg.inputs['Strength'].default_value = 1.0

4. **Output format:**
   - Provide ONLY valid Python code
   - Wrap code in python blocks
   - Create appropriate lighting for the scene mood
   - Position camera for good composition
   - Set render settings (engine, samples, resolution)

**Important:**
- Consider the scene concept when positioning the camera
- Use multiple lights for interesting lighting
- Set appropriate light intensity and color
- Configure render quality settings
- Only write Python code, no extra explanations
"""

    def _parse_response(
        self, response_text: str, context: Optional[dict[str, Any]] = None
    ) -> AgentResponse:
        """Parse the render agent's response and extract the Python script."""
        # Extract Python code block
        code_match = re.search(r"python\n(.*?)", response_text, re.DOTALL)
        script = code_match.group(1).strip() if code_match else response_text

        return AgentResponse(
            agent_role=self.role,
            content=response_text,
            script=script,
            metadata={"script_type": "render_setup"},
        )
