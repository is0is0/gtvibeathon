# Voxel Web Interface Guide

## Overview

The Voxel web interface provides an intuitive, enterprise-grade platform for creating complex 3D scenes in Blender using AI agents. This guide covers installation, configuration, and usage.

## Features

✨ **Interactive Chat Interface**: Describe your scene in natural language
🤖 **Multi-Agent Selection**: Choose which AI agents to employ for your project
📁 **Context Upload**: Upload reference files (3D models, images, videos, text)
🔄 **Dynamic Agent Management**: Add or remove agents during generation
📊 **Real-time Progress**: Watch your scene come to life with live updates
🎨 **Agent Personalities**: Each agent has a unique personality tailored to their role

## Installation

### 1. Prerequisites

- **Python 3.10 or higher**
- **Blender 3.6+** installed on your system
- **API Key** for Anthropic (Claude) or OpenAI (GPT-4)

### 2. Install Voxel

```bash
cd gtvibeathon
pip install -e .
```

### 3. Configuration

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` and configure:

```env
# AI Provider (anthropic or openai)
AI_PROVIDER=anthropic
AI_MODEL=claude-3-5-sonnet-20241022

# API Keys
ANTHROPIC_API_KEY=your_anthropic_api_key_here
# OPENAI_API_KEY=your_openai_api_key_here

# Blender Path
BLENDER_PATH=/Applications/Blender.app/Contents/MacOS/Blender  # macOS
# BLENDER_PATH=/usr/bin/blender  # Linux
# BLENDER_PATH=C:\Program Files\Blender Foundation\Blender 4.0\blender.exe  # Windows

# Web Server (optional)
WEB_HOST=0.0.0.0
WEB_PORT=5000

# Render Settings
RENDER_ENGINE=CYCLES
RENDER_SAMPLES=128
```

## Starting the Web Interface

### Quick Start

```bash
voxel-web
```

The web interface will be available at: `http://localhost:5000`

### Custom Host/Port

```bash
WEB_HOST=127.0.0.1 WEB_PORT=8080 voxel-web
```

## Using the Web Interface

### 1. Welcome Screen

When you first open the application, you'll see:
- **Left Sidebar**: Agent selection panel
- **Center**: Chat interface with welcome message
- **Right Sidebar**: Progress tracking and context management

### 2. Selecting Agents

**Available Agents:**

1. **🎨 Concept Agent** (Creative Visionary)
   - Interprets your vision and creates detailed scene concepts
   - Always recommended

2. **🏗️ Builder Agent** (Technical Architect)
   - Constructs 3D geometry and models
   - Required for all scenes

3. **🎭 Texture Artist Agent** (Artistic Perfectionist)
   - Creates stunning materials and shaders
   - Recommended for visual quality

4. **📸 Cinematographer Agent** (Cinematic Expert)
   - Sets up cameras and lighting
   - Required for rendering

5. **🎬 Animation Director Agent** (Energetic Storyteller)
   - Brings scenes to life with animations
   - Optional, for dynamic scenes

6. **🔍 Quality Reviewer Agent** (Meticulous Critic)
   - Critiques and refines output
   - Optional, for iterative improvement

7. **🦴 Rigging Specialist Agent** (Technical Animator)
   - Creates character rigs and armatures
   - Use for character-based scenes

8. **✨ Compositing Artist Agent** (Visual Effects Wizard)
   - Adds post-processing effects
   - Optional, for cinematic polish

9. **🎞️ Sequence Editor Agent** (Film Editor)
   - Edits multi-shot sequences
   - Optional, for complex narratives

**Selection Tips:**
- Click on any agent card to select/deselect
- Core agents (Concept, Builder, Texture, Render) are selected by default
- Use "Select All" or "Deselect All" buttons for quick configuration
- You can modify agents during generation!

### 3. Uploading Context Files

Click **"📎 Upload Context"** to add reference materials:

**Supported Formats:**

**3D Models:**
- .blend, .obj, .fbx, .dae, .gltf, .glb, .stl, .ply, .3ds, .x3d

**Images:**
- .png, .jpg, .jpeg, .gif, .bmp, .tiff, .webp, .exr, .hdr

**Videos:**
- .mp4, .avi, .mov, .mkv, .webm, .flv

