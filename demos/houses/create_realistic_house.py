
import bpy
import math
import bmesh
from mathutils import Vector

# Clear the scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# House dimensions
house_width = 8
house_depth = 6
wall_height = 3.5
wall_thickness = 0.3

# Create foundation with realistic concrete material
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, -0.15))
foundation = bpy.context.active_object
foundation.name = "Foundation"
foundation.scale = (house_width + 1, house_depth + 1, 0.3)

# Create seamless walls using proper corner connections
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

# Left wall (extends to meet front/back walls)
bpy.ops.mesh.primitive_cube_add(size=1, location=(-house_width/2, 0, wall_height/2))
left_wall = bpy.context.active_object
left_wall.name = "LeftWall"
left_wall.scale = (wall_thickness, house_depth, wall_height)

# Right wall (extends to meet front/back walls)
bpy.ops.mesh.primitive_cube_add(size=1, location=(house_width/2, 0, wall_height/2))
right_wall = bpy.context.active_object
right_wall.name = "RightWall"
right_wall.scale = (wall_thickness, house_depth, wall_height)

# Create floor with wood texture
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.05))
floor = bpy.context.active_object
floor.name = "Floor"
floor.scale = (house_width - 0.1, house_depth - 0.1, 0.1)

# Create door with frame
door_width = 2.2
door_height = 2.5
door_frame_thickness = 0.1

# Door frame
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, house_depth/2 + wall_thickness/2 + 0.01, door_height/2))
door_frame = bpy.context.active_object
door_frame.name = "DoorFrame"
door_frame.scale = (door_width + 0.2, wall_thickness + 0.1, door_height + 0.2)

# Door
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, house_depth/2 + wall_thickness/2 + 0.02, door_height/2))
door = bpy.context.active_object
door.name = "Door"
door.scale = (door_width, wall_thickness, door_height)

# Create windows with frames
window_width = 1.8
window_height = 1.5
window_frame_thickness = 0.08

# Window 1 (front wall, left)
bpy.ops.mesh.primitive_cube_add(size=1, location=(2.5, house_depth/2 + wall_thickness/2 + 0.01, 2.2))
window1_frame = bpy.context.active_object
window1_frame.name = "Window1Frame"
window1_frame.scale = (window_width + 0.15, wall_thickness + 0.1, window_height + 0.15)

bpy.ops.mesh.primitive_cube_add(size=1, location=(2.5, house_depth/2 + wall_thickness/2 + 0.02, 2.2))
window1 = bpy.context.active_object
window1.name = "Window1"
window1.scale = (window_width, wall_thickness, window_height)

# Window 2 (front wall, right)
bpy.ops.mesh.primitive_cube_add(size=1, location=(-2.5, house_depth/2 + wall_thickness/2 + 0.01, 2.2))
window2_frame = bpy.context.active_object
window2_frame.name = "Window2Frame"
window2_frame.scale = (window_width + 0.15, wall_thickness + 0.1, window_height + 0.15)

bpy.ops.mesh.primitive_cube_add(size=1, location=(-2.5, house_depth/2 + wall_thickness/2 + 0.02, 2.2))
window2 = bpy.context.active_object
window2.name = "Window2"
window2.scale = (window_width, wall_thickness, window_height)

# Create realistic roof with overhang
roof_width = house_width + 1.5
roof_depth = house_depth + 1.5
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, wall_height + 0.4))
roof = bpy.context.active_object
roof.name = "Roof"
roof.scale = (roof_width, roof_depth, 0.5)

# Add realistic materials with proper nodes
def create_realistic_material(name, base_color, roughness=0.5, metallic=0.0, emission_strength=0.0):
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
    bsdf.inputs['Emission Strength'].default_value = emission_strength
    
    return material

# Create realistic materials
materials = {
    "Foundation": create_realistic_material("FoundationMat", (0.4, 0.4, 0.4), 0.8, 0.0),  # Concrete
    "Floor": create_realistic_material("FloorMat", (0.6, 0.4, 0.2), 0.3, 0.0),  # Wood
    "FrontWall": create_realistic_material("WallMat", (0.95, 0.95, 0.95), 0.2, 0.0),  # White paint
    "BackWall": create_realistic_material("WallMat", (0.95, 0.95, 0.95), 0.2, 0.0),
    "LeftWall": create_realistic_material("WallMat", (0.95, 0.95, 0.95), 0.2, 0.0),
    "RightWall": create_realistic_material("WallMat", (0.95, 0.95, 0.95), 0.2, 0.0),
    "DoorFrame": create_realistic_material("DoorFrameMat", (0.3, 0.2, 0.1), 0.4, 0.0),  # Wood frame
    "Door": create_realistic_material("DoorMat", (0.2, 0.15, 0.1), 0.3, 0.0),  # Dark wood
    "Window1Frame": create_realistic_material("WindowFrameMat", (0.8, 0.8, 0.8), 0.1, 0.0),  # White frame
    "Window2Frame": create_realistic_material("WindowFrameMat", (0.8, 0.8, 0.8), 0.1, 0.0),
    "Window1": create_realistic_material("WindowMat", (0.7, 0.9, 1.0), 0.0, 0.0),  # Glass
    "Window2": create_realistic_material("WindowMat", (0.7, 0.9, 1.0), 0.0, 0.0),
    "Roof": create_realistic_material("RoofMat", (0.6, 0.3, 0.3), 0.7, 0.0)  # Red tiles
}

# Apply materials to objects
for obj_name, material in materials.items():
    obj = bpy.data.objects.get(obj_name)
    if obj:
        obj.data.materials.append(material)

# Add realistic lighting setup
# Main sun light
bpy.ops.object.light_add(type='SUN', location=(15, 15, 20))
sun = bpy.context.active_object
sun.name = "SunLight"
sun.data.energy = 8
sun.data.angle = math.radians(30)

# Fill light for shadows
bpy.ops.object.light_add(type='SUN', location=(-10, -10, 15))
fill_light = bpy.context.active_object
fill_light.name = "FillLight"
fill_light.data.energy = 3
fill_light.data.color = (0.9, 0.9, 1.0)  # Slightly blue

# Interior lighting
bpy.ops.object.light_add(type='AREA', location=(0, 0, 2.5))
interior_light = bpy.context.active_object
interior_light.name = "InteriorLight"
interior_light.data.energy = 200
interior_light.data.size = 5
interior_light.data.color = (1.0, 0.95, 0.8)  # Warm white

# Set up realistic camera
bpy.ops.object.camera_add(location=(12, -10, 6))
camera = bpy.context.active_object
camera.name = "Camera"
camera.rotation_euler = (1.2, 0, 0.8)

# Set camera as active
bpy.context.scene.camera = camera

# Set render settings for realism
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 256
bpy.context.scene.cycles.device = 'GPU' if bpy.context.preferences.addons['cycles'].preferences.has_active_device() else 'CPU'

# Save the file
output_path = "/Users/justin/Desktop/gthh/gtvibeathon/realistic_house.blend"
bpy.ops.wm.save_as_mainfile(filepath=output_path)
print(f"✅ Saved realistic house: {output_path}")
