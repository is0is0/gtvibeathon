# VoxelWeaver

> AI-Powered Procedural 3D Scene Generation Subsystem

VoxelWeaver is a comprehensive backend system for generating production-ready 3D scenes in Blender from natural language descriptions. It handles voxel-level geometry reasoning, proportion analysis, spatial positioning, lighting, texturing, and quality validation.

## 🎯 Purpose

VoxelWeaver serves as the core procedural subsystem for AI-driven 3D scene generation. It bridges the gap between natural language scene descriptions and fully realized, edit-ready Blender scenes.

### Key Capabilities

- 🔍 **Reference Search**: Cross-references public 3D model repositories and datasets
- 📐 **Proportion Analysis**: Ensures realistic real-world scales and measurements
- 🎨 **Procedural Generation**: Creates geometry when references aren't available
- 🚫 **Collision Detection**: Prevents overlapping objects with spatial optimization
- 💡 **Smart Lighting**: Applies context-aware realistic or stylized lighting
- 🎭 **Material System**: Generates PBR materials and procedural textures
- ✅ **Quality Validation**: Ensures scenes meet production standards
- 📤 **Multi-Format Export**: Outputs to .blend, .glb, .fbx, .obj, and more

## 🏗️ Architecture

### Module Overview

```
voxelweaver/
├── voxelweaver_core.py      # Main orchestration layer
├── geometry_handler.py       # Voxel geometry generation
├── proportion_analyzer.py    # Real-world scale normalization
├── context_alignment.py      # Spatial positioning & collision detection
├── lighting_engine.py        # Scene lighting system
├── texture_mapper.py         # Material and texture generation
├── blender_bridge.py         # Blender Python API integration
├── search_scraper.py         # Online reference gathering
├── model_formatter.py        # 3D format conversion
└── scene_validator.py        # Quality assurance
```

### Data Flow

```
User Prompt
    ↓
[Search References] → Online Model Databases
    ↓
[Generate Geometry] → Voxel Meshes
    ↓
[Normalize Proportions] → Real-World Scales
    ↓
[Align Objects] → Spatial Positioning (No Overlap)
    ↓
[Apply Lighting] → Realistic/Stylized Lights
    ↓
[Apply Textures] → PBR Materials
    ↓
[Validate Scene] → Quality Checks
    ↓
[Export to Blender] → .blend / .glb / .fbx
```

## 🚀 Quick Start

### Installation

```python
# Add to your Python path
import sys
sys.path.append('path/to/backend')

# Import VoxelWeaver
from voxelweaver import VoxelWeaverCore
```

### Basic Usage

```python
from voxelweaver import VoxelWeaverCore, VoxelWeaverConfig

# Create configuration
config = VoxelWeaverConfig(
    style="realistic",
    voxel_resolution=0.1,
    search_references=True,
    validate_scene=True
)

# Initialize VoxelWeaver
weaver = VoxelWeaverCore(config)

# Generate a scene
result = weaver.generate_scene(
    prompt="A cozy living room with a sofa, coffee table, and floor lamp",
    style="realistic"
)

# Check result
if result['success']:
    print(f"✓ Scene generated: {result['output_path']}")
    print(f"  Objects: {result['metadata']['object_count']}")
else:
    print(f"✗ Generation failed: {result['errors']}")
```

### Batch Generation

```python
# Generate multiple scenes
prompts = [
    "A modern kitchen with stainless steel appliances",
    "A bedroom with a king-size bed and nightstands",
    "An office with a desk and ergonomic chair"
]

results = weaver.generate_batch(prompts, style="realistic")

for i, result in enumerate(results):
    print(f"Scene {i+1}: {result['output_path']}")
```

## 📖 Module Documentation

### VoxelWeaverCore

**Main orchestration class** that coordinates all subsystems.

```python
from voxelweaver import VoxelWeaverCore

weaver = VoxelWeaverCore()
result = weaver.generate_scene("A scene description")
```

**Key Methods:**
- `generate_scene(prompt, style, custom_config)` - Generate single scene
- `generate_batch(prompts, style)` - Generate multiple scenes

