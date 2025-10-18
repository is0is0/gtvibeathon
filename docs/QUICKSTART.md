# Quick Start Guide

Get up and running with Voxel in 5 minutes.

## Prerequisites

Before you begin, ensure you have:

- **Python 3.10+** installed
- **Blender 3.6+** installed
- An **API key** from Anthropic (Claude) or OpenAI (GPT-4)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/voxel.git
cd voxel
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -e .
```

Or with development tools:

```bash
pip install -e ".[dev]"
```

### 4. Configure Environment

```bash
# Copy example config
cp .env.example .env

# Edit .env with your favorite editor
nano .env
```

**Required settings in `.env`:**

```bash
# Add your API key
ANTHROPIC_API_KEY=sk-ant-...  # For Anthropic/Claude
# OR
OPENAI_API_KEY=sk-...         # For OpenAI/GPT-4

# Set AI provider
AI_PROVIDER=anthropic  # or "openai"

# Set Blender path (adjust for your system)
# macOS:
BLENDER_PATH=/Applications/Blender.app/Contents/MacOS/Blender
# Linux:
# BLENDER_PATH=/usr/bin/blender
# Windows:
# BLENDER_PATH=C:\Program Files\Blender Foundation\Blender 4.0\blender.exe
```

### 5. Verify Configuration

```bash
voxel config-check
```

You should see green checkmarks ✓ for all required components.

## First Scene Generation

### Simple Example

```bash
voxel create "a cozy cyberpunk cafe at sunset"
```

This will:
1. Generate a scene concept
2. Create 3D geometry
3. Apply materials and textures
4. Set up lighting and camera
5. Render the final image

The output will be saved to `output/session_YYYYMMDD_HHMMSS/renders/render_iter1.png`

### With Options

```bash
# Higher quality render
voxel create "a mystical forest clearing" --samples 256

# Faster preview with EEVEE
voxel create "a futuristic spaceship interior" --engine EEVEE --samples 64

# Without review (faster)
voxel create "a simple geometric composition" --no-review

# With custom session name
voxel create "an underwater scene" --session underwater_test
```

## Using the Python API

Create a file `my_scene.py`:

```python
from agency3d import Agency3D

# Initialize
agency = Agency3D()

# Generate scene
result = agency.create_scene("a cozy cyberpunk cafe at sunset")

# Check result
if result.success:
    print(f"✓ Render saved to: {result.output_path}")
    print(f"  Generated in {result.iterations} iteration(s)")
    print(f"  Render time: {result.render_time:.2f}s")
else:
    print(f"✗ Failed: {result.error}")
```

Run it:

```bash
python my_scene.py
```

## Understanding Output

After generation, you'll find:

```
output/session_YYYYMMDD_HHMMSS/
├── concept.md              # The AI's scene concept
├── scene.blend             # Blender file (open in Blender!)
├── renders/
│   └── render_iter1.png    # Your rendered image
├── scripts/                # Generated Python scripts
│   ├── 01_builder_iter1.py     # Geometry creation
│   ├── 02_texture_iter1.py     # Materials
│   ├── 03_render_iter1.py      # Camera & lighting
│   └── combined_iter1.py       # All combined
└── metadata.json           # Generation info
```

**Pro tip:** Open `scene.blend` in Blender to explore the 3D scene interactively!

## Common Options

| Option | Description | Example |
|--------|-------------|---------|
| `--samples N` | Render quality (higher = better, slower) | `--samples 256` |
| `--engine ENGINE` | Render engine (CYCLES or EEVEE) | `--engine EEVEE` |
| `--review` / `--no-review` | Enable/disable quality review | `--no-review` |
| `--max-iterations N` | Max refinement iterations | `--max-iterations 3` |
| `--session NAME` | Custom session name | `--session my_scene` |
| `--log-level LEVEL` | Logging verbosity | `--log-level DEBUG` |

## Next Steps

- **Read the full docs**: Check out `README.md` for detailed usage
- **Try example prompts**: See `examples/prompts/example_prompts.md`
- **Explore the API**: Look at `examples/api_usage.py`
- **Customize settings**: Edit `.env` for your preferences
- **Read architecture**: See `docs/ARCHITECTURE.md` to understand internals

## Troubleshooting

### "Blender executable not found"
- Check that Blender is installed
- Verify `BLENDER_PATH` in `.env` points to the correct location
- On macOS, use: `/Applications/Blender.app/Contents/MacOS/Blender`

### "API key not set"
- Make sure `.env` exists (copy from `.env.example`)
- Add your API key for your chosen provider
- Don't commit `.env` to git!

### "Script execution failed"
- Check the logs in `output/session_*/logs/`
- Review generated scripts in `output/session_*/scripts/`
- Try running scripts manually in Blender to debug

### Slow generation
- Use `--no-review` for faster results
- Use `--engine EEVEE` instead of CYCLES
- Reduce `--samples` (try 64 or 128)
- Set `--max-iterations 1`

## Getting Help

- **Documentation**: Read `README.md` and docs in `docs/`
- **Examples**: Check `examples/` directory
- **Issues**: Report bugs on GitHub
- **Community**: Join discussions on GitHub Discussions

Happy scene generation! 🎨
