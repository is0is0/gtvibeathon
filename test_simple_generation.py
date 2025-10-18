#!/usr/bin/env python3
"""
Simple Voxel Generation Test
This script tests the Voxel system with a simple prompt to verify everything works.
"""

import sys
import os
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from voxel import Voxel

def main():
    print("🧪 Testing Voxel Generation")
    print("=" * 40)
    
    try:
        # Initialize Voxel system
        print("📦 Initializing Voxel system...")
        voxel = Voxel()
        
        # Create a project
        print("📁 Creating project...")
        project = voxel.create_project(
            name="Simple Test Scene",
            description="Testing the Voxel system with a simple prompt"
        )
        print(f"✅ Project created: {project['name']} (ID: {project['id']})")
        
        # Test with a simple prompt
        print("\n🎬 Testing scene generation...")
        print("Prompt: 'a simple cube with a red material'")
        
        result = voxel.create_scene(
            prompt="a simple cube with a red material",
            session_name="simple_test"
        )
        
        if result.success:
            print(f"\n✅ Scene generated successfully!")
            print(f"📁 Output path: {result.output_path}")
            print(f"📊 Quality score: {result.quality_score}")
            print(f"⏱️  Generation time: {result.generation_time:.2f}s")
            
            # Check if files were created
            if result.output_path and Path(result.output_path).exists():
                print(f"📄 Blender file exists: {result.output_path}")
            else:
                print("⚠️  Blender file not found")
                
        else:
            print(f"\n❌ Scene generation failed: {result.error}")
            
    except Exception as e:
        print(f"\n💥 Error during test: {e}")
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