### GeometryHandler

**Generates voxel-based 3D geometries** from prompts or imports.

```python
from voxelweaver import GeometryHandler

handler = GeometryHandler(voxel_resolution=0.1)
objects = handler.generate_from_prompt(
    "A table with four chairs",
    references={}
)
```

**Features:**
- Primitive shapes (cube, sphere, cylinder, etc.)
- Procedural furniture generation
- Model import and voxelization
- Mesh optimization

### ProportionAnalyzer

**Normalizes object scales** to real-world measurements.

```python
from voxelweaver import ProportionAnalyzer

analyzer = ProportionAnalyzer()
normalized = analyzer.normalize(objects, references={})
```

**Features:**
- Real-world dimension database (25+ objects)
- Automatic scale detection
- Proportion consistency checking
- Reference-based scaling

### ContextAlignment

**Positions objects** without collisions in 3D space.

```python
from voxelweaver import ContextAlignment

aligner = ContextAlignment()
positioned = aligner.align(objects)
```

**Features:**
- 5 placement strategies (grid, random, circular, linear, clustered)
- Bounding box collision detection
- Spatial optimization
- Scene hierarchy generation

### LightingEngine

**Applies scene lighting** with multiple styles.

```python
from voxelweaver import LightingEngine

engine = LightingEngine()
lit_scene = engine.apply(scene, style="realistic")
```

**Lighting Styles:**
- `realistic` - Natural daylight simulation
- `studio` - Three-point studio setup
- `cinematic` - Dramatic film lighting
- `sunset` - Golden hour ambiance
- `night` - Low-light scene
- `neon` - Cyberpunk/neon aesthetic
- `soft` - Diffused ambient lighting

**Light Types:**
- Sun (directional)
- Point lights
- Spot lights
- Area lights
- HDRI environments

### TextureMapper

**Generates materials and textures** for objects.

```python
from voxelweaver import TextureMapper

mapper = TextureMapper()
textured = mapper.apply(scene, style="realistic")
```

**Material Presets:**
- Metals (brushed aluminum, copper, gold)
- Wood (oak, walnut, pine)
- Glass (clear, frosted)
- Plastic, Rubber, Fabric
- Stone, Concrete, Ceramic

**Features:**
- PBR material generation
- Procedural textures
- UV mapping (smart, box, cylindrical, spherical)
- Emission materials

### BlenderBridge

**Exports scenes to Blender** formats.

```python
from voxelweaver import BlenderBridge

bridge = BlenderBridge()
result = bridge.export_scene(
    scene_data,
    format="blend",
    output_dir="output/"
)
```

**Supported Formats:**
- `.blend` - Native Blender
- `.glb` - glTF Binary
- `.fbx` - Autodesk FBX
- `.obj` - Wavefront OBJ
- `.stl` - STL (3D printing)
- `.usd` - Universal Scene Description
- `.dae` - COLLADA

### SearchScraper

**Gathers reference data** from online sources.

```python
from voxelweaver import SearchScraper

scraper = SearchScraper()
references = scraper.search_references("modern sofa")
```

**Features:**
- Built-in dimension database
- File-based caching
- Metadata extraction
- Reference matching

### ModelFormatter

**Converts between 3D formats** and optimizes meshes.

```python
from voxelweaver import ModelFormatter

formatter = ModelFormatter()
result = formatter.convert(
    "model.obj",
    output_format="glb",
    optimize_level=3
)
```

**Optimization Levels:**
- 0: None
- 1: Basic (remove doubles)
- 2: Moderate (decimate 25%)
- 3: Aggressive (decimate 50%)
- 4: Maximum (decimate 75%)

### SceneValidator

**Validates scene quality** and correctness.

```python
from voxelweaver import SceneValidator

validator = SceneValidator()
result = validator.check(scene)

if result['valid']:
    print("✓ Scene passed validation")
else:
    print("Issues found:")
    for issue in result['issues']:
        print(f"  - {issue}")
```

