#!/usr/bin/env python3
"""
House Scene Generator for Blender
Run this script in Blender to create a complete 3D house scene.
"""

# This script should be run in Blender's Scripting workspace
# It will create a complete house scene and save it as a .blend file

import bpy
import math
from math import radians, sin, cos
import random

print("🏠 Creating realistic house scene...")

# Clear the default scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Set up collections
main_col = bpy.data.collections.new("House_Scene")
bpy.context.scene.collection.children.link(main_col)

house_col = bpy.data.collections.new("House")
main_col.children.link(house_col)

landscape_col = bpy.data.collections.new("Landscape")
main_col.children.link(landscape_col)

vegetation_col = bpy.data.collections.new("Vegetation")
main_col.children.link(vegetation_col)

print("🏗️ Building house structure...")

# Foundation
bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0.15), scale=(5.5, 4.5, 0.15))
foundation = bpy.context.active_object
foundation.name = "Foundation"
house_col.objects.link(foundation)
bpy.context.scene.collection.objects.unlink(foundation)

# First floor
bpy.ops.mesh.primitive_cube_add(location=(0, 0, 1.5), scale=(5, 4, 1.5))
first_floor = bpy.context.active_object
first_floor.name = "FirstFloor_Base"
house_col.objects.link(first_floor)
bpy.context.scene.collection.objects.unlink(first_floor)

# Second floor
bpy.ops.mesh.primitive_cube_add(location=(0, 0, 4), scale=(4.8, 3.8, 1.5))
second_floor = bpy.context.active_object
second_floor.name = "SecondFloor_Base"
house_col.objects.link(second_floor)
bpy.context.scene.collection.objects.unlink(second_floor)

# Roof
bpy.ops.mesh.primitive_cube_add(location=(-2.5, 0, 6.2), scale=(3, 4.5, 0.1))
roof_left = bpy.context.active_object
roof_left.name = "Roof_Left"
roof_left.rotation_euler = (0, 0.785, 0)  # 45 degrees
house_col.objects.link(roof_left)
bpy.context.scene.collection.objects.unlink(roof_left)

bpy.ops.mesh.primitive_cube_add(location=(2.5, 0, 6.2), scale=(3, 4.5, 0.1))
roof_right = bpy.context.active_object
roof_right.name = "Roof_Right"
roof_right.rotation_euler = (0, -0.785, 0)  # -45 degrees
house_col.objects.link(roof_right)
bpy.context.scene.collection.objects.unlink(roof_right)

# Chimney
bpy.ops.mesh.primitive_cube_add(location=(3, 2, 7.5), scale=(0.6, 0.6, 1.5))
chimney = bpy.context.active_object
chimney.name = "Chimney"
house_col.objects.link(chimney)
bpy.context.scene.collection.objects.unlink(chimney)

# Windows
bpy.ops.mesh.primitive_cube_add(location=(-2, -4.05, 1.8), scale=(0.6, 0.05, 0.8))
window1 = bpy.context.active_object
window1.name = "Window_F1_Left"
house_col.objects.link(window1)
bpy.context.scene.collection.objects.unlink(window1)

bpy.ops.mesh.primitive_cube_add(location=(2, -4.05, 1.8), scale=(0.6, 0.05, 0.8))
window2 = bpy.context.active_object
window2.name = "Window_F1_Right"
house_col.objects.link(window2)
bpy.context.scene.collection.objects.unlink(window2)

# Door
bpy.ops.mesh.primitive_cube_add(location=(0, -4.05, 0.9), scale=(0.5, 0.05, 1.1))
door = bpy.context.active_object
door.name = "Front_Door"
house_col.objects.link(door)
bpy.context.scene.collection.objects.unlink(door)

print("🌱 Creating landscape...")

# Ground
bpy.ops.mesh.primitive_plane_add(location=(0, 0, 0), size=50)
ground = bpy.context.active_object
ground.name = "Ground_Meadow"
landscape_col.objects.link(ground)
bpy.context.scene.collection.objects.unlink(ground)

# Trees
bpy.ops.mesh.primitive_cylinder_add(location=(-8, 6, 2), radius=0.4, depth=4)
tree1_trunk = bpy.context.active_object
tree1_trunk.name = "Tree1_Trunk"
vegetation_col.objects.link(tree1_trunk)
bpy.context.scene.collection.objects.unlink(tree1_trunk)

bpy.ops.mesh.primitive_uv_sphere_add(location=(-8, 6, 5), radius=2.5)
tree1_foliage = bpy.context.active_object
tree1_foliage.name = "Tree1_Foliage"
vegetation_col.objects.link(tree1_foliage)
bpy.context.scene.collection.objects.unlink(tree1_foliage)

