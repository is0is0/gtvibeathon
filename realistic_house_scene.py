#!/usr/bin/env python3
"""
Realistic House Scene Generator for Blender
This script creates a photorealistic 3D house scene with advanced materials,
textures, reflections, and lighting.
Run this in Blender's Scripting workspace.
"""

import bpy
import math
import bmesh
from mathutils import Vector

print("🏠 Creating realistic house scene...")

# Clear the default scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# ============================================================================
# ADVANCED HOUSE STRUCTURE
# ============================================================================

print("🏗️ Building detailed house structure...")

# Foundation with proper proportions
bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0.1), scale=(6, 4, 0.1))
foundation = bpy.context.active_object
foundation.name = "Foundation"

# Main house structure
bpy.ops.mesh.primitive_cube_add(location=(0, 0, 2), scale=(5, 3.5, 2))
house_main = bpy.context.active_object
house_main.name = "House_Main"

# Second floor
bpy.ops.mesh.primitive_cube_add(location=(0, 0, 4.5), scale=(4.5, 3, 1.5))
house_second = bpy.context.active_object
house_second.name = "House_Second"

# Detailed roof with proper pitch
bpy.ops.mesh.primitive_cube_add(location=(-1.5, 0, 6.5), scale=(3, 3.5, 0.2))
roof_left = bpy.context.active_object
roof_left.name = "Roof_Left"
roof_left.rotation_euler = (0, math.radians(30), 0)

bpy.ops.mesh.primitive_cube_add(location=(1.5, 0, 6.5), scale=(3, 3.5, 0.2))
roof_right = bpy.context.active_object
roof_right.name = "Roof_Right"
roof_right.rotation_euler = (0, math.radians(-30), 0)

# Chimney with detail
bpy.ops.mesh.primitive_cube_add(location=(2.5, 1.5, 7.5), scale=(0.4, 0.4, 1.2))
chimney = bpy.context.active_object
chimney.name = "Chimney"

# Windows with frames
window_positions = [
    (-2, -1.8, 2.5),  # Front left
    (2, -1.8, 2.5),   # Front right
    (-2, -1.8, 4.8),  # Second floor left
    (2, -1.8, 4.8),   # Second floor right
]

for i, pos in enumerate(window_positions):
    # Window frame
    bpy.ops.mesh.primitive_cube_add(location=pos, scale=(0.8, 0.1, 1.2))
    frame = bpy.context.active_object
    frame.name = f"Window_Frame_{i+1}"
    
    # Window glass
    bpy.ops.mesh.primitive_cube_add(location=(pos[0], pos[1]-0.05, pos[2]), scale=(0.7, 0.02, 1.1))
    glass = bpy.context.active_object
    glass.name = f"Window_Glass_{i+1}"

# Front door with detail
bpy.ops.mesh.primitive_cube_add(location=(0, -1.8, 1.2), scale=(0.6, 0.1, 1.4))
door = bpy.context.active_object
door.name = "Front_Door"

# Door frame
bpy.ops.mesh.primitive_cube_add(location=(0, -1.85, 1.2), scale=(0.8, 0.15, 1.5))
door_frame = bpy.context.active_object
door_frame.name = "Door_Frame"

# ============================================================================
# LANDSCAPE WITH DETAIL
# ============================================================================

print("🌱 Creating detailed landscape...")

# Main ground plane
bpy.ops.mesh.primitive_plane_add(location=(0, 0, 0), size=50)
ground = bpy.context.active_object
ground.name = "Ground"

# Add subdivision for terrain detail
ground.modifiers.new(name="Subdivision", type='SUBSURF')
ground.modifiers["Subdivision"].levels = 3

# Add displacement for natural terrain
displace_mod = ground.modifiers.new(name="Displace", type='DISPLACE')
displace_mod.strength = 0.5

# Create displacement texture
terrain_tex = bpy.data.textures.new("Terrain_Texture", type='VORONOI')
terrain_tex.noise_scale = 2.0
displace_mod.texture = terrain_tex

# Trees with more detail
tree_positions = [
    (-12, 8, 0), (12, 8, 0), (-15, -5, 0), (15, -5, 0)
]

