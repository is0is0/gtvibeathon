# Voxel Weaver Architecture

> AI-Driven 3D Scene Builder - Complete System Architecture

## Overview

Voxel Weaver is a comprehensive AI-driven 3D scene generation system that transforms natural language descriptions into production-ready Blender scenes. The system integrates multiple specialized subsystems coordinated by a central orchestrator.

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        User Input                            │
│                  (Natural Language Prompt)                   │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    Main Entry Point                          │
│                      (main.py)                               │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                  Scene Orchestrator                          │
│            (orchestrator/scene_orchestrator.py)              │
│                                                              │
│  Coordinates all subsystems in correct order:                │
│  1. Prompt Interpretation                                    │
│  2. VoxelWeaver Integration                                  │
│  3. Texture Synthesis                                        │
│  4. Lighting AI                                              │
│  5. Spatial Validation                                       │
│  6. Render Direction                                         │
│  7. Asset Management                                         │
└──────────────────────┬──────────────────────────────────────┘
                       │
          ┌────────────┴────────────┐
          │                         │
          ▼                         ▼
┌──────────────────┐     ┌──────────────────┐
│   Subsystems     │     │  VoxelWeaver     │
│                  │     │  Integration     │
│  - Prompt        │     │                  │
│  - Texture       │     │  Wraps backend   │
│  - Lighting      │     │  VoxelWeaver     │
│  - Spatial       │     │  system          │
│  - Render        │     │                  │
│  - Assets        │     │                  │
└──────────────────┘     └──────────────────┘
          │                         │
          └────────────┬────────────┘
                       │
                       ▼
          ┌────────────────────────┐
          │    Blender API Tools   │
          │   (utils/blender_*)    │
          └────────────┬───────────┘
                       │
                       ▼
          ┌────────────────────────┐
          │   Blender Output       │
          │   (.blend, .glb, etc)  │
          └────────────────────────┘