**Validation Categories:**
- Geometry (overlap, scale, normals)
- Naming conventions
- Scene organization
- Lighting (exposure, setup)
- Materials (assignment, quality)
- Performance (polygon count)
- Export readiness

## 🎨 Style System

VoxelWeaver supports multiple visual styles:

### Realistic

```python
result = weaver.generate_scene(
    "A living room",
    style="realistic"
)
```

- Accurate proportions
- Natural materials
- Realistic lighting (HDRI)
- High detail

### Stylized

```python
result = weaver.generate_scene(
    "A living room",
    style="stylized"
)
```

- Artistic interpretation
- Enhanced colors
- Stylized materials
- Dramatic lighting

### Low Poly

```python
result = weaver.generate_scene(
    "A living room",
    style="lowpoly"
)
```

- Simplified geometry
- Flat shading
- Minimal polygons
- Solid colors

### Cartoon

```python
result = weaver.generate_scene(
    "A living room",
    style="cartoon"
)
```

- Exaggerated proportions
- Bright colors
- Cel-shading
- Outline effects

## 🔧 Configuration

### VoxelWeaverConfig

```python
from voxelweaver import VoxelWeaverConfig
from pathlib import Path

config = VoxelWeaverConfig(
    style="realistic",                    # Visual style
    voxel_resolution=0.1,                 # Voxel grid size (meters)
    search_references=True,               # Enable online search
    validate_scene=True,                  # Run validation
    auto_lighting=True,                   # Automatic lighting
    export_format="blend",                # Output format
    output_dir=Path("output/voxelweaver") # Output directory
)
```

### Custom Configuration

```python
custom_config = {
    "style": "cinematic",
    "voxel_resolution": 0.05,  # Higher detail
    "validate_scene": False     # Skip validation
}

result = weaver.generate_scene(
    "A scene",
    custom_config=custom_config
)
```

## 📊 Output Structure

Generated scenes follow this structure:

```
output/voxelweaver/
└── scene_YYYYMMDD_HHMMSS/
    ├── scene.blend                 # Blender file
    ├── scene.glb                   # glTF export (if requested)
    ├── metadata.json               # Scene metadata
    ├── validation_report.json      # Validation results
    └── preview.png                 # Scene preview (optional)
```

### Metadata Format

```json
{
    "prompt": "A cozy living room...",
    "style": "realistic",
    "status": "completed",
    "object_count": 8,
    "export_format": "blend",
    "validation": {
        "valid": true,
        "issues": []
    },
    "statistics": {
        "total_vertices": 45632,
        "total_faces": 42108,
        "lights": 3,
        "materials": 8
    }
}
```

## 🎯 Integration with AI Agents

VoxelWeaver integrates seamlessly with the main Voxel AI agent system:

```python
from agency3d import Agency3D
from voxelweaver import VoxelWeaverCore

# Create both systems
agency = Agency3D(config)
weaver = VoxelWeaverCore()

# Use VoxelWeaver for geometric processing
result = weaver.generate_scene(
    prompt="User's scene description",
    style="realistic"
)

# Pass to Agency3D for AI enhancement
if result['success']:
    # Import VoxelWeaver output into Agency3D workflow
    enhanced_scene = agency.enhance_scene(result['output_path'])
```

### Integration Points

1. **Geometry Generation**: VoxelWeaver generates base geometry
2. **AI Enhancement**: Agency3D agents add details and refinements
3. **Material Enhancement**: TextureAgent improves VoxelWeaver materials
4. **Lighting Refinement**: RenderAgent enhances lighting setup
5. **Animation**: AnimationAgent adds motion to VoxelWeaver scenes

## 🔬 Advanced Usage

### Custom Geometry Generation

```python
from voxelweaver import GeometryHandler

handler = GeometryHandler(voxel_resolution=0.05)

# Generate specific object types
table = handler._create_table()
chair = handler._create_chair()

# Custom primitive
custom = handler._create_primitive_box(
    name="custom_object",
    size=(2.0, 1.0, 0.5)
)
```

