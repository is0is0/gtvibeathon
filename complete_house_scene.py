#!/usr/bin/env python3
"""
Complete House Scene Generator for Blender
Run this script in Blender to create the full 3D house scene.
"""

# ============================================================================
# COMPLETE HOUSE SCENE GENERATOR
# ============================================================================
# This script creates a realistic house in a grassy landscape with sunny weather
# Run this in Blender's Scripting workspace

import bpy
import math
from math import radians, sin, cos
import random

print("🏠 Creating realistic house scene...")

# Clear the default scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def create_collection(name, parent=None):
    """Create a collection and link it to parent or scene."""
    col = bpy.data.collections.new(name)
    if parent:
        parent.children.link(col)
    else:
        bpy.context.scene.collection.children.link(col)
    return col

def create_cube(name, location, scale, collection):
    """Create a cube and add it to collection."""
    bpy.ops.mesh.primitive_cube_add(location=location, scale=scale)
    obj = bpy.context.active_object
    obj.name = name
    collection.objects.link(obj)
    bpy.context.scene.collection.objects.unlink(obj)
    return obj

def create_cylinder(name, location, radius, depth, collection):
    """Create a cylinder and add it to collection."""
    bpy.ops.mesh.primitive_cylinder_add(location=location, radius=radius, depth=depth)
    obj = bpy.context.active_object
    obj.name = name
    collection.objects.link(obj)
    bpy.context.scene.collection.objects.unlink(obj)
    return obj

def create_plane(name, location, size, collection):
    """Create a plane and add it to collection."""
    bpy.ops.mesh.primitive_plane_add(location=location, size=size)
    obj = bpy.context.active_object
    obj.name = name
    collection.objects.link(obj)
    bpy.context.scene.collection.objects.unlink(obj)
    return obj

# ============================================================================
# COLLECTIONS
# ============================================================================

print("📁 Creating collections...")

main_col = create_collection("House_Scene")
house_col = create_collection("House", main_col)
landscape_col = create_collection("Landscape", main_col)
vegetation_col = create_collection("Vegetation", main_col)
details_col = create_collection("Details", main_col)

# ============================================================================
# HOUSE STRUCTURE
# ============================================================================

print("🏗️ Building house structure...")

# Foundation
foundation = create_cube("Foundation", (0, 0, 0.15), (5.5, 4.5, 0.15), house_col)

# First floor walls
first_floor = create_cube("FirstFloor_Base", (0, 0, 1.5), (5, 4, 1.5), house_col)

# Second floor walls
second_floor = create_cube("SecondFloor_Base", (0, 0, 4), (4.8, 3.8, 1.5), house_col)

# Individual walls for more detail
front_wall_1 = create_cube("FrontWall_Floor1", (0, -4, 1.5), (5, 0.15, 1.5), house_col)
back_wall_1 = create_cube("BackWall_Floor1", (0, 4, 1.5), (5, 0.15, 1.5), house_col)
left_wall_1 = create_cube("LeftWall_Floor1", (-5, 0, 1.5), (0.15, 4, 1.5), house_col)
right_wall_1 = create_cube("RightWall_Floor1", (5, 0, 1.5), (0.15, 4, 1.5), house_col)

front_wall_2 = create_cube("FrontWall_Floor2", (0, -3.8, 4), (4.8, 0.15, 1.5), house_col)
back_wall_2 = create_cube("BackWall_Floor2", (0, 3.8, 4), (4.8, 0.15, 1.5), house_col)
left_wall_2 = create_cube("LeftWall_Floor2", (-4.8, 0, 4), (0.15, 3.8, 1.5), house_col)
right_wall_2 = create_cube("RightWall_Floor2", (4.8, 0, 4), (0.15, 3.8, 1.5), house_col)

# ============================================================================
# ROOF
# ============================================================================

print("🏠 Creating roof...")

# Pitched roof using rotated cubes
roof_left = create_cube("Roof_Left", (-2.5, 0, 6.2), (3, 4.5, 0.1), house_col)
roof_left.rotation_euler = (0, radians(45), 0)

roof_right = create_cube("Roof_Right", (2.5, 0, 6.2), (3, 4.5, 0.1), house_col)
roof_right.rotation_euler = (0, radians(-45), 0)

# Roof ridge
roof_ridge = create_cube("Roof_Ridge", (0, 0, 7.3), (0.2, 4.5, 0.2), house_col)

# Front and back roof gables
front_gable = create_cube("Front_Gable", (0, -3.8, 5.75), (4.8, 0.15, 0.75), house_col)
back_gable = create_cube("Back_Gable", (0, 3.8, 5.75), (4.8, 0.15, 0.75), house_col)

# Chimney
chimney = create_cube("Chimney", (3, 2, 7.5), (0.6, 0.6, 1.5), house_col)

# ============================================================================
# WINDOWS AND DOORS
# ============================================================================

print("🪟 Adding windows and doors...")

# First floor windows
window_front_left = create_cube("Window_F1_Left", (-2, -4.05, 1.8), (0.6, 0.05, 0.8), house_col)
window_front_right = create_cube("Window_F1_Right", (2, -4.05, 1.8), (0.6, 0.05, 0.8), house_col)

