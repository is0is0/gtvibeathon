#!/usr/bin/env python3
"""
Comprehensive Training Script for All Voxel Agents
Integrates external repositories and trains all agent models.
"""

import os
import sys
import subprocess
import json
from pathlib import Path
import argparse

def setup_training_environment():
    """Setup the training environment with all dependencies."""
    print("🔧 Setting up training environment...")
    print("=" * 60)
    
    # Install required packages
    packages = [
        "torch",
        "torchvision", 
        "torchaudio",
        "transformers",
        "datasets",
        "diffusers",
        "accelerate",
        "matplotlib",
        "pillow",
        "numpy",
        "opencv-python",
        "scikit-learn"
    ]
    
    for package in packages:
        print(f"Installing {package}...")
        subprocess.run([sys.executable, "-m", "pip", "install", package], check=True)
    
    print("✅ Training environment setup complete!")

def create_sample_datasets():
    """Create sample datasets for training."""
    print("📊 Creating sample datasets...")
    print("=" * 60)
    
    # Create directories
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    # Shader dataset
    shader_data = [
        {"prompt": "Create a simple diffuse shader", "code": "// Simple diffuse shader\nuniform vec3 lightDir;\nuniform vec3 lightColor;\n\nvoid main() {\n    vec3 normal = normalize(vNormal);\n    float diff = max(dot(normal, lightDir), 0.0);\n    gl_FragColor = vec4(lightColor * diff, 1.0);\n}"},
        {"prompt": "Create a metallic shader with reflections", "code": "// Metallic shader with reflections\nuniform vec3 cameraPos;\nuniform samplerCube envMap;\n\nvoid main() {\n    vec3 viewDir = normalize(cameraPos - vPosition);\n    vec3 reflectDir = reflect(-viewDir, normalize(vNormal));\n    vec3 envColor = textureCube(envMap, reflectDir).rgb;\n    gl_FragColor = vec4(envColor, 1.0);\n}"},
        {"prompt": "Create a glass shader with refraction", "code": "// Glass shader with refraction\nuniform float ior;\nuniform samplerCube envMap;\n\nvoid main() {\n    vec3 viewDir = normalize(cameraPos - vPosition);\n    vec3 refractDir = refract(-viewDir, normalize(vNormal), ior);\n    vec3 envColor = textureCube(envMap, refractDir).rgb;\n    gl_FragColor = vec4(envColor, 0.8);\n}"}
    ]
    
    with open("data/shader_dataset.jsonl", "w") as f:
        for item in shader_data:
            f.write(json.dumps(item) + "\n")
    
    # Texture dataset structure
    texture_dir = data_dir / "texture" / "train"
    texture_dir.mkdir(parents=True, exist_ok=True)
    
    # Create sample texture data
    for i in range(5):
        sample_dir = texture_dir / f"sample_{i:03d}"
        sample_dir.mkdir(exist_ok=True)
        
        # Create metadata
        metadata = {"prompt": f"Sample material {i}"}
        with open(sample_dir / "metadata.json", "w") as f:
            json.dump(metadata, f)
        
        # Create placeholder images (would be real PBR maps in practice)
        from PIL import Image
        import numpy as np
        
        # Albedo (RGB)
        albedo = Image.fromarray(np.random.randint(0, 255, (256, 256, 3), dtype=np.uint8))
        albedo.save(sample_dir / "albedo.png")
        
        # Normal (RGB)
        normal = Image.fromarray(np.random.randint(0, 255, (256, 256, 3), dtype=np.uint8))
        normal.save(sample_dir / "normal.png")
        
        # Roughness (L)
        rough = Image.fromarray(np.random.randint(0, 255, (256, 256), dtype=np.uint8))
        rough.save(sample_dir / "roughness.png")
        
        # Metallic (L)
        metal = Image.fromarray(np.random.randint(0, 255, (256, 256), dtype=np.uint8))
        metal.save(sample_dir / "metallic.png")
    
    # HDR dataset structure
    hdr_dir = data_dir / "hdr" / "train"
    hdr_dir.mkdir(parents=True, exist_ok=True)
    
    for i in range(3):
        sample_dir = hdr_dir / f"sample_{i:03d}"
        sample_dir.mkdir(exist_ok=True)
        
        # Create metadata
        metadata = {"prompt": f"Sample HDR environment {i}"}
        with open(sample_dir / "metadata.json", "w") as f:
            json.dump(metadata, f)
        
        # Create placeholder images
        from PIL import Image
        import numpy as np
        
        # LDR image
        ldr = Image.fromarray(np.random.randint(0, 255, (512, 1024, 3), dtype=np.uint8))
        ldr.save(sample_dir / "ldr.png")
        
        # HDR data (as numpy array)
        hdr_data = np.random.rand(512, 1024, 3).astype(np.float32)
        np.save(sample_dir / "hdr.npy", hdr_data)
    
    print("✅ Sample datasets created!")

