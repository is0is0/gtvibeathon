#!/usr/bin/env python3
"""Fix markdown code blocks in agent files."""

import os
import re
from pathlib import Path

def fix_markdown_in_file(file_path):
    """Remove markdown code blocks from a Python file."""
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Remove ```python and ``` markers
    content = re.sub(r'```python\n', '', content)
    content = re.sub(r'```\n', '', content)
    content = re.sub(r'```', '', content)
    
    with open(file_path, 'w') as f:
        f.write(content)
    
    print(f"Fixed: {file_path}")

def main():
    """Fix all agent files."""
    agent_files = [
        "src/agency3d/agents/builder.py",
        "src/agency3d/agents/texture.py", 
        "src/agency3d/agents/render.py",
        "src/agency3d/agents/animation.py",
        "src/agency3d/agents/rigging.py",
        "src/agency3d/agents/compositing.py",
        "src/agency3d/agents/sequence.py"
    ]
    
    for file_path in agent_files:
        if os.path.exists(file_path):
            fix_markdown_in_file(file_path)
        else:
            print(f"Not found: {file_path}")

if __name__ == "__main__":
    main()
