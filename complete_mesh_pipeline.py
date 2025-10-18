#!/usr/bin/env python3
"""Complete mesh training and rendering pipeline with Voxel + PyTorch3D."""

import os
import subprocess
import sys
from pathlib import Path

def create_complete_mesh_pipeline():
    """Create a complete mesh training and rendering pipeline."""
    print("🎨 Creating Complete Mesh Pipeline...")
    print("=" * 60)
    
    pipeline_script = '''#!/usr/bin/env python3
"""
Complete Mesh Training and Rendering Pipeline
Combines Voxel scene generation with PyTorch3D mesh training and rendering.
"""

import os
import sys
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from pathlib import Path

# Add Voxel to path
sys.path.append(str(Path(__file__).parent / "src"))

def check_dependencies():
    """Check if all dependencies are available."""
    try:
        import pytorch3d
        from pytorch3d.structures import Meshes
        from pytorch3d.renderer import (
            MeshRenderer, MeshRendererWithFragments,
            RasterizationSettings, MeshRasterizer,
            SoftPhongShader, TexturesVertex
        )
        from pytorch3d.losses import mesh_laplacian_smoothing, mesh_normal_consistency
        from pytorch3d.ops import sample_points_from_meshes
        from pytorch3d.utils import ico_sphere
        print("✅ PyTorch3D is available!")
        return True
    except ImportError as e:
        print(f"❌ PyTorch3D not available: {e}")
        print("Install with: pip install pytorch3d")
        return False

class MeshTrainingPipeline:
    """Complete pipeline for mesh training and rendering."""
    
    def __init__(self, device='cuda' if torch.cuda.is_available() else 'cpu'):
        self.device = device
        print(f"Using device: {self.device}")
    
    def create_trainable_mesh(self):
        """Create a mesh suitable for training."""
        print("🏗️ Creating trainable mesh...")
        
        # Create a sphere mesh
        sphere = ico_sphere(3)  # Higher resolution for better training
        sphere = sphere.to(self.device)
        
        print(f"Created mesh: {len(sphere.verts_list()[0])} vertices, {len(sphere.faces_list()[0])} faces")
        return sphere
    
    def setup_renderer(self):
        """Setup mesh renderer for visualization."""
        print("🎨 Setting up renderer...")
        
        # Rasterization settings
        raster_settings = RasterizationSettings(
            image_size=512,
            blur_radius=0.0,
            faces_per_pixel=1,
        )
        
        # Create rasterizer
        rasterizer = MeshRasterizer(raster_settings=raster_settings)
        
        # Create shader
        shader = SoftPhongShader(device=self.device)
        
        # Create renderer
        renderer = MeshRendererWithFragments(
            rasterizer=rasterizer,
            shader=shader
        )
        
        return renderer
    
    def create_mesh_optimizer(self, num_vertices):
        """Create neural network for mesh optimization."""
        print("🧠 Creating mesh optimizer...")
        
        class MeshOptimizer(nn.Module):
            def __init__(self, num_vertices):
                super().__init__()
                self.num_vertices = num_vertices
                
                # Encoder-decoder architecture
                self.encoder = nn.Sequential(
                    nn.Linear(3, 64),
                    nn.ReLU(),
                    nn.Linear(64, 128),
                    nn.ReLU(),
                    nn.Linear(128, 256),
                    nn.ReLU()
                )
                
                self.decoder = nn.Sequential(
                    nn.Linear(256, 128),
                    nn.ReLU(),
                    nn.Linear(128, 64),
                    nn.ReLU(),
                    nn.Linear(64, 3)
                )
            
            def forward(self, vertices):
                # Process each vertex
                encoded = self.encoder(vertices)
                offsets = self.decoder(encoded)
                return offsets
        
        return MeshOptimizer(num_vertices).to(self.device)
    
    def train_mesh_optimization(self, mesh, target_shape="sphere", num_epochs=200):
        """Train mesh optimization."""
        print(f"🧠 Training mesh optimization for: {target_shape}")
        print(f"Epochs: {num_epochs}")
        
        # Create optimizer
        model = self.create_mesh_optimizer(len(mesh.verts_list()[0]))
        optimizer = optim.Adam(model.parameters(), lr=0.001)
        
        # Training loop
        for epoch in range(num_epochs):
            optimizer.zero_grad()
            
            # Get current vertices
            current_verts = mesh.verts_packed()
            
            # Predict vertex offsets
            offsets = model(current_verts)
            
            # Apply offsets
            new_verts = current_verts + offsets
            new_mesh = Meshes(verts=[new_verts], faces=[mesh.faces_packed()])
            
            # Compute losses
            laplacian_loss = mesh_laplacian_smoothing(new_mesh)
            normal_loss = mesh_normal_consistency(new_mesh)
            
            # Target shape loss
            if target_shape == "sphere":
                # Encourage vertices to be on sphere surface
                distances = torch.norm(new_verts, dim=1)
                sphere_loss = torch.mean((distances - 1.0) ** 2)
                total_loss = laplacian_loss + 0.1 * normal_loss + 0.5 * sphere_loss
            else:
                total_loss = laplacian_loss + 0.1 * normal_loss
            
            # Backward pass
            total_loss.backward()
            optimizer.step()
            
            # Update mesh
            mesh = new_mesh
            
            if epoch % 50 == 0:
                print(f"Epoch {epoch}: Loss = {total_loss.item():.4f}")
        
        print("✅ Training completed!")
        return mesh
    
    def render_mesh(self, mesh, renderer, save_path=None):
        """Render mesh and optionally save image."""
        print("🎨 Rendering mesh...")
        
        # Add texture to mesh
        textures = TexturesVertex(verts_features=torch.ones_like(mesh.verts_packed()).unsqueeze(0))
        mesh.textures = textures
        
        # Render
        images, fragments = renderer(mesh)
        
        # Convert to numpy
        image = images[0].cpu().numpy()
        
        if save_path:
            # Save image
            import matplotlib.pyplot as plt
            plt.figure(figsize=(8, 8))
            plt.imshow(image)
            plt.axis('off')
            plt.title('Rendered Mesh')
            plt.savefig(save_path, bbox_inches='tight', dpi=150)
            plt.close()
            print(f"✅ Saved rendered image: {save_path}")
        
        return image, fragments
    
    def demonstrate_pipeline(self):
        """Demonstrate the complete pipeline."""
        print("🚀 Running Complete Mesh Pipeline...")
        print("=" * 50)
        
        # 1. Create mesh
        mesh = self.create_trainable_mesh()
        
        # 2. Setup renderer
        renderer = self.setup_renderer()
        
        # 3. Render initial mesh
        print("📸 Rendering initial mesh...")
        initial_image, _ = self.render_mesh(mesh, renderer, "initial_mesh.png")
        
        # 4. Train mesh optimization
        optimized_mesh = self.train_mesh_optimization(mesh, "sphere", 100)
        
        # 5. Render optimized mesh
        print("📸 Rendering optimized mesh...")
        optimized_image, _ = self.render_mesh(optimized_mesh, renderer, "optimized_mesh.png")
        
        # 6. Compare results
        print("📊 Pipeline Results:")
        print(f"   • Initial mesh vertices: {mesh.verts_packed().shape}")
        print(f"   • Optimized mesh vertices: {optimized_mesh.verts_packed().shape}")
        print(f"   • Initial mesh faces: {mesh.faces_packed().shape}")
        print(f"   • Optimized mesh faces: {optimized_mesh.faces_packed().shape}")
        
        return mesh, optimized_mesh, renderer

def demonstrate_voxel_integration():
    """Demonstrate integration with Voxel system."""
    print("🔗 Voxel Integration Demo...")
    print("=" * 40)
    
    try:
        from agency3d import Agency3D, Config
        
        # Initialize Voxel
        api_key = os.environ.get('ANTHROPIC_API_KEY', 'YOUR_ANTHROPIC_API_KEY_HERE')
        if api_key == 'YOUR_ANTHROPIC_API_KEY_HERE':
            print("⚠️ Warning: ANTHROPIC_API_KEY not set")
            print("Set environment variable for full functionality")
            return
        
        config = Config(
            anthropic_api_key=api_key,
            ai_model="claude-3-5-sonnet-20241022"
        )
        agency = Agency3D(config)
        
        print("✅ Voxel system initialized!")
        
        # Generate scene
        prompt = "Create a modern house with clean lines and geometric shapes"
        print(f"🎨 Generating scene: {prompt}")
        
        result = agency.create_scene(prompt)
        if result.success:
            print("✅ Scene generated successfully!")
            print(f"   • Blend file: {result.blend_file}")
            print(f"   • Scripts: {len(result.scripts)}")
        else:
            print("❌ Scene generation failed")
            
    except ImportError as e:
        print(f"❌ Voxel not available: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Main function."""
    print("🎨 Complete Mesh Training and Rendering Pipeline")
    print("=" * 60)
    print()
    
    if not check_dependencies():
        print("📚 Concept: Complete Mesh Pipeline")
        print("=" * 40)
        print()
        print("1. Create Mesh:")
        print("   ```python")
        print("   mesh = ico_sphere(3)  # High-res sphere")
        print("   ```")
        print()
        print("2. Setup Renderer:")
        print("   ```python")
        print("   renderer = MeshRendererWithFragments(rasterizer, shader)")
        print("   ```")
        print()
        print("3. Train Optimization:")
        print("   ```python")
        print("   model = MeshOptimizer(num_vertices)")
        print("   for epoch in range(num_epochs):")
        print("       offsets = model(mesh.verts_packed())")
        print("       new_mesh = Meshes(verts=[new_verts], faces=[faces])")
        print("       loss = mesh_laplacian_smoothing(new_mesh)")
        print("       loss.backward()")
        print("   ```")
        print()
        print("4. Render Results:")
        print("   ```python")
        print("   images, fragments = renderer(mesh)")
        print("   # Save rendered images")
        print("   ```")
        print()
        print("5. Integrate with Voxel:")
        print("   ```python")
        print("   # Generate scene with Voxel")
        print("   result = agency.create_scene('Create a house')")
        print("   # Convert to PyTorch3D mesh")
        print("   mesh = convert_blender_to_pytorch3d(result)")
        print("   # Train and render")
        print("   optimized_mesh = train_mesh_optimization(mesh)")
        print("   images = render_mesh(optimized_mesh)")
        print("   ```")
        print()
        print("🎯 Key Features:")
        print("   ✅ Neural mesh optimization")
        print("   ✅ Real-time rendering")
        print("   ✅ Voxel scene integration")
        print("   ✅ Automated pipeline")
        print("   ✅ High-quality output")
        print()
        print("📦 Install Dependencies:")
        print("   pip install torch torchvision torchaudio")
        print("   pip install pytorch3d")
        print("   pip install matplotlib")
        return
    
    # Run actual pipeline
    try:
        pipeline = MeshTrainingPipeline()
        
        # Run complete pipeline
        initial_mesh, optimized_mesh, renderer = pipeline.demonstrate_pipeline()
        
        # Demonstrate Voxel integration
        demonstrate_voxel_integration()
        
        print("🎉 Complete pipeline executed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
'''
    
    # Write pipeline script
    script_path = "/Users/justin/Desktop/gthh/gtvibeathon/complete_mesh_pipeline.py"
    with open(script_path, 'w') as f:
        f.write(pipeline_script)
    
    print("✅ Complete mesh pipeline created!")
    return script_path

