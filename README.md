# Voxel

> AI-powered autonomous 3D scene generation system for Blender

**Voxel** is a local-first Python tool that orchestrates a team of AI agents to automatically create complete 3D scenes in Blender. Simply describe what you want, and watch as autonomous agents brainstorm concepts, generate geometry, apply textures, configure lighting, and render professional results.

## ✨ Features

- 🤖 **Multi-Agent System**: Six specialized AI agents work together (Concept, Builder, Texture, Render, Animation, Reviewer)
- 🎨 **Natural Language Input**: Describe scenes in plain English
- 🔧 **Advanced Code Generation**: Agents write sophisticated Blender Python scripts using ALL available features
- 🎬 **Complete Pipeline**: From concept to final rendered image or animation
- 🎞️ **Cinematic Animation**: Keyframe animation with professional easing and motion
- 🎭 **Multiple Models**: Build complex scenes with 10-20+ objects per scene
- 🌈 **Advanced Materials**: Use all 50+ shader nodes for stunning visuals
- 🔄 **Iterative Refinement**: Auto-critique and improve results
- 🏠 **Local-First**: Runs entirely on your machine with your Blender installation

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- Blender 3.6+ installed on your system
- An API key for Anthropic (Claude) or OpenAI (GPT-4)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/voxel.git
cd voxel
```

2. **Create a virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install the package**
```bash
pip install -e .
```

4. **Configure environment**
```bash
cp .env.example .env
# Edit .env and add your API key and Blender path
```

### Web Interface (Recommended)

**Start the web interface:**

```bash
# Easy startup script
./start_web.sh  # On macOS/Linux
# OR
start_web.bat  # On Windows

# OR manually
voxel-web
```

Then open your browser to: `http://localhost:5000`

**Features:**
- 🎨 Interactive chat interface for scene descriptions
- 🤖 Visual agent selection with multi-select
- 📁 Drag-and-drop context file upload (3D models, images, videos)
- 📊 Real-time progress tracking
- ⚡ Dynamic agent management during generation
- 🎭 Unique agent personalities

See [WEB_INTERFACE_GUIDE.md](WEB_INTERFACE_GUIDE.md) for detailed usage instructions.

### Command Line Interface

```bash
# Generate a scene from a prompt
voxel create "a cozy cyberpunk cafe at sunset"

# With custom settings
voxel create "a mysterious forest clearing" --samples 256 --engine CYCLES

# Review mode enabled (auto-refinement)
voxel create "a futuristic spaceship interior" --review --max-iterations 3
```

## 🏗️ Architecture

### Agent System

Voxel uses six specialized agents:

1. **Concept Agent** - Interprets prompts and generates detailed scene concepts
2. **Builder Agent** - Writes Blender Python scripts to create MULTIPLE 3D models (10-20+ objects per scene)
   - Uses ALL modifiers (Array, Bevel, Boolean, Subdivision, Mirror, Screw, etc.)
   - Creates complex geometry with mesh operations and curves
   - Organizes scenes with hierarchical collections
3. **Texture Agent** - Creates advanced materials using ALL 50+ shader nodes
   - Procedural textures (Noise, Voronoi, Wave, Magic, Musgrave, etc.)
   - Complex node networks with mixing and layering
   - PBR materials, emission, glass, subsurface scattering
   - Bump and normal mapping for surface detail
4. **Render Agent** - Configures camera, lighting, and render settings
5. **Animation Agent** - Creates cinematic animations with keyframes
   - Animates 5-10+ objects per scene with varied techniques
   - Uses ALL easing types (Bezier, Sine, Bounce, Elastic, etc.)
   - Camera animation for dynamic shots
   - Material property animation
   - F-Curve modifiers and constraints
6. **Reviewer Agent** - Critiques results and suggests improvements

### Workflow

