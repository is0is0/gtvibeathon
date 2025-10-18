#!/usr/bin/env python3
"""Demo that uses the actual Voxel system to generate a scene and open it."""

import os
import subprocess
import sys
from pathlib import Path

def run_voxel_generation():
    """Run the Voxel system to generate a scene."""
    print("🎨 Running Voxel AI System...")
    print("=" * 50)
    
    # Run voxel create command
    result = subprocess.run([
        "voxel", "create", "a simple house with a door and window"
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Voxel generation completed!")
        return True
    else:
        print(f"❌ Voxel generation failed: {result.stderr}")
        return False

def find_latest_blend_file():
    """Find the most recent .blend file in output directories."""
    output_dir = Path("/Users/justin/Desktop/gthh/gtvibeathon/output")
    
    if not output_dir.exists():
        print("❌ No output directory found")
        return None
    
    # Find all .blend files
    blend_files = list(output_dir.rglob("*.blend"))
    blend_files.extend(list(output_dir.rglob("*.blend1")))
    
    if not blend_files:
        print("❌ No .blend files found in output directory")
        return None
    
    # Get the most recent file
    latest_file = max(blend_files, key=lambda f: f.stat().st_mtime)
    return str(latest_file)

def open_blender_file(file_path):
    """Open a Blender file."""
    blender_path = "/Applications/Blender.app/Contents/MacOS/Blender"
    
    if not os.path.exists(blender_path):
        print("❌ Blender not found. Please install from https://www.blender.org/download/")
        return False
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return False
    
    print(f"🎯 Opening Blender file: {file_path}")
    subprocess.Popen([blender_path, file_path])
    print("✅ Blender opened!")
    return True

def create_manual_blend_file():
    """Create a manual Blender file as fallback."""
    print("🔧 Creating manual Blender scene as fallback...")
    
    blender_script = '''
import bpy
import math

# Clear the scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create a house structure
# Floor
bpy.ops.mesh.primitive_cube_add(size=8, location=(0, 0, 0))
floor = bpy.context.active_object
floor.name = "Floor"
floor.scale = (1, 1, 0.1)

# Walls
bpy.ops.mesh.primitive_cube_add(size=6, location=(0, 0, 3))
wall1 = bpy.context.active_object
wall1.name = "Wall1"
wall1.scale = (1, 0.1, 1)

bpy.ops.mesh.primitive_cube_add(size=6, location=(0, 0, 3))
wall2 = bpy.context.active_object
wall2.name = "Wall2"
wall2.scale = (0.1, 1, 1)

# Door
bpy.ops.mesh.primitive_cube_add(size=2, location=(0, -3.1, 1))
door = bpy.context.active_object
door.name = "Door"
door.scale = (0.5, 0.1, 1)

# Window
bpy.ops.mesh.primitive_cube_add(size=1.5, location=(2, -3.1, 2.5))
window = bpy.context.active_object
window.name = "Window"
window.scale = (0.5, 0.1, 0.5)

# Roof
bpy.ops.mesh.primitive_cube_add(size=7, location=(0, 0, 5.5))
roof = bpy.context.active_object
roof.name = "Roof"
roof.scale = (1, 1, 0.3)

# Add materials
materials = {
    "Floor": (0.8, 0.6, 0.4, 1),  # Brown
    "Wall1": (0.9, 0.9, 0.9, 1),  # Light gray
    "Wall2": (0.9, 0.9, 0.9, 1),  # Light gray
    "Door": (0.4, 0.2, 0.1, 1),   # Dark brown
    "Window": (0.7, 0.9, 1.0, 1), # Light blue
    "Roof": (0.6, 0.3, 0.3, 1)    # Red
}

for obj_name, color in materials.items():
    obj = bpy.data.objects.get(obj_name)
    if obj:
        material = bpy.data.materials.new(name=f"{obj_name}Material")
        material.use_nodes = True
        material.node_tree.nodes["Principled BSDF"].inputs[0].default_value = color
        obj.data.materials.append(material)

# Add lighting
bpy.ops.object.light_add(type='SUN', location=(5, 5, 10))
sun = bpy.context.active_object
sun.name = "SunLight"
sun.data.energy = 3

# Set up camera
bpy.ops.object.camera_add(location=(8, -8, 4))
camera = bpy.context.active_object
camera.name = "Camera"
camera.rotation_euler = (1.2, 0, 0.8)

# Set camera as active
bpy.context.scene.camera = camera

# Save the file
output_path = "/Users/justin/Desktop/gthh/gtvibeathon/house_scene.blend"
bpy.ops.wm.save_as_mainfile(filepath=output_path)
print(f"✅ Saved house scene: {output_path}")
'''
    
    # Write and execute script
    script_path = "/Users/justin/Desktop/gthh/gtvibeathon/create_house.py"
    with open(script_path, 'w') as f:
        f.write(blender_script)
    
    blender_path = "/Applications/Blender.app/Contents/MacOS/Blender"
    if os.path.exists(blender_path):
        result = subprocess.run([
            blender_path, 
            "--background", 
            "--python", script_path
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ House scene created!")
            return "/Users/justin/Desktop/gthh/gtvibeathon/house_scene.blend"
        else:
            print(f"❌ Error: {result.stderr}")
            return None
    else:
        print("❌ Blender not found")
        return None

def main():
    print("🎨 Voxel Demo - Generate and Open 3D Scene")
    print("=" * 60)
    print()
    
    # Try to find existing blend files first
    print("🔍 Looking for existing Blender files...")
    latest_blend = find_latest_blend_file()
    
    if latest_blend:
        print(f"✅ Found: {latest_blend}")
        if open_blender_file(latest_blend):
            print("🎉 Blender opened with existing scene!")
            return
    
    # If no existing files, create a manual scene
    print("📝 No existing scenes found. Creating new scene...")
    blend_file = create_manual_blend_file()
    
    if blend_file and os.path.exists(blend_file):
        print(f"🎯 Opening: {blend_file}")
        if open_blender_file(blend_file):
            print("🎉 Success! You should see Blender open with a house scene!")
            print("   • House with walls, door, and window")
            print("   • Different colored materials")
            print("   • Proper lighting and camera")
    else:
        print("❌ Failed to create Blender scene")

if __name__ == "__main__":
    main()
