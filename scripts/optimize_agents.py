#!/usr/bin/env python3
"""Optimize agent scripts by removing redundant content."""

import re
from pathlib import Path

def optimize_agent_file(file_path: Path) -> int:
    """Optimize a single agent file by removing redundant content."""
    with open(file_path, 'r') as f:
        content = f.read()
    
    original_lines = len(content.split('\n'))
    
    # Remove excessive examples (keep only 2-3)
    # Find example sections and limit them
    example_pattern = r'(## Example.*?)(?=## |\Z)'
    examples = re.findall(example_pattern, content, re.DOTALL)
    
    if len(examples) > 3:
        # Keep only first 3 examples
        examples_to_keep = examples[:3]
        for i, example in enumerate(examples[3:], 3):
            content = content.replace(example, '')
    
    # Remove excessive system prompt details (keep core functionality)
    # This is more complex and would need careful analysis
    
    # Remove duplicate imports
    lines = content.split('\n')
    seen_imports = set()
    optimized_lines = []
    
    for line in lines:
        if line.strip().startswith('import ') or line.strip().startswith('from '):
            if line not in seen_imports:
                seen_imports.add(line)
                optimized_lines.append(line)
        else:
            optimized_lines.append(line)
    
    optimized_content = '\n'.join(optimized_lines)
    optimized_lines = len(optimized_content.split('\n'))
    
    lines_saved = original_lines - optimized_lines
    
    if lines_saved > 10:  # Only save if significant reduction
        with open(file_path, 'w') as f:
            f.write(optimized_content)
        return lines_saved
    
    return 0

def main():
    """Optimize all agent files."""
    print("🔧 Optimizing Agent Scripts...")
    print()
    
    agents_dir = Path("src/agency3d/agents")
    total_saved = 0
    
    for agent_file in agents_dir.glob("*.py"):
        if agent_file.name == "__init__.py":
            continue
            
        print(f"📝 Optimizing {agent_file.name}...")
        saved = optimize_agent_file(agent_file)
        
        if saved > 0:
            print(f"   ✅ Saved {saved} lines")
            total_saved += saved
        else:
            print(f"   ⚠️  No significant optimization possible")
    
    print()
    print(f"🎯 Total lines saved: {total_saved}")
    print("💡 Agent scripts optimized!")

if __name__ == "__main__":
    main()
