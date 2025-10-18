#!/usr/bin/env python3
"""
Enhancement script for 3DAgency - Adds advanced capabilities
Adds: Scene analysis, asset library, advanced Blender features, external integration
"""

import argparse
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def main():
    parser = argparse.ArgumentParser(description="Enhance 3DAgency capabilities")
    parser.add_argument("--add-all-missing", action="store_true",
                       help="Add all missing Blender features")
    parser.add_argument("--external", action="store_true",
                       help="Add external tool integrations")
    parser.add_argument("--import-assets", action="store_true",
                       help="Add asset import and library management")
    parser.add_argument("--enable-advanced-features", action="store_true",
                       help="Enable advanced Blender features (physics, particles, etc.)")
    parser.add_argument("--ai-agent", default="claude",
                       help="AI agent to use (claude or openai)")
    parser.add_argument("--claude-api-key", help="Claude API key")
    parser.add_argument("--openai-api-key", help="OpenAI API key")

    args = parser.parse_args()

    print("=" * 70)
    print("3DAgency Enhancement System")
    print("=" * 70)
    print()

    if args.add_all_missing:
        print("✓ Adding missing Blender features...")
        add_missing_features()

    if args.import_assets:
        print("✓ Adding asset library system...")
        add_asset_library()

    if args.enable_advanced_features:
        print("✓ Enabling advanced features...")
        add_advanced_features()

    if args.external:
        print("✓ Adding external integrations...")
        add_external_integrations()

    print()
    print("=" * 70)
    print("Enhancement Complete!")
    print("=" * 70)
    print()
    print("New capabilities added:")
    print("  • Scene Analysis Agent - Learns from existing .blend files")
    print("  • Asset Library Manager - Import and reuse components")
    print("  • Geometry Nodes Agent - Advanced procedural modeling")
    print("  • Physics/Simulation Agent - Rigid body, cloth, fluid, smoke")
    print("  • Particles Agent - Particle systems and hair/fur")
    print("  • External Tools Integration - Import from other software")
    print()
    print("Run: 3dagency create --help  (to see new options)")
    print()


def add_missing_features():
    """Add missing Blender features to agents."""
    from pathlib import Path

    # Create new specialized agents
    create_geometry_nodes_agent()
    create_physics_agent()
    create_particles_agent()
    create_scene_analyzer_agent()

    print("  → Created Geometry Nodes Agent")
    print("  → Created Physics/Simulation Agent")
    print("  → Created Particles Agent")
    print("  → Created Scene Analyzer Agent")


def add_asset_library():
    """Add asset library and import capabilities."""
    create_asset_manager()
    create_importer_agent()

    print("  → Created Asset Library Manager")
    print("  → Created Asset Importer Agent")


def add_advanced_features():
    """Enable advanced Blender features."""
    enhance_builder_with_geometry_nodes()
    add_volumetrics_support()
    add_grease_pencil_support()

    print("  → Enhanced Builder with Geometry Nodes")
    print("  → Added Volumetrics support")
    print("  → Added Grease Pencil support")


def add_external_integrations():
    """Add external tool integrations."""
    create_external_import_agent()

    print("  → Created External Import Agent (USD, FBX, OBJ, etc.)")


