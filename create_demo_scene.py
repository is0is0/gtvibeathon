
import bpy
import math

# Clear the scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create a red cube
bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 1))
cube = bpy.context.active_object
cube.name = "RedCube"

# Create material for the cube
material = bpy.data.materials.new(name="RedMaterial")
material.use_nodes = True
material.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (1, 0, 0, 1)  # Red color
cube.data.materials.append(material)

# Create a white plane
bpy.ops.mesh.primitive_plane_add(size=10, location=(0, 0, 0))
plane = bpy.context.active_object
plane.name = "WhitePlane"

# Create material for the plane
plane_material = bpy.data.materials.new(name="WhiteMaterial")
plane_material.use_nodes = True
plane_material.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (1, 1, 1, 1)  # White color
plane.data.materials.append(plane_material)

# Add lighting
bpy.ops.object.light_add(type='SUN', location=(5, 5, 10))
sun = bpy.context.active_object
sun.name = "SunLight"
sun.data.energy = 3

# Set up camera
bpy.ops.object.camera_add(location=(5, -5, 5))
camera = bpy.context.active_object
camera.name = "Camera"
camera.rotation_euler = (1.1, 0, 0.785)

# Set camera as active
bpy.context.scene.camera = camera

# Save the file
output_path = "/Users/justin/Desktop/gthh/gtvibeathon/demo_scene.blend"
bpy.ops.wm.save_as_mainfile(filepath=output_path)
print(f"✅ Saved Blender file: {output_path}")
