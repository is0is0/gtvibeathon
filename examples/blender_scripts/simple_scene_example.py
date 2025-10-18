"""
Example Blender Python script showing the structure of generated scripts.

This is a simple scene with a cube, plane, and lighting that demonstrates
the kind of code the agents generate. You can run this directly in Blender:

1. Open Blender
2. Switch to the Scripting workspace
3. Open this file
4. Click "Run Script"
"""

import bpy
import math

# ===== STEP 1: Clear Scene =====
# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# ===== STEP 2: Create Geometry =====

# Create a cube (main object)
bpy.ops.mesh.primitive_cube_add(location=(0, 0, 1))
cube = bpy.context.active_object
cube.name = "MainCube"
cube.scale = (1, 1, 1)

# Create a ground plane
bpy.ops.mesh.primitive_plane_add(location=(0, 0, 0))
plane = bpy.context.active_object
plane.name = "GroundPlane"
plane.scale = (5, 5, 1)

# ===== STEP 3: Create Materials =====

# Material for the cube
cube_mat = bpy.data.materials.new(name="CubeMaterial")
cube_mat.use_nodes = True
nodes = cube_mat.node_tree.nodes
links = cube_mat.node_tree.links

# Clear default nodes
nodes.clear()

# Create Principled BSDF and Material Output
bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
output = nodes.new(type='ShaderNodeOutputMaterial')

# Set material properties
bsdf.inputs['Base Color'].default_value = (0.8, 0.2, 0.1, 1.0)  # Red-orange
bsdf.inputs['Metallic'].default_value = 0.0
bsdf.inputs['Roughness'].default_value = 0.3

# Connect nodes
links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

# Apply material to cube
cube.data.materials.append(cube_mat)

# Material for the plane
plane_mat = bpy.data.materials.new(name="PlaneMaterial")
plane_mat.use_nodes = True
nodes = plane_mat.node_tree.nodes
links = plane_mat.node_tree.links
nodes.clear()

bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
output = nodes.new(type='ShaderNodeOutputMaterial')

bsdf.inputs['Base Color'].default_value = (0.8, 0.8, 0.8, 1.0)  # Light gray
bsdf.inputs['Roughness'].default_value = 0.9

links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
plane.data.materials.append(plane_mat)

# ===== STEP 4: Set Up Camera =====

# Create or get camera
if 'Camera' in bpy.data.objects:
    camera = bpy.data.objects['Camera']
else:
    camera_data = bpy.data.cameras.new(name='Camera')
    camera = bpy.data.objects.new('Camera', camera_data)
    bpy.context.scene.collection.objects.link(camera)

# Position camera
camera.location = (5, -5, 4)
camera.rotation_euler = (math.radians(63), 0, math.radians(45))

# Camera settings
camera.data.lens = 50
camera.data.clip_start = 0.1
camera.data.clip_end = 100

# Set as active camera
bpy.context.scene.camera = camera

# ===== STEP 5: Set Up Lighting =====

# Create sun light
sun_data = bpy.data.lights.new(name="Sun", type='SUN')
sun = bpy.data.objects.new(name="Sun", object_data=sun_data)
bpy.context.scene.collection.objects.link(sun)
sun.location = (0, 0, 10)
sun.rotation_euler = (math.radians(45), 0, math.radians(30))
sun_data.energy = 3.0

# Create area light (fill light)
area_data = bpy.data.lights.new(name="FillLight", type='AREA')
area = bpy.data.objects.new(name="FillLight", object_data=area_data)
bpy.context.scene.collection.objects.link(area)
area.location = (-3, -3, 3)
area.rotation_euler = (math.radians(60), 0, math.radians(-45))
area_data.energy = 50
area_data.size = 2

# ===== STEP 6: Configure Render Settings =====

scene = bpy.context.scene

# Set render engine
scene.render.engine = 'CYCLES'

# Render quality
scene.cycles.samples = 128

# Output settings
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.filepath = '/tmp/render.png'

# World background
world = bpy.data.worlds.get('World')
if world:
    world.use_nodes = True
    bg = world.node_tree.nodes.get('Background')
    if bg:
        bg.inputs['Color'].default_value = (0.5, 0.6, 0.7, 1.0)  # Sky blue
        bg.inputs['Strength'].default_value = 1.0

print("Scene setup complete!")
print(f"Objects in scene: {len(bpy.data.objects)}")
print(f"Camera: {camera.name} at {camera.location}")
print(f"Ready to render!")
