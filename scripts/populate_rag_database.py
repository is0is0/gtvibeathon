#!/usr/bin/env python3
"""Script to populate the RAG database with comprehensive examples."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from agency3d.utils.example_generator import ExampleGenerator

def main():
    """Populate the RAG database with examples."""
    print("🧠 Populating RAG Database with Comprehensive Examples...")
    print()
    
    # Create example generator
    generator = ExampleGenerator()
    
    # Generate comprehensive examples
    generator.generate_comprehensive_examples()
    
    # Print summary
    print()
    print("📊 RAG Database Summary:")
    print(f"   📝 Examples: {len(generator.database.examples)}")
    print(f"   🎯 Patterns: {len(generator.database.patterns)}")
    
    # Show example categories
    categories = {}
    for example in generator.database.examples:
        for tag in example.tags:
            categories[tag] = categories.get(tag, 0) + 1
    
    print()
    print("📂 Example Categories:")
    for category, count in sorted(categories.items()):
        print(f"   - {category}: {count} examples")
    
    print()
    print("✅ RAG database populated successfully!")
    print("   The system now has rich examples for pattern matching and learning.")

if __name__ == "__main__":
    main()