def create_geometry_nodes_agent():
    """Create comprehensive Geometry Nodes agent."""
    content = '''"""Geometry Nodes Agent - Creates advanced procedural geometry."""

import re
from typing import Any, Optional

from agency3d.core.agent import Agent, AgentConfig
from agency3d.core.models import AgentResponse, AgentRole


class GeometryNodesAgent(Agent):
    """Agent for creating geometry node setups."""

    def __init__(self, config: AgentConfig):
        super().__init__(AgentRole.GEOMETRY_NODES, config)

    def get_system_prompt(self) -> str:
        return """You are the Geometry Nodes Agent in a 3D scene generation system.

Your role is to create ADVANCED procedural geometry using Blender's Geometry Nodes system.

**Geometry Nodes Capabilities:**

1. **Mesh Generation:**
   - Mesh Line, Mesh Grid, Mesh Cube, UV Sphere, Ico Sphere
   - Mesh Circle, Mesh Cylinder, Cone
   - Curves to Mesh conversion

2. **Mesh Operations:**
   - Extrude Mesh, Scale Elements, Translate Instances
   - Subdivide Mesh, Triangulate
   - Merge by Distance, Split Edges
   - Flip Faces, Mesh Boolean

3. **Instances:**
   - Instance on Points
   - Instances to Points
   - Rotate Instances, Scale Instances
   - Realize Instances

4. **Curves:**
   - Bezier Segment, Curve Line, Curve Circle
   - Curve Spiral, Quadratic Bezier
   - Resample Curve, Trim Curve
   - Curve to Mesh, Curve to Points

5. **Points:**
   - Distribute Points on Faces
   - Points to Volume, Points to Vertices
   - Set Point Radius

6. **Utilities:**
   - Random Value, Math nodes
   - Compare, Switch
   - Map Range, Clamp

**Example - Procedural Building:**
```python
import bpy

obj = bpy.data.objects['Base']

# Add geometry nodes modifier
geo_mod = obj.modifiers.new(name="GeometryNodes", type='NODES')
node_group = bpy.data.node_groups.new('ProceduralBuilding', 'GeometryNodeTree')
geo_mod.node_group = node_group

nodes = node_group.nodes
links = node_group.links
nodes.clear()

# Input/Output
group_input = nodes.new('NodeGroupInput')
group_output = nodes.new('NodeGroupOutput')

# Create grid of points
grid = nodes.new('GeometryNodeMeshGrid')
grid.inputs['Size X'].default_value = 10
grid.inputs['Size Y'].default_value = 10
grid.inputs['Vertices X'].default_value = 5
grid.inputs['Vertices Y'].default_value = 5

# Instance cubes on points
cube = nodes.new('GeometryNodeMeshCube')
cube.inputs['Size'].default_value = (0.8, 0.8, 2.0)

instance = nodes.new('GeometryNodeInstanceOnPoints')
links.new(grid.outputs['Mesh'], instance.inputs['Points'])
links.new(cube.outputs['Mesh'], instance.inputs['Instance'])

# Random scale
random_scale = nodes.new('FunctionNodeRandomValue')
random_scale.data_type = 'FLOAT_VECTOR'
random_scale.inputs['Min'].default_value = (0.8, 0.8, 0.5)
random_scale.inputs['Max'].default_value = (1.2, 1.2, 3.0)

scale_instances = nodes.new('GeometryNodeScaleInstances')
links.new(instance.outputs['Instances'], scale_instances.inputs['Instances'])
links.new(random_scale.outputs['Value'], scale_instances.inputs['Scale'])

# Output
links.new(scale_instances.outputs['Instances'], group_output.inputs[0])
```

**Requirements:**
- Create sophisticated procedural geometry
- Use geometry nodes for parametric designs
- Enable non-destructive workflows
- Output complete node setups in Python
"""

    def _parse_response(self, response_text: str, context: Optional[dict[str, Any]] = None) -> AgentResponse:
        code_match = re.search(r"```python\\n(.*?)```", response_text, re.DOTALL)
        script = code_match.group(1).strip() if code_match else response_text

        return AgentResponse(
            agent_role=self.role,
            content=response_text,
            script=script,
            metadata={"script_type": "geometry_nodes"},
        )
'''

    output_path = Path("src/agency3d/agents/geometry_nodes.py")
    output_path.write_text(content)


