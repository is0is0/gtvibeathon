#!/usr/bin/env python3
"""
Test Voxel Generation with Proper Agent Workflow
This script uses the actual Voxel system with all agents to generate a scene.
"""

import sys
import os
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from voxel import Voxel

def main():
    print("🚀 Testing Voxel Generation with Proper Agent Workflow")
    print("=" * 60)
    
    try:
        # Initialize Voxel system
        print("📦 Initializing Voxel system...")
        voxel = Voxel()
        
        # Create a project
        print("📁 Creating project...")
        project = voxel.create_project(
            name="Test House Scene",
            description="Testing the Voxel agent workflow for house generation"
        )
        print(f"✅ Project created: {project['name']} (ID: {project['id']})")
        
        # Generate scene using the proper Voxel workflow
        print("\n🎬 Starting scene generation with agents...")
        print("Prompt: 'create a 3d scene of a house in a grassy land, sunny weather, realistic'")
        
        result = voxel.create_scene(
            prompt="create a 3d scene of a house in a grassy land, sunny weather, realistic",
            session_name="test_house_generation"
        )
        
        if result.success:
            print(f"\n✅ Scene generated successfully!")
            print(f"📁 Output path: {result.output_path}")
            print(f"📊 Quality score: {result.quality_score}")
            print(f"⏱️  Generation time: {result.generation_time:.2f}s")
            
            # Get project statistics
            print("\n📈 Project Statistics:")
            stats = voxel.get_project_statistics(project['id'])
            print(f"   • Total generations: {stats.get('total_generations', 0)}")
            print(f"   • Success rate: {stats.get('success_rate', 0):.1f}%")
            print(f"   • Average quality: {stats.get('avg_quality', 0):.1f}")
            
            # Get system analytics
            print("\n🔍 System Analytics:")
            analytics = voxel.get_system_analytics(days=1)
            print(f"   • Total generations today: {analytics.get('total_generations', 0)}")
            print(f"   • Success rate: {analytics.get('success_rate', 0):.1f}%")
            print(f"   • Average render time: {analytics.get('avg_render_time', 0):.1f}s")
            
        else:
            print(f"\n❌ Scene generation failed: {result.error}")
            
    except Exception as e:
        print(f"\n💥 Error during generation: {e}")
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
