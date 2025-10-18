#!/usr/bin/env python3
"""Working demo that creates and opens a Blender file."""

import os
import subprocess
import sys
from pathlib import Path

def create_blender_scene():
    """Create a simple Blender scene and save it."""
    print("🎨 Creating Blender scene...")
    
    # Create a simple Blender script
    blender_script = '''
import bpy
import math

# Clear the scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create a red cube
bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 1))
cube = bpy.context.active_object
cube.name = "RedCube"

# Create material for the cube
material = bpy.data.materials.new(name="RedMaterial")
material.use_nodes = True
material.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (1, 0, 0, 1)  # Red color
cube.data.materials.append(material)

# Create a white plane
bpy.ops.mesh.primitive_plane_add(size=10, location=(0, 0, 0))
plane = bpy.context.active_object
plane.name = "WhitePlane"

# Create material for the plane
plane_material = bpy.data.materials.new(name="WhiteMaterial")
plane_material.use_nodes = True
plane_material.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (1, 1, 1, 1)  # White color
plane.data.materials.append(plane_material)

# Add lighting
bpy.ops.object.light_add(type='SUN', location=(5, 5, 10))
sun = bpy.context.active_object
sun.name = "SunLight"
sun.data.energy = 3

# Set up camera
bpy.ops.object.camera_add(location=(5, -5, 5))
camera = bpy.context.active_object
camera.name = "Camera"
camera.rotation_euler = (1.1, 0, 0.785)

# Set camera as active
bpy.context.scene.camera = camera

# Save the file
output_path = "/Users/justin/Desktop/gthh/gtvibeathon/demo_scene.blend"
bpy.ops.wm.save_as_mainfile(filepath=output_path)
print(f"✅ Saved Blender file: {output_path}")
'''
    
    # Write script to file
    script_path = "/Users/justin/Desktop/gthh/gtvibeathon/create_demo_scene.py"
    with open(script_path, 'w') as f:
        f.write(blender_script)
    
    # Execute the script with Blender
    blender_path = "/Applications/Blender.app/Contents/MacOS/Blender"
    if os.path.exists(blender_path):
        print("🚀 Executing Blender script...")
        result = subprocess.run([
            blender_path, 
            "--background", 
            "--python", script_path
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Blender scene created successfully!")
            return True
        else:
            print(f"❌ Error: {result.stderr}")
            return False
    else:
        print(f"❌ Blender not found at {blender_path}")
        return False

def open_blender_file():
    """Open the generated Blender file."""
    blend_file = "/Users/justin/Desktop/gthh/gtvibeathon/demo_scene.blend"
    
    if os.path.exists(blend_file):
        print(f"🎯 Opening Blender file: {blend_file}")
        blender_path = "/Applications/Blender.app/Contents/MacOS/Blender"
        
        if os.path.exists(blender_path):
            # Open Blender with the file
            subprocess.Popen([blender_path, blend_file])
            print("✅ Blender opened with the scene!")
            return True
        else:
            print("❌ Blender not found. Please install Blender from https://www.blender.org/download/")
            return False
    else:
        print("❌ Blender file not found. Run the scene creation first.")
        return False

def main():
    print("🎨 Voxel Working Demo - Create and Open Blender Scene")
    print("=" * 60)
    print()
    
    # Step 1: Create the scene
    if create_blender_scene():
        print()
        print("🎯 Scene created! Opening in Blender...")
        print()
        
        # Step 2: Open the file
        if open_blender_file():
            print()
            print("🎉 Success! You should see Blender open with:")
            print("   • A red cube on a white plane")
            print("   • Proper lighting and camera setup")
            print("   • Materials applied to objects")
            print()
            print("📁 File saved at: /Users/justin/Desktop/gthh/gtvibeathon/demo_scene.blend")
        else:
            print("❌ Failed to open Blender file")
    else:
        print("❌ Failed to create Blender scene")

if __name__ == "__main__":
    main()
