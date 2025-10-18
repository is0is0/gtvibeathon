# voxel

a calm space for creating, learning, and experimenting with 3d worlds. voxel helps artists and developers shape materials, light, and form through simple procedural tools and intelligent guidance. it's built to feel effortless—whether you're sketching a concept, training a model, or generating scenes from scratch.

## features

procedural 3d generation with adaptive learning

real-time material and lighting synthesis

modular design for training and experimentation

minimal, focused interface

## vision

voxel exists to make 3d creation intuitive, meditative, and open.

## getting started

### prerequisites

python 3.10 or higher
blender 3.6+ installed on your system
api key for anthropic (claude) or openai (gpt-4)

### installation

1. clone the repository
```bash
git clone https://github.com/yourusername/voxel.git
cd voxel
```

2. create a virtual environment
```bash
python -m venv venv
source venv/bin/activate  # on windows: venv\scripts\activate
```

3. install the package
```bash
pip install -e .
```

4. configure environment
```bash
cp .env.example .env
# edit .env and add your api key and blender path
```

### web interface

start the web interface:

```bash
# easy startup script
./start_web.sh  # on macos/linux
# or
start_web.bat  # on windows

# or manually
voxel-web
```

then open your browser to: `http://localhost:5000`

features:
- interactive chat interface for scene descriptions
- visual agent selection with multi-select
- drag-and-drop context file upload (3d models, images, videos)
- real-time progress tracking
- dynamic agent management during generation
- unique agent personalities

see [WEB_INTERFACE_GUIDE.md](WEB_INTERFACE_GUIDE.md) for detailed usage instructions.

### command line interface

```bash
# generate a scene from a prompt
voxel create "a cozy cyberpunk cafe at sunset"

# with custom settings
voxel create "a mysterious forest clearing" --samples 256 --engine CYCLES

# review mode enabled (auto-refinement)
voxel create "a futuristic spaceship interior" --review --max-iterations 3
```

## architecture

### agent system

voxel uses six specialized agents:

1. **concept agent** - interprets prompts and generates detailed scene concepts
2. **builder agent** - writes blender python scripts to create multiple 3d models (10-20+ objects per scene)
   - uses all modifiers (array, bevel, boolean, subdivision, mirror, screw, etc.)
   - creates complex geometry with mesh operations and curves
   - organizes scenes with hierarchical collections
3. **texture agent** - creates advanced materials using all 50+ shader nodes
   - procedural textures (noise, voronoi, wave, magic, musgrave, etc.)
   - complex node networks with mixing and layering
   - pbr materials, emission, glass, subsurface scattering
   - bump and normal mapping for surface detail
4. **render agent** - configures camera, lighting, and render settings
5. **animation agent** - creates cinematic animations with keyframes
   - animates 5-10+ objects per scene with varied techniques
   - uses all easing types (bezier, sine, bounce, elastic, etc.)
   - camera animation for dynamic shots
   - material property animation
   - f-curve modifiers and constraints
6. **reviewer agent** - critiques results and suggests improvements

### workflow

```
user prompt
    ↓
concept agent (generates scene description)
    ↓
builder agent (creates 10-20+ objects with advanced geometry)
    ↓
texture agent (applies advanced shader node materials)
    ↓
render agent (sets up camera/lighting)
    ↓
animation agent (creates keyframe animations with easing)
    ↓
blender execution (runs all scripts)
    ↓
reviewer agent (optional critique)
    ↓
final render or animation
```

## development

### project structure

```
voxel/
├── src/voxel/
│   ├── agents/          # ai agent implementations
│   ├── blender/         # blender integration layer
│   ├── core/            # core framework
│   ├── database/        # database models and management
│   ├── orchestrator/    # workflow engine
│   ├── voxelweaver/     # voxelweaver backend modules
│   ├── utils/           # utilities
│   ├── web/             # web interface
│   └── cli.py           # command-line interface
├── demos/               # demo scripts organized by category
│   ├── basic/           # simple demos
│   ├── houses/          # house generation demos
│   └── advanced/        # complex pipeline demos
├── training/            # training scripts and demos
├── database/            # database files and migrations
├── tests/               # test suite
├── examples/            # api examples and usage
└── docs/                # documentation
```

### running tests

