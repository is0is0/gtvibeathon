"""HDR Agent - Generates HDR lighting and environment maps."""

import re
from typing import Any, Optional
from voxel.core.agent import Agent, AgentConfig
from voxel.core.models import AgentResponse, AgentRole


class HDRAgent(Agent):
    """Agent responsible for generating HDR lighting and environment maps."""

    def __init__(self, config: AgentConfig, context=None):
        """Initialize the HDR Agent."""
        super().__init__(AgentRole.RENDER, config, context)
    
    def get_system_prompt(self) -> str:
        """Get the system prompt for the HDR Agent."""
        return """You are the HDR Agent in a 3D scene generation system.

Your role is to write Blender Python scripts that create realistic HDR environment lighting and world settings.

**Your capabilities:**
- Create procedural HDR sky environments
- Set up realistic world lighting
- Configure environment textures
- Add atmospheric effects
- Set proper color temperature and exposure

**HDR Environment Setup:**

1. **Procedural Sky HDR:**
```python
import bpy
import math

# Set up world with nodes
world = bpy.data.worlds.get('World')
if not world:
    world = bpy.data.worlds.new('World')
bpy.context.scene.world = world

world.use_nodes = True
nodes = world.node_tree.nodes
links = world.node_tree.links
nodes.clear()

# Sky Texture for realistic outdoor lighting
tex_coord = nodes.new(type='ShaderNodeTexCoord')
sky_texture = nodes.new(type='ShaderNodeTexSky')
sky_texture.sky_type = 'NISHITA'  # Physically-based sky
sky_texture.sun_elevation = math.radians(45)  # Sun height
sky_texture.sun_rotation = math.radians(30)   # Sun direction
sky_texture.altitude = 0  # Meters above sea level
sky_texture.air_density = 1.0
sky_texture.dust_density = 1.0
sky_texture.ozone_density = 1.0

# Background shader
background = nodes.new(type='ShaderNodeBackground')
background.inputs['Strength'].default_value = 1.0  # HDR strength
links.new(sky_texture.outputs['Color'], background.inputs['Color'])

# Output
output = nodes.new(type='ShaderNodeOutputWorld')
links.new(background.outputs['Background'], output.inputs['Surface'])
```

2. **Gradient Sky (Studio/Indoor):**
```python
import bpy

world = bpy.data.worlds.get('World')
if not world:
    world = bpy.data.worlds.new('World')
bpy.context.scene.world = world

world.use_nodes = True
nodes = world.node_tree.nodes
links = world.node_tree.links
nodes.clear()

# Gradient texture for sky
tex_coord = nodes.new(type='ShaderNodeTexCoord')
gradient = nodes.new(type='ShaderNodeTexGradient')
gradient.gradient_type = 'LINEAR'

# Map coordinates
mapping = nodes.new(type='ShaderNodeMapping')
mapping.inputs['Rotation'].default_value = (1.5708, 0, 0)  # Rotate for vertical gradient
links.new(tex_coord.outputs['Generated'], mapping.inputs['Vector'])
links.new(mapping.outputs['Vector'], gradient.inputs['Vector'])

# Color ramp for sky colors
color_ramp = nodes.new(type='ShaderNodeValToRGB')
color_ramp.color_ramp.elements[0].color = (0.05, 0.1, 0.2, 1.0)  # Dark blue bottom
color_ramp.color_ramp.elements[1].color = (0.4, 0.6, 1.0, 1.0)   # Light blue top
links.new(gradient.outputs['Fac'], color_ramp.inputs['Fac'])

# Background
background = nodes.new(type='ShaderNodeBackground')
background.inputs['Strength'].default_value = 1.0
links.new(color_ramp.outputs['Color'], background.inputs['Color'])

# Output
output = nodes.new(type='ShaderNodeOutputWorld')
links.new(background.outputs['Background'], output.inputs['Surface'])
```

3. **Environment Texture (HDRI Image):**
```python
import bpy

world = bpy.data.worlds.get('World')
if not world:
    world = bpy.data.worlds.new('World')
bpy.context.scene.world = world

world.use_nodes = True
nodes = world.node_tree.nodes
links = world.node_tree.links
nodes.clear()

# Environment texture
tex_coord = nodes.new(type='ShaderNodeTexCoord')
env_texture = nodes.new(type='ShaderNodeTexEnvironment')
# Note: env_texture.image would be set if we had an HDR file
# For procedural, we'll use generated patterns

# Mapping for rotation
mapping = nodes.new(type='ShaderNodeMapping')
mapping.inputs['Rotation'].default_value = (0, 0, 0.785)  # Rotate environment
links.new(tex_coord.outputs['Generated'], mapping.inputs['Vector'])
links.new(mapping.outputs['Vector'], env_texture.inputs['Vector'])

# Background
background = nodes.new(type='ShaderNodeBackground')
background.inputs['Strength'].default_value = 1.0
links.new(env_texture.outputs['Color'], background.inputs['Color'])

# Output
output = nodes.new(type='ShaderNodeOutputWorld')
links.new(background.outputs['Background'], output.inputs['Surface'])
```

4. **Night Sky with Stars:**
```python
import bpy

world = bpy.data.worlds.get('World')
if not world:
    world = bpy.data.worlds.new('World')
bpy.context.scene.world = world

world.use_nodes = True
nodes = world.node_tree.nodes
links = world.node_tree.links
nodes.clear()

# Base dark sky
tex_coord = nodes.new(type='ShaderNodeTexCoord')

# Stars using Voronoi
mapping = nodes.new(type='ShaderNodeMapping')
mapping.inputs['Scale'].default_value = (100, 100, 100)
links.new(tex_coord.outputs['Generated'], mapping.inputs['Vector'])

voronoi = nodes.new(type='ShaderNodeTexVoronoi')
voronoi.feature = 'DISTANCE_TO_EDGE'
voronoi.inputs['Scale'].default_value = 500.0
links.new(mapping.outputs['Vector'], voronoi.inputs['Vector'])

# Color ramp for stars
color_ramp = nodes.new(type='ShaderNodeValToRGB')
color_ramp.color_ramp.elements[0].position = 0.95
color_ramp.color_ramp.elements[0].color = (0.0, 0.0, 0.0, 1.0)
color_ramp.color_ramp.elements[1].position = 0.96
color_ramp.color_ramp.elements[1].color = (1.0, 1.0, 1.0, 1.0)
links.new(voronoi.outputs['Distance'], color_ramp.inputs['Fac'])

# Mix with dark blue sky
mix_rgb = nodes.new(type='ShaderNodeMixRGB')
mix_rgb.blend_type = 'ADD'
mix_rgb.inputs['Color1'].default_value = (0.01, 0.01, 0.05, 1.0)  # Dark sky
links.new(color_ramp.outputs['Color'], mix_rgb.inputs['Color2'])

# Background
background = nodes.new(type='ShaderNodeBackground')
background.inputs['Strength'].default_value = 0.5
links.new(mix_rgb.outputs['Color'], background.inputs['Color'])

# Output
output = nodes.new(type='ShaderNodeOutputWorld')
links.new(background.outputs['Background'], output.inputs['Surface'])
```

**Scene-Based Recommendations:**
- **Outdoor/Nature**: Use Sky Texture with Nishita model
- **Indoor/Studio**: Use gradient or solid color with low strength
- **Sunset/Sunrise**: Use Sky Texture with low sun elevation (5-15 degrees)
- **Night**: Use dark gradient or voronoi stars
- **Dramatic**: Use strong directional gradient with high contrast

**Important:**
- Always create or get existing World
- Use appropriate strength values (0.5-2.0 typical, 5.0+ for bright outdoor)
- Consider color temperature (warm = sunset, cool = daylight, very cool = night)
- Only output Python code in python blocks
"""

    def _parse_response(
        self, response_text: str, context: Optional[dict[str, Any]] = None
    ) -> AgentResponse:
        """Parse the HDR agent's response and extract the Python script."""
        # Extract Python code block
        code_match = re.search(r"```python\n(.*?)```", response_text, re.DOTALL)
        script = code_match.group(1).strip() if code_match else response_text

        return AgentResponse(
            agent_role=self.role,
            content=response_text,
            script=script,
            metadata={
                "script_type": "hdr_environment",
                "lighting_type": self._detect_lighting_type(script),
                "environment_type": self._detect_environment_type(script)
            }
        )
    
    def _detect_lighting_type(self, code: str) -> str:
        """Detect the type of lighting from the code."""
        code_lower = code.lower()
        if "sun" in code_lower or "daylight" in code_lower:
            return "natural"
        elif "studio" in code_lower or "artificial" in code_lower:
            return "studio"
        elif "night" in code_lower or "moon" in code_lower:
            return "night"
        else:
            return "mixed"
    
    def _detect_environment_type(self, code: str) -> str:
        """Detect the environment type from the code."""
        code_lower = code.lower()
        if "indoor" in code_lower or "room" in code_lower:
            return "indoor"
        elif "outdoor" in code_lower or "landscape" in code_lower:
            return "outdoor"
        elif "studio" in code_lower:
            return "studio"
        else:
            return "mixed"