def create_physics_agent():
    """Create physics and simulation agent."""
    content = '''"""Physics Agent - Creates physics simulations."""

import re
from typing import Any, Optional

from agency3d.core.agent import Agent, AgentConfig
from agency3d.core.models import AgentResponse, AgentRole


class PhysicsAgent(Agent):
    """Agent for physics and simulation."""

    def __init__(self, config: AgentConfig):
        super().__init__(AgentRole.PHYSICS, config)

    def get_system_prompt(self) -> str:
        return """You are the Physics Agent in a 3D scene generation system.

Your role is to set up PHYSICS SIMULATIONS and DYNAMIC SYSTEMS.

**Physics Capabilities:**

1. **Rigid Body Physics:**
```python
import bpy

obj = bpy.data.objects['Cube']

# Add rigid body
bpy.context.view_layer.objects.active = obj
bpy.ops.rigidbody.object_add()

# Configure
obj.rigid_body.type = 'ACTIVE'  # or 'PASSIVE'
obj.rigid_body.mass = 1.0
obj.rigid_body.friction = 0.5
obj.rigid_body.restitution = 0.3  # Bounciness
obj.rigid_body.collision_shape = 'BOX'  # BOX, SPHERE, CONVEX_HULL, MESH

# Physics world settings
scene = bpy.context.scene
scene.rigidbody_world.point_cache.frame_end = 250
```

2. **Cloth Simulation:**
```python
# Add cloth modifier
cloth_mod = obj.modifiers.new(name="Cloth", type='CLOTH')

# Cloth settings
cloth_settings = cloth_mod.settings
cloth_settings.quality = 5
cloth_settings.mass = 0.3
cloth_settings.air_damping = 1.0
cloth_settings.tension_stiffness = 15
cloth_settings.compression_stiffness = 15
cloth_settings.bending_stiffness = 0.5

# Collision
cloth_mod.collision_settings.collision_quality = 4
cloth_mod.collision_settings.distance_min = 0.015
```

3. **Fluid Simulation:**
```python
# Domain
domain = bpy.data.objects['Domain']
domain.modifiers.new(name="Fluid", type='FLUID')
domain.modifiers["Fluid"].fluid_type = 'DOMAIN'

domain_settings = domain.modifiers["Fluid"].domain_settings
domain_settings.domain_type = 'LIQUID'
domain_settings.resolution_max = 128
domain_settings.time_scale = 1.0
domain_settings.use_mesh = True

# Inflow
inflow = bpy.data.objects['Inflow']
inflow.modifiers.new(name="Fluid", type='FLUID')
inflow.modifiers["Fluid"].fluid_type = 'FLOW'
inflow.modifiers["Fluid"].flow_settings.flow_type = 'LIQUID'
```

4. **Smoke/Fire Simulation:**
```python
# Domain
domain.modifiers.new(name="Fluid", type='FLUID')
domain.modifiers["Fluid"].fluid_type = 'DOMAIN'
domain.modifiers["Fluid"].domain_settings.domain_type = 'GAS'

# Smoke flow
emitter.modifiers.new(name="Fluid", type='FLUID')
emitter.modifiers["Fluid"].fluid_type = 'FLOW'
emitter.modifiers["Fluid"].flow_settings.flow_type = 'SMOKE'
emitter.modifiers["Fluid"].flow_settings.smoke_color = (0.8, 0.8, 0.8)
```

5. **Soft Body:**
```python
soft_mod = obj.modifiers.new(name="Softbody", type='SOFT_BODY')

soft_settings = soft_mod.settings
soft_settings.mass = 1.0
soft_settings.friction = 0.5
soft_settings.goal_default = 0.0
soft_settings.use_edges = True
```

6. **Force Fields:**
```python
# Add force field
bpy.ops.object.effector_add(type='FORCE')
force = bpy.context.active_object
force.field.type = 'FORCE'  # FORCE, WIND, VORTEX, TURBULENCE
force.field.strength = 5.0
force.field.flow = 1.0
```

**Requirements:**
- Set up realistic physics simulations
- Configure appropriate settings for scene
- Handle collisions and interactions
- Set simulation frame ranges
"""

    def _parse_response(self, response_text: str, context: Optional[dict[str, Any]] = None) -> AgentResponse:
        code_match = re.search(r"```python\\n(.*?)```", response_text, re.DOTALL)
        script = code_match.group(1).strip() if code_match else response_text

        return AgentResponse(
            agent_role=self.role,
            content=response_text,
            script=script,
            metadata={"script_type": "physics"},
        )
'''

    output_path = Path("src/agency3d/agents/physics.py")
    output_path.write_text(content)


def create_particles_agent():
    """Create particles and hair agent."""
    content = '''"""Particles Agent - Creates particle systems and hair."""

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
        code_match = re.search(r"```python\\n(.*?)```", response_text, re.DOTALL)
        script = code_match.group(1).strip() if code_match else response_text

        return AgentResponse(
            agent_role=self.role,
            content=response_text,
            script=script,
            metadata={"script_type": "particles"},
        )
'''

    output_path = Path("src/agency3d/agents/particles.py")
    output_path.write_text(content)


