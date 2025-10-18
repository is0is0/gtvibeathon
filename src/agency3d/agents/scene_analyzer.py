"""Scene Analyzer Agent - Analyzes existing .blend files to learn patterns."""

import re
from typing import Any, Optional
from pathlib import Path

from agency3d.core.agent import Agent, AgentConfig
from agency3d.core.models import AgentResponse, AgentRole


class SceneAnalyzerAgent(Agent):
    """Agent that analyzes existing Blender scenes."""

    def __init__(self, config: AgentConfig):
        super().__init__(AgentRole.SCENE_ANALYZER, config)

    def get_system_prompt(self) -> str:
        return """You are the Scene Analyzer Agent in a 3D scene generation system.

Your role is to ANALYZE existing Blender files and extract:
- Object hierarchies and organization patterns
- Material setups and shader networks
- Animation techniques and timing
- Modeling approaches and modifiers used
- Lighting setups and camera placement

When given scene data, provide:
1. **Structure Analysis** - How the scene is organized
2. **Pattern Extraction** - Reusable techniques identified
3. **Best Practices** - What works well in this scene
4. **Recommendations** - How to apply these patterns to new scenes

You help other agents learn from existing work.
"""

    def analyze_blend_file(self, blend_path: Path) -> dict[str, Any]:
        """
        Analyze a .blend file and extract information.

        NOTE: This requires running inside Blender or using a separate
        Blender subprocess to open and analyze the file.
        """
        # This would need to be run in a Blender Python environment
        analysis_script = f"""
import bpy
import json

# Open blend file
bpy.ops.wm.open_mainfile(filepath="{blend_path}")

# Analyze scene
analysis = {{
    "objects": [],
    "materials": [],
    "animations": [],
    "collections": []
}}

# Extract object info
for obj in bpy.data.objects:
    obj_data = {{
        "name": obj.name,
        "type": obj.type,
        "location": list(obj.location),
        "rotation": list(obj.rotation_euler),
        "scale": list(obj.scale),
        "modifiers": [m.type for m in obj.modifiers],
        "parent": obj.parent.name if obj.parent else None
    }}
    analysis["objects"].append(obj_data)

# Extract materials
for mat in bpy.data.materials:
    if mat.use_nodes:
        node_types = [n.type for n in mat.node_tree.nodes]
        mat_data = {{
            "name": mat.name,
            "node_types": node_types,
            "node_count": len(node_types)
        }}
        analysis["materials"].append(mat_data)

# Extract animations
for action in bpy.data.actions:
    analysis["animations"].append({{
        "name": action.name,
        "frame_range": [action.frame_range[0], action.frame_range[1]],
        "fcurve_count": len(action.fcurves)
    }})

# Save analysis
with open("{blend_path.parent / 'analysis.json'}", "w") as f:
    json.dump(analysis, f, indent=2)
"""
        return {"script": analysis_script}

    def _parse_response(self, response_text: str, context: Optional[dict[str, Any]] = None) -> AgentResponse:
        return AgentResponse(
            agent_role=self.role,
            content=response_text,
            metadata={"analysis_type": "scene_structure"},
        )