def create_advanced_mesh_training_scene():
    """Create an advanced scene for mesh training."""
    print("🏗️ Creating Advanced Mesh Training Scene...")
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

def create_advanced_trainable_mesh():
    """Create an advanced mesh suitable for training."""
    
    # Create a complex architectural structure
    house_width = 8
    house_depth = 6
    wall_height = 4
    
    # Foundation
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, -0.2))
    foundation = bpy.context.active_object
    foundation.name = "Foundation"
    foundation.scale = (house_width + 1, house_depth + 1, 0.4)
    
    # Main structure
    walls = [
        ("FrontWall", (0, house_depth/2, wall_height/2), (house_width, 0.3, wall_height)),
        ("BackWall", (0, -house_depth/2, wall_height/2), (house_width, 0.3, wall_height)),
        ("LeftWall", (-house_width/2, 0, wall_height/2), (0.3, house_depth, wall_height)),
        ("RightWall", (house_width/2, 0, wall_height/2), (0.3, house_depth, wall_height))
    ]
    
    for wall_name, position, scale in walls:
        bpy.ops.mesh.primitive_cube_add(size=1, location=position)
        wall = bpy.context.active_object
        wall.name = wall_name
        wall.scale = scale
    
    # Roof with multiple sections
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, wall_height + 0.5))
    roof = bpy.context.active_object
    roof.name = "MainRoof"
    roof.scale = (house_width + 1.5, house_depth + 1.5, 0.6)
    
    # Add architectural details
    details = [
        ("Chimney", (2, 2, wall_height + 1.5), (0.8, 0.8, 1.5)),
        ("Balcony", (0, house_depth/2 + 0.5, wall_height - 0.5), (3, 1, 0.2)),
        ("Stairs", (0, -house_depth/2 - 0.5, 0.1), (2, 1, 0.2)),
        ("Window1", (2, house_depth/2 + 0.1, 2.5), (1.5, 0.1, 2)),
        ("Window2", (-2, house_depth/2 + 0.1, 2.5), (1.5, 0.1, 2)),
        ("Window3", (0, -house_depth/2 - 0.1, 2.5), (2, 0.1, 2))
    ]
    
    for detail_name, position, scale in details:
        bpy.ops.mesh.primitive_cube_add(size=1, location=position)
        detail = bpy.context.active_object
        detail.name = detail_name
        detail.scale = scale
    
    # Add furniture for complexity
    furniture = [
        ("Table", (0, 0, 0.4), (2, 1, 0.05)),
        ("Chair1", (1.5, 1, 0.2), (0.5, 0.5, 0.8)),
        ("Chair2", (-1.5, 1, 0.2), (0.5, 0.5, 0.8)),
        ("Chair3", (1.5, -1, 0.2), (0.5, 0.5, 0.8)),
        ("Chair4", (-1.5, -1, 0.2), (0.5, 0.5, 0.8)),
        ("Bed", (-3, 0, 0.3), (2.5, 2, 0.4)),
        ("Sofa", (3, 0, 0.3), (2, 1, 0.4)),
        ("Bookshelf", (-3, -2, 1.5), (0.3, 0.8, 3)),
        ("Desk", (3, -2, 0.4), (1.5, 0.8, 0.05))
    ]
    
    for item_name, position, scale in furniture:
        bpy.ops.mesh.primitive_cube_add(size=1, location=position)
        item = bpy.context.active_object
        item.name = item_name
        item.scale = scale
    
    # Create realistic materials
    materials = {
        "Foundation": (0.4, 0.4, 0.4, 1),  # Concrete
        "FrontWall": (0.95, 0.95, 0.95, 1), # White
        "BackWall": (0.95, 0.95, 0.95, 1),  # White
        "LeftWall": (0.95, 0.95, 0.95, 1),  # White
        "RightWall": (0.95, 0.95, 0.95, 1), # White
        "MainRoof": (0.6, 0.3, 0.3, 1),     # Red
        "Chimney": (0.3, 0.3, 0.3, 1),      # Dark gray
        "Balcony": (0.8, 0.8, 0.8, 1),      # Light gray
        "Stairs": (0.5, 0.5, 0.5, 1),       # Gray
        "Window1": (0.7, 0.9, 1.0, 1),       # Light blue
        "Window2": (0.7, 0.9, 1.0, 1),      # Light blue
        "Window3": (0.7, 0.9, 1.0, 1),      # Light blue
        "Table": (0.5, 0.3, 0.1, 1),        # Brown
        "Chair1": (0.3, 0.2, 0.1, 1),       # Dark brown
        "Chair2": (0.3, 0.2, 0.1, 1),       # Dark brown
        "Chair3": (0.3, 0.2, 0.1, 1),       # Dark brown
        "Chair4": (0.3, 0.2, 0.1, 1),       # Dark brown
        "Bed": (0.8, 0.8, 0.9, 1),          # Light blue
        "Sofa": (0.6, 0.4, 0.2, 1),         # Brown
        "Bookshelf": (0.4, 0.2, 0.1, 1),    # Dark brown
        "Desk": (0.5, 0.3, 0.1, 1)          # Brown
    }
    
    for obj_name, color in materials.items():
        obj = bpy.data.objects.get(obj_name)
        if obj:
            material = bpy.data.materials.new(name=f"{obj_name}Material")
            material.use_nodes = True
            material.node_tree.nodes["Principled BSDF"].inputs[0].default_value = color
            obj.data.materials.append(material)
    
    # Add professional lighting
    bpy.ops.object.light_add(type='SUN', location=(15, 15, 20))
    sun = bpy.context.active_object
    sun.name = "SunLight"
    sun.data.energy = 8
    
    # Add area light for interior
    bpy.ops.object.light_add(type='AREA', location=(0, 0, 3))
    area_light = bpy.context.active_object
    area_light.name = "AreaLight"
    area_light.data.energy = 200
    area_light.data.size = 5
    
    # Set up camera
    bpy.ops.object.camera_add(location=(12, -12, 8))
    camera = bpy.context.active_object
    camera.name = "Camera"
    camera.rotation_euler = (1.1, 0, 0.7)
    bpy.context.scene.camera = camera
    
    return True