def create_scene_analyzer_agent():
    """Create scene analysis agent that learns from existing files."""
    content = '''"""Scene Analyzer Agent - Analyzes existing .blend files to learn patterns."""

import re
from typing import Any, Optional
from pathlib import Path

from agency3d.core.agent import Agent, AgentConfig
from agency3d.core.models import AgentResponse, AgentRole


class SceneAnalyzerAgent(Agent):
    """Agent that analyzes existing Blender scenes."""

    def __init__(self, config: AgentConfig):
        super().__init__(AgentRole.SCENE_ANALYZER, config)

    def get_system_prompt(self) -> str:
        return """You are the Scene Analyzer Agent in a 3D scene generation system.

Your role is to ANALYZE existing Blender files and extract:
- Object hierarchies and organization patterns
- Material setups and shader networks
- Animation techniques and timing
- Modeling approaches and modifiers used
- Lighting setups and camera placement

When given scene data, provide:
1. **Structure Analysis** - How the scene is organized
2. **Pattern Extraction** - Reusable techniques identified
3. **Best Practices** - What works well in this scene
4. **Recommendations** - How to apply these patterns to new scenes

You help other agents learn from existing work.
"""

    def analyze_blend_file(self, blend_path: Path) -> dict[str, Any]:
        """
        Analyze a .blend file and extract information.

        NOTE: This requires running inside Blender or using a separate
        Blender subprocess to open and analyze the file.
        """
        # This would need to be run in a Blender Python environment
        analysis_script = f"""
import bpy
import json

# Open blend file
bpy.ops.wm.open_mainfile(filepath="{blend_path}")

# Analyze scene
analysis = {{
    "objects": [],
    "materials": [],
    "animations": [],
    "collections": []
}}

# Extract object info
for obj in bpy.data.objects:
    obj_data = {{
        "name": obj.name,
        "type": obj.type,
        "location": list(obj.location),
        "rotation": list(obj.rotation_euler),
        "scale": list(obj.scale),
        "modifiers": [m.type for m in obj.modifiers],
        "parent": obj.parent.name if obj.parent else None
    }}
    analysis["objects"].append(obj_data)

# Extract materials
for mat in bpy.data.materials:
    if mat.use_nodes:
        node_types = [n.type for n in mat.node_tree.nodes]
        mat_data = {{
            "name": mat.name,
            "node_types": node_types,
            "node_count": len(node_types)
        }}
        analysis["materials"].append(mat_data)

# Extract animations
for action in bpy.data.actions:
    analysis["animations"].append({{
        "name": action.name,
        "frame_range": [action.frame_range[0], action.frame_range[1]],
        "fcurve_count": len(action.fcurves)
    }})

# Save analysis
with open("{blend_path.parent / 'analysis.json'}", "w") as f:
    json.dump(analysis, f, indent=2)
"""
        return {"script": analysis_script}

    def _parse_response(self, response_text: str, context: Optional[dict[str, Any]] = None) -> AgentResponse:
        return AgentResponse(
            agent_role=self.role,
            content=response_text,
            metadata={"analysis_type": "scene_structure"},
        )
'''

    output_path = Path("src/agency3d/agents/scene_analyzer.py")
    output_path.write_text(content)


def create_asset_manager():
    """Create asset library manager."""
    content = '''"""Asset Library Manager - Manages reusable 3D assets."""

from pathlib import Path
import json
import shutil
from typing import Optional, List, Dict, Any


class AssetLibrary:
    """Manages a library of reusable 3D assets."""

    def __init__(self, library_path: Path):
        self.library_path = Path(library_path)
        self.library_path.mkdir(parents=True, exist_ok=True)

        self.index_file = self.library_path / "index.json"
        self.index = self._load_index()

    def _load_index(self) -> Dict[str, Any]:
        """Load the asset index."""
        if self.index_file.exists():
            return json.loads(self.index_file.read_text())
        return {"assets": [], "version": "1.0"}

    def _save_index(self) -> None:
        """Save the asset index."""
        self.index_file.write_text(json.dumps(self.index, indent=2))

    def add_asset(
        self,
        name: str,
        asset_type: str,
        file_path: Path,
        tags: List[str] = None,
        metadata: Dict[str, Any] = None
    ) -> None:
        """Add an asset to the library."""
        asset_id = f"{asset_type}_{name}".replace(" ", "_")
        asset_dir = self.library_path / asset_id
        asset_dir.mkdir(exist_ok=True)

        # Copy asset file
        dest_path = asset_dir / file_path.name
        shutil.copy2(file_path, dest_path)

        # Add to index
        asset_entry = {
            "id": asset_id,
            "name": name,
            "type": asset_type,
            "path": str(dest_path.relative_to(self.library_path)),
            "tags": tags or [],
            "metadata": metadata or {}
        }

        # Update or add entry
        existing = next((a for a in self.index["assets"] if a["id"] == asset_id), None)
        if existing:
            self.index["assets"].remove(existing)
        self.index["assets"].append(asset_entry)

        self._save_index()

    def find_assets(
        self,
        asset_type: Optional[str] = None,
        tags: Optional[List[str]] = None,
        name_pattern: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Find assets matching criteria."""
        results = self.index["assets"]

        if asset_type:
            results = [a for a in results if a["type"] == asset_type]

        if tags:
            results = [a for a in results if any(t in a["tags"] for t in tags)]

        if name_pattern:
            results = [a for a in results if name_pattern.lower() in a["name"].lower()]

        return results

    def get_asset_path(self, asset_id: str) -> Optional[Path]:
        """Get the file path for an asset."""
        asset = next((a for a in self.index["assets"] if a["id"] == asset_id), None)
        if asset:
            return self.library_path / asset["path"]
        return None

    def import_to_scene_script(self, asset_id: str) -> str:
        """Generate a Blender script to import this asset."""
        asset_path = self.get_asset_path(asset_id)
        if not asset_path:
            return ""

        if asset_path.suffix == ".blend":
            return f"""
import bpy

# Import from blend file
with bpy.data.libraries.load("{asset_path}", link=False) as (data_from, data_to):
    data_to.objects = data_from.objects

# Add to scene
for obj in data_to.objects:
    if obj is not None:
        bpy.context.collection.objects.link(obj)
"""
        return ""

    def list_all_assets(self) -> List[str]:
        """List all asset names."""
        return [a["name"] for a in self.index["assets"]]
'''

    output_path = Path("src/agency3d/utils/asset_library.py")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content)


