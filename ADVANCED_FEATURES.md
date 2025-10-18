# Advanced Features - 3DAgency Extended

## 🚀 New Capabilities Added

This document describes the advanced features added to 3DAgency beyond the core system.

---

## 📊 **Summary of Enhancements**

### **New Agents Added:** 5 specialized agents
### **New Features:** Asset library, scene analysis, external imports
### **Total Agent Count:** 11 agents (6 core + 5 advanced)

---

## 🎯 **New Agent Capabilities**

### **1. Geometry Nodes Agent** 🔷
**Purpose:** Advanced procedural modeling using Blender's Geometry Nodes system

**Capabilities:**
- ✅ Mesh generation (grids, curves, primitives)
- ✅ Mesh operations (extrude, subdivide, boolean)
- ✅ Instance systems (points, arrays, scattering)
- ✅ Curve operations (resample, trim, to mesh)
- ✅ Procedural distributions
- ✅ Non-destructive workflows

**Example Use Cases:**
```python
# Procedural building generation
"create a cityscape using geometry nodes with randomized building heights"

# Organic scattering
"scatter rocks across a terrain using geometry nodes with size variation"

# Parametric design
"create a parametric fence using geometry nodes that can be adjusted"
```

**Script Generation:**
Generates complete geometry node setups with:
- Node groups
- Input/output connections
- Parameter controls
- Modifier application

---

### **2. Physics Agent** ⚛️
**Purpose:** Physics simulations and dynamic systems

**Capabilities:**
- ✅ **Rigid Body Physics** - Falling, colliding objects
- ✅ **Cloth Simulation** - Fabric, flags, draping
- ✅ **Fluid Simulation** - Liquid flows, splashes
- ✅ **Smoke/Fire** - Gas dynamics, explosions
- ✅ **Soft Body** - Deformable objects
- ✅ **Force Fields** - Wind, turbulence, vortex

**Example Use Cases:**
```python
# Domino cascade
"create dominoes that fall in sequence using rigid body physics"

# Cloth draping
"drape a tablecloth over a table using cloth simulation"

# Water pouring
"animate water pouring from a jug into a glass using fluid simulation"

# Smoke effect
"create rising smoke from a chimney using smoke simulation"
```

**Simulation Types:**
- Collision detection
- Mass and gravity
- Friction and bounciness
- Fluid domains and flows
- Smoke emission and dissipation

---

### **3. Particles Agent** ✨
**Purpose:** Particle systems for effects and hair/fur

**Capabilities:**
- ✅ **Emitter Particles** - Sparks, dust, debris
- ✅ **Hair Systems** - Fur, grass, hair
- ✅ **Particle Instances** - Scatter objects as particles
- ✅ **Force Fields** - Control particle behavior
- ✅ **Particle Physics** - Newtonian, Boids, Fluid

**Example Use Cases:**
```python
# Fireflies
"create fireflies using emitter particles with glowing emission materials"

# Grass field
"add grass to the ground using a hair particle system"

# Debris explosion
"create an explosion with debris particles flying outward"

# Snow falling
"animate falling snow using particle system with turbulence"
```

**Particle Features:**
- Emission timing and count
- Velocity and randomization
- Lifespan control
- Instance rendering
- Dynamic properties

---

### **4. Scene Analyzer Agent** 🔍
**Purpose:** Analyze existing .blend files to learn patterns and techniques

**Capabilities:**
- ✅ Extract object hierarchies
- ✅ Analyze material setups
- ✅ Identify animation patterns
- ✅ Catalog modifiers used
- ✅ Document lighting approaches
- ✅ Generate analysis reports

**Example Use Cases:**
```python
# Learn from reference
"analyze this architectural scene and extract the lighting setup"

# Pattern extraction
"identify the material network used for this wood texture"

# Technique documentation
"document the animation approach used in this character rig"
```

**Analysis Output:**
```json
{
  "objects": [
    {
      "name": "Chair",
      "type": "MESH",
      "modifiers": ["BEVEL", "SUBSURF"],
      "parent": "Furniture_Group"
    }
  ],
  "materials": [
    {
      "name": "Wood",
      "node_types": ["BSDF_PRINCIPLED", "TEX_NOISE", "BUMP"],
      "node_count": 12
    }
  ],
  "animations": [
    {
      "name": "CameraFlythrough",
      "frame_range": [1, 250],
      "fcurve_count": 6
    }
  ]
}
```

