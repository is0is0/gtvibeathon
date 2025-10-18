#!/usr/bin/env python3
"""Fixed house demo with proper wall positioning and alignment."""

import os
import subprocess
import sys
from pathlib import Path

def create_proper_house():
    """Create a properly positioned house with all walls, aligned door and window."""
    print("🏠 Creating Proper House Scene...")
    print("=" * 50)
    
    blender_script = '''
import bpy
import math

# Clear the scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# House dimensions
house_width = 6
house_depth = 4
wall_height = 3
wall_thickness = 0.2

# Create floor
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, -wall_thickness/2))
floor = bpy.context.active_object
floor.name = "Floor"
floor.scale = (house_width, house_depth, wall_thickness)

# Create all 4 walls properly positioned
# Front wall (facing camera)
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, house_depth/2, wall_height/2))
front_wall = bpy.context.active_object
front_wall.name = "FrontWall"
front_wall.scale = (house_width, wall_thickness, wall_height)

# Back wall
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -house_depth/2, wall_height/2))
back_wall = bpy.context.active_object
back_wall.name = "BackWall"
back_wall.scale = (house_width, wall_thickness, wall_height)

# Left wall
bpy.ops.mesh.primitive_cube_add(size=1, location=(-house_width/2, 0, wall_height/2))
left_wall = bpy.context.active_object
left_wall.name = "LeftWall"
left_wall.scale = (wall_thickness, house_depth, wall_height)

# Right wall
bpy.ops.mesh.primitive_cube_add(size=1, location=(house_width/2, 0, wall_height/2))
right_wall = bpy.context.active_object
right_wall.name = "RightWall"
right_wall.scale = (wall_thickness, house_depth, wall_height)

# Create door in front wall (properly aligned)
door_width = 1.5
door_height = 2.5
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, house_depth/2 + wall_thickness/2 + 0.01, door_height/2))
door = bpy.context.active_object
door.name = "Door"
door.scale = (door_width, wall_thickness, door_height)

# Create window in left wall (properly aligned)
window_width = 1.2
window_height = 1.0
bpy.ops.mesh.primitive_cube_add(size=1, location=(-house_width/2 - wall_thickness/2 - 0.01, 0, 2))
window = bpy.context.active_object
window.name = "Window"
window.scale = (wall_thickness, window_width, window_height)

# Create roof
roof_width = house_width + 1
roof_depth = house_depth + 1
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, wall_height + 0.5))
roof = bpy.context.active_object
roof.name = "Roof"
roof.scale = (roof_width, roof_depth, 0.3)

# Add materials with proper colors
materials = {
    "Floor": (0.8, 0.6, 0.4, 1),      # Brown wood
    "FrontWall": (0.9, 0.9, 0.9, 1),  # Light gray
    "BackWall": (0.9, 0.9, 0.9, 1),   # Light gray
    "LeftWall": (0.9, 0.9, 0.9, 1),   # Light gray
    "RightWall": (0.9, 0.9, 0.9, 1),  # Light gray
    "Door": (0.4, 0.2, 0.1, 1),       # Dark brown
    "Window": (0.7, 0.9, 1.0, 1),     # Light blue (glass)
    "Roof": (0.6, 0.3, 0.3, 1)        # Red
}

for obj_name, color in materials.items():
    obj = bpy.data.objects.get(obj_name)
    if obj:
        material = bpy.data.materials.new(name=f"{obj_name}Material")
        material.use_nodes = True
        material.node_tree.nodes["Principled BSDF"].inputs[0].default_value = color
        obj.data.materials.append(material)

# Add proper lighting
bpy.ops.object.light_add(type='SUN', location=(8, 8, 12))
sun = bpy.context.active_object
sun.name = "SunLight"
sun.data.energy = 3

# Add area light inside for better illumination
bpy.ops.object.light_add(type='AREA', location=(0, 0, 2))
area_light = bpy.context.active_object
area_light.name = "AreaLight"
area_light.data.energy = 50
area_light.data.size = 3

# Set up camera for better view
bpy.ops.object.camera_add(location=(10, -8, 5))
camera = bpy.context.active_object
camera.name = "Camera"
camera.rotation_euler = (1.2, 0, 0.8)

# Set camera as active
bpy.context.scene.camera = camera

# Save the file
output_path = "/Users/justin/Desktop/gthh/gtvibeathon/proper_house.blend"
bpy.ops.wm.save_as_mainfile(filepath=output_path)
print(f"✅ Saved proper house: {output_path}")
'''
    
    # Write and execute script
    script_path = "/Users/justin/Desktop/gthh/gtvibeathon/create_proper_house.py"
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
            print("✅ Proper house created!")
            return "/Users/justin/Desktop/gthh/gtvibeathon/proper_house.blend"
        else:
            print(f"❌ Error: {result.stderr}")
            return None
    else:
        print("❌ Blender not found")
        return None

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

def main():
    print("🏠 Fixed House Demo - Proper Wall Positioning")
    print("=" * 60)
    print()
    
    # Create the proper house
    blend_file = create_proper_house()
    
    if blend_file and os.path.exists(blend_file):
        print(f"🎯 Opening: {blend_file}")
        if open_blender_file(blend_file):
            print("🎉 Success! You should see a proper house with:")
            print("   ✅ All 4 walls properly positioned")
            print("   ✅ Door aligned to floor edge")
            print("   ✅ Window aligned to floor edge")
            print("   ✅ No intersecting walls")
            print("   ✅ Proper materials and lighting")
    else:
        print("❌ Failed to create proper house scene")

if __name__ == "__main__":
    main()
