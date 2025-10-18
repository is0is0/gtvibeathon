
import bpy
import bmesh
import math
import numpy as np
from mathutils import Vector

# Clear the scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def create_advanced_3d_scene():
    """Create an advanced 3D scene suitable for complete pipeline."""
    
    # Create a complex architectural structure
    house_width = 10
    house_depth = 8
    wall_height = 5
    
    # Foundation
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, -0.3))
    foundation = bpy.context.active_object
    foundation.name = "Foundation"
    foundation.scale = (house_width + 2, house_depth + 2, 0.6)
    
    # Main structure with multiple levels
    walls = [
        ("FrontWall", (0, house_depth/2, wall_height/2), (house_width, 0.4, wall_height)),
        ("BackWall", (0, -house_depth/2, wall_height/2), (house_width, 0.4, wall_height)),
        ("LeftWall", (-house_width/2, 0, wall_height/2), (0.4, house_depth, wall_height)),
        ("RightWall", (house_width/2, 0, wall_height/2), (0.4, house_depth, wall_height))
    ]
    
    for wall_name, position, scale in walls:
        bpy.ops.mesh.primitive_cube_add(size=1, location=position)
        wall = bpy.context.active_object
        wall.name = wall_name
        wall.scale = scale
    
    # Multi-level roof
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, wall_height + 0.8))
    roof = bpy.context.active_object
    roof.name = "MainRoof"
    roof.scale = (house_width + 2, house_depth + 2, 1.0)
    
    # Add architectural details
    details = [
        ("Chimney", (3, 3, wall_height + 2), (1.2, 1.2, 2.0)),
        ("Balcony", (0, house_depth/2 + 0.8, wall_height - 0.8), (4, 2, 0.3)),
        ("Stairs", (0, -house_depth/2 - 0.8, 0.2), (3, 2, 0.3)),
        ("Window1", (3, house_depth/2 + 0.2, 3), (2, 0.2, 2.5)),
        ("Window2", (-3, house_depth/2 + 0.2, 3), (2, 0.2, 2.5)),
        ("Window3", (0, -house_depth/2 - 0.2, 3), (3, 0.2, 2.5)),
        ("Door", (0, house_depth/2 + 0.2, 1.5), (2.5, 0.2, 3))
    ]
    
    for detail_name, position, scale in details:
        bpy.ops.mesh.primitive_cube_add(size=1, location=position)
        detail = bpy.context.active_object
        detail.name = detail_name
        detail.scale = scale
    
    # Add furniture for complexity
    furniture = [
        ("Table", (0, 0, 0.5), (3, 1.5, 0.1)),
        ("Chair1", (2, 1.5, 0.3), (0.6, 0.6, 1.0)),
        ("Chair2", (-2, 1.5, 0.3), (0.6, 0.6, 1.0)),
        ("Chair3", (2, -1.5, 0.3), (0.6, 0.6, 1.0)),
        ("Chair4", (-2, -1.5, 0.3), (0.6, 0.6, 1.0)),
        ("Bed", (-4, 0, 0.4), (3, 2.5, 0.6)),
        ("Sofa", (4, 0, 0.4), (2.5, 1.5, 0.6)),
        ("Bookshelf", (-4, -3, 1.5), (0.4, 1.2, 3)),
        ("Desk", (4, -3, 0.5), (2, 1, 0.1)),
        ("TV", (4, -3, 1.5), (1.5, 0.1, 1)),
        ("Lamp1", (2, 2, 0.8), (0.2, 0.2, 1.5)),
        ("Lamp2", (-2, 2, 0.8), (0.2, 0.2, 1.5))
    ]
    
    for item_name, position, scale in furniture:
        bpy.ops.mesh.primitive_cube_add(size=1, location=position)
        item = bpy.context.active_object
        item.name = item_name
        item.scale = scale
    
    # Create realistic materials
    materials = {
        "Foundation": (0.4, 0.4, 0.4, 1),  # Concrete
        "FrontWall": (0.98, 0.98, 0.98, 1), # White
        "BackWall": (0.98, 0.98, 0.98, 1),  # White
        "LeftWall": (0.98, 0.98, 0.98, 1),  # White
        "RightWall": (0.98, 0.98, 0.98, 1), # White
        "MainRoof": (0.6, 0.3, 0.3, 1),     # Red
        "Chimney": (0.3, 0.3, 0.3, 1),      # Dark gray
        "Balcony": (0.8, 0.8, 0.8, 1),      # Light gray
        "Stairs": (0.5, 0.5, 0.5, 1),       # Gray
        "Window1": (0.7, 0.9, 1.0, 1),       # Light blue
        "Window2": (0.7, 0.9, 1.0, 1),      # Light blue
        "Window3": (0.7, 0.9, 1.0, 1),      # Light blue
        "Door": (0.3, 0.2, 0.1, 1),         # Dark brown
        "Table": (0.5, 0.3, 0.1, 1),        # Brown
        "Chair1": (0.3, 0.2, 0.1, 1),       # Dark brown
        "Chair2": (0.3, 0.2, 0.1, 1),       # Dark brown
        "Chair3": (0.3, 0.2, 0.1, 1),       # Dark brown
        "Chair4": (0.3, 0.2, 0.1, 1),       # Dark brown
        "Bed": (0.8, 0.8, 0.9, 1),          # Light blue
        "Sofa": (0.6, 0.4, 0.2, 1),         # Brown
        "Bookshelf": (0.4, 0.2, 0.1, 1),    # Dark brown
        "Desk": (0.5, 0.3, 0.1, 1),         # Brown
        "TV": (0.1, 0.1, 0.1, 1),          # Black
        "Lamp1": (0.9, 0.9, 0.7, 1),       # Light yellow
        "Lamp2": (0.9, 0.9, 0.7, 1)        # Light yellow
    }
    
    for obj_name, color in materials.items():
        obj = bpy.data.objects.get(obj_name)
        if obj:
            material = bpy.data.materials.new(name=f"{obj_name}Material")
            material.use_nodes = True
            material.node_tree.nodes["Principled BSDF"].inputs[0].default_value = color
            obj.data.materials.append(material)
    
    # Add professional lighting
    bpy.ops.object.light_add(type='SUN', location=(20, 20, 25))
    sun = bpy.context.active_object
    sun.name = "SunLight"
    sun.data.energy = 10
    
    # Add area light for interior
    bpy.ops.object.light_add(type='AREA', location=(0, 0, 4))
    area_light = bpy.context.active_object
    area_light.name = "AreaLight"
    area_light.data.energy = 300
    area_light.data.size = 8
    
    # Add spot lights
    bpy.ops.object.light_add(type='SPOT', location=(2, 2, 2))
    spot1 = bpy.context.active_object
    spot1.name = "SpotLight1"
    spot1.data.energy = 200
    spot1.data.spot_size = math.radians(45)
    
    bpy.ops.object.light_add(type='SPOT', location=(-2, 2, 2))
    spot2 = bpy.context.active_object
    spot2.name = "SpotLight2"
    spot2.data.energy = 200
    spot2.data.spot_size = math.radians(45)
    
    # Set up camera
    bpy.ops.object.camera_add(location=(15, -15, 10))
    camera = bpy.context.active_object
    camera.name = "Camera"
    camera.rotation_euler = (1.0, 0, 0.6)
    bpy.context.scene.camera = camera
    
    return True

# Create the advanced 3D scene
create_advanced_3d_scene()

# Save the file
output_path = "/Users/justin/Desktop/gthh/gtvibeathon/advanced_3d_scene.blend"
bpy.ops.wm.save_as_mainfile(filepath=output_path)
print(f"✅ Saved advanced 3D scene: {output_path}")
