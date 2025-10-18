#!/usr/bin/env python3
"""
Test generation script for Voxel system.
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_generation():
    """Test Voxel generation with a simple prompt."""
    try:
        from voxel import Voxel, Config
        
        print("Initializing Voxel...")
        
        # Create config with minimal settings for testing
        config = Config()
        
        # Set some basic settings
        config.max_iterations = 1  # Keep it simple for testing
        config.enable_reviewer = False  # Disable reviewer for simple test
        
        # Initialize Voxel
        voxel = Voxel(config)
        print("✓ Voxel initialized")
        
        # Test prompt
        prompt = "create a 3d scene of a house in a grassy land, sunny weather, realistic"
        
        print(f"Generating scene: '{prompt}'")
        print("This may take a few minutes...")
        
        # Create a project first
        project = voxel.create_project(
            name="Test House Scene",
            description="A test generation for a house in grassy land",
            settings={"render_samples": 128, "engine": "CYCLES"}
        )
        print(f"✓ Created project: {project['name']} (ID: {project['id']})")
        
        # Generate the scene
        result = voxel.create_scene(
            prompt=prompt,
            session_name="test_house_generation",
            enable_review=False,
            max_iterations=1
        )
        
        print("✓ Scene generation completed!")
        print(f"Result: {result}")
        
        # Get project history
        history = voxel.get_project_history(project['id'])
        print(f"✓ Project has {len(history)} generations")
        
        # Get system analytics
        analytics = voxel.get_system_analytics(days=1)
        print(f"✓ System analytics: {analytics}")
        
        # Close Voxel
        voxel.close()
        print("✓ Voxel closed successfully")
        
        return True
        
    except Exception as e:
        print(f"✗ Error during generation: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run the generation test."""
    print("Testing Voxel Scene Generation")
    print("=" * 50)
    
    success = test_generation()
    
    if success:
        print("\n✓ Generation test completed successfully!")
        print("Check the output directory for generated files.")
    else:
        print("\n✗ Generation test failed.")
        print("Check the error messages above.")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
