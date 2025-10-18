#!/usr/bin/env python3
"""Test script to verify Blender addon functionality."""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def test_addon_structure():
    """Test the addon file structure and content."""
    print("🎨 Testing Blender Addon Structure...")
    print()
    
    addon_path = Path("addons/voxel_addon")
    
    # Test 1: Check addon directory
    if not addon_path.exists():
        print("❌ Addon directory not found")
        return False
    
    print(f"✅ Addon directory found: {addon_path}")
    
    # Test 2: Check required files
    required_files = {
        "__init__.py": "Main addon file",
        "operators.py": "Blender operators",
        "panels.py": "UI panels", 
        "preferences.py": "Addon preferences"
    }
    
    missing_files = []
    for filename, description in required_files.items():
        file_path = addon_path / filename
        if file_path.exists():
            print(f"✅ {filename}: {description}")
        else:
            print(f"❌ {filename}: {description} - MISSING")
            missing_files.append(filename)
    
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False
    
    # Test 3: Check bl_info in __init__.py
    init_file = addon_path / "__init__.py"
    with open(init_file, 'r') as f:
        content = f.read()
    
    if 'bl_info' in content:
        print("✅ bl_info metadata found")
    else:
        print("❌ bl_info metadata missing")
        return False
    
    if 'def register():' in content:
        print("✅ register function found")
    else:
        print("❌ register function missing")
        return False
    
    if 'def unregister():' in content:
        print("✅ unregister function found")
    else:
        print("❌ unregister function missing")
        return False
    
    # Test 4: Check for Voxel-specific content
    voxel_checks = [
        ('VOXEL_OT_generate', 'Generate operator'),
        ('VOXEL_PT_main_panel', 'Main panel'),
        ('VoxelAddonPreferences', 'Preferences class'),
        ('voxel_prompt', 'Scene property')
    ]
    
    for check, description in voxel_checks:
        if check in content:
            print(f"✅ {description}: {check}")
        else:
            print(f"❌ {description}: {check} - MISSING")
    
    print()
    print("🎯 Addon structure test complete!")
    return True

def test_addon_syntax():
    """Test addon Python syntax."""
    print("🔍 Testing Addon Python Syntax...")
    print()
    
    addon_path = Path("addons/voxel_addon")
    python_files = ["__init__.py", "operators.py", "panels.py", "preferences.py"]
    
    syntax_errors = []
    
    for filename in python_files:
        file_path = addon_path / filename
        try:
            with open(file_path, 'r') as f:
                code = f.read()
            compile(code, str(file_path), 'exec')
            print(f"✅ {filename}: Syntax OK")
        except SyntaxError as e:
            print(f"❌ {filename}: Syntax error - {e}")
            syntax_errors.append(f"{filename}: {e}")
        except Exception as e:
            print(f"❌ {filename}: {e}")
            syntax_errors.append(f"{filename}: {e}")
    
    if syntax_errors:
        print(f"❌ Syntax errors found: {syntax_errors}")
        return False
    
    print("✅ All addon files have valid Python syntax")
    return True

def test_addon_metadata():
    """Test addon metadata and structure."""
    print("📋 Testing Addon Metadata...")
    print()
    
    addon_path = Path("addons/voxel_addon")
    init_file = addon_path / "__init__.py"
    
    with open(init_file, 'r') as f:
        content = f.read()
    
    # Extract bl_info
    if 'bl_info = {' in content:
        print("✅ bl_info dictionary found")
        
        # Check for required bl_info fields
        required_fields = ['name', 'author', 'version', 'blender', 'location', 'description', 'category']
        for field in required_fields:
            if f'"{field}"' in content or f"'{field}'" in content:
                print(f"✅ bl_info.{field} found")
            else:
                print(f"❌ bl_info.{field} missing")
    else:
        print("❌ bl_info dictionary not found")
        return False
    
    # Check for class definitions
    classes_to_check = [
        'VOXEL_OT_generate',
        'VOXEL_PT_main_panel', 
        'VoxelAddonPreferences'
    ]
    
    for class_name in classes_to_check:
        if f'class {class_name}' in content:
            print(f"✅ Class {class_name} found")
        else:
            print(f"❌ Class {class_name} missing")
    
    print("✅ Addon metadata test complete")
    return True

def test_addon_installation():
    """Test addon installation requirements."""
    print("📦 Testing Addon Installation Requirements...")
    print()
    
    addon_path = Path("addons/voxel_addon")
    
    # Check if addon has proper structure for Blender installation
    if (addon_path / "__init__.py").exists():
        print("✅ __init__.py found (required for Blender addon)")
    else:
        print("❌ __init__.py missing (required for Blender addon)")
        return False
    
    # Check for proper addon structure
    required_structure = [
        "addons/voxel_addon/__init__.py",
        "addons/voxel_addon/operators.py",
        "addons/voxel_addon/panels.py", 
        "addons/voxel_addon/preferences.py"
    ]
    
    all_files_exist = True
    for file_path in required_structure:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - MISSING")
            all_files_exist = False
    
    if not all_files_exist:
        print("❌ Addon structure incomplete")
        return False
    
    print("✅ Addon installation requirements met")
    return True

def main():
    """Run all addon tests."""
    print("🎨 Blender Addon Comprehensive Test")
    print("=" * 50)
    print()
    
    tests = [
        ("Structure Test", test_addon_structure),
        ("Syntax Test", test_addon_syntax), 
        ("Metadata Test", test_addon_metadata),
        ("Installation Test", test_addon_installation)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"🧪 Running {test_name}...")
        try:
            result = test_func()
            results.append((test_name, result))
            print()
        except Exception as e:
            print(f"❌ {test_name} failed with error: {e}")
            results.append((test_name, False))
            print()
    
    # Summary
    print("📊 Test Results Summary:")
    print("-" * 30)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print()
    print(f"🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Addon is ready for Blender installation.")
    else:
        print("⚠️  Some tests failed. Please fix issues before installing in Blender.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
