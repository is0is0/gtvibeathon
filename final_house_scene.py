#!/usr/bin/env python3
"""
Final Working House Scene - Complete with Geometry, Textures, and Lighting
This script creates a complete 3D house scene with proper materials and lighting.
Run this in Blender's Scripting workspace.
"""

import bpy
import math

print("🏠 Creating complete house scene...")

# Clear the default scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# ============================================================================
# CREATE HOUSE STRUCTURE
# ============================================================================

print("🏗️ Building house structure...")

# House base
bpy.ops.mesh.primitive_cube_add(location=(0, 0, 1), scale=(4, 3, 1))
house_base = bpy.context.active_object
house_base.name = "House_Base"

# Roof
bpy.ops.mesh.primitive_cube_add(location=(0, 0, 3), scale=(4.5, 3.5, 0.5))
roof = bpy.context.active_object
roof.name = "Roof"

# Windows
bpy.ops.mesh.primitive_cube_add(location=(-1.5, -1.6, 1.5), scale=(0.8, 0.1, 0.8))
window1 = bpy.context.active_object
window1.name = "Window_1"

bpy.ops.mesh.primitive_cube_add(location=(1.5, -1.6, 1.5), scale=(0.8, 0.1, 0.8))
window2 = bpy.context.active_object
window2.name = "Window_2"

# Door
bpy.ops.mesh.primitive_cube_add(location=(0, -1.6, 0.5), scale=(0.6, 0.1, 1))
door = bpy.context.active_object
door.name = "Door"

# Ground
bpy.ops.mesh.primitive_plane_add(location=(0, 0, 0), size=20)
ground = bpy.context.active_object
ground.name = "Ground"

# Trees
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

# ============================================================================
# CREATE MATERIALS
# ============================================================================

print("🎨 Creating materials...")

# House material (brick-like)
house_material = bpy.data.materials.new(name="House_Material")
house_material.use_nodes = True
house_material.node_tree.nodes.clear()

# Get the material nodes
nodes = house_material.node_tree.nodes
links = house_material.node_tree.links

# Add Principled BSDF
bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
output = nodes.new(type='ShaderNodeOutputMaterial')
links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

# Add brick texture
brick_tex = nodes.new(type='ShaderNodeTexBrick')
brick_tex.inputs['Color1'].default_value = (0.8, 0.6, 0.4, 1.0)  # Light brick
brick_tex.inputs['Color2'].default_value = (0.6, 0.4, 0.2, 1.0)  # Dark brick
brick_tex.inputs['Scale'].default_value = 3.0

# Connect brick texture to base color
links.new(brick_tex.outputs['Color'], bsdf.inputs['Base Color'])

# Set material properties
bsdf.inputs['Roughness'].default_value = 0.7
bsdf.inputs['Metallic'].default_value = 0.0

# Apply to house
house_base.data.materials.append(house_material)

# Roof material (dark shingles)
roof_material = bpy.data.materials.new(name="Roof_Material")
roof_material.use_nodes = True
roof_material.node_tree.nodes.clear()

nodes = roof_material.node_tree.nodes
links = roof_material.node_tree.links

bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
output = nodes.new(type='ShaderNodeOutputMaterial')
links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

# Dark roof color
bsdf.inputs['Base Color'].default_value = (0.2, 0.2, 0.2, 1.0)  # Dark gray
bsdf.inputs['Roughness'].default_value = 0.8
bsdf.inputs['Metallic'].default_value = 0.1

# Apply to roof
roof.data.materials.append(roof_material)

# Glass material (transparent)
glass_material = bpy.data.materials.new(name="Glass_Material")
glass_material.use_nodes = True
glass_material.node_tree.nodes.clear()

nodes = glass_material.node_tree.nodes
links = glass_material.node_tree.links

bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
output = nodes.new(type='ShaderNodeOutputMaterial')
links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

# Glass properties
bsdf.inputs['Base Color'].default_value = (0.8, 0.9, 1.0, 1.0)  # Slight blue
bsdf.inputs['Roughness'].default_value = 0.0
bsdf.inputs['Metallic'].default_value = 0.0
bsdf.inputs['Transmission'].default_value = 0.9
bsdf.inputs['IOR'].default_value = 1.45

# Apply to windows
window1.data.materials.append(glass_material)
window2.data.materials.append(glass_material)

# Grass material (green)
grass_material = bpy.data.materials.new(name="Grass_Material")
grass_material.use_nodes = True
grass_material.node_tree.nodes.clear()

nodes = grass_material.node_tree.nodes
links = grass_material.node_tree.links

bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
output = nodes.new(type='ShaderNodeOutputMaterial')
links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

# Grass color
bsdf.inputs['Base Color'].default_value = (0.2, 0.8, 0.2, 1.0)  # Green
bsdf.inputs['Roughness'].default_value = 0.8

# Apply to ground
ground.data.materials.append(grass_material)

# Tree material (brown trunk, green foliage)
tree_trunk_material = bpy.data.materials.new(name="Tree_Trunk_Material")
tree_trunk_material.use_nodes = True
tree_trunk_material.node_tree.nodes.clear()

nodes = tree_trunk_material.node_tree.nodes
links = tree_trunk_material.node_tree.links

bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
output = nodes.new(type='ShaderNodeOutputMaterial')
links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

bsdf.inputs['Base Color'].default_value = (0.4, 0.2, 0.1, 1.0)  # Brown
bsdf.inputs['Roughness'].default_value = 0.8

# Apply to tree trunks
tree1_trunk.data.materials.append(tree_trunk_material)
tree2_trunk.data.materials.append(tree_trunk_material)

# Tree foliage material (green)
tree_foliage_material = bpy.data.materials.new(name="Tree_Foliage_Material")
tree_foliage_material.use_nodes = True
tree_foliage_material.node_tree.nodes.clear()

nodes = tree_foliage_material.node_tree.nodes
links = tree_foliage_material.node_tree.links

bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
output = nodes.new(type='ShaderNodeOutputMaterial')
links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

bsdf.inputs['Base Color'].default_value = (0.2, 0.6, 0.2, 1.0)  # Green
bsdf.inputs['Roughness'].default_value = 0.8

# Apply to tree foliage
tree1_foliage.data.materials.append(tree_foliage_material)
tree2_foliage.data.materials.append(tree_foliage_material)

# ============================================================================
# SETUP LIGHTING
# ============================================================================

print("☀️ Setting up lighting...")

# Clear existing lights
for obj in bpy.data.objects:
    if obj.type == 'LIGHT':
        bpy.data.objects.remove(obj, do_unlink=True)

# Main sun light
bpy.ops.object.light_add(type='SUN', location=(5, 5, 10))
sun = bpy.context.active_object
sun.name = "Sun"
sun.data.energy = 3.0
sun.data.color = (1.0, 0.95, 0.8)  # Warm white
sun.rotation_euler = (math.radians(45), math.radians(30), 0)

# Fill light
bpy.ops.object.light_add(type='AREA', location=(-10, 5, 5))
fill_light = bpy.context.active_object
fill_light.name = "Fill_Light"
fill_light.data.energy = 100
fill_light.data.color = (0.7, 0.8, 1.0)  # Cool blue
fill_light.data.size = 5

# ============================================================================
# SETUP CAMERA
# ============================================================================

print("📸 Setting up camera...")

# Clear existing camera
for obj in bpy.data.objects:
    if obj.type == 'CAMERA':
        bpy.data.objects.remove(obj, do_unlink=True)

# Create camera
bpy.ops.object.camera_add(location=(8, -8, 3))
camera = bpy.context.active_object
camera.name = "Camera"

# Point camera at house
camera.rotation_euler = (math.radians(70), 0, math.radians(45))

# Set as active camera
bpy.context.scene.camera = camera

# ============================================================================
# RENDER SETTINGS
# ============================================================================

print("🎬 Setting up render settings...")

# Set render engine to Cycles
bpy.context.scene.render.engine = 'CYCLES'

# Set samples for good quality
bpy.context.scene.cycles.samples = 128
bpy.context.scene.cycles.use_denoising = True

# Output resolution
bpy.context.scene.render.resolution_x = 1920
bpy.context.scene.render.resolution_y = 1080

# ============================================================================
# SAVE SCENE
# ============================================================================

print("💾 Saving scene...")

# Save the file
output_path = "/Users/justin/Desktop/gthh/gtvibeathon/final_house_scene.blend"
bpy.ops.wm.save_as_mainfile(filepath=output_path)

print("✅ Complete house scene created successfully!")
print(f"📁 File saved to: {output_path}")
print("\n🎯 Your scene includes:")
print("   • House with brick texture")
print("   • Dark shingle roof")
print("   • Glass windows with transparency")
print("   • Green grass ground")
print("   • Trees with trunk and foliage")
print("   • Professional lighting setup")
print("\n🎮 To view your scene:")
print("   • Press Numpad 0 to view through camera")
print("   • Press F12 to render the scene")
print("   • Switch to 'Material Preview' or 'Rendered' view for best results")
print("   • Use middle mouse button to orbit around")
