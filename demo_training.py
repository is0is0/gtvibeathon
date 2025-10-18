#!/usr/bin/env python3
"""
Demo script showing how to train and use all Voxel agents.
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def check_external_repos():
    """Check if external repositories are available."""
    print("🔍 Checking External Repositories...")
    print("=" * 50)
    
    repos = [
        "external/ShaderGen",
        "external/shd_sokol", 
        "external/Step1X-3D",
        "external/single_image_hdr"
    ]
    
    available_repos = []
    for repo in repos:
        if Path(repo).exists():
            print(f"✅ {repo}")
            available_repos.append(repo)
        else:
            print(f"❌ {repo} - Not found")
    
    return available_repos

def demonstrate_shader_training():
    """Demonstrate shader agent training."""
    print("🎨 Shader Agent Training Demo")
    print("=" * 40)
    
    # Create sample shader dataset
    shader_data = [
        {
            "prompt": "Create a simple diffuse shader for a red material",
            "code": """// Simple diffuse shader
uniform vec3 lightDir;
uniform vec3 lightColor;
uniform vec3 baseColor;

void main() {
    vec3 normal = normalize(vNormal);
    float diff = max(dot(normal, lightDir), 0.0);
    vec3 color = baseColor * lightColor * diff;
    gl_FragColor = vec4(color, 1.0);
}"""
        },
        {
            "prompt": "Create a metallic shader with environment reflections",
            "code": """// Metallic shader with reflections
uniform vec3 cameraPos;
uniform samplerCube envMap;
uniform float metallic;
uniform float roughness;

void main() {
    vec3 viewDir = normalize(cameraPos - vPosition);
    vec3 normal = normalize(vNormal);
    vec3 reflectDir = reflect(-viewDir, normal);
    vec3 envColor = textureCube(envMap, reflectDir).rgb;
    
    // Mix between diffuse and metallic
    vec3 diffuse = baseColor * (1.0 - metallic);
    vec3 specular = envColor * metallic;
    vec3 finalColor = diffuse + specular;
    
    gl_FragColor = vec4(finalColor, 1.0);
}"""
        }
    ]
    
    # Save dataset
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    with open("data/shader_demo.jsonl", "w") as f:
        for item in shader_data:
            f.write(json.dumps(item) + "\n")
    
    print("✅ Sample shader dataset created")
    print("📁 Dataset: data/shader_demo.jsonl")
    print("🎯 To train: python -m src.agency3d.agents.shader.train --train-file data/shader_demo.jsonl")

def demonstrate_texture_training():
    """Demonstrate texture agent training."""
    print("🎨 Texture Agent Training Demo")
    print("=" * 40)
    
    # Create sample texture dataset structure
    texture_dir = Path("data/texture_demo")
    texture_dir.mkdir(parents=True, exist_ok=True)
    
    # Create sample material
    sample_dir = texture_dir / "wood_material"
    sample_dir.mkdir(exist_ok=True)
    
    # Create metadata
    metadata = {
        "prompt": "Weathered oak wood with natural grain patterns",
        "material_type": "wood",
        "roughness": 0.8,
        "metallic": 0.0
    }
    
    import json
    with open(sample_dir / "metadata.json", "w") as f:
        json.dump(metadata, f)
    
    print("✅ Sample texture dataset structure created")
    print("📁 Dataset: data/texture_demo/")
    print("🎯 To train: python -m src.agency3d.agents.texture.train --data-dir data/texture_demo")

def demonstrate_hdr_training():
    """Demonstrate HDR agent training."""
    print("🎨 HDR Agent Training Demo")
    print("=" * 40)
    
    # Create sample HDR dataset structure
    hdr_dir = Path("data/hdr_demo")
    hdr_dir.mkdir(parents=True, exist_ok=True)
    
    # Create sample environment
    sample_dir = hdr_dir / "sunset_environment"
    sample_dir.mkdir(exist_ok=True)
    
    # Create metadata
    metadata = {
        "prompt": "Golden hour sunset with warm lighting",
        "time_of_day": "sunset",
        "lighting_type": "natural",
        "color_temperature": 3000
    }
    
    import json
    with open(sample_dir / "metadata.json", "w") as f:
        json.dump(metadata, f)
    
    print("✅ Sample HDR dataset structure created")
    print("📁 Dataset: data/hdr_demo/")
    print("🎯 To train: python -m src.agency3d.agents.hdr.train --data-dir data/hdr_demo")

def show_training_commands():
    """Show all training commands."""
    print("🚀 Training Commands")
    print("=" * 50)
    print()
    
    print("1. Setup Environment:")
    print("   python train_all_agents.py --setup-only")
    print()
    
    print("2. Train All Agents:")
    print("   python train_all_agents.py")
    print()
    
    print("3. Train Specific Agents:")
    print("   python train_all_agents.py --agents shader texture")
    print()
    
    print("4. Individual Agent Training:")
    print("   # Shader Agent")
    print("   python -m src.agency3d.agents.shader.train --train-file data/shader_dataset.jsonl")
    print()
    print("   # Texture Agent")
    print("   python -m src.agency3d.agents.texture.train --data-dir data/texture/train")
    print()
    print("   # HDR Agent")
    print("   python -m src.agency3d.agents.hdr.train --data-dir data/hdr/train")
    print()

def show_external_repo_integration():
    """Show how to integrate external repositories."""
    print("🔗 External Repository Integration")
    print("=" * 50)
    print()
    
    print("📁 Available Repositories:")
    repos = check_external_repos()
    
    if repos:
        print("\n🎯 Integration Examples:")
        print()
        
        if "external/ShaderGen" in repos:
            print("ShaderGen Integration:")
            print("   • Use ShaderGen for shader code generation")
            print("   • Integrate with ShaderAgent for enhanced capabilities")
            print("   • Support for multiple shader languages")
            print()
        
        if "external/shd_sokol" in repos:
            print("Sokol Shader Integration:")
            print("   • Use sokol shaders for cross-platform rendering")
            print("   • Integrate with Voxel's rendering pipeline")
            print("   • Support for WebGL, Metal, DirectX, etc.")
            print()
        
        if "external/Step1X-3D" in repos:
            print("Step1X-3D Integration:")
            print("   • Use Step1X-3D for 3D generation")
            print("   • Integrate with Voxel's 3D pipeline")
            print("   • Support for advanced 3D models")
            print()
        
        if "external/single_image_hdr" in repos:
            print("Single Image HDR Integration:")
            print("   • Use for HDR image processing")
            print("   • Integrate with HDRAgent")
            print("   • Support for HDR environment generation")
            print()
    else:
        print("❌ No external repositories found")
        print("Run: python train_all_agents.py --setup-only")

def main():
    """Main demo function."""
    print("🎨 Voxel Agent Training Demo")
    print("=" * 70)
    print()
    
    # Check external repositories
    available_repos = check_external_repos()
    
    # Demonstrate training setups
    demonstrate_shader_training()
    print()
    
    demonstrate_texture_training()
    print()
    
    demonstrate_hdr_training()
    print()
    
    # Show training commands
    show_training_commands()
    
    # Show external repo integration
    show_external_repo_integration()
    
    print("🎉 Demo complete!")
    print()
    print("📚 Next Steps:")
    print("   1. Run: python train_all_agents.py --setup-only")
    print("   2. Prepare your datasets")
    print("   3. Run: python train_all_agents.py")
    print("   4. Use trained models in Voxel system")

if __name__ == "__main__":
    main()