```bash
# install dev dependencies
pip install -e ".[dev]"

# run tests
pytest

# with coverage
pytest --cov=voxel --cov-report=html
```

### code quality

```bash
# format code
black src/ tests/

# lint
ruff check src/ tests/

# type check
mypy src/
```

## advanced usage

### python api

```python
from voxel import Voxel
from voxel.config import Config

# initialize
config = Config()
voxel = Voxel(config)

# generate scene
result = voxel.create_scene(
    prompt="a mystical library with floating books",
    enable_review=True,
    max_iterations=2
)

print(f"render saved to: {result.output_path}")
print(f"scripts generated: {len(result.scripts)}")
```

### custom agent configuration

```python
from voxel.agents import ConceptAgent, BuilderAgent
from voxel.core import AgentConfig

# custom agent settings
agent_config = AgentConfig(
    model="claude-3-5-sonnet-20241022",
    temperature=0.7,
    max_tokens=4000
)

concept_agent = ConceptAgent(agent_config)
```

## example prompts

### static scenes
- "a cozy cyberpunk cafe at sunset with multiple tables, chairs, decorations, and ambient lighting"
- "a mystical forest clearing with ancient ruins, glowing crystals, and atmospheric fog"
- "a medieval blacksmith workshop filled with tools, anvils, and a glowing forge"

### animated scenes
- "a futuristic spaceship cockpit with animated holographic displays, blinking lights, and camera orbiting the scene"
- "an underwater coral reef with fish swimming, kelp swaying, and camera descending from surface to sea floor"
- "a cyberpunk city street with neon signs flickering, steam rising, holographic ads animating, camera flying through"
- "floating islands with waterfalls, slowly drifting in the sky, camera circling around them"

see `examples/animation_examples.md` for more animation prompt ideas!

## database system

voxel includes a comprehensive sqlite database system for tracking all projects, generations, and analytics:

### database features
- **project management**: track multiple projects with metadata
- **generation history**: complete history of all scene generations
- **agent analytics**: performance metrics for each ai agent
- **quality tracking**: monitor quality scores and trends over time
- **search & discovery**: search through all generations by prompt text
- **system analytics**: comprehensive usage statistics and reporting

### database commands
```bash
# list all projects
voxel list-projects

# show project history
voxel project-history 1

# show system statistics
voxel stats --days 30

# search generations
voxel search "cyberpunk" --limit 10

# create a new project
voxel create-project "my project" --description "a test project"
```

### database api
```python
from voxel import Voxel

voxel = Voxel()

# create a project
project = voxel.create_project("my scene", "a test project")

# get analytics
analytics = voxel.get_system_analytics(days=30)
print(f"success rate: {analytics['success_rate']:.1f}%")

# search generations
results = voxel.search_generations("house", limit=10)
```

see [DATABASE.md](docs/DATABASE.md) for complete database documentation.

## configuration

see `.env.example` for all available configuration options. key settings:

- `AI_PROVIDER`: choose between "anthropic" or "openai"
- `AI_MODEL`: specific model to use
- `BLENDER_PATH`: path to your blender executable
- `DATABASE_URL`: database connection url (default: sqlite:///database/voxel.db)
- `RENDER_SAMPLES`: quality of final render (higher = better but slower)
- `ENABLE_REVIEWER`: enable automatic critique and refinement
- `ENABLE_ANIMATION`: enable animation generation (default: true)
- `ANIMATION_FRAMES`: default animation length in frames (default: 180)
- `ANIMATION_FPS`: animation framerate (default: 24fps for cinematic look)

## contributing

contributions are welcome! please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## license

mit license - see [LICENSE](LICENSE) for details

## acknowledgments

- built with [anthropic claude](https://www.anthropic.com/) and [openai gpt](https://openai.com/)
- powered by [blender](https://www.blender.org/)

## troubleshooting

### blender not found
ensure `BLENDER_PATH` in `.env` points to your blender executable.

### api errors
check that your api key is valid and has sufficient credits.

### render failures
check the generated scripts in `output/<session>/scripts/` and the logs in `logs/`.

## support

- issues: [github issues](https://github.com/yourusername/voxel/issues)
- discussions: [github discussions](https://github.com/yourusername/voxel/discussions)
