"""Voxel Blender Addon - AI-powered 3D scene generation inside Blender."""

bl_info = {
    "name": "Voxel",
    "author": "Voxel Team",
    "version": (1, 0, 0),
    "blender": (3, 6, 0),
    "location": "View3D > Sidebar > Voxel",
    "description": "AI-powered autonomous 3D scene generation system",
    "category": "3D View",
    "doc_url": "https://github.com/yourusername/voxel",
    "tracker_url": "https://github.com/yourusername/voxel/issues",
}

import bpy
import sys
import os
from pathlib import Path

# Add the voxel source to Python path
addon_dir = Path(__file__).parent
voxel_src = addon_dir.parent.parent / "src"
if str(voxel_src) not in sys.path:
    sys.path.insert(0, str(voxel_src))

# Import voxel modules
try:
    from agency3d import Agency3D, Config
    from agency3d.core.models import AgentRole
    VOXEL_AVAILABLE = True
except ImportError as e:
    print(f"Voxel addon: Could not import voxel modules: {e}")
    VOXEL_AVAILABLE = False

# Import addon modules
from . import operators
from . import panels
from . import preferences

# Addon classes
classes = []

def register():
    """Register the addon."""
    if not VOXEL_AVAILABLE:
        print("Voxel addon: Voxel modules not available. Addon will be limited.")
        return
    
    # Register preferences first
    preferences.register()
    
    # Register operators
    operators.register()
    
    # Register panels
    panels.register()
    
    # Register all classes
    for cls in classes:
        bpy.utils.register_class(cls)
    
    print("Voxel addon registered successfully")

def unregister():
    """Unregister the addon."""
    # Unregister in reverse order
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    
    # Unregister modules
    panels.unregister()
    operators.unregister()
    preferences.unregister()
    
    print("Voxel addon unregistered")

if __name__ == "__main__":
    register()
