# Voxel Weaver - Source Directory

> AI-Driven 3D Scene Builder - Orchestration Layer

## Directory Structure

```
src/
├── voxel_weaver/              # VoxelWeaver integration
├── orchestrator/              # Main coordination
├── subsystems/                # Specialized systems
├── utils/                     # Utilities
├── agency3d/                  # AI agent system (existing)
├── main.py                    # CLI entry point
└── ARCHITECTURE.md            # Architecture documentation
```

## Quick Start

### Run from Command Line

```bash
# Basic usage
python src/main.py "A cozy living room"

# With options
python src/main.py "A futuristic city" --style stylized --validate
```

### Use as Python Module

```python
from orchestrator.scene_orchestrator import SceneOrchestrator

orchestrator = SceneOrchestrator()
result = orchestrator.generate_complete_scene(
    prompt="A medieval castle",
    style="realistic"
)
```

## Module Overview

### VoxelWeaver Integration (`voxel_weaver/`)
Wraps the backend VoxelWeaver system with enhancements.

### Orchestrator (`orchestrator/`)
Coordinates all subsystems for complete scene generation.

### Subsystems (`subsystems/`)
Six specialized modules:
- **prompt_interpreter** - NLP prompt analysis
- **texture_synth** - Advanced texture generation
- **lighting_ai** - Intelligent lighting
- **spatial_validator** - Physics validation
- **render_director** - Render orchestration
- **asset_registry** - Asset management

### Utilities (`utils/`)
Helper modules:
- **logger** - Production logging system ✅
- **blender_api_tools** - Blender API wrappers

## Documentation

- **ARCHITECTURE.md** - Complete system architecture
- **../VOXEL_WEAVER_COMPLETE.md** - Full implementation summary
- **../WEB_INTERFACE_GUIDE.md** - Web interface guide
- **../backend/voxelweaver/README.md** - Backend documentation

## Development

### Adding a New Subsystem

1. Create module in `subsystems/`
2. Add class with clear docstrings
3. Implement methods with type hints
4. Add to orchestrator workflow
5. Document in ARCHITECTURE.md

### Testing

```bash
# Run tests (when implemented)
pytest tests/

# Run specific module tests
pytest tests/test_prompt_interpreter.py
```

## Status

- **Backend VoxelWeaver**: ✅ Complete (11 modules)
- **Orchestration Layer**: ✅ Foundational structure complete
- **Logger**: ✅ Fully implemented
- **Other Modules**: ⏳ Stubs ready for implementation

## Next Steps

1. Implement scene_orchestrator logic
2. Complete prompt_interpreter NLP
3. Implement subsystem functionality
4. Add comprehensive tests
5. Performance optimization

---

**For detailed architecture information, see [ARCHITECTURE.md](ARCHITECTURE.md)**
