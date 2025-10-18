#!/usr/bin/env python3
"""
Test Scene Generation - Demonstrates AI agent script generation without Blender execution
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def main():
    """Test AI agent script generation."""
    print("🎨 Voxel Scene Generation Test")
    print("=" * 50)
    print()
    
    # Set API key
    api_key = "YOUR_ANTHROPIC_API_KEY_HERE"
    os.environ['ANTHROPIC_API_KEY'] = api_key
    
    print("✅ API key configured")
    print()
    
    # Test prompt
    prompt = "a simple cube with metallic material"
    print(f"🎯 Testing prompt: '{prompt}'")
    print()
    
    try:
        from agency3d.agents import ConceptAgent, BuilderAgent, TextureAgent, RenderAgent
        from agency3d.core.agent import AgentConfig
        from agency3d.core.agent_context import AgentContext
        
        # Create configuration
        config = AgentConfig(
            provider='anthropic',
            model='claude-3-5-sonnet-20241022',
            api_key=api_key
        )
        context = AgentContext()
        
        print("🤖 Initializing AI agents...")
        
        # Create agents
        concept_agent = ConceptAgent(config, context)
        builder_agent = BuilderAgent(config, context)
        texture_agent = TextureAgent(config, context)
        render_agent = RenderAgent(config, context)
        
        print("✅ Agents initialized")
        print()
        
        # Test concept generation
        print("🧠 Generating scene concept...")
        concept_response = concept_agent.generate_response(prompt)
        concept = concept_response.content
        print(f"✅ Concept generated ({len(concept)} characters)")
        print(f"   Preview: {concept[:100]}...")
        print()
        
        # Test builder script generation
        print("🔨 Generating builder script...")
        builder_response = builder_agent.generate_response(concept)
        builder_script = builder_response.content
        print(f"✅ Builder script generated ({len(builder_script)} characters)")
        print(f"   Preview: {builder_script[:100]}...")
        print()
        
        # Test texture script generation
        print("🎨 Generating texture script...")
        texture_response = texture_agent.generate_response(concept)
        texture_script = texture_response.content
        print(f"✅ Texture script generated ({len(texture_script)} characters)")
        print(f"   Preview: {texture_script[:100]}...")
        print()
        
        # Test render script generation
        print("📷 Generating render script...")
        render_response = render_agent.generate_response(concept)
        render_script = render_response.content
        print(f"✅ Render script generated ({len(render_script)} characters)")
        print(f"   Preview: {render_script[:100]}...")
        print()
        
        # Save generated scripts
        output_dir = Path("./demo_output")
        output_dir.mkdir(exist_ok=True)
        
        scripts_dir = output_dir / "scripts"
        scripts_dir.mkdir(exist_ok=True)
        
        # Save individual scripts
        with open(scripts_dir / "concept.py", "w") as f:
            f.write(concept)
        
        with open(scripts_dir / "builder.py", "w") as f:
            f.write(builder_script)
        
        with open(scripts_dir / "texture.py", "w") as f:
            f.write(texture_script)
        
        with open(scripts_dir / "render.py", "w") as f:
            f.write(render_script)
        
        print("💾 Scripts saved to demo_output/scripts/")
        print()
        
        # Show file sizes
        print("📊 Generated Scripts:")
        for script_file in scripts_dir.glob("*.py"):
            size = script_file.stat().st_size
            print(f"   📄 {script_file.name}: {size} bytes")
        
        print()
        print("🎉 Scene generation test complete!")
        print()
        print("📋 Next steps:")
        print("   1. Install Blender: https://www.blender.org/download/")
        print("   2. Run: voxel create 'a simple cube with metallic material'")
        print("   3. Or manually execute the generated scripts in Blender")
        print()
        print("🔍 Check the generated scripts in demo_output/scripts/")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
