
import bpy
import math
import bmesh
from mathutils import Vector

# Clear the scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create a modern architectural scene
house_width = 10
house_depth = 8
wall_height = 4

# Foundation with realistic concrete
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, -0.2))
foundation = bpy.context.active_object
foundation.name = "Foundation"
foundation.scale = (house_width + 2, house_depth + 2, 0.4)

# Create seamless walls with perfect corners
wall_thickness = 0.25

# Front wall
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

# Create floor with wood planks
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.05))
floor = bpy.context.active_object
floor.name = "Floor"
floor.scale = (house_width - 0.2, house_depth - 0.2, 0.1)

# Create realistic door with handle
door_width = 2.5
door_height = 2.8

# Door frame
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, house_depth/2 + wall_thickness/2 + 0.01, door_height/2))
door_frame = bpy.context.active_object
door_frame.name = "DoorFrame"
door_frame.scale = (door_width + 0.3, wall_thickness + 0.15, door_height + 0.3)

# Door
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, house_depth/2 + wall_thickness/2 + 0.02, door_height/2))
door = bpy.context.active_object
door.name = "Door"
door.scale = (door_width, wall_thickness, door_height)

# Door handle
bpy.ops.mesh.primitive_cylinder_add(radius=0.05, depth=0.1, location=(0.8, house_depth/2 + wall_thickness/2 + 0.03, 1.4))
door_handle = bpy.context.active_object
door_handle.name = "DoorHandle"
door_handle.rotation_euler = (0, math.radians(90), 0)

# Create large windows
window_width = 2.5
window_height = 2.0

# Window 1
bpy.ops.mesh.primitive_cube_add(size=1, location=(3, house_depth/2 + wall_thickness/2 + 0.01, 2.5))
window1_frame = bpy.context.active_object
window1_frame.name = "Window1Frame"
window1_frame.scale = (window_width + 0.2, wall_thickness + 0.1, window_height + 0.2)

bpy.ops.mesh.primitive_cube_add(size=1, location=(3, house_depth/2 + wall_thickness/2 + 0.02, 2.5))
window1 = bpy.context.active_object
window1.name = "Window1"
window1.scale = (window_width, wall_thickness, window_height)

# Window 2
bpy.ops.mesh.primitive_cube_add(size=1, location=(-3, house_depth/2 + wall_thickness/2 + 0.01, 2.5))
window2_frame = bpy.context.active_object
window2_frame.name = "Window2Frame"
window2_frame.scale = (window_width + 0.2, wall_thickness + 0.1, window_height + 0.2)

bpy.ops.mesh.primitive_cube_add(size=1, location=(-3, house_depth/2 + wall_thickness/2 + 0.02, 2.5))
window2 = bpy.context.active_object
window2.name = "Window2"
window2.scale = (window_width, wall_thickness, window_height)

# Create modern roof
roof_width = house_width + 2
roof_depth = house_depth + 2
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, wall_height + 0.5))
roof = bpy.context.active_object
roof.name = "Roof"
roof.scale = (roof_width, roof_depth, 0.6)

# Add realistic materials with advanced node setup
def create_advanced_material(name, base_color, roughness=0.5, metallic=0.0, normal_strength=1.0):
    material = bpy.data.materials.new(name=name)
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    
    # Clear default nodes
    nodes.clear()
    
    # Add Principled BSDF
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.location = (0, 0)
    
    # Add Material Output
    output = nodes.new(type='ShaderNodeOutputMaterial')
    output.location = (400, 0)
    
    # Connect BSDF to output
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    
    # Set material properties
    bsdf.inputs['Base Color'].default_value = (*base_color, 1.0)
    bsdf.inputs['Roughness'].default_value = roughness
    bsdf.inputs['Metallic'].default_value = metallic
    bsdf.inputs['Normal'].default_value = (0.5, 0.5, 1.0)
    
    return material

# Create advanced materials
materials = {
    "Foundation": create_advanced_material("FoundationMat", (0.35, 0.35, 0.35), 0.9, 0.0),  # Concrete
    "Floor": create_advanced_material("FloorMat", (0.5, 0.3, 0.15), 0.4, 0.0),  # Wood
    "FrontWall": create_advanced_material("WallMat", (0.98, 0.98, 0.98), 0.1, 0.0),  # White paint
    "BackWall": create_advanced_material("WallMat", (0.98, 0.98, 0.98), 0.1, 0.0),
    "LeftWall": create_advanced_material("WallMat", (0.98, 0.98, 0.98), 0.1, 0.0),
    "RightWall": create_advanced_material("WallMat", (0.98, 0.98, 0.98), 0.1, 0.0),
    "DoorFrame": create_advanced_material("DoorFrameMat", (0.25, 0.15, 0.08), 0.3, 0.0),  # Wood
    "Door": create_advanced_material("DoorMat", (0.15, 0.1, 0.05), 0.2, 0.0),  # Dark wood
    "DoorHandle": create_advanced_material("HandleMat", (0.8, 0.8, 0.8), 0.1, 0.8),  # Metal
    "Window1Frame": create_advanced_material("WindowFrameMat", (0.9, 0.9, 0.9), 0.05, 0.0),  # White
    "Window2Frame": create_advanced_material("WindowFrameMat", (0.9, 0.9, 0.9), 0.05, 0.0),
    "Window1": create_advanced_material("WindowMat", (0.8, 0.9, 1.0), 0.0, 0.0),  # Glass
    "Window2": create_advanced_material("WindowMat", (0.8, 0.9, 1.0), 0.0, 0.0),
    "Roof": create_advanced_material("RoofMat", (0.5, 0.2, 0.2), 0.8, 0.0)  # Red tiles
}

# Apply materials
for obj_name, material in materials.items():
    obj = bpy.data.objects.get(obj_name)
    if obj:
        obj.data.materials.append(material)

# Add professional lighting
# Main key light
bpy.ops.object.light_add(type='SUN', location=(20, 20, 25))
key_light = bpy.context.active_object
key_light.name = "KeyLight"
key_light.data.energy = 12
key_light.data.angle = math.radians(25)

# Fill light
bpy.ops.object.light_add(type='SUN', location=(-15, -15, 20))
fill_light = bpy.context.active_object
fill_light.name = "FillLight"
fill_light.data.energy = 4
fill_light.data.color = (0.95, 0.95, 1.0)

# Rim light
bpy.ops.object.light_add(type='SUN', location=(0, -20, 15))
rim_light = bpy.context.active_object
rim_light.name = "RimLight"
rim_light.data.energy = 2
rim_light.data.color = (1.0, 0.9, 0.8)

# Interior lighting
bpy.ops.object.light_add(type='AREA', location=(0, 0, 3))
interior_light = bpy.context.active_object
interior_light.name = "InteriorLight"
interior_light.data.energy = 300
interior_light.data.size = 6
interior_light.data.color = (1.0, 0.95, 0.85)

# Set up professional camera
bpy.ops.object.camera_add(location=(15, -12, 8))
camera = bpy.context.active_object
camera.name = "Camera"
camera.rotation_euler = (1.1, 0, 0.7)

# Set camera as active
bpy.context.scene.camera = camera

# Set render settings for maximum quality
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 512
bpy.context.scene.cycles.device = 'GPU' if bpy.context.preferences.addons['cycles'].preferences.has_active_device() else 'CPU'
bpy.context.scene.cycles.use_denoising = True

# Save the file
output_path = "/Users/justin/Desktop/gthh/gtvibeathon/ultra_realistic_house.blend"
bpy.ops.wm.save_as_mainfile(filepath=output_path)
print(f"✅ Saved ultra-realistic house: {output_path}")
