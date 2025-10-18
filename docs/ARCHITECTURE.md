# 3DAgency Architecture

## System Overview

3DAgency is a multi-agent system that generates 3D scenes in Blender through AI-driven code generation. The system follows a pipeline architecture where specialized agents collaborate to transform natural language prompts into rendered 3D images.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        User Interface                        │
│                    (CLI / Python API)                        │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                     Agency3D Core                            │
│                  (Orchestration Layer)                       │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                  Workflow Orchestrator                       │
│              (Multi-Agent Coordination)                      │
└──┬────────┬────────┬────────┬────────┬────────────────────┬─┘
   │        │        │        │        │                    │
   ▼        ▼        ▼        ▼        ▼                    ▼
┌──────┐┌────────┐┌────────┐┌────────┐┌──────────┐  ┌──────────┐
│Concept││Builder││Texture││Render ││Reviewer │  │Blender  │
│Agent ││Agent  ││Agent  ││Agent  ││Agent    │  │Executor │
└──────┘└────────┘└────────┘└────────┘└──────────┘  └──────────┘
   │        │        │        │        │                    │
   └────────┴────────┴────────┴────────┴────────────────────┘
                              │
                              ▼
                     ┌────────────────┐
                     │  Blender       │
                     │  (External)    │
                     └────────────────┘
```

## Core Components

### 1. Agent System

**Base Agent Class** (`core/agent.py`)
- Abstract base class for all agents
- Handles AI provider abstraction (Anthropic/OpenAI)
- Manages conversation history
- Provides response generation interface

**Specialized Agents** (`agents/`)

1. **ConceptAgent**
   - Input: Natural language prompt
   - Output: Detailed scene concept with objects, mood, lighting plan
   - Role: Scene designer and creative director

2. **BuilderAgent**
   - Input: Scene concept
   - Output: Blender Python script for geometry creation
   - Role: 3D modeler and geometry expert

3. **TextureAgent**
   - Input: Scene concept + geometry script
   - Output: Blender Python script for materials and textures
   - Role: Material artist and shader programmer

4. **RenderAgent**
   - Input: Scene concept
   - Output: Blender Python script for camera, lighting, render settings
   - Role: Cinematographer and lighting artist

5. **ReviewerAgent**
   - Input: Original prompt + concept + all scripts
   - Output: Quality rating + feedback + refinement suggestions
   - Role: Art director and quality control

### 2. Blender Integration Layer

**BlenderExecutor** (`blender/executor.py`)
- Executes Python scripts in Blender via subprocess
- Handles background/GUI modes
- Manages timeouts and error handling
- Provides rendering capabilities

**ScriptManager** (`blender/script_manager.py`)
- Creates and organizes session directories
- Saves generated scripts with naming conventions
- Combines scripts for sequential execution
- Manages metadata and artifacts

### 3. Orchestration Layer

**WorkflowOrchestrator** (`orchestrator/workflow.py`)
- Coordinates agent execution in sequence
- Manages iterative refinement loop
- Handles script execution and rendering
- Collects results and metadata

**Workflow Pipeline:**
```
1. Concept Generation
   ↓
2. Geometry Script Creation
   ↓
3. Material Script Creation
   ↓
4. Render Setup Script Creation
   ↓
5. Script Execution in Blender
   ↓
6. Scene Rendering
   ↓
7. Review (if enabled)
   ↓
8. Refinement Loop (if needed) → back to step 1
```

### 4. Configuration System

**Config** (`core/config.py`)
- Pydantic-based settings management
- Environment variable loading (.env)
- Validation for paths and API keys
- Type-safe configuration access

### 5. Data Models

**Core Models** (`core/models.py`)
- `Message`: Agent conversation messages
- `AgentResponse`: Structured agent outputs
- `SceneResult`: Complete generation results
- `BlenderScriptResult`: Script execution results
- `ReviewFeedback`: Quality assessment data

## Data Flow

### Scene Generation Flow

```
User Prompt
    │
    ▼
