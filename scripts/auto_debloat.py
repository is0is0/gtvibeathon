#!/usr/bin/env python3
"""Auto-debloating script for Voxel - Remove redundant files safely."""

import os
from pathlib import Path

def main():
    """Remove redundant files automatically."""
    print("🧹 Voxel Auto-Debloating Script")
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
    
    print("📁 Removing redundant documentation files...")
    total_lines_saved = 0
    
    for file_path in files_to_remove:
        if os.path.exists(file_path):
            # Count lines before removal
            with open(file_path, 'r') as f:
                lines = len(f.readlines())
            total_lines_saved += lines
            
            # Remove file
            os.remove(file_path)
            print(f"   ✅ Removed {file_path} ({lines} lines)")
        else:
            print(f"   ⚠️  {file_path} (not found)")
    
    print()
    print("🎯 Debloating complete!")
    print(f"   📉 Removed {total_lines_saved} lines")
    print("   🚀 Codebase is now more streamlined")
    
    # Show remaining size
    print()
    print("📊 Remaining codebase size:")
    os.system("find . -name '*.py' -type f -exec wc -l {} + | tail -1")
    
    print()
    print("💡 Additional optimization suggestions:")
    print("   1. Run: python3 scripts/optimize_agents.py")
    print("   2. Merge remaining docs into README.md")
    print("   3. Consider removing unused test files")

if __name__ == "__main__":
    main()