for i, pos in enumerate(tree_positions):
    # Tree trunk
    bpy.ops.mesh.primitive_cylinder_add(location=pos, radius=0.4, depth=4)
    trunk = bpy.context.active_object
    trunk.name = f"Tree_Trunk_{i+1}"
    
    # Tree foliage (multiple spheres for natural look)
    for j in range(3):
        bpy.ops.mesh.primitive_uv_sphere_add(
            location=(pos[0] + (j-1)*0.5, pos[1] + (j-1)*0.3, pos[2] + 4 + j*0.5), 
            radius=1.5 + j*0.3
        )
        foliage = bpy.context.active_object
        foliage.name = f"Tree_Foliage_{i+1}_{j+1}"

# ============================================================================
# ADVANCED MATERIALS WITH TEXTURES
# ============================================================================

print("🎨 Creating realistic materials...")

# House wall material with brick texture
house_material = bpy.data.materials.new(name="House_Wall_Material")
house_material.use_nodes = True
house_material.node_tree.nodes.clear()

# Get nodes
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
brick_tex.inputs['Scale'].default_value = 5.0
brick_tex.inputs['Mortar Size'].default_value = 0.02

# Add normal map for brick detail
normal_map = nodes.new(type='ShaderNodeNormalMap')
brick_normal = nodes.new(type='ShaderNodeTexBrick')
brick_normal.inputs['Scale'].default_value = 5.0
brick_normal.inputs['Mortar Size'].default_value = 0.02

# Connect nodes
links.new(brick_tex.outputs['Color'], bsdf.inputs['Base Color'])
links.new(brick_normal.outputs['Normal'], normal_map.inputs['Color'])
links.new(normal_map.outputs['Normal'], bsdf.inputs['Normal'])

# Set material properties
bsdf.inputs['Roughness'].default_value = 0.7
bsdf.inputs['Metallic'].default_value = 0.0

# Apply to house objects
for obj in bpy.data.objects:
    if 'House' in obj.name and 'Frame' not in obj.name and 'Glass' not in obj.name:
        obj.data.materials.append(house_material)

# Roof material with shingles
roof_material = bpy.data.materials.new(name="Roof_Material")
roof_material.use_nodes = True
roof_material.node_tree.nodes.clear()

nodes = roof_material.node_tree.nodes
links = roof_material.node_tree.links

bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
output = nodes.new(type='ShaderNodeOutputMaterial')
links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

# Add shingle texture
shingle_tex = nodes.new(type='ShaderNodeTexBrick')
shingle_tex.inputs['Color1'].default_value = (0.3, 0.3, 0.3, 1.0)  # Dark shingles
shingle_tex.inputs['Color2'].default_value = (0.2, 0.2, 0.2, 1.0)  # Darker shingles
shingle_tex.inputs['Scale'].default_value = 8.0
shingle_tex.inputs['Mortar Size'].default_value = 0.01

# Add displacement for 3D shingles
displacement = nodes.new(type='ShaderNodeDisplacement')
shingle_disp = nodes.new(type='ShaderNodeTexBrick')
shingle_disp.inputs['Scale'].default_value = 8.0

links.new(shingle_tex.outputs['Color'], bsdf.inputs['Base Color'])
links.new(shingle_disp.outputs['Color'], displacement.inputs['Height'])
links.new(displacement.outputs['Displacement'], output.inputs['Displacement'])

bsdf.inputs['Roughness'].default_value = 0.8
bsdf.inputs['Metallic'].default_value = 0.1

# Apply to roof
for obj in bpy.data.objects:
    if 'Roof' in obj.name:
        obj.data.materials.append(roof_material)

# Glass material with reflections
glass_material = bpy.data.materials.new(name="Glass_Material")
glass_material.use_nodes = True
glass_material.node_tree.nodes.clear()

nodes = glass_material.node_tree.nodes
links = glass_material.node_tree.links

bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
output = nodes.new(type='ShaderNodeOutputMaterial')
links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

# Glass properties
bsdf.inputs['Base Color'].default_value = (0.8, 0.9, 1.0, 1.0)  # Slight blue tint
bsdf.inputs['Roughness'].default_value = 0.0
bsdf.inputs['Metallic'].default_value = 0.0
bsdf.inputs['Transmission'].default_value = 0.95
bsdf.inputs['Transmission Roughness'].default_value = 0.0
bsdf.inputs['IOR'].default_value = 1.45