bpy.ops.mesh.primitive_cylinder_add(location=(7, 8, 2.5), radius=0.45, depth=5)
tree2_trunk = bpy.context.active_object
tree2_trunk.name = "Tree2_Trunk"
vegetation_col.objects.link(tree2_trunk)
bpy.context.scene.collection.objects.unlink(tree2_trunk)

bpy.ops.mesh.primitive_uv_sphere_add(location=(7, 8, 6), radius=3)
tree2_foliage = bpy.context.active_object
tree2_foliage.name = "Tree2_Foliage"
vegetation_col.objects.link(tree2_foliage)
bpy.context.scene.collection.objects.unlink(tree2_foliage)

print("🎨 Applying materials...")

# House material
house_material = bpy.data.materials.new(name="House_Material")
house_material.use_nodes = True
house_material.node_tree.nodes.clear()

bsdf = house_material.node_tree.nodes.new(type='ShaderNodeBsdfPrincipled')
output = house_material.node_tree.nodes.new(type='ShaderNodeOutputMaterial')
house_material.node_tree.links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

bsdf.inputs['Base Color'].default_value = (0.8, 0.6, 0.4, 1.0)  # Beige
bsdf.inputs['Roughness'].default_value = 0.6
bsdf.inputs['Metallic'].default_value = 0.0

# Apply to house objects
for obj in bpy.data.objects:
    if 'House' in obj.name or 'Roof' in obj.name or 'Foundation' in obj.name:
        if obj.data.materials:
            obj.data.materials[0] = house_material
        else:
            obj.data.materials.append(house_material)

# Grass material
grass_material = bpy.data.materials.new(name="Grass_Material")
grass_material.use_nodes = True
grass_material.node_tree.nodes.clear()

bsdf_grass = grass_material.node_tree.nodes.new(type='ShaderNodeBsdfPrincipled')
output_grass = grass_material.node_tree.nodes.new(type='ShaderNodeOutputMaterial')
grass_material.node_tree.links.new(bsdf_grass.outputs['BSDF'], output_grass.inputs['Surface'])

bsdf_grass.inputs['Base Color'].default_value = (0.2, 0.8, 0.2, 1.0)  # Green
bsdf_grass.inputs['Roughness'].default_value = 0.8

# Apply to ground
for obj in bpy.data.objects:
    if 'Ground' in obj.name:
        if obj.data.materials:
            obj.data.materials[0] = grass_material
        else:
            obj.data.materials.append(grass_material)

print("📸 Setting up camera and lighting...")

# Clear existing cameras and lights
for obj in bpy.data.objects:
    if obj.type in ['CAMERA', 'LIGHT']:
        bpy.data.objects.remove(obj, do_unlink=True)

# Create camera
camera_data = bpy.data.cameras.new(name='Camera')
camera = bpy.data.objects.new('Camera', camera_data)
bpy.context.scene.collection.objects.link(camera)

# Position camera
camera.location = (18, -12, 1.7)
camera.rotation_euler = (1.1, 0, 0.5)  # Point at house

# Set as active camera
bpy.context.scene.camera = camera

# Create sun light
sun_data = bpy.data.lights.new(name="Sun", type='SUN')
sun = bpy.data.objects.new(name="Sun", object_data=sun_data)
bpy.context.scene.collection.objects.link(sun)

sun.location = (10, 10, 20)
sun.rotation_euler = (0.7, 0, 2.4)  # Afternoon sun
sun_data.energy = 5.0
sun_data.color = (1.0, 0.95, 0.9)  # Warm white

print("🎬 Configuring render settings...")

# Set render engine to Cycles
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 256
bpy.context.scene.cycles.use_denoising = True

# Output resolution
bpy.context.scene.render.resolution_x = 1920
bpy.context.scene.render.resolution_y = 1080

print("💾 Saving Blender file...")

# Save the file
output_path = "/Users/justin/Desktop/gthh/gtvibeathon/house_scene.blend"
bpy.ops.wm.save_as_mainfile(filepath=output_path)

print("✅ Complete house scene created!")
print(f"📁 File saved to: {output_path}")
print("\n🎯 Your scene includes:")
print("   • Two-story house with pitched roof")
print("   • Windows, doors, and chimney")
print("   • Grassy landscape with trees")
print("   • Realistic lighting and materials")
print("   • Professional camera setup")
print("\n🎮 To view your scene:")
print("   • Press Numpad 0 to view through camera")
print("   • Press F12 to render the scene")
print("   • Use middle mouse button to orbit around")
