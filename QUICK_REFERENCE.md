# 3DAgency - Quick Reference Card

**Version:** 1.0.0
**Status:** Production Ready ✅
**Agents:** 11 (6 Core + 5 Advanced)

---

## 🚀 Quick Start

```bash
# 1. Configure
cp .env.example .env
# Edit .env: add API key and Blender path

# 2. Install
pip install -e .

# 3. Create!
3dagency create "your scene description here"
```

---

## 📚 Documentation Map

| File | Purpose | When to Read |
|------|---------|--------------|
| **README.md** | User guide & installation | Start here |
| **QUICKSTART.md** | 5-minute setup | First time setup |
| **PROJECT_COMPLETE.md** | Complete feature list | Reference all capabilities |
| **CLAUDE.md** | Developer guide | Contributing code |
| **ARCHITECTURE.md** | System design | Understanding internals |
| **ENHANCEMENTS.md** | Enhancement details | See what changed |
| **ADVANCED_FEATURES.md** | Advanced capabilities | Using physics, particles, etc. |
| **CONTRIBUTING.md** | How to contribute | Before submitting PRs |
| **examples/animation_examples.md** | 50+ animation ideas | Inspiration |

---

## 🎯 Common Commands

```bash
# Basic scene
3dagency create "cozy cafe with tables and chairs"

# Animated scene
3dagency create "rotating geometric shapes" --enable-animation

# High quality
3dagency create "luxury watch" --render-samples 256

# Physics simulation
3dagency create "falling dominoes" --enable-physics

# With particles
3dagency create "fireflies in forest" --enable-particles

# Procedural modeling
3dagency create "city block" --enable-geometry-nodes

# From asset library
3dagency create "conference room" --import-from-library

# Configuration check
3dagency config-check

# Help
3dagency --help
```

---

## 🤖 The 11 Agents

### Core Pipeline (6)
1. **ConceptAgent** - Conceptualizes scene
2. **BuilderAgent** - Creates 10-20+ objects
3. **TextureAgent** - Applies materials (50+ nodes)
4. **RenderAgent** - Camera & lighting
5. **AnimationAgent** - Keyframe animation
6. **ReviewerAgent** - Quality control

### Advanced Features (5)
7. **GeometryNodesAgent** - Procedural modeling
8. **PhysicsAgent** - Simulations (rigid body, cloth, fluid, smoke)
9. **ParticlesAgent** - Particles & hair systems
10. **SceneAnalyzerAgent** - Learn from existing scenes
11. **ImporterAgent** - Import assets (USD, FBX, OBJ, .blend)

---

## ✨ Key Features

- ✅ **10-20+ objects** per scene
- ✅ **50+ shader nodes** for materials
- ✅ **All easing types** for animation
- ✅ **Physics simulation** (rigid body, cloth, fluid, smoke)
- ✅ **Particle systems** (emitters, hair)
- ✅ **Asset library** management
- ✅ **Scene analysis** (learn from .blend files)

---

## 🎨 Example Prompts

### Multi-Object Scenes
```
"medieval blacksmith workshop with anvil, forge, hammers, tongs, horseshoes"
"sci-fi laboratory with holographic displays, robotic arms, control panels"
"underwater coral reef with fish, kelp, rocks, anemones"
```

### Animated Scenes
```
"floating islands with waterfalls, camera orbiting around"
"geometric shapes rotating at different speeds with pulsing colors"
"cyberpunk street with flickering neon signs and rising steam"
```

### Physics & Particles
```
"dominoes arranged in spiral that fall in sequence"
"fireflies in magical forest with falling leaves"
"water pouring from jug into glass"
```

More examples in `examples/animation_examples.md`

---

## 🔧 Configuration (.env)

