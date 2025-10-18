#!/usr/bin/env python3
"""
VoxelWeaver Module Verification Script
Verifies all modules are properly installed and functional.
"""

import sys
from pathlib import Path

def verify_modules():
    """Verify all VoxelWeaver modules."""
    
    print("="*60)
    print("VoxelWeaver Module Verification")
    print("="*60)
    
    modules_to_verify = [
        ('geometry_handler', 'GeometryHandler'),
        ('proportion_analyzer', 'ProportionAnalyzer'),
        ('context_alignment', 'ContextAlignment'),
        ('lighting_engine', 'LightingEngine'),
        ('texture_mapper', 'TextureMapper'),
        ('blender_bridge', 'BlenderBridge'),
        ('search_scraper', 'SearchScraper'),
        ('model_formatter', 'ModelFormatter'),
        ('scene_validator', 'SceneValidator'),
        ('voxelweaver_core', 'VoxelWeaverCore'),
    ]
    
    results = []
    
    for module_name, class_name in modules_to_verify:
        try:
            # Import module
            module = __import__(module_name, fromlist=[class_name])
            
            # Get class
            cls = getattr(module, class_name)
            
            # Check if callable
            if callable(cls):
                results.append((module_name, class_name, True, None))
                print(f"✓ {module_name}.{class_name}")
            else:
                results.append((module_name, class_name, False, "Not callable"))
                print(f"✗ {module_name}.{class_name} - Not callable")
                
        except Exception as e:
            results.append((module_name, class_name, False, str(e)))
            print(f"✗ {module_name}.{class_name} - {e}")
    
    # Summary
    print("\n" + "="*60)
    print("Summary")
    print("="*60)
    
    total = len(results)
    passed = sum(1 for r in results if r[2])
    failed = total - passed
    
    print(f"Total Modules: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    
    if failed == 0:
        print("\n✓ All modules verified successfully!")
        return 0
    else:
        print(f"\n✗ {failed} module(s) failed verification")
        return 1

if __name__ == "__main__":
    sys.exit(verify_modules())
