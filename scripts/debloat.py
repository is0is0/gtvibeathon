#!/usr/bin/env python3
"""Debloating script for Voxel - Remove redundant files and optimize codebase."""

import os
import shutil
from pathlib import Path

def main():
    """Remove redundant files and optimize the codebase."""
    print("🧹 Voxel Debloating Script")
    print("=" * 50)
    print()
    
    # Files to remove (safe to delete)
    files_to_remove = [
        "PROJECT_COMPLETE.md",
        "INITIALIZATION_COMPLETE.md", 
        "PROJECT_SUMMARY.md",
        "ENHANCEMENTS.md",
        "ADVANCED_FEATURES.md"
    ]
    
    # Directories to clean up
    dirs_to_clean = [
        "examples/prompts/",  # Keep only essential examples
    ]
    
    print("📁 Files to remove:")
    total_lines_saved = 0
    
    for file_path in files_to_remove:
        if os.path.exists(file_path):
            # Count lines before removal
            with open(file_path, 'r') as f:
                lines = len(f.readlines())
            total_lines_saved += lines
            print(f"   ❌ {file_path} ({lines} lines)")
        else:
            print(f"   ⚠️  {file_path} (not found)")
    
    print()
    print(f"📊 Total lines to be removed: {total_lines_saved}")
    print()
    
    # Ask for confirmation
    response = input("🤔 Proceed with debloating? (y/N): ").strip().lower()
    
    if response == 'y':
        print("🗑️  Removing redundant files...")
        
        for file_path in files_to_remove:
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"   ✅ Removed {file_path}")
        
        print()
        print("🎯 Debloating complete!")
        print(f"   📉 Removed {total_lines_saved} lines")
        print("   🚀 Codebase is now more streamlined")
        
    else:
        print("❌ Debloating cancelled")
    
    print()
    print("💡 Additional optimization suggestions:")
    print("   1. Merge remaining docs into README.md")
    print("   2. Compress enhance_capabilities.py (remove examples)")
    print("   3. Remove unused test files")
    print("   4. Optimize agent scripts (remove duplicate code)")

if __name__ == "__main__":
    main()