# Apply to windows
for obj in bpy.data.objects:
    if 'Glass' in obj.name:
        obj.data.materials.append(glass_material)

# Grass material with subsurface scattering
grass_material = bpy.data.materials.new(name="Grass_Material")
grass_material.use_nodes = True
grass_material.node_tree.nodes.clear()

nodes = grass_material.node_tree.nodes
links = grass_material.node_tree.links

bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
output = nodes.new(type='ShaderNodeOutputMaterial')
links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

# Add grass texture
grass_tex = nodes.new(type='ShaderNodeTexVoronoi')
grass_tex.inputs['Scale'].default_value = 10.0
grass_tex.inputs['Randomness'].default_value = 0.8

# Color ramp for grass variation
color_ramp = nodes.new(type='ShaderNodeValToRGB')
color_ramp.color_ramp.elements[0].color = (0.1, 0.6, 0.1, 1.0)  # Dark green
color_ramp.color_ramp.elements[1].color = (0.3, 0.8, 0.3, 1.0)  # Light green

links.new(grass_tex.outputs['Color'], color_ramp.inputs['Fac'])
links.new(color_ramp.outputs['Color'], bsdf.inputs['Base Color'])

bsdf.inputs['Roughness'].default_value = 0.9
bsdf.inputs['Subsurface'].default_value = 0.1
bsdf.inputs['Subsurface Color'].default_value = (0.2, 0.8, 0.2, 1.0)

# Apply to ground
ground.data.materials.append(grass_material)

# Tree material
tree_material = bpy.data.materials.new(name="Tree_Material")
tree_material.use_nodes = True
tree_material.node_tree.nodes.clear()

nodes = tree_material.node_tree.nodes
links = tree_material.node_tree.links

bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
output = nodes.new(type='ShaderNodeOutputMaterial')
links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

bsdf.inputs['Base Color'].default_value = (0.2, 0.6, 0.2, 1.0)  # Green
bsdf.inputs['Roughness'].default_value = 0.8
bsdf.inputs['Subsurface'].default_value = 0.2
bsdf.inputs['Subsurface Color'].default_value = (0.1, 0.8, 0.1, 1.0)

# Apply to trees
for obj in bpy.data.objects:
    if 'Tree' in obj.name:
        obj.data.materials.append(tree_material)

# ============================================================================
# PROFESSIONAL LIGHTING SETUP
# ============================================================================

print("☀️ Setting up professional lighting...")

# Clear existing lights
for obj in bpy.data.objects:
    if obj.type == 'LIGHT':
        bpy.data.objects.remove(obj, do_unlink=True)

# Main sun light
bpy.ops.object.light_add(type='SUN', location=(10, 10, 15))
sun = bpy.context.active_object
sun.name = "Sun"
sun.data.energy = 5.0
sun.data.color = (1.0, 0.95, 0.8)  # Warm sunlight
sun.rotation_euler = (math.radians(45), math.radians(30), 0)

# Fill light for shadows
bpy.ops.object.light_add(type='AREA', location=(-15, 5, 8))
fill_light = bpy.context.active_object
fill_light.name = "Fill_Light"
fill_light.data.energy = 200
fill_light.data.color = (0.7, 0.8, 1.0)  # Cool fill
fill_light.data.size = 10

# Rim light for depth
bpy.ops.object.light_add(type='AREA', location=(15, -10, 6))
rim_light = bpy.context.active_object
rim_light.name = "Rim_Light"
rim_light.data.energy = 150
rim_light.data.color = (1.0, 0.9, 0.7)  # Warm rim
rim_light.data.size = 8

# ============================================================================
# CAMERA AND RENDER SETUP
# ============================================================================

print("📸 Setting up camera and render...")

# Clear existing camera
for obj in bpy.data.objects:
    if obj.type == 'CAMERA':
        bpy.data.objects.remove(obj, do_unlink=True)

# Create camera
bpy.ops.object.camera_add(location=(15, -12, 4))
camera = bpy.context.active_object
camera.name = "Camera"

# Position camera for best view
camera.location = (15, -12, 4)
camera.rotation_euler = (math.radians(70), 0, math.radians(45))

# Set as active camera
bpy.context.scene.camera = camera

# Camera settings
camera.data.lens = 35  # Wide angle
camera.data.clip_start = 0.1
camera.data.clip_end = 1000