```

## Directory Structure

```
src/
├── voxel_weaver/              # VoxelWeaver integration layer
│   └── voxel_weaver_core.py   # Wrapper for backend VoxelWeaver
│
├── orchestrator/              # Main coordination layer
│   └── scene_orchestrator.py  # Central orchestrator
│
├── subsystems/                # Specialized subsystems
│   ├── prompt_interpreter.py  # NLP prompt analysis
│   ├── texture_synth.py       # Texture generation
│   ├── lighting_ai.py         # Intelligent lighting
│   ├── spatial_validator.py   # Physics validation
│   ├── render_director.py     # Render orchestration
│   └── asset_registry.py      # Asset management
│
├── utils/                     # Utility modules
│   ├── blender_api_tools.py   # Blender API wrappers
│   └── logger.py              # Logging system
│
├── main.py                    # CLI entry point
└── ARCHITECTURE.md            # This file
```

## Module Descriptions

### Core Orchestration

#### `main.py`
**Purpose**: Command-line interface and main entry point

**Responsibilities**:
- Parse command-line arguments
- Initialize logging system
- Create Scene Orchestrator
- Handle user input/output
- Error reporting

**Key Functions**:
- `main()` - Entry point
- `parse_arguments()` - CLI argument parsing

---

#### `orchestrator/scene_orchestrator.py`
**Purpose**: Central coordinator for entire scene generation pipeline

**Responsibilities**:
- Coordinate all subsystems
- Manage workflow execution order
- Track progress and state
- Handle error recovery
- Aggregate results from all subsystems

**Key Classes**:
- `SceneOrchestrator` - Main orchestration class

**Key Methods**:
- `generate_complete_scene()` - Main generation method
- `coordinate_subsystems()` - Subsystem coordination
- `track_progress()` - Progress tracking

**Workflow**:
1. Receive user prompt
2. Initialize all subsystems
3. Execute prompt interpretation
4. Generate geometry via VoxelWeaver
5. Synthesize textures
6. Apply intelligent lighting
7. Validate spatial relationships
8. Direct rendering
9. Manage assets
10. Return complete scene

---

### VoxelWeaver Integration

#### `voxel_weaver/voxel_weaver_core.py`
**Purpose**: Integration wrapper for backend VoxelWeaver system

**Responsibilities**:
- Bridge between orchestrator and backend VoxelWeaver
- Preprocess prompts for VoxelWeaver
- Post-process VoxelWeaver results
- Add integration enhancements

**Key Classes**:
- `VoxelWeaverIntegration` - Integration wrapper

**Key Methods**:
- `generate_scene()` - Generate scene via backend
- `preprocess_prompt()` - Enhance prompts
- `postprocess_result()` - Enhance results

**Integration Points**:
- Imports from `../backend/voxelweaver`
- Coordinates with Scene Orchestrator
- Passes data to subsystems

---

### Subsystems

#### `subsystems/prompt_interpreter.py`
**Purpose**: Advanced NLP-based prompt analysis

**Responsibilities**:
- Parse natural language prompts
- Extract scene elements (objects, relationships)
- Identify visual style
- Determine mood/atmosphere
- Generate structured scene graph

**Key Classes**:
- `PromptInterpreter` - Main interpreter
- `SceneElement` - Dataclass for scene elements

**Key Methods**:
- `parse_prompt()` - Main parsing method
- `identify_objects()` - Object extraction
- `extract_style()` - Style detection
- `analyze_relationships()` - Spatial relationships
- `extract_mood()` - Mood/atmosphere analysis
- `generate_scene_graph()` - Structured representation

**Output**:
```python
{
    'objects': [SceneElement, ...],
    'style': str,
    'mood': Dict[str, float],
    'relationships': Dict[str, Any],
    'scene_graph': Dict[str, Any]
}
```

---

#### `subsystems/texture_synth.py`
**Purpose**: Advanced texture synthesis and enhancement

**Responsibilities**:
- AI-driven texture generation
- Style transfer for materials
- Procedural texture enhancement
- UV optimization
- Texture atlasing

**Key Classes**:
- `TextureSynthesizer` - Main synthesizer

**Key Methods**:
- `synthesize_texture()` - Generate textures
- `apply_style_transfer()` - Style transfer
- `enhance_procedural()` - Procedural enhancement
- `optimize_uvs()` - UV mapping optimization
- `create_texture_atlas()` - Texture atlasing

**Features**:
- Multiple synthesis methods
- Caching system
- Format conversion
- Resolution management

---

#### `subsystems/lighting_ai.py`
**Purpose**: Intelligent lighting analysis and setup

**Responsibilities**:
- Analyze scene geometry
- Suggest optimal lighting setups
- Auto-place lights intelligently
- Calculate exposure
- Optimize shadows

**Key Classes**:
- `LightingAI` - Main lighting AI

**Key Methods**:
- `analyze_scene()` - Scene analysis
- `suggest_lighting_setup()` - AI recommendations
- `auto_place_lights()` - Intelligent placement
- `calculate_exposure()` - Exposure calculation
- `optimize_shadows()` - Shadow optimization

**Lighting Styles**:
- Realistic (HDRI + sun)
- Studio (three-point lighting)
- Cinematic (dramatic lighting)
- Natural (daylight simulation)

---

#### `subsystems/spatial_validator.py`
**Purpose**: Physics-aware spatial validation

**Responsibilities**:
- Validate physics consistency
- Check object support/gravity
- Detect floating objects
- Fix intersections automatically
- Validate scale relationships

**Key Classes**:
- `SpatialValidator` - Main validator

**Key Methods**:
- `validate_scene()` - Complete validation
- `check_physics()` - Physics checks
- `validate_gravity()` - Gravity validation
- `check_support()` - Support validation
- `detect_floating_objects()` - Floating detection
- `fix_intersections()` - Auto-fix overlaps
- `validate_scale_relationships()` - Scale validation

**Validation Report**:
```python
{
    'valid': bool,
    'issues': List[Dict[str, str]],
    'fixes_applied': List[str],
    'warnings': List[str]
}
```

---

#### `subsystems/render_director.py`
**Purpose**: Render orchestration and optimization

**Responsibilities**:
- Plan rendering strategy
- Optimize render settings
- Manage multi-pass rendering
- Apply AI denoising
- Post-process outputs
- Batch rendering

**Key Classes**:
- `RenderDirector` - Main director

**Key Methods**:
- `plan_render()` - Rendering strategy
- `optimize_settings()` - Setting optimization
- `manage_render_passes()` - Multi-pass management
- `denoise_output()` - AI denoising
- `post_process()` - Post-processing
- `batch_render()` - Batch operations

**Quality Presets**:
- Draft (fast preview)
- Balanced (production quality)
- Final (maximum quality)

---

#### `subsystems/asset_registry.py`
**Purpose**: Asset management and library

**Responsibilities**:
- Register and catalog assets
- Search asset database
- Download from online sources
- Cache management
- Version control
- Metadata extraction

**Key Classes**:
- `AssetRegistry` - Main registry

**Key Methods**:
- `register_asset()` - Add to library
- `search_assets()` - Query by criteria
- `download_asset()` - Online download
- `cache_asset()` - Local caching
- `get_asset_metadata()` - Metadata retrieval
- `update_asset_version()` - Version management

**Storage**:
- SQLite database for metadata
- File system for asset files
- Indexed search

---

### Utilities

#### `utils/blender_api_tools.py`
**Purpose**: Blender Python API integration utilities

**Responsibilities**:
- Execute scripts in Blender subprocess
- Import/export operations
- Material creation
- Camera/lighting setup
- Rendering operations
- Cross-platform compatibility

**Key Classes**:
- `BlenderAPIWrapper` - Main API wrapper
- `BlenderImporter` - Import utilities
- `BlenderExporter` - Export utilities
- `BlenderMaterialCreator` - Material helpers
- `BlenderCameraSetup` - Camera utilities
- `BlenderLightingSetup` - Lighting helpers
- `BlenderRenderer` - Rendering utilities

**Key Features**:
- Auto-detect Blender installation
- Subprocess execution
- Format conversion
- Batch operations

---

#### `utils/logger.py`
**Purpose**: Centralized logging system

**Responsibilities**:
- Configure logging for entire system
- Colored console output
- File logging with rotation
- JSON structured logging
- Module-specific loggers

**Key Classes**:
- `VoxelWeaverLogger` - Main logger (singleton)
- `ColoredFormatter` - Console formatter
- `JSONFormatter` - JSON formatter

**Key Functions**:
- `setup_logging()` - Initialize logging
- `get_logger()` - Get module logger
- `set_log_level()` - Dynamic level changes

---

## Data Flow

### 1. Input Processing
```
User Prompt → main.py → SceneOrchestrator
```

### 2. Prompt Analysis
```
SceneOrchestrator → PromptInterpreter → Structured Scene Data
```

### 3. Geometry Generation
```
Scene Data → VoxelWeaverIntegration → Backend VoxelWeaver → 3D Geometry
```

### 4. Enhancement Pipeline
```
Geometry → TextureSynthesizer → Textured Objects
         → LightingAI → Lit Scene
         → SpatialValidator → Validated Scene
