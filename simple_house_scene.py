#!/usr/bin/env python3
"""
Simple House Scene Generator for Blender
This script creates a complete 3D house scene with textures.
Run this in Blender's Scripting workspace.
"""

import bpy
import math

print("🏠 Creating house scene...")

# Clear the default scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create the house base
bpy.ops.mesh.primitive_cube_add(location=(0, 0, 1), scale=(4, 3, 1))
house_base = bpy.context.active_object
house_base.name = "House_Base"

# Create the roof
bpy.ops.mesh.primitive_cube_add(location=(0, 0, 3), scale=(4.5, 3.5, 0.5))
roof = bpy.context.active_object
roof.name = "Roof"
roof.rotation_euler = (0, 0, 0.3)  # Slight angle

# Create windows
bpy.ops.mesh.primitive_cube_add(location=(-1.5, -1.6, 1.5), scale=(0.8, 0.1, 0.8))
window1 = bpy.context.active_object
window1.name = "Window_1"

bpy.ops.mesh.primitive_cube_add(location=(1.5, -1.6, 1.5), scale=(0.8, 0.1, 0.8))
window2 = bpy.context.active_object
window2.name = "Window_2"

# Create door
bpy.ops.mesh.primitive_cube_add(location=(0, -1.6, 0.5), scale=(0.6, 0.1, 1))
door = bpy.context.active_object
door.name = "Door"

# Create ground
bpy.ops.mesh.primitive_plane_add(location=(0, 0, 0), size=20)
ground = bpy.context.active_object
ground.name = "Ground"

# Create trees
bpy.ops.mesh.primitive_cylinder_add(location=(-8, 5, 1), radius=0.3, depth=3)
tree1_trunk = bpy.context.active_object
tree1_trunk.name = "Tree1_Trunk"

bpy.ops.mesh.primitive_uv_sphere_add(location=(-8, 5, 3), radius=2)
tree1_foliage = bpy.context.active_object
tree1_foliage.name = "Tree1_Foliage"

bpy.ops.mesh.primitive_cylinder_add(location=(8, 5, 1), radius=0.3, depth=3)
tree2_trunk = bpy.context.active_object
tree2_trunk.name = "Tree2_Trunk"

bpy.ops.mesh.primitive_uv_sphere_add(location=(8, 5, 3), radius=2)
tree2_foliage = bpy.context.active_object
tree2_foliage.name = "Tree2_Foliage"

print("🎨 Creating materials...")

# House material (beige)
house_material = bpy.data.materials.new(name="House_Material")
house_material.use_nodes = True
house_material.node_tree.nodes.clear()

bsdf = house_material.node_tree.nodes.new(type='ShaderNodeBsdfPrincipled')
output = house_material.node_tree.nodes.new(type='ShaderNodeOutputMaterial')
house_material.node_tree.links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

bsdf.inputs['Base Color'].default_value = (0.8, 0.6, 0.4, 1.0)  # Beige
bsdf.inputs['Roughness'].default_value = 0.6

# Apply to house objects
for obj in bpy.data.objects:
    if 'House' in obj.name or 'Roof' in obj.name:
        obj.data.materials.append(house_material)

# Grass material (green)
grass_material = bpy.data.materials.new(name="Grass_Material")
grass_material.use_nodes = True
grass_material.node_tree.nodes.clear()

bsdf_grass = grass_material.node_tree.nodes.new(type='ShaderNodeBsdfPrincipled')
output_grass = grass_material.node_tree.nodes.new(type='ShaderNodeOutputMaterial')
grass_material.node_tree.links.new(bsdf_grass.outputs['BSDF'], output_grass.inputs['Surface'])

bsdf_grass.inputs['Base Color'].default_value = (0.2, 0.8, 0.2, 1.0)  # Green
bsdf_grass.inputs['Roughness'].default_value = 0.8

# Apply to ground
ground.data.materials.append(grass_material)

# Tree material (brown)
tree_material = bpy.data.materials.new(name="Tree_Material")
tree_material.use_nodes = True
tree_material.node_tree.nodes.clear()

bsdf_tree = tree_material.node_tree.nodes.new(type='ShaderNodeBsdfPrincipled')
output_tree = tree_material.node_tree.nodes.new(type='ShaderNodeOutputMaterial')
tree_material.node_tree.links.new(bsdf_tree.outputs['BSDF'], output_tree.inputs['Surface'])

bsdf_tree.inputs['Base Color'].default_value = (0.4, 0.2, 0.1, 1.0)  # Brown
bsdf_tree.inputs['Roughness'].default_value = 0.8

# Apply to trees
for obj in bpy.data.objects:
    if 'Tree' in obj.name:
        obj.data.materials.append(tree_material)

print("📸 Setting up camera...")

# Clear existing camera
for obj in bpy.data.objects:
    if obj.type == 'CAMERA':
        bpy.data.objects.remove(obj, do_unlink=True)

# Create camera
bpy.ops.object.camera_add(location=(10, -10, 3))
camera = bpy.context.active_object
camera.name = "Camera"

# Point camera at house
camera.rotation_euler = (1.1, 0, 0.8)

# Set as active camera
bpy.context.scene.camera = camera

print("☀️ Adding lighting...")

# Clear existing lights
for obj in bpy.data.objects:
    if obj.type == 'LIGHT':
        bpy.data.objects.remove(obj, do_unlink=True)

# Create sun light
bpy.ops.object.light_add(type='SUN', location=(5, 5, 10))
sun = bpy.context.active_object
sun.name = "Sun"
sun.data.energy = 3.0
sun.data.color = (1.0, 0.95, 0.8)  # Warm white

print("🎬 Setting up render...")

# Set render engine to Cycles
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 128
bpy.context.scene.cycles.use_denoising = True

# Output resolution
bpy.context.scene.render.resolution_x = 1920
bpy.context.scene.render.resolution_y = 1080

print("💾 Saving file...")

# Save the file
output_path = "/Users/justin/Desktop/gthh/gtvibeathon/house_scene.blend"
bpy.ops.wm.save_as_mainfile(filepath=output_path)

print("✅ House scene created successfully!")
print(f"📁 File saved to: {output_path}")
print("\n🎯 Your scene includes:")
print("   • House with roof, windows, and door")
print("   • Grassy ground with trees")
print("   • Realistic materials and lighting")
print("   • Camera setup for viewing")
print("\n🎮 To view your scene:")
print("   • Press Numpad 0 to view through camera")
print("   • Press F12 to render the scene")
print("   • Use middle mouse button to orbit around")
