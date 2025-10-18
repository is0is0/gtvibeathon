#!/usr/bin/env python3
"""
Test script for Voxel system.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_imports():
    """Test that all imports work correctly."""
    try:
        from voxel import Voxel, Config, SceneResult
        print("✓ Core imports successful")
        
        from voxel.database import DatabaseManager, DatabaseQueries
        print("✓ Database imports successful")
        
        # Test individual agent imports
        from voxel.agents.concept import ConceptAgent
        from voxel.agents.builder import BuilderAgent
        print("✓ Core agent imports successful")
        
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def test_database():
    """Test database functionality."""
    try:
        from voxel.database import DatabaseManager
        
        # Test database manager creation
        db_manager = DatabaseManager("sqlite:///:memory:")
        print("✓ Database manager created")
        
        # Test table creation
        db_manager.create_tables()
        print("✓ Database tables created")
        
        # Test connection
        if db_manager.check_connection():
            print("✓ Database connection successful")
        else:
            print("✗ Database connection failed")
            return False
            
        return True
    except Exception as e:
        print(f"✗ Database error: {e}")
        return False

def test_voxel_init():
    """Test Voxel initialization."""
    try:
        from voxel import Voxel, Config
        
        # Test config creation
        config = Config()
        print("✓ Config created")
        
        # Test Voxel initialization (without API keys for now)
        try:
            voxel = Voxel(config)
            print("✓ Voxel initialized")
            voxel.close()
        except ValueError as e:
            if "API key" in str(e):
                print("✓ Voxel initialization works (API key required)")
            else:
                raise
        
        return True
    except Exception as e:
        print(f"✗ Voxel initialization error: {e}")
        return False

def main():
    """Run all tests."""
    print("Testing Voxel system...")
    print("=" * 40)
    
    tests = [
        ("Import Test", test_imports),
        ("Database Test", test_database),
        ("Voxel Init Test", test_voxel_init),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        if test_func():
            passed += 1
        else:
            print(f"✗ {test_name} failed")
    
    print(f"\n{'=' * 40}")
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("✓ All tests passed! Voxel is ready to use.")
        return True
    else:
        print("✗ Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
