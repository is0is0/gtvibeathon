#!/usr/bin/env python3
"""Demo showing how to train meshes using PyTorch3D with Voxel system."""

import os
import subprocess
import sys
import torch
import numpy as np
from pathlib import Path

def create_mesh_training_scene():
    """Create a scene that demonstrates mesh training capabilities."""
    print("🧠 Creating Mesh Training Scene...")
    print("=" * 60)
    
    blender_script = '''
import bpy
import bmesh
import math
import numpy as np
from mathutils import Vector

# Clear the scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create a complex mesh suitable for training
def create_trainable_mesh():
    """Create a mesh with multiple objects for training."""
    
    # Create a house with multiple components
    house_width = 6
    house_depth = 4
    wall_height = 3
    
    # Foundation
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, -0.1))
    foundation = bpy.context.active_object
    foundation.name = "Foundation"
    foundation.scale = (house_width + 0.5, house_depth + 0.5, 0.2)
    
    # Walls
    walls = [
        ("FrontWall", (0, house_depth/2, wall_height/2), (house_width, 0.2, wall_height)),
        ("BackWall", (0, -house_depth/2, wall_height/2), (house_width, 0.2, wall_height)),
        ("LeftWall", (-house_width/2, 0, wall_height/2), (0.2, house_depth, wall_height)),
        ("RightWall", (house_width/2, 0, wall_height/2), (0.2, house_depth, wall_height))
    ]
    
    for wall_name, position, scale in walls:
        bpy.ops.mesh.primitive_cube_add(size=1, location=position)
        wall = bpy.context.active_object
        wall.name = wall_name
        wall.scale = scale
    
    # Roof
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, wall_height + 0.3))
    roof = bpy.context.active_object
    roof.name = "Roof"
    roof.scale = (house_width + 1, house_depth + 1, 0.4)
    
    # Add some furniture for complexity
    furniture = [
        ("Table", (0, 0, 0.4), (1.5, 0.8, 0.05)),
        ("Chair1", (1, 1, 0.2), (0.4, 0.4, 0.8)),
        ("Chair2", (-1, 1, 0.2), (0.4, 0.4, 0.8)),
        ("Bed", (-2, 0, 0.2), (2, 1.5, 0.3))
    ]
    
    for item_name, position, scale in furniture:
        bpy.ops.mesh.primitive_cube_add(size=1, location=position)
        item = bpy.context.active_object
        item.name = item_name
        item.scale = scale
    
    # Create materials for different components
    materials = {
        "Foundation": (0.4, 0.4, 0.4, 1),  # Concrete
        "FrontWall": (0.9, 0.9, 0.9, 1),   # White
        "BackWall": (0.9, 0.9, 0.9, 1),    # White
        "LeftWall": (0.9, 0.9, 0.9, 1),    # White
        "RightWall": (0.9, 0.9, 0.9, 1),   # White
        "Roof": (0.6, 0.3, 0.3, 1),        # Red
        "Table": (0.5, 0.3, 0.1, 1),       # Brown
        "Chair1": (0.3, 0.2, 0.1, 1),      # Dark brown
        "Chair2": (0.3, 0.2, 0.1, 1),      # Dark brown
        "Bed": (0.8, 0.8, 0.9, 1)          # Light blue
    }
    
    for obj_name, color in materials.items():
        obj = bpy.data.objects.get(obj_name)
        if obj:
            material = bpy.data.materials.new(name=f"{obj_name}Material")
            material.use_nodes = True
            material.node_tree.nodes["Principled BSDF"].inputs[0].default_value = color
            obj.data.materials.append(material)
    
    # Add lighting
    bpy.ops.object.light_add(type='SUN', location=(10, 10, 15))
    sun = bpy.context.active_object
    sun.name = "SunLight"
    sun.data.energy = 5
    
    # Set up camera
    bpy.ops.object.camera_add(location=(8, -8, 6))
    camera = bpy.context.active_object
    camera.name = "Camera"
    camera.rotation_euler = (1.2, 0, 0.8)
    bpy.context.scene.camera = camera
    
    return True

# Create the trainable mesh
create_trainable_mesh()

# Save the file
output_path = "/Users/justin/Desktop/gthh/gtvibeathon/trainable_mesh.blend"
bpy.ops.wm.save_as_mainfile(filepath=output_path)
print(f"✅ Saved trainable mesh: {output_path}")
'''
    
    # Write and execute script
    script_path = "/Users/justin/Desktop/gthh/gtvibeathon/create_trainable_mesh.py"
    with open(script_path, 'w') as f:
        f.write(blender_script)
    
    blender_path = "/Applications/Blender.app/Contents/MacOS/Blender"
    if os.path.exists(blender_path):
        result = subprocess.run([
            blender_path, 
            "--background", 
            "--python", script_path
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Trainable mesh created!")
            return "/Users/justin/Desktop/gthh/gtvibeathon/trainable_mesh.blend"
        else:
            print(f"❌ Error: {result.stderr}")
            return None
    else:
        print("❌ Blender not found")
        return None

def create_pytorch3d_training_script():
    """Create a PyTorch3D training script for mesh optimization."""
    print("🧠 Creating PyTorch3D Training Script...")
    print("=" * 60)
    
    training_script = '''#!/usr/bin/env python3
"""
PyTorch3D Mesh Training Script
Demonstrates how to train meshes using the PyTorch3D Meshes class.
"""

import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from pytorch3d.structures import Meshes
from pytorch3d.losses import mesh_laplacian_smoothing, mesh_normal_consistency
from pytorch3d.ops import sample_points_from_meshes
from pytorch3d.utils import ico_sphere

class MeshOptimizer(nn.Module):
    """Neural network for optimizing mesh vertices."""
    
    def __init__(self, num_vertices):
        super().__init__()
        self.num_vertices = num_vertices
        
        # Simple MLP to predict vertex offsets
        self.mlp = nn.Sequential(
            nn.Linear(3, 64),
            nn.ReLU(),
            nn.Linear(64, 64),
            nn.ReLU(),
            nn.Linear(64, 3)
        )
    
    def forward(self, vertices):
        """Predict vertex offsets."""
        return self.mlp(vertices)

def create_simple_mesh():
    """Create a simple mesh for training."""
    # Create a simple cube mesh
    vertices = torch.tensor([
        [-1, -1, -1], [1, -1, -1], [1, 1, -1], [-1, 1, -1],
        [-1, -1, 1], [1, -1, 1], [1, 1, 1], [-1, 1, 1]
    ], dtype=torch.float32)
    
    faces = torch.tensor([
        [0, 1, 2], [0, 2, 3],  # bottom
        [4, 7, 6], [4, 6, 5],  # top
        [0, 4, 5], [0, 5, 1],  # front
        [2, 6, 7], [2, 7, 3],  # back
        [0, 3, 7], [0, 7, 4],  # left
        [1, 5, 6], [1, 6, 2]   # right
    ], dtype=torch.long)
    
    return vertices, faces

def train_mesh_optimization():
    """Train a mesh optimization model."""
    print("🧠 Starting Mesh Training...")
    print("=" * 50)
    
    # Create mesh
    vertices, faces = create_simple_mesh()
    mesh = Meshes(verts=[vertices], faces=[faces])
    
    print(f"Initial mesh: {len(vertices)} vertices, {len(faces)} faces")
    
    # Create optimizer
    optimizer_model = MeshOptimizer(len(vertices))
    optimizer = optim.Adam(optimizer_model.parameters(), lr=0.01)
    
    # Training loop
    num_epochs = 100
    for epoch in range(num_epochs):
        optimizer.zero_grad()
        
        # Get current vertices
        current_verts = mesh.verts_packed()
        
        # Predict vertex offsets
        offsets = optimizer_model(current_verts)
        
        # Apply offsets
        new_verts = current_verts + offsets
        new_mesh = Meshes(verts=[new_verts], faces=[faces])
        
        # Compute losses
        laplacian_loss = mesh_laplacian_smoothing(new_mesh)
        normal_loss = mesh_normal_consistency(new_mesh)
        
        # Total loss
        total_loss = laplacian_loss + 0.1 * normal_loss
        
        # Backward pass
        total_loss.backward()
        optimizer.step()
        
        # Update mesh
        mesh = new_mesh
        
        if epoch % 20 == 0:
            print(f"Epoch {epoch}: Loss = {total_loss.item():.4f}")
    
    print("✅ Training completed!")
    return mesh

def demonstrate_mesh_operations():
    """Demonstrate various mesh operations."""
    print("🔧 Demonstrating Mesh Operations...")
    print("=" * 50)
    
    # Create a sphere mesh
    sphere = ico_sphere(2)
    print(f"Sphere mesh: {len(sphere.verts_list()[0])} vertices")
    
    # Sample points from mesh
    points = sample_points_from_meshes(sphere, num_samples=1000)
    print(f"Sampled {len(points)} points from sphere")
    
    # Compute normals
    verts_normals = sphere.verts_normals_packed()
    faces_normals = sphere.faces_normals_packed()
    print(f"Computed normals: {verts_normals.shape}, {faces_normals.shape}")
    
    # Compute face areas
    face_areas = sphere.faces_areas_packed()
    print(f"Face areas: {face_areas.shape}, mean: {face_areas.mean():.4f}")
    
    # Get bounding box
    bbox = sphere.get_bounding_boxes()
    print(f"Bounding box: {bbox}")
    
    return sphere

def main():
    """Main training function."""
    print("🧠 PyTorch3D Mesh Training Demo")
    print("=" * 60)
    print()
    
    try:
        # Demonstrate mesh operations
        sphere = demonstrate_mesh_operations()
        print()
        
        # Train mesh optimization
        optimized_mesh = train_mesh_optimization()
        print()
        
        print("🎉 All mesh operations completed successfully!")
        print("📊 Training results:")
        print(f"   • Optimized mesh vertices: {optimized_mesh.verts_packed().shape}")
        print(f"   • Mesh faces: {optimized_mesh.faces_packed().shape}")
        print(f"   • Mesh normals: {optimized_mesh.verts_normals_packed().shape}")
        
    except ImportError as e:
        print(f"❌ PyTorch3D not installed: {e}")
        print("Install with: pip install pytorch3d")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
'''
    
    # Write training script
    script_path = "/Users/justin/Desktop/gthh/gtvibeathon/pytorch3d_training.py"
    with open(script_path, 'w') as f:
        f.write(training_script)
    
    print("✅ PyTorch3D training script created!")
    return script_path

def create_voxel_mesh_integration():
    """Create integration between Voxel and PyTorch3D for mesh training."""
    print("🔗 Creating Voxel-PyTorch3D Integration...")
    print("=" * 60)
    
    integration_script = '''#!/usr/bin/env python3
"""
Voxel-PyTorch3D Integration
Shows how to use Voxel system with PyTorch3D for mesh training.
"""

import os
import sys
import torch
import numpy as np
from pathlib import Path

# Add Voxel to path
sys.path.append(str(Path(__file__).parent / "src"))

try:
    from agency3d import Agency3D, Config
    from agency3d.core.models import SceneResult
    from pytorch3d.structures import Meshes
    from pytorch3d.losses import mesh_laplacian_smoothing
    from pytorch3d.ops import sample_points_from_meshes
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure Voxel and PyTorch3D are installed")
    sys.exit(1)

class VoxelMeshTrainer:
    """Trainer that combines Voxel scene generation with PyTorch3D mesh training."""
    
    def __init__(self, api_key: str):
        """Initialize the trainer."""
        self.config = Config(
            anthropic_api_key=api_key,
            ai_model="claude-3-5-sonnet-20241022"
        )
        self.agency = Agency3D(self.config)
    
    def generate_scene_mesh(self, prompt: str) -> Meshes:
        """Generate a scene using Voxel and convert to PyTorch3D mesh."""
        print(f"🎨 Generating scene: {prompt}")
        
        try:
            # Generate scene using Voxel
            result = self.agency.create_scene(prompt)
            
            if result.success:
                print("✅ Scene generated successfully!")
                
                # Convert Blender scene to PyTorch3D mesh
                # This is a simplified example - in practice you'd need
                # to export the Blender scene and import it into PyTorch3D
                mesh = self._create_mock_mesh_from_scene(result)
                return mesh
            else:
                print("❌ Scene generation failed")
                return None
                
        except Exception as e:
            print(f"❌ Error generating scene: {e}")
            return None
    
    def _create_mock_mesh_from_scene(self, scene_result: SceneResult) -> Meshes:
        """Create a mock PyTorch3D mesh from Voxel scene result."""
        # This is a simplified example - in practice you'd need to
        # properly convert from Blender to PyTorch3D format
        
        # Create a simple cube mesh as placeholder
        vertices = torch.tensor([
            [-1, -1, -1], [1, -1, -1], [1, 1, -1], [-1, 1, -1],
            [-1, -1, 1], [1, -1, 1], [1, 1, 1], [-1, 1, 1]
        ], dtype=torch.float32)
        
        faces = torch.tensor([
            [0, 1, 2], [0, 2, 3], [4, 7, 6], [4, 6, 5],
            [0, 4, 5], [0, 5, 1], [2, 6, 7], [2, 7, 3],
            [0, 3, 7], [0, 7, 4], [1, 5, 6], [1, 6, 2]
        ], dtype=torch.long)
        
        return Meshes(verts=[vertices], faces=[faces])
    
    def train_mesh_optimization(self, mesh: Meshes, target_shape: str = "sphere"):
        """Train mesh to optimize for a target shape."""
        print(f"🧠 Training mesh optimization for: {target_shape}")
        
        # Create target mesh (sphere)
        if target_shape == "sphere":
            target_verts = self._create_sphere_vertices()
        else:
            target_verts = mesh.verts_packed()
        
        # Training parameters
        learning_rate = 0.01
        num_epochs = 50
        
        # Initialize optimizer
        vertices = mesh.verts_packed().clone().requires_grad_(True)
        optimizer = torch.optim.Adam([vertices], lr=learning_rate)
        
        print(f"Starting training: {num_epochs} epochs, lr={learning_rate}")
        
        for epoch in range(num_epochs):
            optimizer.zero_grad()
            
            # Create mesh with current vertices
            current_mesh = Meshes(verts=[vertices], faces=[mesh.faces_packed()])
            
            # Compute losses
            laplacian_loss = mesh_laplacian_smoothing(current_mesh)
            
            # Target shape loss (simplified)
            if target_shape == "sphere":
                # Encourage vertices to be on sphere surface
                distances = torch.norm(vertices, dim=1)
                sphere_loss = torch.mean((distances - 1.0) ** 2)
                total_loss = laplacian_loss + 0.1 * sphere_loss
            else:
                total_loss = laplacian_loss
            
            # Backward pass
            total_loss.backward()
            optimizer.step()
            
            if epoch % 10 == 0:
                print(f"Epoch {epoch}: Loss = {total_loss.item():.4f}")
        
        print("✅ Training completed!")
        return Meshes(verts=[vertices.detach()], faces=[mesh.faces_packed()])
    
    def _create_sphere_vertices(self):
        """Create sphere vertices for target shape."""
        # Simple sphere vertices
        phi = torch.linspace(0, 2 * np.pi, 8)
        theta = torch.linspace(0, np.pi, 4)
        
        vertices = []
        for t in theta:
            for p in phi:
                x = torch.sin(t) * torch.cos(p)
                y = torch.sin(t) * torch.sin(p)
                z = torch.cos(t)
                vertices.append([x, y, z])
        
        return torch.stack(vertices, dim=0)

def main():
    """Main function."""
    print("🔗 Voxel-PyTorch3D Integration Demo")
    print("=" * 60)
    print()
    
    # Get API key
    api_key = os.environ.get('ANTHROPIC_API_KEY', 'YOUR_ANTHROPIC_API_KEY_HERE')
    if api_key == 'YOUR_ANTHROPIC_API_KEY_HERE':
        print("⚠️ Warning: ANTHROPIC_API_KEY not set")
        print("Set environment variable for full functionality")
        return
    
    try:
        # Initialize trainer
        trainer = VoxelMeshTrainer(api_key)
        
        # Generate scene
        prompt = "Create a simple house with a door and two windows"
        mesh = trainer.generate_scene_mesh(prompt)
        
        if mesh is not None:
            print(f"✅ Generated mesh: {mesh.verts_packed().shape}")
            
            # Train mesh optimization
            optimized_mesh = trainer.train_mesh_optimization(mesh, "sphere")
            print(f"✅ Optimized mesh: {optimized_mesh.verts_packed().shape}")
            
            print("🎉 Integration demo completed successfully!")
        else:
            print("❌ Failed to generate mesh")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
'''
    
    # Write integration script
    script_path = "/Users/justin/Desktop/gthh/gtvibeathon/voxel_pytorch3d_integration.py"
    with open(script_path, 'w') as f:
        f.write(integration_script)
    
    print("✅ Voxel-PyTorch3D integration created!")
    return script_path

def open_blender_file(file_path):
    """Open a Blender file."""
    blender_path = "/Applications/Blender.app/Contents/MacOS/Blender"
    
    if not os.path.exists(blender_path):
        print("❌ Blender not found")
        return False
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return False
    
    print(f"🎯 Opening: {file_path}")
    subprocess.Popen([blender_path, file_path])
    print("✅ Blender opened!")
    return True

def main():
    print("🧠 Mesh Training Demo - PyTorch3D Integration")
    print("=" * 70)
    print()
    
    # Create trainable mesh scene
    print("🏠 Creating Trainable Mesh Scene...")
    mesh_file = create_mesh_training_scene()
    if mesh_file and os.path.exists(mesh_file):
        open_blender_file(mesh_file)
        print("✅ Trainable mesh scene opened!")
    
    print()
    
    # Create PyTorch3D training script
    print("🧠 Creating PyTorch3D Training Script...")
    training_script = create_pytorch3d_training_script()
    print(f"✅ Training script: {training_script}")
    
    print()
    
    # Create Voxel-PyTorch3D integration
    print("🔗 Creating Voxel-PyTorch3D Integration...")
    integration_script = create_voxel_mesh_integration()
    print(f"✅ Integration script: {integration_script}")
    
    print()
    print("🎉 All mesh training components created!")
    print()
    print("📚 What you can do with PyTorch3D Meshes:")
    print("   ✅ Train mesh vertex positions")
    print("   ✅ Optimize mesh topology")
    print("   ✅ Apply geometric constraints")
    print("   ✅ Generate new mesh variations")
    print("   ✅ Integrate with Voxel scene generation")
    print()
    print("🚀 To run the training:")
    print("   python3 pytorch3d_training.py")
    print("   python3 voxel_pytorch3d_integration.py")

if __name__ == "__main__":
    main()