# Window frames
frame_fl = create_cube("Frame_F1_Left", (-2, -4.1, 1.8), (0.7, 0.08, 0.9), house_col)
frame_fr = create_cube("Frame_F1_Right", (2, -4.1, 1.8), (0.7, 0.08, 0.9), house_col)

# Second floor windows
window_front_2_left = create_cube("Window_F2_Left", (-2, -3.85, 4.2), (0.5, 0.05, 0.7), house_col)
window_front_2_right = create_cube("Window_F2_Right", (2, -3.85, 4.2), (0.5, 0.05, 0.7), house_col)

frame_f2l = create_cube("Frame_F2_Left", (-2, -3.9, 4.2), (0.6, 0.08, 0.8), house_col)
frame_f2r = create_cube("Frame_F2_Right", (2, -3.9, 4.2), (0.6, 0.08, 0.8), house_col)

# Front door
door = create_cube("Front_Door", (0, -4.05, 0.9), (0.5, 0.05, 1.1), house_col)
door_frame = create_cube("Door_Frame", (0, -4.1, 0.9), (0.65, 0.1, 1.25), house_col)
door_step = create_cube("Door_Step", (0, -4.3, 0.1), (0.8, 0.3, 0.1), house_col)

# ============================================================================
# LANDSCAPE
# ============================================================================

print("🌱 Creating landscape...")

# Ground plane
ground = create_plane("Ground_Meadow", (0, 0, 0), 50, landscape_col)

# Add subdivision to ground for undulation
ground_subsurf = ground.modifiers.new(name="Subdivision", type='SUBSURF')
ground_subsurf.levels = 4
ground_subsurf.render_levels = 5

# Enter edit mode to add some vertex displacement
bpy.context.view_layer.objects.active = ground
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.subdivide(number_cuts=20)
bpy.ops.object.mode_set(mode='OBJECT')

# Add displacement modifier for terrain
displace_mod = ground.modifiers.new(name="Displace", type='DISPLACE')
displace_mod.strength = 0.3

# Driveway
driveway = create_cube("Driveway", (0, -12, 0.02), (1, 8, 0.02), landscape_col)

# ============================================================================
# VEGETATION
# ============================================================================

print("🌳 Adding trees and vegetation...")

# Tree 1 - Behind house left
tree1_trunk = create_cylinder("Tree1_Trunk", (-8, 6, 2), 0.4, 4, vegetation_col)

# Tree foliage using multiple spheres
bpy.ops.mesh.primitive_uv_sphere_add(location=(-8, 6, 5), radius=2.5)
tree1_f1 = bpy.context.active_object
tree1_f1.name = "Tree1_Foliage_1"
vegetation_col.objects.link(tree1_f1)
bpy.context.scene.collection.objects.unlink(tree1_f1)

bpy.ops.mesh.primitive_uv_sphere_add(location=(-7.5, 6.5, 5.5), radius=2)
tree1_f2 = bpy.context.active_object
tree1_f2.name = "Tree1_Foliage_2"
vegetation_col.objects.link(tree1_f2)
bpy.context.scene.collection.objects.unlink(tree1_f2)

# Tree 2 - Behind house right
tree2_trunk = create_cylinder("Tree2_Trunk", (7, 8, 2.5), 0.45, 5, vegetation_col)

bpy.ops.mesh.primitive_uv_sphere_add(location=(7, 8, 6), radius=3)
tree2_f1 = bpy.context.active_object
tree2_f1.name = "Tree2_Foliage_1"
vegetation_col.objects.link(tree2_f1)
bpy.context.scene.collection.objects.unlink(tree2_f1)

# Tree 3 - Side of house
tree3_trunk = create_cylinder("Tree3_Trunk", (-10, -2, 1.8), 0.35, 3.6, vegetation_col)

bpy.ops.mesh.primitive_uv_sphere_add(location=(-10, -2, 4.5), radius=2.2)
tree3_f1 = bpy.context.active_object
tree3_f1.name = "Tree3_Foliage_1"
vegetation_col.objects.link(tree3_f1)
bpy.context.scene.collection.objects.unlink(tree3_f1)

# Bushes
bpy.ops.mesh.primitive_uv_sphere_add(location=(-4, -5, 0.4), radius=0.6)
bush1 = bpy.context.active_object
bush1.name = "Bush_Front_Left"
bush1.scale = (1, 1, 0.7)
vegetation_col.objects.link(bush1)
bpy.context.scene.collection.objects.unlink(bush1)

bpy.ops.mesh.primitive_uv_sphere_add(location=(4, -5, 0.35), radius=0.5)
bush2 = bpy.context.active_object
bush2.name = "Bush_Front_Right"
bush2.scale = (1, 1, 0.65)
vegetation_col.objects.link(bush2)
bpy.context.scene.collection.objects.unlink(bush2)

# ============================================================================
# MATERIALS
# ============================================================================

print("🎨 Applying materials...")

# House material
house_material = bpy.data.materials.new(name="House_Material")
house_material.use_nodes = True
house_material.node_tree.nodes.clear()

