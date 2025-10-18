
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
