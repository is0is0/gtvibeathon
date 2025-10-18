#!/usr/bin/env python3
"""
Debug script for Voxel system.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def debug_imports():
    """Debug import issues."""
    try:
        print("Testing imports...")
        
        from voxel import Voxel, Config
        print("✓ Core imports successful")
        
        from voxel.database import DatabaseManager
        print("✓ Database manager import successful")
        
        from voxel.orchestrator import WorkflowOrchestrator
        print("✓ WorkflowOrchestrator import successful")
        
        # Test individual components
        config = Config()
        print("✓ Config created")
        
        db_manager = DatabaseManager("sqlite:///:memory:")
        print("✓ Database manager created")
        
        # Test WorkflowOrchestrator creation
        try:
            orchestrator = WorkflowOrchestrator(config)
            print("✓ WorkflowOrchestrator created")
        except Exception as e:
            print(f"✗ WorkflowOrchestrator error: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        # Test Voxel creation
        try:
            voxel = Voxel(config)
            print("✓ Voxel created successfully")
            voxel.close()
        except Exception as e:
            print(f"✗ Voxel creation error: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = debug_imports()
    sys.exit(0 if success else 1)