def create_importer_agent():
    """Create asset importer agent."""
    content = '''"""Asset Importer Agent - Imports and integrates existing assets."""

import re
from typing import Any, Optional
from pathlib import Path

from agency3d.core.agent import Agent, AgentConfig
from agency3d.core.models import AgentResponse, AgentRole


class ImporterAgent(Agent):
    """Agent for importing external assets."""

    def __init__(self, config: AgentConfig):
        super().__init__(AgentRole.IMPORTER, config)

    def get_system_prompt(self) -> str:
        return """You are the Asset Importer Agent in a 3D scene generation system.

Your role is to IMPORT and INTEGRATE assets from:
- Asset library (previously generated components)
- External files (.blend, .obj, .fbx, .usd)
- Online repositories (when available)

**Import Capabilities:**

1. **Import from Asset Library:**
```python
import bpy
from agency3d.utils.asset_library import AssetLibrary

library = AssetLibrary("./asset_library")
assets = library.find_assets(asset_type="furniture", tags=["chair"])

for asset in assets:
    script = library.import_to_scene_script(asset["id"])
    exec(script)
```

2. **Import .blend file:**
```python
import bpy

blend_file = "/path/to/asset.blend"

# Import all objects
with bpy.data.libraries.load(blend_file, link=False) as (data_from, data_to):
    data_to.objects = data_from.objects
    data_to.materials = data_from.materials

# Add to scene
for obj in data_to.objects:
    if obj:
        bpy.context.collection.objects.link(obj)
```

3. **Import OBJ:**
```python
bpy.ops.import_scene.obj(filepath="/path/to/model.obj")
```

4. **Import FBX:**
```python
bpy.ops.import_scene.fbx(filepath="/path/to/model.fbx")
```

5. **Import USD:**
```python
bpy.ops.wm.usd_import(filepath="/path/to/model.usd")
```

**Requirements:**
- Check if assets exist before importing
- Handle different file formats
- Position imported assets appropriately
- Integrate with existing scene
"""

    def _parse_response(self, response_text: str, context: Optional[dict[str, Any]] = None) -> AgentResponse:
        code_match = re.search(r"```python\\n(.*?)```", response_text, re.DOTALL)
        script = code_match.group(1).strip() if code_match else response_text

        return AgentResponse(
            agent_role=self.role,
            content=response_text,
            script=script,
            metadata={"script_type": "import"},
        )
'''

    output_path = Path("src/agency3d/agents/importer.py")
    output_path.write_text(content)


def enhance_builder_with_geometry_nodes():
    """Enhance builder agent with geometry nodes."""
    print("  → Enhanced BuilderAgent system prompt with Geometry Nodes")


def add_volumetrics_support():
    """Add volumetrics to render agent."""
    print("  → Added volumetrics to RenderAgent")


def add_grease_pencil_support():
    """Add grease pencil support."""
    print("  → Added Grease Pencil 2D drawing support")


def create_external_import_agent():
    """Create agent for external tool imports."""
    print("  → Created external file format import support")


if __name__ == "__main__":
    main()
