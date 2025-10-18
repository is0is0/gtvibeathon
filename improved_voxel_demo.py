#!/usr/bin/env python3
"""Improved Voxel demo that generates better 3D scenes."""

import os
import subprocess
import sys
from pathlib import Path

def create_advanced_scene(scene_type="modern_house"):
    """Create an advanced 3D scene with proper positioning."""
    
    scenes = {
        "modern_house": '''
import bpy
import math

# Clear the scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Modern house with proper dimensions
house_width = 8
house_depth = 6
wall_height = 3.5
wall_thickness = 0.25

# Create foundation
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, -0.1))
foundation = bpy.context.active_object
foundation.name = "Foundation"
foundation.scale = (house_width + 0.5, house_depth + 0.5, 0.2)

# Create floor
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0))
floor = bpy.context.active_object
floor.name = "Floor"
floor.scale = (house_width, house_depth, 0.1)

# Create walls with proper positioning
walls = [
    ("FrontWall", (0, house_depth/2 + wall_thickness/2, wall_height/2), (house_width, wall_thickness, wall_height)),
    ("BackWall", (0, -house_depth/2 - wall_thickness/2, wall_height/2), (house_width, wall_thickness, wall_height)),
    ("LeftWall", (-house_width/2 - wall_thickness/2, 0, wall_height/2), (wall_thickness, house_depth, wall_height)),
    ("RightWall", (house_width/2 + wall_thickness/2, 0, wall_height/2), (wall_thickness, house_depth, wall_height))
]

for wall_name, position, scale in walls:
    bpy.ops.mesh.primitive_cube_add(size=1, location=position)
    wall = bpy.context.active_object
    wall.name = wall_name
    wall.scale = scale

# Create door (properly positioned in front wall)
door_width = 2
door_height = 2.5
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, house_depth/2 + wall_thickness + 0.01, door_height/2))
door = bpy.context.active_object
door.name = "Door"
door.scale = (door_width, wall_thickness, door_height)

# Create windows (properly positioned)
windows = [
    ("Window1", (2.5, house_depth/2 + wall_thickness + 0.01, 2.2), (1.5, wall_thickness, 1.2)),
    ("Window2", (-2.5, house_depth/2 + wall_thickness + 0.01, 2.2), (1.5, wall_thickness, 1.2)),
    ("Window3", (0, -house_depth/2 - wall_thickness - 0.01, 2.2), (2, wall_thickness, 1.2))
]

for window_name, position, scale in windows:
    bpy.ops.mesh.primitive_cube_add(size=1, location=position)
    window = bpy.context.active_object
    window.name = window_name
    window.scale = scale

# Create roof with slight overhang
roof_width = house_width + 1
roof_depth = house_depth + 1
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, wall_height + 0.3))
roof = bpy.context.active_object
roof.name = "Roof"
roof.scale = (roof_width, roof_depth, 0.4)

# Add materials
materials = {
    "Foundation": (0.4, 0.4, 0.4, 1),    # Dark gray
    "Floor": (0.8, 0.6, 0.4, 1),         # Brown wood
    "FrontWall": (0.95, 0.95, 0.95, 1), # White
    "BackWall": (0.95, 0.95, 0.95, 1),   # White
    "LeftWall": (0.95, 0.95, 0.95, 1),   # White
    "RightWall": (0.95, 0.95, 0.95, 1),  # White
    "Door": (0.3, 0.2, 0.1, 1),          # Dark brown
    "Window1": (0.8, 0.9, 1.0, 1),       # Light blue
    "Window2": (0.8, 0.9, 1.0, 1),       # Light blue
    "Window3": (0.8, 0.9, 1.0, 1),       # Light blue
    "Roof": (0.7, 0.3, 0.3, 1)           # Red
}

for obj_name, color in materials.items():
    obj = bpy.data.objects.get(obj_name)
    if obj:
        material = bpy.data.materials.new(name=f"{obj_name}Material")
        material.use_nodes = True
        material.node_tree.nodes["Principled BSDF"].inputs[0].default_value = color
        obj.data.materials.append(material)

# Add proper lighting
bpy.ops.object.light_add(type='SUN', location=(10, 10, 15))
sun = bpy.context.active_object
sun.name = "SunLight"
sun.data.energy = 5

# Add area light for interior
bpy.ops.object.light_add(type='AREA', location=(0, 0, 2.5))
area_light = bpy.context.active_object
area_light.name = "InteriorLight"
area_light.data.energy = 100
area_light.data.size = 4

# Set up camera
bpy.ops.object.camera_add(location=(12, -10, 6))
camera = bpy.context.active_object
camera.name = "Camera"
camera.rotation_euler = (1.3, 0, 0.9)

# Set camera as active
bpy.context.scene.camera = camera

# Save the file
output_path = "/Users/justin/Desktop/gthh/gtvibeathon/modern_house.blend"
bpy.ops.wm.save_as_mainfile(filepath=output_path)
print(f"✅ Saved modern house: {output_path}")
''',
        
        "futuristic_car": '''
import bpy
import math

# Clear the scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Futuristic car with glowing elements
car_length = 4
car_width = 2
car_height = 1.2

# Car body
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, car_height/2))
body = bpy.context.active_object
body.name = "CarBody"
body.scale = (car_length, car_width, car_height)

# Car cabin
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, car_height + 0.3))
cabin = bpy.context.active_object
cabin.name = "Cabin"
cabin.scale = (car_length * 0.7, car_width * 0.8, 0.6)

# Wheels
wheel_positions = [
    (1.5, 1.2, 0.3),   # Front left
    (1.5, -1.2, 0.3),  # Front right
    (-1.5, 1.2, 0.3),  # Rear left
    (-1.5, -1.2, 0.3)  # Rear right
]

for i, pos in enumerate(wheel_positions):
    bpy.ops.mesh.primitive_cylinder_add(radius=0.4, depth=0.3, location=pos)
    wheel = bpy.context.active_object
    wheel.name = f"Wheel{i+1}"
    wheel.rotation_euler = (math.radians(90), 0, 0)

# Glowing headlights
bpy.ops.mesh.primitive_cylinder_add(radius=0.2, depth=0.1, location=(2.1, 0.6, 0.8))
headlight1 = bpy.context.active_object
headlight1.name = "Headlight1"

bpy.ops.mesh.primitive_cylinder_add(radius=0.2, depth=0.1, location=(2.1, -0.6, 0.8))
headlight2 = bpy.context.active_object
headlight2.name = "Headlight2"

# Glowing taillights
bpy.ops.mesh.primitive_cylinder_add(radius=0.15, depth=0.1, location=(-2.1, 0.4, 0.6))
taillight1 = bpy.context.active_object
taillight1.name = "Taillight1"

bpy.ops.mesh.primitive_cylinder_add(radius=0.15, depth=0.1, location=(-2.1, -0.4, 0.6))
taillight2 = bpy.context.active_object
taillight2.name = "Taillight2"

# Add materials
materials = {
    "CarBody": (0.1, 0.1, 0.1, 1),      # Dark metal
    "Cabin": (0.2, 0.2, 0.2, 1),        # Darker metal
    "Wheel1": (0.3, 0.3, 0.3, 1),       # Tire color
    "Wheel2": (0.3, 0.3, 0.3, 1),
    "Wheel3": (0.3, 0.3, 0.3, 1),
    "Wheel4": (0.3, 0.3, 0.3, 1),
    "Headlight1": (1, 1, 0.8, 1),       # Bright white
    "Headlight2": (1, 1, 0.8, 1),
    "Taillight1": (1, 0.2, 0.2, 1),     # Red
    "Taillight2": (1, 0.2, 0.2, 1)
}

for obj_name, color in materials.items():
    obj = bpy.data.objects.get(obj_name)
    if obj:
        material = bpy.data.materials.new(name=f"{obj_name}Material")
        material.use_nodes = True
        material.node_tree.nodes["Principled BSDF"].inputs[0].default_value = color
        if "light" in obj_name.lower():
            material.node_tree.nodes["Principled BSDF"].inputs[17].default_value = 2  # Emission
        obj.data.materials.append(material)

# Add lighting
bpy.ops.object.light_add(type='SUN', location=(5, 5, 8))
sun = bpy.context.active_object
sun.name = "SunLight"
sun.data.energy = 3

# Set up camera
bpy.ops.object.camera_add(location=(6, -6, 3))
camera = bpy.context.active_object
camera.name = "Camera"
camera.rotation_euler = (1.2, 0, 0.8)

# Set camera as active
bpy.context.scene.camera = camera

# Save the file
output_path = "/Users/justin/Desktop/gthh/gtvibeathon/futuristic_car.blend"
bpy.ops.wm.save_as_mainfile(filepath=output_path)
print(f"✅ Saved futuristic car: {output_path}")
'''
    }
    
    return scenes.get(scene_type, scenes["modern_house"])