```

### 5. Rendering
```
Validated Scene → RenderDirector → Final Images/Animations
```

### 6. Asset Management
```
All Steps → AssetRegistry → Asset Database (for reuse)
```

## Configuration

### Environment Variables
```bash
BLENDER_PATH=/path/to/blender
LOG_LEVEL=INFO
OUTPUT_DIR=output/
CACHE_DIR=cache/
```

### Configuration File Structure
```python
{
    'style': 'realistic',
    'quality': 'balanced',
    'output_format': 'blend',
    'enable_validation': True,
    'enable_denoising': True,
    'subsystems': {
        'prompt_interpreter': {...},
        'texture_synth': {...},
        'lighting_ai': {...},
        'spatial_validator': {...},
        'render_director': {...}
    }
}
```

## Integration with Backend

### Backend VoxelWeaver
Located at: `../backend/voxelweaver/`

**Integration Flow**:
1. `voxel_weaver_core.py` imports backend modules
2. Wraps backend functionality with enhancements
3. Passes results to orchestrator
4. Backend handles core voxel operations

**Backend Modules Used**:
- `VoxelWeaverCore` - Main backend orchestrator
- `GeometryHandler` - Geometry generation
- `ProportionAnalyzer` - Scale normalization
- `ContextAlignment` - Spatial positioning
- `LightingEngine` - Basic lighting
- `TextureMapper` - Basic materials
- `BlenderBridge` - Blender export
- `SearchScraper` - Reference search
- `ModelFormatter` - Format conversion
- `SceneValidator` - Quality validation

## Error Handling

### Error Recovery Strategy
1. **Graceful Degradation**: Fall back to simpler approaches
2. **Logging**: Comprehensive error logging
3. **User Feedback**: Clear error messages
4. **Validation**: Detect issues early
5. **Auto-Correction**: Fix common issues automatically

### Error Types
- Input validation errors
- Subsystem failures
- Blender API errors
- Resource limitations
- Export failures

## Performance Considerations

### Optimization Strategies
1. **Caching**: Asset and texture caching
2. **Parallel Processing**: Multi-core utilization
3. **Progressive Enhancement**: Start simple, add detail
4. **Adaptive Quality**: Adjust based on scene complexity
5. **Batch Operations**: Group similar operations

### Resource Management
- Memory limits for large scenes
- GPU utilization for rendering
- Disk space for cache
- Network bandwidth for asset downloads

## Future Extensions

### Planned Features
1. **Real-time Preview**: Live scene updates
2. **Interactive Editing**: Post-generation tweaks
3. **Animation Support**: Complex animations
4. **Multi-Scene Management**: Scene collections
5. **Cloud Integration**: Cloud rendering
6. **Collaborative Editing**: Multi-user support
7. **Plugin System**: Extensible architecture
8. **AI Training**: Learn from user preferences

## Usage Examples

### Basic Usage
```bash
python src/main.py "A cozy living room with modern furniture"
```

### Advanced Usage
```bash
python src/main.py \
    "A futuristic cityscape at sunset" \
    --style stylized \
    --output output/cityscape \
    --format glb \
    --validate \
    --log-level DEBUG
```

### Python API
```python
from orchestrator.scene_orchestrator import SceneOrchestrator

orchestrator = SceneOrchestrator(config={
    'style': 'realistic',
    'quality': 'final'
})

result = orchestrator.generate_complete_scene(
    prompt="A medieval castle on a hilltop",
    style="realistic",
    validate=True
)
```

## Testing

### Test Strategy
- Unit tests for each module
- Integration tests for subsystems
- End-to-end tests for complete pipeline
- Performance benchmarks
- Visual regression tests

### Test Coverage
Target: 80%+ code coverage

## Documentation

### Code Documentation
- Module-level docstrings
- Class docstrings
- Method docstrings with Args/Returns
- Type hints throughout
- Inline comments for complex logic

### User Documentation
- README.md - Quick start
- ARCHITECTURE.md - This file
- API_REFERENCE.md - Detailed API docs
- EXAMPLES.md - Usage examples
- TROUBLESHOOTING.md - Common issues

---

**Version**: 1.0.0
**Last Updated**: 2025-01-18
**Status**: Foundational Structure Complete ✅