┌───────────────────┐
│ ConceptAgent      │ → Scene Concept (markdown)
└───────────────────┘
    │
    ▼
┌───────────────────┐
│ BuilderAgent      │ → geometry.py (Blender script)
└───────────────────┘
    │
    ▼
┌───────────────────┐
│ TextureAgent      │ → materials.py (Blender script)
└───────────────────┘
    │
    ▼
┌───────────────────┐
│ RenderAgent       │ → render_setup.py (Blender script)
└───────────────────┘
    │
    ▼
┌───────────────────┐
│ ScriptManager     │ → combined.py (all scripts)
└───────────────────┘
    │
    ▼
┌───────────────────┐
│ BlenderExecutor   │ → Execute combined.py
└───────────────────┘
    │
    ▼
┌───────────────────┐
│ Blender Process   │ → scene.blend + render.png
└───────────────────┘
    │
    ▼
┌───────────────────┐
│ ReviewerAgent     │ → ReviewFeedback
└───────────────────┘
    │
    ▼
If rating < threshold → Refinement loop
Else → Final output
```

## Session Management

Each generation creates a session directory:

```
output/
└── session_20241017_143022/
    ├── concept.md              # Scene concept
    ├── metadata.json           # Session metadata
    ├── scene.blend             # Saved Blender file
    ├── scripts/
    │   ├── 01_builder_iter1.py
    │   ├── 02_texture_iter1.py
    │   ├── 03_render_iter1.py
    │   ├── combined_iter1.py
    │   └── ...
    ├── renders/
    │   ├── render_iter1.png
    │   └── ...
    └── logs/
        └── execution.log
```

## Extension Points

### Adding New Agents

1. Create agent class inheriting from `Agent`
2. Implement `get_system_prompt()` and `_parse_response()`
3. Add to workflow in `WorkflowOrchestrator`
4. Update data models if needed

### Supporting New AI Providers

1. Add provider case in `Agent._setup_client()`
2. Implement provider-specific call method
3. Update `Config` with provider settings
4. Add API key validation

### Custom Workflows

1. Extend `WorkflowOrchestrator`
2. Override `execute_workflow()` method
3. Implement custom agent coordination logic
4. Use existing agents or create new ones

## Performance Considerations

### Parallelization Opportunities
- Agent calls are currently sequential (by design for context flow)
- Future: Parallel texture + lighting generation
- Batch processing multiple prompts independently

### Caching Strategy
- Agent responses could be cached by prompt hash
- Blender scripts could be cached and reused
- Material libraries could be pre-generated

### Optimization Targets
- Reduce AI API calls through better prompts
- Optimize Blender script execution (combine operations)
- Use faster render engines (EEVEE) for previews
- Implement progressive refinement

## Security Considerations

### Code Execution
- Generated Blender scripts execute arbitrary Python
- Run in isolated Blender process (some protection)
- Future: Sandbox/validate generated scripts
- Review scripts before execution in production

### API Keys
- Stored in .env (git-ignored)
- Never logged or exposed
- Validated at startup
- Use environment-specific keys

### File System
- Output limited to configured directories
- No path traversal in script saving
- Temporary files cleaned up
- Blender files are self-contained

## Testing Strategy

### Unit Tests
- Individual agent logic
- Configuration validation
- Script management
- Data model validation

### Integration Tests
- Multi-agent workflows
- Blender script execution (mocked)
- End-to-end pipeline (with fixtures)

### System Tests
- Real Blender execution
- Full generation pipeline
- Performance benchmarks
- Quality assessments

## Future Architecture Enhancements

1. **Async Agent Execution**
   - Use asyncio for concurrent agent calls
   - Stream agent responses
   - Real-time progress updates

2. **Distributed Processing**
   - Queue-based job system
   - Distributed rendering
   - Agent load balancing

3. **Persistent State**
   - Database for sessions/results
   - Agent learning from feedback
   - Style/preset library

4. **Advanced Features**
   - Animation support (frame generation)
   - Interactive refinement UI
   - Real-time Blender preview
   - Multi-scene composition