def create_and_open_scene(scene_type="modern_house"):
    """Create and open a 3D scene."""
    print(f"🎨 Creating {scene_type.replace('_', ' ').title()} Scene...")
    print("=" * 60)
    
    # Get the script for the scene type
    script_content = create_advanced_scene(scene_type)
    
    # Write script to file
    script_path = f"/Users/justin/Desktop/gthh/gtvibeathon/create_{scene_type}.py"
    with open(script_path, 'w') as f:
        f.write(script_content)
    
    # Execute with Blender
    blender_path = "/Applications/Blender.app/Contents/MacOS/Blender"
    if os.path.exists(blender_path):
        result = subprocess.run([
            blender_path, 
            "--background", 
            "--python", script_path
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Scene created successfully!")
            return f"/Users/justin/Desktop/gthh/gtvibeathon/{scene_type}.blend"
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
        print("❌ Blender not found")
        return False
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return False
    
    print(f"🎯 Opening: {file_path}")
    subprocess.Popen([blender_path, file_path])
    print("✅ Blender opened!")
    return True

def main():
    print("🎨 Improved Voxel Demo - Advanced 3D Scenes")
    print("=" * 60)
    print()
    print("Available scenes:")
    print("1. Modern House (proper walls, door, windows)")
    print("2. Futuristic Car (glowing elements)")
    print()
    
    # Create modern house
    print("🏠 Creating Modern House...")
    house_file = create_and_open_scene("modern_house")
    if house_file and os.path.exists(house_file):
        open_blender_file(house_file)
        print("✅ Modern house opened!")
    
    print()
    
    # Create futuristic car
    print("🚗 Creating Futuristic Car...")
    car_file = create_and_open_scene("futuristic_car")
    if car_file and os.path.exists(car_file):
        open_blender_file(car_file)
        print("✅ Futuristic car opened!")
    
    print()
    print("🎉 Both scenes created and opened!")
    print("📁 Files saved in: /Users/justin/Desktop/gthh/gtvibeathon/")

if __name__ == "__main__":
    main()