```bash
# AI Provider
AI_PROVIDER=anthropic          # or "openai"
AI_MODEL=claude-3-5-sonnet-20241022
ANTHROPIC_API_KEY=your_key_here

# Blender
BLENDER_PATH=/path/to/blender

# Rendering
RENDER_ENGINE=CYCLES           # or "EEVEE"
RENDER_SAMPLES=128             # 64=fast, 256=quality
RENDER_RESOLUTION_X=1920
RENDER_RESOLUTION_Y=1080

# Animation
ENABLE_ANIMATION=true
ANIMATION_FRAMES=180
ANIMATION_FPS=24

# Agents
ENABLE_REVIEWER=true
MAX_ITERATIONS=3
```

---

## 🐍 Python API

```python
from agency3d import Agency3D

# Initialize
agency = Agency3D()

# Create scene
result = agency.create_scene(
    prompt="cozy cafe with tables and chairs",
    enable_animation=True,
    render_samples=128
)

# Check result
if result.success:
    print(f"Scene: {result.output_path}")
    print(f"Time: {result.render_time}s")

# Access scripts
for script in result.scripts:
    print(f"Script: {script}")
```

See `examples/example_api_usage.py` for more examples.

---

## 🛠️ Development

```bash
# Setup
python3 -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
pre-commit install

# Test
pytest
pytest --cov=agency3d

# Format
make format
black src/ tests/
ruff check src/ tests/ --fix

# Type check
mypy src/

# All checks
make check
```

---

## 🔍 Troubleshooting

### Blender not found
```bash
# Check path
which blender

# Update .env
BLENDER_PATH=/correct/path/to/blender
```

### API key issues
```bash
# Verify key is set
echo $ANTHROPIC_API_KEY

# Update .env
ANTHROPIC_API_KEY=sk-ant-...
```

### Slow rendering
```bash
# Use EEVEE for speed
RENDER_ENGINE=EEVEE

# Lower samples
RENDER_SAMPLES=64

# Disable animation for static scenes
ENABLE_ANIMATION=false
```

---

## 📊 Project Stats

- **Files:** 50+
- **Code:** 7,000+ lines
- **Agents:** 11
- **Docs:** 9 pages
- **Tests:** 4 files
- **Modifiers:** 20+
- **Shader Nodes:** 50+
- **Easing Types:** 12+

---

## 🎯 What's Included vs Missing

### ✅ Included
- Multi-agent orchestration
- 10-20+ objects per scene
- ALL Blender modifiers
- 50+ shader nodes
- Keyframe animation (all easing)
- Physics simulation
- Particle systems
- Geometry nodes
- Asset library
- Scene analysis

### 🔴 Not Included (Yet)
- Blender addon UI
- Agent fine-tuning
- Character rigging
- Compositing nodes
- Video sequence editor

**See how to add:** `python3 scripts/enhance_capabilities.py --show-limitations`

---

## 🚦 Status Indicators

When running `3dagency create`:

- 🟢 **Success** - Scene generated successfully
- 🟡 **Review** - Needs refinement (will auto-retry)
- 🔴 **Error** - Check logs for details

---

## 💡 Tips

1. **Start simple** - Test basic prompts first
2. **Use EEVEE** - Faster iteration
3. **Lower samples** - 64-128 for testing
4. **Disable review** - Use `--no-review` for speed
5. **Check scripts** - Review in `output/*/scripts/`
6. **Open in Blender** - Explore generated `.blend` files

---

## 📦 File Locations

```
output/
└── scene_YYYYMMDD_HHMMSS/
    ├── scene.blend          # Blender file
    ├── render.png           # Rendered image
    ├── animation/           # Animation frames
    └── scripts/
        ├── 01_builder.py
        ├── 02_texture.py
        ├── 03_render.py
        ├── 04_animation.py
        └── combined.py      # All scripts combined
```

---

## 🔗 Quick Links

- **Blender API:** https://docs.blender.org/api/current/
- **Shader Nodes:** https://docs.blender.org/manual/en/latest/render/shader_nodes/
- **Animation:** https://docs.blender.org/manual/en/latest/animation/

---

## 🎊 You're Ready!

```bash
3dagency create "your imagination here"
```

For more help: `3dagency --help` or read **README.md**

**Happy creating!** 🎨✨
