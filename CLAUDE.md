# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Voxel** is an AI-powered multi-agent system that generates complete 3D scenes and animations in Blender from natural language prompts. The system orchestrates six specialized AI agents (Concept, Builder, Texture, Render, Animation, and Reviewer) to autonomously create complex multi-object scenes with advanced materials, lighting, and cinematic animations.

## Architecture

### Core Components

1. **Agent System** (`src/agency3d/agents/`)
   - **ConceptAgent**: Interprets prompts and generates detailed scene concepts
   - **BuilderAgent**: Writes scripts to create MULTIPLE 3D models (10-20+ per scene)
     - Uses ALL Blender modifiers (Array, Bevel, Boolean, Subdivision, Mirror, Screw, etc.)
     - Creates complex geometry with mesh operations, curves, and beziers
     - Organizes scenes with hierarchical collections
   - **TextureAgent**: Creates advanced materials using ALL 50+ shader nodes
     - Procedural textures (Noise, Voronoi, Wave, Magic, Musgrave, etc.)
     - Complex node networks with mixing and layering
     - PBR, emission, glass, subsurface scattering materials
   - **RenderAgent**: Configures camera, lighting, and render settings
   - **AnimationAgent**: Creates keyframe animations with professional easing
     - Animates 5-10+ objects with varied techniques
     - Uses ALL easing types (Bezier, Sine, Bounce, Elastic, Expo, etc.)
     - Camera animation, material animation, F-Curve modifiers
   - **ReviewerAgent**: Critiques results and suggests improvements

2. **Core Framework** (`src/agency3d/core/`)
   - **Agent**: Base class for all agents with API abstraction (Anthropic/OpenAI)
   - **Config**: Pydantic-based configuration management with .env support
   - **Models**: Data models for messages, responses, and results

3. **Blender Integration** (`src/agency3d/blender/`)
   - **BlenderExecutor**: Executes Python scripts in Blender via subprocess
   - **ScriptManager**: Manages script lifecycle, sessions, and file organization

4. **Orchestrator** (`src/agency3d/orchestrator/`)
   - **WorkflowOrchestrator**: Coordinates multi-agent workflow with iterative refinement

5. **CLI** (`src/agency3d/cli.py`)
   - Typer-based CLI with rich terminal output
   - Commands: `create`, `config-check`, `version`

### Workflow Pipeline

```
User Prompt → Concept Agent → Builder Agent → Texture Agent → Render Agent
                                                                    ↓
                    ← Reviewer Agent (optional) ← Execute in Blender
                                ↓
                        Refine (if needed) or Output Final Render
```

## Development Commands

### Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"

# Configure environment
cp .env.example .env
# Edit .env with API keys and Blender path
```

### Running the Application

```bash
# Basic usage (includes animation by default)
voxel create "a cozy cyberpunk cafe at sunset"

# Static scene with advanced materials
voxel create "mystical forest with glowing crystals" --samples 256 --engine CYCLES

# Animated scene
voxel create "floating islands with waterfalls, camera orbiting around them"

# Without animation
voxel create "still life scene" --no-animation

# Check configuration
voxel config-check

# Show version
voxel version
```

### Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=agency3d --cov-report=html

# Run specific test file
pytest tests/test_agents.py

# Run with verbose output
pytest -v
```

### Code Quality

```bash
# Format code
black src/ tests/

# Lint
ruff check src/ tests/

# Fix auto-fixable issues
ruff check --fix src/ tests/

# Type checking
mypy src/
```

## Key Design Patterns

### Agent Communication

All agents inherit from the `Agent` base class and follow a consistent pattern:

```python
class CustomAgent(Agent):
    def get_system_prompt(self) -> str:
        # Return specialized system prompt

    def _parse_response(self, response_text: str, context: dict) -> AgentResponse:
        # Extract structured data from AI response
```

Agents maintain conversation history and support both Anthropic and OpenAI APIs through a unified interface.

### Script Generation and Execution

1. Agents generate Blender Python scripts as text
2. ScriptManager saves scripts to session directories
3. BlenderExecutor runs scripts via subprocess in Blender
4. Scripts are executed sequentially: geometry → materials → render setup

### Session Management

Each generation creates a session directory:
```
output/
  session_YYYYMMDD_HHMMSS/
    concept.md              # Scene concept
    scripts/                # All generated scripts
      01_builder_iter1.py
      02_texture_iter1.py
      03_render_iter1.py
      combined_iter1.py
    renders/                # Output images
      render_iter1.png
    metadata.json           # Session metadata
    scene.blend             # Saved Blender file
```

### Configuration Management

Configuration uses Pydantic Settings with `.env` file support:
- Validates API keys and paths on initialization
- Supports both Anthropic and OpenAI providers
- Configurable render settings (samples, engine)
- Adjustable agent behavior (temperature, max_tokens)

## Blender Python Patterns

### Script Structure

All generated scripts follow this pattern:

```python
import bpy
import math

# 1. Clear scene (Builder only)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# 2. Create/modify objects
obj = bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0))
obj = bpy.context.active_object
obj.name = "MyObject"

# 3. Apply modifiers/materials/settings
# ... agent-specific code ...
```

### Common Blender Operations

- **Object creation**: `bpy.ops.mesh.primitive_*_add()`
- **Material setup**: Use shader nodes with `mat.use_nodes = True`
- **Camera positioning**: Set `camera.location` and `camera.rotation_euler`
- **Lighting**: Create light data objects (`bpy.data.lights.new()`)
- **Rendering**: Configure via `bpy.context.scene.render.*`

## Iterative Refinement

When `enable_reviewer=True` and `auto_refine=True`:

1. Generate initial scene
2. Reviewer critiques (rating 1-10, strengths, improvements)
3. If rating < 7 or `should_refine=True`, regenerate with feedback
4. Repeat up to `max_iterations` times
5. Each iteration creates new scripts and renders

## Error Handling

- **Script execution errors**: Captured in `BlenderScriptResult.stderr`
- **API errors**: Logged and propagated with context
- **Configuration errors**: Validated at startup with clear messages
- **Blender not found**: Checked during initialization

## Adding New Agents

1. Create class in `src/agency3d/agents/new_agent.py`
2. Inherit from `Agent` base class
3. Implement `get_system_prompt()` and `_parse_response()`
4. Add to `__init__.py` and orchestrator workflow
5. Update documentation

## Testing Strategy

- **Unit tests**: Test individual agents and components
- **Integration tests**: Test workflow orchestration
- **Mock AI responses**: Use fixtures for reproducible tests
- **Blender mocking**: Mock subprocess calls for executor tests

## Common Issues

### Blender Path Issues
- macOS: `/Applications/Blender.app/Contents/MacOS/Blender`
- Linux: `/usr/bin/blender`
- Windows: `C:\Program Files\Blender Foundation\Blender X.X\blender.exe`

### API Rate Limits
- Implement retry logic with exponential backoff
- Monitor token usage in responses

### Script Execution Failures
- Check generated scripts in `output/*/scripts/`
- Review Blender stdout/stderr in logs
- Test scripts manually in Blender

## Performance Optimization

- Scripts execute sequentially (required for Blender state)
- Agent responses are synchronous (AI API calls)
- Render time scales with samples (use lower samples for testing)
- Use EEVEE for faster preview renders, CYCLES for quality

## Future Extensions

- Support for animations (frame-by-frame generation)
- Image-to-3D conversion
- Style transfer between scenes
- Asset library integration
- Real-time preview mode
- Batch processing multiple prompts