**Text/Data:**
- .txt, .md, .json, .yaml, .yml, .xml

**Examples:**
- Upload an iPhone 3D model (.obj) as reference
- Upload a sunset image (.jpg) for color/mood reference
- Upload a text file (.txt) with specific requirements

### 4. Describing Your Scene

Type your scene description in the chat input box. Be specific!

**Example Prompts:**

**Simple Scenes:**
```
A realistic iPhone 15 Pro against a sunset backdrop with warm orange and pink tones
```

**Complex Scenes:**
```
A cozy cyberpunk cafe at night with neon signs, holographic menus, rain-streaked windows,
multiple tables and chairs, a coffee bar with equipment, ambient blue and purple lighting,
and a view of the city through the window
```

**Animated Scenes:**
```
A futuristic spaceship cockpit with animated holographic displays, blinking console lights,
stars slowly moving past the viewport, and the camera orbiting around the pilot's chair
```

**Character Scenes:**
```
A cartoon robot character with movable joints, smooth metallic surfaces, glowing eyes,
standing in a workshop surrounded by tools and spare parts
```

### 5. Generating the Scene

1. **Select your agents** (left sidebar)
2. **Upload any context files** (optional)
3. **Type your scene description**
4. Click **"🚀 Generate Scene"**

### 6. Monitoring Progress

Watch the **right sidebar** for real-time updates:

**Progress Stages:**
- 🎨 **Concept Generation**: Creating scene concept
- 🏗️ **Geometry Creation**: Building 3D models
- 🎭 **Material Creation**: Applying textures and shaders
- 📸 **Render Setup**: Configuring camera and lights
- 🎬 **Animation Creation**: Adding motion (if enabled)
- 🔧 **Script Execution**: Running in Blender
- 🖼️ **Rendering**: Creating final image/animation

Each stage shows:
- Current agent working
- Status message
- Progress indicator (glowing border when active)

### 7. Dynamic Agent Management

**During Generation**, you can:

**Add Agents:**
1. Click **"➕ Add Agents"** in the right sidebar
2. Select agents to add from the list
3. They'll join the workflow

**Remove Agents:**
1. Click **"➖ Remove Agent"**
2. Select agents to remove
3. They'll be excluded from remaining work

**Use Cases:**
- Add the Compositing Agent mid-way for better post-processing
- Remove the Animation Agent if you decide you only want a static render
- Add the Rigging Agent when you realize you need character animation

### 8. Viewing Results

When generation completes:
- A success modal displays with output information
- Output path shows where the render is saved
- Iteration count and render time are displayed
- Check the output folder for all generated files:
  ```
  output/session_YYYYMMDD_HHMMSS/
    ├── concept.md              # Scene concept
    ├── scripts/                # Generated scripts
    ├── renders/                # Output images/animations
    ├── scene.blend             # Blender file
    └── metadata.json           # Session info
  ```

## Advanced Features

### Context-Aware Generation

When you upload context files, agents automatically consider them:

**Example:**
1. Upload `iphone_model.obj`
2. Upload `sunset_reference.jpg`
3. Prompt: "Create a scene using the uploaded iPhone model against a sunset like the reference image"
4. Agents will:
   - Import the 3D model
   - Extract colors from the sunset image
   - Match the mood and lighting

### Multi-Session Workflow

- Each generation creates a unique session
- Upload files are associated with sessions
- Click **"New Session"** to start fresh
- Previous sessions are preserved in the `output/` directory

### Error Handling

The system includes enterprise-grade error recovery:

- **Agent failures**: Automatic fallback to alternative approaches
- **Script errors**: Simplified script generation on retry
- **Context issues**: Graceful degradation if files can't be processed
- All errors are logged and displayed in the UI

## Tips for Best Results

### Scene Descriptions

**Be Specific:**
❌ "A car"
✅ "A sleek red sports car with chrome details, parked on a wet city street at night with reflections"

**Mention Scale:**
❌ "A room with furniture"
✅ "A 4m x 5m living room with a sofa, coffee table, side tables, floor lamp, and wall art"

**Describe Mood:**
❌ "An outdoor scene"
✅ "A serene forest clearing at golden hour with soft, warm sunlight filtering through trees"

