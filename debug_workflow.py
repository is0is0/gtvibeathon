#!/usr/bin/env python3
"""
Debug Voxel Workflow to see what's happening
"""

import sys
import os
from pathlib import Path
import logging

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')

from voxel import Voxel

def main():
    print("🔍 Debugging Voxel Workflow")
    print("=" * 40)
    
    try:
        # Initialize Voxel system
        print("📦 Initializing Voxel system...")
        voxel = Voxel()
        
        # Create a project
        print("📁 Creating project...")
        project = voxel.create_project(
            name="Debug House Scene",
            description="Debugging the Voxel agent workflow"
        )
        print(f"✅ Project created: {project['name']} (ID: {project['id']})")
        
        # Check orchestrator
        print("\n🔧 Checking orchestrator...")
        orchestrator = voxel.orchestrator
        print(f"   • Concept agent: {type(orchestrator.concept_agent).__name__}")
        print(f"   • Builder agent: {type(orchestrator.builder_agent).__name__}")
        print(f"   • Texture agent: {type(orchestrator.texture_agent).__name__ if orchestrator.texture_agent else 'None'}")
        print(f"   • Render agent: {type(orchestrator.render_agent).__name__}")
        print(f"   • Animation agent: {type(orchestrator.animation_agent).__name__ if orchestrator.animation_agent else 'None'}")
        
        # Try to generate scene with detailed error handling
        print("\n🎬 Starting scene generation...")
        print("Prompt: 'create a 3d scene of a house in a grassy land, sunny weather, realistic'")
        
        try:
            result = voxel.create_scene(
                prompt="create a 3d scene of a house in a grassy land, sunny weather, realistic",
                session_name="debug_house_generation"
            )
            
            if result.success:
                print(f"\n✅ Scene generated successfully!")
                print(f"📁 Output path: {result.output_path}")
                print(f"📊 Quality score: {result.quality_score}")
                print(f"⏱️  Generation time: {result.generation_time:.2f}s")
            else:
                print(f"\n❌ Scene generation failed: {result.error}")
                print(f"   Error type: {type(result.error)}")
                if hasattr(result, 'iterations'):
                    print(f"   Iterations completed: {result.iterations}")
                    
        except Exception as e:
            print(f"\n💥 Exception during generation: {e}")
            import traceback
            traceback.print_exc()
            
    except Exception as e:
        print(f"\n💥 Error during initialization: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # Close Voxel
        try:
            voxel.close()
            print("\n🔒 Voxel system closed")
        except:
            pass

if __name__ == "__main__":
    main()