# Add Principled BSDF
bsdf = house_material.node_tree.nodes.new(type='ShaderNodeBsdfPrincipled')
output = house_material.node_tree.nodes.new(type='ShaderNodeOutputMaterial')
house_material.node_tree.links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

# Set material properties
bsdf.inputs['Base Color'].default_value = (0.8, 0.6, 0.4, 1.0)  # Beige color
bsdf.inputs['Roughness'].default_value = 0.6
bsdf.inputs['Metallic'].default_value = 0.0

# Apply to house objects
for obj in bpy.data.objects:
    if 'House' in obj.name or 'Roof' in obj.name':
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

bsdf_grass.inputs['Base Color'].default_value = (0.2, 0.8, 0.2, 1.0)  # Green color
bsdf_grass.inputs['Roughness'].default_value = 0.8

# Apply to terrain
for obj in bpy.data.objects:
    if 'Ground' in obj.name or 'Grass' in obj.name:
        if obj.data.materials:
            obj.data.materials[0] = grass_material
        else:
            obj.data.materials.append(grass_material)

# ============================================================================
# LIGHTING AND CAMERA
# ============================================================================

print("📸 Setting up camera and lighting...")

# Clear existing cameras and lights
for obj in bpy.data.objects:
    if obj.type in ['CAMERA', 'LIGHT']:
        bpy.data.objects.remove(obj, do_unlink=True)

# Create camera
camera_data = bpy.data.cameras.new(name='Camera')
camera = bpy.data.objects.new('Camera', camera_data)
bpy.context.scene.collection.objects.link(camera)

# Position camera: 22m from house, eye level (1.7m), at 30-degree angle
camera.location = (18, -12, 1.7)

# Point camera at house (slightly above ground level to show roof)
direction = (0 - camera.location[0], 0 - camera.location[1], 3.5 - camera.location[2])
rot_quat = direction.__class__((direction[0], direction[1], direction[2])).to_track_quat('-Z', 'Y')
camera.rotation_euler = rot_quat.to_euler()

# Set as active camera
bpy.context.scene.camera = camera

# Camera settings - 40mm focal length for natural perspective
camera.data.lens = 40
camera.data.clip_start = 0.1
camera.data.clip_end = 200

# Primary Sun Light
sun_data = bpy.data.lights.new(name="Sun", type='SUN')
sun = bpy.data.objects.new(name="Sun", object_data=sun_data)
bpy.context.scene.collection.objects.link(sun)

# Sun position: 50 degrees elevation, 45 degrees azimuth (afternoon sun)
sun.location = (10, 10, 20)
sun.rotation_euler = (math.radians(40), 0, math.radians(135))

# Sun settings - warm afternoon light (5500K)
sun_data.energy = 5.0
sun_data.color = (1.0, 0.95, 0.9)  # Warm white
sun_data.angle = math.radians(0.53)  # Sun's angular diameter for soft shadows

# ============================================================================
# RENDER SETTINGS
# ============================================================================

print("🎬 Configuring render settings...")

# Set render engine to Cycles for photorealistic output
bpy.context.scene.render.engine = 'CYCLES'

# Sampling settings for high quality
bpy.context.scene.cycles.samples = 256  # High quality for final render
bpy.context.scene.cycles.preview_samples = 64
bpy.context.scene.cycles.use_adaptive_sampling = True
bpy.context.scene.cycles.adaptive_threshold = 0.01

# Light paths for realistic lighting
bpy.context.scene.cycles.max_bounces = 12
bpy.context.scene.cycles.diffuse_bounces = 4
bpy.context.scene.cycles.glossy_bounces = 4
bpy.context.scene.cycles.transmission_bounces = 8
bpy.context.scene.cycles.volume_bounces = 0
bpy.context.scene.cycles.transparent_max_bounces = 8

# Performance settings
bpy.context.scene.cycles.use_denoising = True
bpy.context.scene.cycles.denoiser = 'OPENIMAGEDENOISE'

# Output resolution - HD quality
bpy.context.scene.render.resolution_x = 1920
bpy.context.scene.render.resolution_y = 1080
bpy.context.scene.render.resolution_percentage = 100

# Output format
bpy.context.scene.render.image_settings.file_format = 'PNG'
bpy.context.scene.render.image_settings.color_mode = 'RGB'
bpy.context.scene.render.image_settings.color_depth = '16'

# ============================================================================
# SAVE THE FILE
# ============================================================================

print("💾 Saving Blender file...")

# Save the file
output_path = "/Users/justin/Desktop/gthh/gtvibeathon/house_scene.blend"
bpy.ops.wm.save_as_mainfile(filepath=output_path)

print("✅ Complete house scene created!")
print(f"📁 File saved to: {output_path}")
print("\n🎯 To view your scene:")
print("   1. Open Blender")
print("   2. File → Open → Select 'house_scene.blend'")
print("   3. Press Numpad 0 to view through camera")
print("   4. Press F12 to render the scene")
print("\n🏠 Your scene includes:")
print("   • Two-story house with pitched roof")
print("   • Windows, doors, and chimney")
print("   • Grassy landscape with trees")
print("   • Realistic lighting and materials")
print("   • Professional camera setup")