**Use Cases:**
1. **Learn from Examples** - Analyze professional scenes
2. **Extract Patterns** - Identify reusable techniques
3. **Document Workflows** - Understand how scenes were built
4. **Transfer Knowledge** - Apply techniques to new scenes

---

### **5. Asset Importer Agent** 📥
**Purpose:** Import and integrate external assets and files

**Capabilities:**
- ✅ **Asset Library Integration** - Import from local library
- ✅ **.blend File Import** - Import from other Blender files
- ✅ **OBJ Import** - Wavefront OBJ files
- ✅ **FBX Import** - Autodesk FBX files
- ✅ **USD Import** - Universal Scene Description
- ✅ **Smart Positioning** - Place imports appropriately

**Example Use Cases:**
```python
# Reuse components
"import chair models from the asset library and arrange around a table"

# External models
"import this FBX character model and position in the scene"

# Library assets
"find all 'tree' assets and scatter them across the terrain"
```

**Supported Formats:**
- `.blend` - Blender native
- `.obj` - Wavefront
- `.fbx` - Autodesk FBX
- `.usd` / `.usda` / `.usdc` - Universal Scene Description
- Asset library references

---

## 🗂️ **Asset Library System**

### **AssetLibrary Manager**

A complete asset management system for organizing and reusing components.

**Features:**
```python
from agency3d.utils.asset_library import AssetLibrary

# Initialize library
library = AssetLibrary("./my_assets")

# Add asset
library.add_asset(
    name="Modern Chair",
    asset_type="furniture",
    file_path=Path("chair.blend"),
    tags=["chair", "modern", "furniture"],
    metadata={"style": "minimalist", "poly_count": 5000}
)

# Find assets
chairs = library.find_assets(asset_type="furniture", tags=["chair"])

# Import to scene
script = library.import_to_scene_script(chairs[0]["id"])
```

**Asset Organization:**
```
asset_library/
├── index.json              # Asset catalog
├── furniture_modern_chair/
│   └── chair.blend
├── prop_coffee_mug/
│   └── mug.blend
└── material_wood_oak/
    └── material.blend
```

**Search Capabilities:**
- By asset type
- By tags
- By name pattern
- By metadata

---

## 🔧 **How to Use Advanced Features**

### **1. Enable in Workflow**

Advanced agents can be added to the orchestrator:

```python
from agency3d import Agency3D
from agency3d.agents import PhysicsAgent, ParticlesAgent

agency = Agency3D()

# Enable physics simulation
result = agency.create_scene(
    prompt="dominoes falling in sequence",
    enable_physics=True
)

# Enable particle effects
result = agency.create_scene(
    prompt="fireflies in a forest",
    enable_particles=True
)
```

### **2. Scene Analysis**

Analyze existing files to learn patterns:

```python
from agency3d.agents import SceneAnalyzerAgent

analyzer = SceneAnalyzerAgent(config)

# Analyze a reference scene
analysis = analyzer.analyze_blend_file(Path("reference_scene.blend"))

# Use insights in new generation
result = agency.create_scene(
    prompt="create similar lighting to the analyzed scene",
    reference_analysis=analysis
)
```

### **3. Asset Import**

Use existing assets in generations:

```python
from agency3d.utils.asset_library import AssetLibrary

library = AssetLibrary("./assets")

# Find relevant assets
chairs = library.find_assets(tags=["chair"])

# Create scene using library
result = agency.create_scene(
    prompt="dining room with table",
    import_assets=chairs  # Will import and arrange chairs
)
```

---

## 📈 **Complete Agent Roster**

### **Core Agents (6)**
1. **ConceptAgent** - Scene concept generation
2. **BuilderAgent** - Multi-model geometry (10-20+ objects)
3. **TextureAgent** - Advanced materials (50+ shader nodes)
4. **RenderAgent** - Camera and lighting
5. **AnimationAgent** - Keyframe animation with easing
6. **ReviewerAgent** - Quality control

