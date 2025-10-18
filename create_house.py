
import bpy
import math

# Clear the scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create a house structure
# Floor
bpy.ops.mesh.primitive_cube_add(size=8, location=(0, 0, 0))
floor = bpy.context.active_object
floor.name = "Floor"
floor.scale = (1, 1, 0.1)

# Walls
bpy.ops.mesh.primitive_cube_add(size=6, location=(0, 0, 3))
wall1 = bpy.context.active_object
wall1.name = "Wall1"
wall1.scale = (1, 0.1, 1)

bpy.ops.mesh.primitive_cube_add(size=6, location=(0, 0, 3))
wall2 = bpy.context.active_object
wall2.name = "Wall2"
wall2.scale = (0.1, 1, 1)

# Door
bpy.ops.mesh.primitive_cube_add(size=2, location=(0, -3.1, 1))
door = bpy.context.active_object
door.name = "Door"
door.scale = (0.5, 0.1, 1)

# Window
bpy.ops.mesh.primitive_cube_add(size=1.5, location=(2, -3.1, 2.5))
window = bpy.context.active_object
window.name = "Window"
window.scale = (0.5, 0.1, 0.5)

# Roof
bpy.ops.mesh.primitive_cube_add(size=7, location=(0, 0, 5.5))
roof = bpy.context.active_object
roof.name = "Roof"
roof.scale = (1, 1, 0.3)

# Add materials
materials = {
    "Floor": (0.8, 0.6, 0.4, 1),  # Brown
    "Wall1": (0.9, 0.9, 0.9, 1),  # Light gray
    "Wall2": (0.9, 0.9, 0.9, 1),  # Light gray
    "Door": (0.4, 0.2, 0.1, 1),   # Dark brown
    "Window": (0.7, 0.9, 1.0, 1), # Light blue
    "Roof": (0.6, 0.3, 0.3, 1)    # Red
}

for obj_name, color in materials.items():
    obj = bpy.data.objects.get(obj_name)
    if obj:
        material = bpy.data.materials.new(name=f"{obj_name}Material")
        material.use_nodes = True
        material.node_tree.nodes["Principled BSDF"].inputs[0].default_value = color
        obj.data.materials.append(material)

# Add lighting
bpy.ops.object.light_add(type='SUN', location=(5, 5, 10))
sun = bpy.context.active_object
sun.name = "SunLight"
sun.data.energy = 3

# Set up camera
bpy.ops.object.camera_add(location=(8, -8, 4))
camera = bpy.context.active_object
camera.name = "Camera"
camera.rotation_euler = (1.2, 0, 0.8)

# Set camera as active
bpy.context.scene.camera = camera

# Save the file
output_path = "/Users/justin/Desktop/gthh/gtvibeathon/house_scene.blend"
bpy.ops.wm.save_as_mainfile(filepath=output_path)
print(f"✅ Saved house scene: {output_path}")