# Depth of field
camera.data.dof.use_dof = True
camera.data.dof.focus_distance = 20.0
camera.data.dof.aperture_fstop = 5.6

# ============================================================================
# ADVANCED RENDER SETTINGS
# ============================================================================

print("🎬 Configuring advanced render settings...")

# Set render engine to Cycles
bpy.context.scene.render.engine = 'CYCLES'

# High quality sampling
bpy.context.scene.cycles.samples = 512
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

# Caustics for realistic light behavior
bpy.context.scene.cycles.caustics_reflective = True
bpy.context.scene.cycles.caustics_refractive = True

# Denoising
bpy.context.scene.cycles.use_denoising = True
bpy.context.scene.cycles.denoiser = 'OPENIMAGEDENOISE'

# Film settings
bpy.context.scene.render.film_transparent = False
bpy.context.scene.cycles.film_exposure = 1.0

# Color management
bpy.context.scene.view_settings.view_transform = 'Filmic'
bpy.context.scene.view_settings.look = 'Medium High Contrast'
bpy.context.scene.sequencer_colorspace_settings.name = 'sRGB'

# Output resolution
bpy.context.scene.render.resolution_x = 1920
bpy.context.scene.render.resolution_y = 1080
bpy.context.scene.render.resolution_percentage = 100

# Output format
bpy.context.scene.render.image_settings.file_format = 'PNG'
bpy.context.scene.render.image_settings.color_mode = 'RGB'
bpy.context.scene.render.image_settings.color_depth = '16'

# ============================================================================
# WORLD ENVIRONMENT
# ============================================================================

print("🌍 Setting up world environment...")

# Configure world background
world = bpy.data.worlds.get('World')
if not world:
    world = bpy.data.worlds.new('World')
bpy.context.scene.world = world

world.use_nodes = True
node_tree = world.node_tree
nodes = node_tree.nodes
links = node_tree.links

# Clear existing nodes
nodes.clear()

# Create sky texture
tex_coord = nodes.new(type='ShaderNodeTexCoord')
mapping = nodes.new(type='ShaderNodeMapping')
sky_texture = nodes.new(type='ShaderNodeTexSky')
background = nodes.new(type='ShaderNodeBackground')
output = nodes.new(type='ShaderNodeOutputWorld')

# Position nodes
tex_coord.location = (-800, 0)
mapping.location = (-600, 0)
sky_texture.location = (-400, 0)
background.location = (-200, 0)
output.location = (0, 0)

# Configure sky texture for realistic sky
sky_texture.sky_type = 'HOSEK_WILKIE'
sky_texture.turbidity = 2.0  # Clear sky
sky_texture.ground_albedo = 0.3  # Grass reflection
sky_texture.sun_elevation = math.radians(45)
sky_texture.sun_rotation = math.radians(30)
sky_texture.sun_intensity = 1.0

# Background strength
background.inputs['Strength'].default_value = 1.0

# Link nodes
links.new(tex_coord.outputs['Generated'], mapping.inputs['Vector'])
links.new(mapping.outputs['Vector'], sky_texture.inputs['Vector'])
links.new(sky_texture.outputs['Color'], background.inputs['Color'])
links.new(background.outputs['Background'], output.inputs['Surface'])

# ============================================================================
# SAVE THE SCENE
# ============================================================================

print("💾 Saving realistic house scene...")

# Save the file
output_path = "/Users/justin/Desktop/gthh/gtvibeathon/realistic_house_scene.blend"
bpy.ops.wm.save_as_mainfile(filepath=output_path)

print("✅ Realistic house scene created!")
print(f"📁 File saved to: {output_path}")
print("\n🎯 Your scene includes:")
print("   • Detailed house with brick walls and shingle roof")
print("   • Realistic glass windows with reflections")
print("   • Natural grass with subsurface scattering")
print("   • Professional 3-point lighting setup")
print("   • Advanced materials with textures and normal maps")
print("   • Realistic sky environment")
print("   • High-quality render settings")
print("\n🎮 To view your scene:")
print("   • Press Numpad 0 to view through camera")
print("   • Press F12 to render the scene")
print("   • Use middle mouse button to orbit around")
print("   • Switch to Material Preview or Rendered view for best results")
