
import bpy
import math

# Clear the scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Futuristic car with glowing elements
car_length = 4
car_width = 2
car_height = 1.2

# Car body
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, car_height/2))
body = bpy.context.active_object
body.name = "CarBody"
body.scale = (car_length, car_width, car_height)

# Car cabin
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, car_height + 0.3))
cabin = bpy.context.active_object
cabin.name = "Cabin"
cabin.scale = (car_length * 0.7, car_width * 0.8, 0.6)

# Wheels
wheel_positions = [
    (1.5, 1.2, 0.3),   # Front left
    (1.5, -1.2, 0.3),  # Front right
    (-1.5, 1.2, 0.3),  # Rear left
    (-1.5, -1.2, 0.3)  # Rear right
]

for i, pos in enumerate(wheel_positions):
    bpy.ops.mesh.primitive_cylinder_add(radius=0.4, depth=0.3, location=pos)
    wheel = bpy.context.active_object
    wheel.name = f"Wheel{i+1}"
    wheel.rotation_euler = (math.radians(90), 0, 0)

# Glowing headlights
bpy.ops.mesh.primitive_cylinder_add(radius=0.2, depth=0.1, location=(2.1, 0.6, 0.8))
headlight1 = bpy.context.active_object
headlight1.name = "Headlight1"

bpy.ops.mesh.primitive_cylinder_add(radius=0.2, depth=0.1, location=(2.1, -0.6, 0.8))
headlight2 = bpy.context.active_object
headlight2.name = "Headlight2"

# Glowing taillights
bpy.ops.mesh.primitive_cylinder_add(radius=0.15, depth=0.1, location=(-2.1, 0.4, 0.6))
taillight1 = bpy.context.active_object
taillight1.name = "Taillight1"

bpy.ops.mesh.primitive_cylinder_add(radius=0.15, depth=0.1, location=(-2.1, -0.4, 0.6))
taillight2 = bpy.context.active_object
taillight2.name = "Taillight2"

# Add materials
materials = {
    "CarBody": (0.1, 0.1, 0.1, 1),      # Dark metal
    "Cabin": (0.2, 0.2, 0.2, 1),        # Darker metal
    "Wheel1": (0.3, 0.3, 0.3, 1),       # Tire color
    "Wheel2": (0.3, 0.3, 0.3, 1),
    "Wheel3": (0.3, 0.3, 0.3, 1),
    "Wheel4": (0.3, 0.3, 0.3, 1),
    "Headlight1": (1, 1, 0.8, 1),       # Bright white
    "Headlight2": (1, 1, 0.8, 1),
    "Taillight1": (1, 0.2, 0.2, 1),     # Red
    "Taillight2": (1, 0.2, 0.2, 1)
}

for obj_name, color in materials.items():
    obj = bpy.data.objects.get(obj_name)
    if obj:
        material = bpy.data.materials.new(name=f"{obj_name}Material")
        material.use_nodes = True
        material.node_tree.nodes["Principled BSDF"].inputs[0].default_value = color
        if "light" in obj_name.lower():
            material.node_tree.nodes["Principled BSDF"].inputs[17].default_value = 2  # Emission
        obj.data.materials.append(material)

# Add lighting
bpy.ops.object.light_add(type='SUN', location=(5, 5, 8))
sun = bpy.context.active_object
sun.name = "SunLight"
sun.data.energy = 3

# Set up camera
bpy.ops.object.camera_add(location=(6, -6, 3))
camera = bpy.context.active_object
camera.name = "Camera"
camera.rotation_euler = (1.2, 0, 0.8)

# Set camera as active
bpy.context.scene.camera = camera

# Save the file
output_path = "/Users/justin/Desktop/gthh/gtvibeathon/futuristic_car.blend"
bpy.ops.wm.save_as_mainfile(filepath=output_path)
print(f"✅ Saved futuristic car: {output_path}")
