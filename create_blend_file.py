#!/usr/bin/env python3
"""
Create a complete Blender file from the generated scripts.
This will run all the generated scripts and save a .blend file.
"""

import subprocess
import sys
from pathlib import Path

def create_blend_file():
    """Create a complete Blender file by running the generated scripts."""
    
    # Path to the generated scripts
    script_dir = Path("/Users/justin/Desktop/gthh/gtvibeathon/output/test_house_generation/scripts")
    output_file = Path("/Users/justin/Desktop/gthh/gtvibeathon/house_scene.blend")
    
    # Check if Blender is available
    try:
        result = subprocess.run(["blender", "--version"], capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ Blender not found. Please install Blender from https://www.blender.org")
            return False
    except FileNotFoundError:
        print("❌ Blender not found. Please install Blender from https://www.blender.org")
        return False
    
    print("🎬 Creating Blender file...")
    print(f"📁 Script directory: {script_dir}")
    print(f"💾 Output file: {output_file}")
    
    # Create a Python script that runs all the generated scripts
    combined_script = f"""
import bpy
import sys
from pathlib import Path

# Clear the default scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

print("🏗️ Building house scene...")

# Run the builder script
exec(open(r"{script_dir}/01_builder_iter1.py").read())

print("🎨 Applying materials...")

# Run the texture script  
exec(open(r"{script_dir}/02_texture_iter1.py").read())

print("📸 Setting up camera and lighting...")

# Run the render script
exec(open(r"{script_dir}/05_save_iter1.py").read())

print("🎬 Adding animation...")

# Run the animation script
exec(open(r"{script_dir}/04_animation_iter1.py").read())

print("💾 Saving Blender file...")

# Save the file
bpy.ops.wm.save_as_mainfile(filepath=r"{output_file}")

print("✅ Blender file created successfully!")
print(f"📁 File saved to: {output_file}")
"""
    
    # Write the combined script
    combined_script_path = script_dir / "create_complete_scene.py"
    with open(combined_script_path, 'w') as f:
        f.write(combined_script)
    
    # Run Blender with the combined script
    try:
        print("🚀 Running Blender...")
        result = subprocess.run([
            "blender", 
            "--background", 
            "--python", str(combined_script_path)
        ], capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print("✅ Blender file created successfully!")
            print(f"📁 File location: {output_file}")
            print("\n🎯 To open the file:")
            print(f"   blender {output_file}")
            print("   or double-click the file in your file manager")
            return True
        else:
            print("❌ Error creating Blender file:")
            print(result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print("⏰ Blender operation timed out")
        return False
    except Exception as e:
        print(f"❌ Error running Blender: {e}")
        return False

if __name__ == "__main__":
    success = create_blend_file()
    if success:
        print("\n🎉 Success! You can now open the Blender file directly.")
    else:
        print("\n❌ Failed to create Blender file.")
        sys.exit(1)