### **Advanced Agents (5)**
7. **GeometryNodesAgent** - Procedural modeling
8. **PhysicsAgent** - Simulations (rigid body, cloth, fluid)
9. **ParticlesAgent** - Particle systems and hair
10. **SceneAnalyzerAgent** - Learn from existing scenes
11. **ImporterAgent** - External asset integration

---

## 🎬 **Advanced Workflow Examples**

### **Example 1: Physics Simulation Scene**

```bash
3dagency create "dominoes arranged in a spiral that fall when first one is tipped" \
  --enable-physics \
  --simulation-frames 250
```

**Generated:**
- Builder creates domino models
- Physics agent sets up rigid body
- Animation agent adds initial tip
- Render agent captures the cascade

### **Example 2: Particle Effect Scene**

```bash
3dagency create "magical forest with fireflies, falling leaves, and mist" \
  --enable-particles \
  --enable-volumetrics
```

**Generated:**
- Builder creates forest environment
- Particles agent adds fireflies (emitter)
- Particles agent adds leaves (hair system)
- Render agent adds volumetric mist

### **Example 3: Procedural City**

```bash
3dagency create "procedural city block with randomized building heights" \
  --enable-geometry-nodes \
  --instances 50
```

**Generated:**
- Geometry Nodes agent creates parametric buildings
- Instances scattered procedurally
- Varied heights and styles
- Complete city block

### **Example 4: Asset Library Integration**

```bash
3dagency create "conference room" \
  --import-from-library \
  --asset-tags "furniture,office"
```

**Generated:**
- Finds chairs, tables, whiteboards from library
- Arranges in conference room layout
- Adds custom elements as needed
- Integrates library assets seamlessly

---

## 🔬 **Technical Implementation**

### **Agent Integration**

All new agents follow the same base architecture:

```python
class AdvancedAgent(Agent):
    def __init__(self, config: AgentConfig):
        super().__init__(AgentRole.AGENT_TYPE, config)

    def get_system_prompt(self) -> str:
        # Comprehensive instructions for Blender features
        return """..."""

    def _parse_response(self, response_text: str, context) -> AgentResponse:
        # Extract generated code
        # Return structured response
```

### **Script Execution**

Advanced features execute in sequence:

1. Core scene setup (Builder, Texture, Render)
2. Advanced feature scripts (Geometry Nodes, Physics, Particles)
3. Animation keyframing
4. Simulation baking (if needed)
5. Final render

---

## 🎓 **Best Practices**

### **Using Physics**
- Set appropriate frame ranges (physics needs time)
- Use collision shapes that match geometry
- Bake simulations for reliability
- Test with lower quality first

### **Using Particles**
- Start with lower counts for testing
- Use instances for complex particles
- Set appropriate lifespans
- Consider performance impact

### **Using Geometry Nodes**
- Build modular node groups
- Use parameters for adjustability
- Test on simple geometry first
- Document node networks

### **Using Asset Library**
- Tag assets thoroughly
- Include metadata for search
- Version control important assets
- Organize by category

---

## 🚦 **Status**

✅ **All agents implemented and functional**
✅ **Asset library system complete**
✅ **Scene analysis framework ready**
✅ **External import support added**
✅ **Documentation comprehensive**

**Ready for production use with advanced features!**

---

## 📖 **Additional Resources**

- **Geometry Nodes:** Blender Manual - Geometry Nodes
- **Physics:** Blender Manual - Physics
- **Particles:** Blender Manual - Particle System
- **USD Import:** Blender Manual - USD
- **Python API:** Blender Python API Documentation

---

## 🎯 **Next Steps**

To use these advanced features:

1. **Update your installation:**
   ```bash
   pip install -e . --upgrade
   ```

2. **Try advanced prompts:**
   ```bash
   3dagency create "your advanced scene description"
   ```

3. **Explore the asset library:**
   ```python
   from agency3d.utils.asset_library import AssetLibrary
   library = AssetLibrary("./assets")
   print(library.list_all_assets())
   ```

**Happy creating with advanced features!** ⚡✨