### Manual Proportion Control

```python
from voxelweaver import ProportionAnalyzer

analyzer = ProportionAnalyzer()

# Override target dimensions
custom_dims = {
    "my_object": {
        "width": 1.5,
        "depth": 0.8,
        "height": 2.0
    }
}

# Create custom references
references = {"dimensions": custom_dims}

# Normalize with custom dimensions
normalized = analyzer.normalize(objects, references)
```

### Custom Lighting Setup

```python
from voxelweaver import LightingEngine

engine = LightingEngine()

# Create custom light configuration
custom_lights = [
    {
        "type": "sun",
        "energy": 5.0,
        "color": (1.0, 0.9, 0.8),
        "direction": (-0.3, -0.5, -1.0)
    },
    {
        "type": "point",
        "energy": 100.0,
        "color": (1.0, 1.0, 1.0),
        "location": (2.0, 0.0, 2.0)
    }
]

# Apply custom lights
scene_with_lights = {
    "objects": objects,
    "lights": custom_lights
}
```

### Validation Customization

```python
from voxelweaver import SceneValidator

validator = SceneValidator()

# Set custom thresholds
validator.max_polygon_count = 500000
validator.min_polygon_count = 100
validator.max_overlap_tolerance = 0.001

# Custom validation
result = validator.check(scene)
```

## 🐛 Troubleshooting

### Common Issues

**Issue**: Objects overlap in scene
```python
# Solution: Adjust collision tolerance
from voxelweaver import ContextAlignment

aligner = ContextAlignment()
aligner.collision_tolerance = 0.1  # Increase tolerance
positioned = aligner.align(objects)
```

**Issue**: Objects are incorrectly scaled
```python
# Solution: Provide custom dimensions
references = {
    "dimensions": {
        "table": {"height": 0.75, "width": 1.2}
    }
}
normalized = analyzer.normalize(objects, references)
```

**Issue**: Blender not found
```python
# Solution: Set Blender path manually
from voxelweaver import BlenderBridge

bridge = BlenderBridge()
bridge.blender_path = "/path/to/blender"
```

**Issue**: Validation fails
```python
# Solution: Get detailed report
result = validator.check(scene)
print("Validation Report:")
print(f"Valid: {result['valid']}")
print(f"Issues: {len(result['issues'])}")
for issue in result['issues']:
    print(f"  - [{issue['category']}] {issue['message']}")
    if 'suggestion' in issue:
        print(f"    Suggestion: {issue['suggestion']}")
```

## 📈 Performance Optimization

### Voxel Resolution

```python
# Lower resolution = faster, less detailed
fast_config = VoxelWeaverConfig(voxel_resolution=0.2)

# Higher resolution = slower, more detailed
detailed_config = VoxelWeaverConfig(voxel_resolution=0.05)
```

### Disable Optional Features

```python
# Skip validation for faster generation
config = VoxelWeaverConfig(
    validate_scene=False,
    search_references=False
)
```

### Batch Processing

```python
# Process multiple scenes efficiently
results = weaver.generate_batch(
    prompts=my_prompts,
    style="lowpoly"  # Faster than realistic
)
```

## 🤝 Contributing

VoxelWeaver is designed to be extended. To add new features:

1. **New Geometry Types**: Extend `GeometryHandler._generate_procedural()`
2. **New Materials**: Add presets to `TextureMapper.material_presets`
3. **New Lighting Styles**: Add to `LightingEngine.lighting_styles`
4. **New Export Formats**: Extend `BlenderBridge.export_scene()`

## 📜 License

Part of the Voxel AI 3D Scene Generation system.

## 🙏 Acknowledgments

- Built for integration with the Voxel AI agent system
- Designed for Blender 3.6+
- Uses NumPy for efficient geometry operations

---

**Version**: 0.1.0
**Status**: Production Ready ✅

For integration with the main Voxel system, see the [main README](../../README.md) and [WEB_INTERFACE_GUIDE](../../WEB_INTERFACE_GUIDE.md).
