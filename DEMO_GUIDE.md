# 🎨 Voxel Demo Guide

## Quick Start (3 ways to run the demo)

### **Method 1: Interactive Demo Script** ⭐ **RECOMMENDED**
```bash
cd /Users/justin/Desktop/gthh/gtvibeathon
python3 demo.py
```

### **Method 2: Command Line Interface**
```bash
# Set your API key
export ANTHROPIC_API_KEY="your-api-key-here"

# Run a simple scene
voxel create "a cozy living room with a sofa and coffee table"

# Run with advanced features
voxel create "a futuristic spaceship interior" --enable-rigging --enable-compositing
```

### **Method 3: Python API**
```python
from agency3d import Agency3D, Config

config = Config(
    ai_provider='anthropic',
    anthropic_api_key='your-api-key',
    blender_path='/usr/bin/blender'
)

agency = Agency3D(config)
result = agency.create_scene("a cyberpunk cafe with neon lights")
```

## 🚀 Demo Examples

### **Simple Scenes (30-60 seconds)**
```bash
voxel create "a simple cube with metallic material"
voxel create "a wooden table with a lamp"
voxel create "a colorful sphere"
```

### **Complex Scenes (2-5 minutes)**
```bash
voxel create "a cozy cyberpunk cafe at sunset"
voxel create "a medieval castle with towers and flags"
voxel create "a futuristic city with flying cars"
```

### **Advanced Features**
```bash
# With rigging for characters
voxel create "a robot character" --enable-rigging

# With post-processing effects
voxel create "a magical forest" --enable-compositing

# With video editing
voxel create "a space battle scene" --enable-sequence

# With AI learning
voxel create "a steampunk workshop" --enable-rag
```

## 📋 Prerequisites

### **Required:**
1. **API Key**: Get from [Anthropic Console](https://console.anthropic.com/)
2. **Blender**: Download from [blender.org](https://www.blender.org/download/)

### **Optional:**
- **OpenAI API Key**: For GPT models (alternative to Claude)
- **GPU**: For faster rendering (CUDA/OpenCL)

## 🔧 Setup Commands

```bash
# 1. Install the package
pip install -e .

# 2. Set your API key
export ANTHROPIC_API_KEY="your-key-here"

# 3. Check configuration
voxel config-check

# 4. Run demo
python3 demo.py
```

## 📁 Output Structure

After running a demo, you'll get:
```
demo_output/
├── scene.blend              # Main Blender file
├── scripts/                 # Generated Python scripts
│   ├── concept.py
│   ├── builder.py
│   ├── texture.py
│   ├── render.py
│   └── animation.py
├── renders/                 # Rendered images/videos
│   ├── scene_001.png
│   └── animation.mp4
└── logs/                    # Generation logs
    └── generation.log
```

## 🎯 What You'll See

1. **AI Agents Working**: Watch 6+ agents collaborate in real-time
2. **Blender Scripts**: Generated Python code for 3D creation
3. **Final Scene**: Complete .blend file ready to open in Blender
4. **Rendered Output**: Images and animations of your scene

## 🚨 Troubleshooting

### **"Blender not found"**
```bash
# Find your Blender path
which blender
# or
find /Applications -name "Blender*" -type d

# Set the path in config
voxel create "test" --blender-path "/Applications/Blender.app/Contents/MacOS/Blender"
```

### **"API key not set"**
```bash
export ANTHROPIC_API_KEY="your-key-here"
# or create .env file with:
echo "ANTHROPIC_API_KEY=your-key-here" > .env
```

### **"Permission denied"**
```bash
chmod +x demo.py
python3 demo.py
```

## 🎉 Success!

If everything works, you'll see:
- ✅ Scene generated successfully!
- 📁 Output: ./demo_output/scene_001/
- 🎬 Blender file: ./demo_output/scene_001/scene.blend

**Open the .blend file in Blender to see your AI-generated 3D scene!**