### Agent Selection

**Minimal Setup** (fastest):
- Concept + Builder + Render

**Recommended Setup** (balanced):
- Concept + Builder + Texture + Render

**Premium Setup** (best quality):
- Concept + Builder + Texture + Render + Animation + Reviewer

**Specialized Scenes:**
- **Characters**: Add Rigging Agent
- **Cinematic**: Add Compositing + Sequence Agents
- **Iterative**: Add Reviewer Agent

### Context Files

**Best Practices:**
- Keep file sizes reasonable (< 100MB each)
- Use high-quality reference images (1920x1080+)
- Provide clean 3D models (properly UV-mapped)
- Include descriptive text files for complex requirements

## Troubleshooting

### Server Won't Start

**Check configuration:**
```bash
voxel config-check
```

**Common Issues:**
- Missing `.env` file → Copy from `.env.example`
- Invalid API key → Check your key is correct
- Blender path wrong → Update `BLENDER_PATH` in `.env`

### Generation Fails

1. **Check agent selection**: Ensure Concept + Builder + Render are selected
2. **Simplify prompt**: Try a simpler description first
3. **Check logs**: Look in `logs/` directory for detailed error messages
4. **Review scripts**: Check `output/session_*/scripts/` for issues

### Upload Fails

- **File too large**: Max 500MB per file
- **Unsupported format**: Check supported formats list
- **Permissions**: Ensure write access to `uploads/` directory

### Connection Issues

- **WebSocket errors**: Try refreshing the page
- **Disconnected**: Server may be overloaded, wait and retry
- **Timeout**: Increase timeout in configuration

## Performance Optimization

### For Faster Generation:

1. **Use fewer agents** (minimum: Concept + Builder + Render)
2. **Disable reviewer** (no iterative refinement)
3. **Lower render samples** (64-128 for preview, 256+ for final)
4. **Use EEVEE** instead of CYCLES for faster rendering

### For Better Quality:

1. **Enable all relevant agents**
2. **Add Reviewer agent** for refinement
3. **Increase render samples** (512-1024)
4. **Use CYCLES** render engine
5. **Upload high-quality references**

## Example Workflows

### Workflow 1: Product Visualization

**Goal**: Realistic iPhone render against sunset

1. **Agents**: Concept, Builder, Texture, Render, Compositing
2. **Context**: Upload iPhone reference images
3. **Prompt**:
   ```
   A photorealistic iPhone 15 Pro in deep purple, positioned at a 45-degree angle
   against a stunning sunset backdrop with vibrant orange, pink, and purple gradients.
   The phone should have realistic reflections of the sunset on its screen and glossy
   surfaces. Add subtle rim lighting to highlight the edges.
   ```
4. **Settings**: CYCLES, 256 samples

### Workflow 2: Architectural Interior

**Goal**: Cozy living room

1. **Agents**: Concept, Builder, Texture, Render, Reviewer
2. **Context**: Upload mood board images
3. **Prompt**:
   ```
   A cozy Scandinavian-style living room with natural wood furniture, a gray fabric sofa,
   white walls, indoor plants, minimalist decor, large windows with soft daylight,
   and a warm, inviting atmosphere. Include details like books, cushions, and a coffee cup.
   ```
4. **Settings**: CYCLES, 512 samples, enable review

### Workflow 3: Character Animation

**Goal**: Animated robot character

1. **Agents**: Concept, Builder, Texture, Render, Rigging, Animation
2. **Context**: Upload character sketches
3. **Prompt**:
   ```
   A friendly cartoon robot character with a round head, expressive LED eyes, articulated
   arms and legs, metallic blue and white color scheme. The robot waves hello, then does
   a little spin. Camera orbits around the character during the animation.
   ```
4. **Settings**: EEVEE, 180 frames, 24fps

## Support

For issues or questions:
- Check the main [README.md](README.md)
- Review [CLAUDE.md](CLAUDE.md) for technical details
- Check the `logs/` directory for error details
- Examine generated scripts in `output/session_*/scripts/`

## Next Steps

- Experiment with different agent combinations
- Try uploading various context file types
- Explore dynamic agent management during generation
- Create complex multi-object scenes
- Generate cinematic animations

Enjoy creating with Voxel! 🎨✨
