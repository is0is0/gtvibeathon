#!/usr/bin/env python3
"""
Verify Voxel Weaver Structure
------------------------------
Checks that all required files and modules are in place.
"""

from pathlib import Path

print("=" * 60)
print("Voxel Weaver Structure Verification")
print("=" * 60)

base_dir = Path(".")

# Required directories
directories = [
    "backend/voxelweaver",
    "src/voxel_weaver",
    "src/orchestrator",
    "src/subsystems",
    "src/utils",
    "src/agency3d",
]

# Required files
required_files = [
    # Backend
    "backend/voxelweaver/__init__.py",
    "backend/voxelweaver/voxelweaver_core.py",
    "backend/voxelweaver/geometry_handler.py",
    "backend/voxelweaver/proportion_analyzer.py",
    "backend/voxelweaver/README.md",
    
    # Orchestration layer
    "src/main.py",
    "src/ARCHITECTURE.md",
    "src/voxel_weaver/__init__.py",
    "src/voxel_weaver/voxel_weaver_core.py",
    "src/orchestrator/__init__.py",
    "src/orchestrator/scene_orchestrator.py",
    
    # Subsystems
    "src/subsystems/__init__.py",
    "src/subsystems/prompt_interpreter.py",
    "src/subsystems/texture_synth.py",
    "src/subsystems/lighting_ai.py",
    "src/subsystems/spatial_validator.py",
    "src/subsystems/render_director.py",
    "src/subsystems/asset_registry.py",
    
    # Utils
    "src/utils/__init__.py",
    "src/utils/logger.py",
    "src/utils/blender_api_tools.py",
    
    # Documentation
    "README.md",
    "VOXEL_WEAVER_COMPLETE.md",
    "WEB_INTERFACE_GUIDE.md",
]

print("\n📁 Checking directories...")
missing_dirs = []
for directory in directories:
    dir_path = base_dir / directory
    if dir_path.exists():
        print(f"  ✓ {directory}")
    else:
        print(f"  ✗ {directory} - MISSING")
        missing_dirs.append(directory)

print("\n📄 Checking required files...")
missing_files = []
for file in required_files:
    file_path = base_dir / file
    if file_path.exists():
        print(f"  ✓ {file}")
    else:
        print(f"  ✗ {file} - MISSING")
        missing_files.append(file)

# Count modules
backend_modules = len(list((base_dir / "backend/voxelweaver").glob("*.py")))
subsystem_modules = len(list((base_dir / "src/subsystems").glob("*.py"))) - 1  # Exclude __init__

print("\n📊 Statistics:")
print(f"  Backend modules: {backend_modules}")
print(f"  Subsystem modules: {subsystem_modules}")
print(f"  Total directories: {len(directories)}")
print(f"  Total files checked: {len(required_files)}")

print("\n" + "=" * 60)
if not missing_dirs and not missing_files:
    print("✅ All components verified successfully!")
    print("✅ Voxel Weaver structure is complete!")
else:
    print("⚠️  Some components are missing:")
    if missing_dirs:
        print(f"  Missing directories: {len(missing_dirs)}")
    if missing_files:
        print(f"  Missing files: {len(missing_files)}")
print("=" * 60)
