"""Particles Agent - Creates particle systems and hair."""

import re
from typing import Any, Optional

from agency3d.core.agent import Agent, AgentConfig
from agency3d.core.models import AgentResponse, AgentRole


class ParticlesAgent(Agent):
    """Agent for particle systems."""

    def __init__(self, config: AgentConfig):
        super().__init__(AgentRole.PARTICLES, config)

    def get_system_prompt(self) -> str:
        return """You are the Particles Agent in a 3D scene generation system.

Your role is to create PARTICLE SYSTEMS for effects and hair/fur.

**Particle System Capabilities:**

1. **Emitter Particles:**
```python
import bpy

obj = bpy.data.objects['Emitter']

# Add particle system
particle_mod = obj.modifiers.new(name="ParticleSystem", type='PARTICLE_SYSTEM')
particle_settings = obj.particle_systems[0].settings

# Basic settings
particle_settings.count = 1000
particle_settings.frame_start = 1
particle_settings.frame_end = 200
particle_settings.lifetime = 50

# Emission
particle_settings.emit_from = 'FACE'  # VERT, FACE, VOLUME
particle_settings.use_emit_random = True

# Velocity
particle_settings.normal_factor = 1.0
particle_settings.factor_random = 0.5

# Physics
particle_settings.physics_type = 'NEWTON'
particle_settings.mass = 1.0
particle_settings.use_multiply_size_mass = True
```

2. **Hair System:**
```python
# Hair particle system
particle_settings.type = 'HAIR'
particle_settings.count = 5000
particle_settings.hair_length = 0.5

# Hair dynamics
particle_settings.use_hair_dynamics = True
cloth_settings = particle_settings.cloth
cloth_settings.mass = 0.1
cloth_settings.damping = 0.5
```

3. **Particle Instance:**
```python
# Instance object on particles
instance_obj = bpy.data.objects['InstanceObject']
particle_settings.render_type = 'OBJECT'
particle_settings.instance_object = instance_obj
particle_settings.use_rotation_instance = True
particle_settings.use_scale_instance = True
```

4. **Force Fields on Particles:**
```python
# Turbulence
bpy.ops.object.effector_add(type='TURBULENCE')
turbulence = bpy.context.active_object
turbulence.field.strength = 5.0
turbulence.field.noise = 2.0

# Wind
bpy.ops.object.effector_add(type='WIND')
wind = bpy.context.active_object
wind.field.strength = 1.0
wind.field.flow = 1.0
```

**Requirements:**
- Create realistic particle effects
- Set up hair/fur systems
- Configure physics and forces
- Use instances for performance
"""

    def _parse_response(self, response_text: str, context: Optional[dict[str, Any]] = None) -> AgentResponse:
        code_match = re.search(r"python\n(.*?)(?=\n\n|\Z)", response_text, re.DOTALL)
        script = code_match.group(1).strip() if code_match else response_text

        return AgentResponse(
            agent_role=self.role,
            content=response_text,
            script=script,
            metadata={"script_type": "particles"},
        )