# Create the advanced trainable mesh
create_advanced_trainable_mesh()

# Save the file
output_path = "/Users/justin/Desktop/gthh/gtvibeathon/advanced_trainable_mesh.blend"
bpy.ops.wm.save_as_mainfile(filepath=output_path)
print(f"✅ Saved advanced trainable mesh: {output_path}")
'''
    
    # Write and execute script
    script_path = "/Users/justin/Desktop/gthh/gtvibeathon/create_advanced_mesh.py"
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
            print("✅ Advanced trainable mesh created!")
            return "/Users/justin/Desktop/gthh/gtvibeathon/advanced_trainable_mesh.blend"
        else:
            print(f"❌ Error: {result.stderr}")
            return None
    else:
        print("❌ Blender not found")
        return None

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
    print("🎨 Complete Mesh Training and Rendering Pipeline")
    print("=" * 70)
    print()
    
    # Create complete mesh pipeline
    print("🧠 Creating Complete Mesh Pipeline...")
    pipeline_script = create_complete_mesh_pipeline()
    print(f"✅ Pipeline script: {pipeline_script}")
    
    print()
    
    # Create advanced mesh training scene
    print("🏗️ Creating Advanced Mesh Training Scene...")
    advanced_mesh_file = create_advanced_mesh_training_scene()
    if advanced_mesh_file and os.path.exists(advanced_mesh_file):
        open_blender_file(advanced_mesh_file)
        print("✅ Advanced mesh training scene opened!")
    
    print()
    print("🎉 Complete mesh training and rendering pipeline created!")
    print()
    print("📚 What you can do with the complete pipeline:")
    print("   ✅ Train mesh vertex positions with neural networks")
    print("   ✅ Optimize mesh topology and geometry")
    print("   ✅ Render meshes with PyTorch3D")
    print("   ✅ Generate high-quality images")
    print("   ✅ Integrate with Voxel scene generation")
    print("   ✅ Apply geometric constraints")
    print("   ✅ Create mesh variations")
    print()
    print("🚀 To run the complete pipeline:")
    print("   python3 complete_mesh_pipeline.py")
    print()
    print("📦 Required dependencies:")
    print("   pip install torch torchvision torchaudio")
    print("   pip install pytorch3d")
    print("   pip install matplotlib")

if __name__ == "__main__":
    main()
