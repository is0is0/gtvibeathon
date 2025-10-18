#!/usr/bin/env python3
"""
Voxel Demo Script - Quick demonstration of the AI-powered 3D scene generation system.
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from agency3d import Agency3D, Config

def main():
    """Run a quick demo of the Voxel system."""
    print("🎨 Voxel Demo - AI-Powered 3D Scene Generation")
    print("=" * 60)
    print()
    
    # Check if API key is set
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print("⚠️  No API key found. Please set ANTHROPIC_API_KEY environment variable.")
        print("   Example: export ANTHROPIC_API_KEY='your-key-here'")
        print()
        print("🔧 For demo purposes, we'll show the system structure instead.")
        show_system_structure()
        return
    
    print("✅ API key found. Running full demo...")
    print()
    
    # Demo prompts
    demo_prompts = [
        "a simple cube with a metallic material",
        "a cozy living room with a sofa and coffee table",
        "a futuristic spaceship interior"
    ]
    
    print("🎯 Demo Prompts:")
    for i, prompt in enumerate(demo_prompts, 1):
        print(f"   {i}. {prompt}")
    print()
    
    # Choose prompt
    try:
        choice = input("Choose a prompt (1-3) or press Enter for default: ").strip()
        if choice in ['1', '2', '3']:
            selected_prompt = demo_prompts[int(choice) - 1]
        else:
            selected_prompt = demo_prompts[0]
    except (ValueError, KeyboardInterrupt):
        selected_prompt = demo_prompts[0]
    
    print(f"🎨 Generating scene: '{selected_prompt}'")
    print()
    
    # Create configuration
    config = Config(
        ai_provider='anthropic',
        ai_model='claude-3-5-sonnet-20241022',
        anthropic_api_key=api_key,
        blender_path=Path('/usr/bin/blender'),  # Default path
        output_dir=Path('./demo_output')
    )
    
    # Create agency
    agency = Agency3D(config)
    
    try:
        # Generate scene
        print("🚀 Starting scene generation...")
        result = agency.create_scene(prompt=selected_prompt)
        
        if result.success:
            print("✅ Scene generated successfully!")
            print(f"   📁 Output: {result.output_path}")
            print(f"   🎬 Blender file: {result.output_path / 'scene.blend'}")
            print()
            print("🎉 Demo complete! Open the .blend file in Blender to see your scene.")
        else:
            print("❌ Scene generation failed:")
            print(f"   Error: {result.error_message}")
            
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        print()
        print("🔧 This might be due to:")
        print("   - Missing Blender installation")
        print("   - Invalid API key")
        print("   - Network connectivity issues")

def show_system_structure():
    """Show the system structure without running the full demo."""
    print("🏗️  Voxel System Architecture:")
    print()
    
    # Show agents
    print("🤖 AI Agents:")
    agents = [
        "ConceptAgent - Interprets prompts and generates scene concepts",
        "BuilderAgent - Creates 3D geometry and objects", 
        "TextureAgent - Applies materials and textures",
        "RenderAgent - Sets up lighting and camera",
        "AnimationAgent - Creates animations and keyframes",
        "ReviewerAgent - Reviews and improves generated scenes"
    ]
    
    for agent in agents:
        print(f"   • {agent}")
    
    print()
    print("🔧 Advanced Features:")
    features = [
        "Real-time agent collaboration",
        "RAG database with 12+ examples", 
        "Error recovery and fallback mechanisms",
        "Performance optimization with caching",
        "Blender addon integration",
        "Parallel processing"
    ]
    
    for feature in features:
        print(f"   • {feature}")
    
    print()
    print("📁 Output Structure:")
    print("   demo_output/")
    print("   ├── scene.blend          # Main Blender file")
    print("   ├── scripts/             # Generated Python scripts")
    print("   ├── renders/             # Rendered images/videos")
    print("   └── logs/                # Generation logs")
    
    print()
    print("🚀 To run the full demo:")
    print("   1. Set your API key: export ANTHROPIC_API_KEY='your-key'")
    print("   2. Install Blender: https://www.blender.org/download/")
    print("   3. Run: python3 demo.py")

if __name__ == "__main__":
    main()