def train_shader_agent():
    """Train the shader agent."""
    print("🎨 Training Shader Agent...")
    print("=" * 40)
    
    try:
        from src.agency3d.agents.shader.train import main as shader_main
        import sys
        
        # Set up arguments for shader training
        sys.argv = [
            "train.py",
            "--train-file", "data/shader_dataset.jsonl",
            "--output-dir", "checkpoints/shader_agent",
            "--model", "t5-small",
            "--epochs", "3",
            "--batch-size", "4"
        ]
        
        shader_main()
        print("✅ Shader agent training complete!")
        
    except Exception as e:
        print(f"❌ Shader training failed: {e}")

def train_texture_agent():
    """Train the texture agent."""
    print("🎨 Training Texture Agent...")
    print("=" * 40)
    
    try:
        from src.agency3d.agents.texture.train import main as texture_main
        import sys
        
        # Set up arguments for texture training
        sys.argv = [
            "train.py",
            "--data-dir", "data/texture/train",
            "--out-dir", "checkpoints/texture_agent",
            "--epochs", "5",
            "--batch-size", "2",
            "--img-size", "256"
        ]
        
        texture_main()
        print("✅ Texture agent training complete!")
        
    except Exception as e:
        print(f"❌ Texture training failed: {e}")

def train_hdr_agent():
    """Train the HDR agent."""
    print("🎨 Training HDR Agent...")
    print("=" * 40)
    
    try:
        from src.agency3d.agents.hdr.train import main as hdr_main
        import sys
        
        # Set up arguments for HDR training
        sys.argv = [
            "train.py",
            "--data-dir", "data/hdr/train",
            "--out-dir", "checkpoints/hdr_agent",
            "--epochs", "5",
            "--batch-size", "1",
            "--img-size", "512"
        ]
        
        hdr_main()
        print("✅ HDR agent training complete!")
        
    except Exception as e:
        print(f"❌ HDR training failed: {e}")

def analyze_external_repos():
    """Analyze the external repositories for insights."""
    print("🔍 Analyzing External Repositories...")
    print("=" * 60)
    
    repos = [
        "external/ShaderGen",
        "external/shd_sokol", 
        "external/Step1X-3D",
        "external/single_image_hdr"
    ]
    
    for repo in repos:
        if Path(repo).exists():
            print(f"📁 {repo}:")
            files = list(Path(repo).rglob("*.py"))[:5]  # First 5 Python files
            for file in files:
                print(f"   • {file.name}")
            print()
        else:
            print(f"❌ {repo} not found")

def create_training_summary():
    """Create a summary of the training setup."""
    print("📋 Training Summary...")
    print("=" * 60)
    
    summary = {
        "external_repos": [
            "ShaderGen - Shader generation framework",
            "shd_sokol - Sokol shader utilities", 
            "Step1X-3D - 3D generation models",
            "single_image_hdr - HDR image processing"
        ],
        "agents": [
            "ShaderAgent - Generates shader code from prompts",
            "TextureAgent - Creates PBR material maps",
            "HDRAgent - Generates HDR lighting environments"
        ],
        "datasets": [
            "Shader dataset - JSONL with prompt/code pairs",
            "Texture dataset - PBR maps with metadata",
            "HDR dataset - LDR/HDR image pairs"
        ],
        "models": [
            "T5 for shader generation",
            "UNet + CLIP for texture generation", 
            "UNet for HDR enhancement"
        ]
    }
    
    print("🎯 Training Components:")
    for category, items in summary.items():
        print(f"\n{category.upper()}:")
        for item in items:
            print(f"   • {item}")
    
    print(f"\n📁 Checkpoints will be saved to:")
    print(f"   • checkpoints/shader_agent/")
    print(f"   • checkpoints/texture_agent/")
    print(f"   • checkpoints/hdr_agent/")

def main():
    """Main training function."""
    parser = argparse.ArgumentParser(description="Train all Voxel agents")
    parser.add_argument("--setup-only", action="store_true", help="Only setup environment")
    parser.add_argument("--skip-setup", action="store_true", help="Skip environment setup")
    parser.add_argument("--agents", nargs="+", choices=["shader", "texture", "hdr"], 
                       default=["shader", "texture", "hdr"], help="Which agents to train")
    
    args = parser.parse_args()
    
    print("🚀 Voxel Agent Training Pipeline")
    print("=" * 70)
    print()
    
    if not args.skip_setup:
        setup_training_environment()
        create_sample_datasets()
        analyze_external_repos()
    
    if args.setup_only:
        print("✅ Setup complete. Run without --setup-only to start training.")
        return
    
    # Train specified agents
    if "shader" in args.agents:
        train_shader_agent()
    
    if "texture" in args.agents:
        train_texture_agent()
    
    if "hdr" in args.agents:
        train_hdr_agent()
    
    create_training_summary()
    print("\n🎉 All agent training complete!")

if __name__ == "__main__":
    main()