```
User Prompt
    ↓
Concept Agent (generates scene description)
    ↓
Builder Agent (creates 10-20+ objects with advanced geometry)
    ↓
Texture Agent (applies advanced shader node materials)
    ↓
Render Agent (sets up camera/lighting)
    ↓
Animation Agent (creates keyframe animations with easing)
    ↓
Blender Execution (runs all scripts)
    ↓
Reviewer Agent (optional critique)
    ↓
Final Render or Animation
```

## 🛠️ Development

### Project Structure

```
voxel/
├── src/agency3d/
│   ├── agents/          # AI agent implementations
│   ├── blender/         # Blender integration layer
│   ├── core/            # Core framework
│   ├── orchestrator/    # Workflow engine
│   └── cli.py           # Command-line interface
├── tests/               # Test suite
├── examples/            # Example prompts and outputs
└── docs/                # Documentation
```

### Running Tests

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# With coverage
pytest --cov=agency3d --cov-report=html
```

### Code Quality

```bash
# Format code
black src/ tests/

# Lint
ruff check src/ tests/

# Type check
mypy src/
```

## 📖 Advanced Usage

### Python API

```python
from agency3d import Agency3D
from agency3d.config import Config

# Initialize
config = Config()
agency = Agency3D(config)

# Generate scene
result = agency.create_scene(
    prompt="a mystical library with floating books",
    enable_review=True,
    max_iterations=2
)

print(f"Render saved to: {result.output_path}")
print(f"Scripts generated: {len(result.scripts)}")
```

### Custom Agent Configuration

```python
from agency3d.agents import ConceptAgent, BuilderAgent
from agency3d.core import AgentConfig

# Custom agent settings
agent_config = AgentConfig(
    model="claude-3-5-sonnet-20241022",
    temperature=0.7,
    max_tokens=4000
)

concept_agent = ConceptAgent(agent_config)
```

## 🎯 Example Prompts

### Static Scenes
- "a cozy cyberpunk cafe at sunset with multiple tables, chairs, decorations, and ambient lighting"
- "a mystical forest clearing with ancient ruins, glowing crystals, and atmospheric fog"
- "a medieval blacksmith workshop filled with tools, anvils, and a glowing forge"

### Animated Scenes
- "a futuristic spaceship cockpit with animated holographic displays, blinking lights, and camera orbiting the scene"
- "an underwater coral reef with fish swimming, kelp swaying, and camera descending from surface to sea floor"
- "a cyberpunk city street with neon signs flickering, steam rising, holographic ads animating, camera flying through"
- "floating islands with waterfalls, slowly drifting in the sky, camera circling around them"

See `examples/animation_examples.md` for more animation prompt ideas!

## 🔧 Configuration

See `.env.example` for all available configuration options. Key settings:

- `AI_PROVIDER`: Choose between "anthropic" or "openai"
- `AI_MODEL`: Specific model to use
- `BLENDER_PATH`: Path to your Blender executable
- `RENDER_SAMPLES`: Quality of final render (higher = better but slower)
- `ENABLE_REVIEWER`: Enable automatic critique and refinement
- `ENABLE_ANIMATION`: Enable animation generation (default: true)
- `ANIMATION_FRAMES`: Default animation length in frames (default: 180)
- `ANIMATION_FPS`: Animation framerate (default: 24fps for cinematic look)

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

MIT License - see [LICENSE](LICENSE) for details

## 🙏 Acknowledgments

- Built with [Anthropic Claude](https://www.anthropic.com/) and [OpenAI GPT](https://openai.com/)
- Powered by [Blender](https://www.blender.org/)

## 🐛 Troubleshooting

### Blender not found
Ensure `BLENDER_PATH` in `.env` points to your Blender executable.

### API errors
Check that your API key is valid and has sufficient credits.

### Render failures
Check the generated scripts in `output/<session>/scripts/` and the logs in `logs/`.

## 📮 Support

- Issues: [GitHub Issues](https://github.com/yourusername/voxel/issues)
- Discussions: [GitHub Discussions](https://github.com/yourusername/voxel/discussions)
