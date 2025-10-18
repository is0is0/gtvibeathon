#!/usr/bin/env python3
"""Create a simple cube in Blender and save it."""

import bpy
import os

# Clear the scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create a simple cube
bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0))

# Get the cube object
cube = bpy.context.active_object
cube.name = "SimpleCube"

# Create a basic material
material = bpy.data.materials.new(name="CubeMaterial")
material.use_nodes = True

# Set the material to the cube
cube.data.materials.append(material)

# Add some basic lighting
bpy.ops.object.light_add(type='SUN', location=(5, 5, 10))
sun = bpy.context.active_object
sun.name = "SunLight"

# Set up camera
bpy.ops.object.camera_add(location=(5, -5, 5))
camera = bpy.context.active_object
camera.name = "Camera"

# Point camera at cube
camera.rotation_euler = (1.1, 0, 0.785)

# Set camera as active
bpy.context.scene.camera = camera

# Save the file
output_path = "/Users/justin/Desktop/gthh/gtvibeathon/simple_cube.blend"
bpy.ops.wm.save_as_mainfile(filepath=output_path)
print(f"✅ Saved Blender file: {output_path}")

# Also save as .blend1 backup
bpy.ops.wm.save_as_mainfile(filepath=output_path + "1")
print(f"✅ Saved backup: {output_path}1")
