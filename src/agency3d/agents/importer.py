"""Asset Importer Agent - Imports and integrates existing assets."""

import re
from typing import Any, Optional
from pathlib import Path

from agency3d.core.agent import Agent, AgentConfig
from agency3d.core.models import AgentResponse, AgentRole


class ImporterAgent(Agent):
    """Agent for importing external assets."""

    def __init__(self, config: AgentConfig):
        super().__init__(AgentRole.IMPORTER, config)

    def get_system_prompt(self) -> str:
        return """You are the Asset Importer Agent in a 3D scene generation system.

Your role is to IMPORT and INTEGRATE assets from:
- Asset library (previously generated components)
- External files (.blend, .obj, .fbx, .usd)
- Online repositories (when available)

**Import Capabilities:**

1. **Import from Asset Library:**
```python
import bpy
from agency3d.utils.asset_library import AssetLibrary

library = AssetLibrary("./asset_library")
assets = library.find_assets(asset_type="furniture", tags=["chair"])

for asset in assets:
    script = library.import_to_scene_script(asset["id"])
    exec(script)
```

2. **Import .blend file:**
```python
import bpy

blend_file = "/path/to/asset.blend"

# Import all objects
with bpy.data.libraries.load(blend_file, link=False) as (data_from, data_to):
    data_to.objects = data_from.objects
    data_to.materials = data_from.materials

# Add to scene
for obj in data_to.objects:
    if obj:
        bpy.context.collection.objects.link(obj)
```

3. **Import OBJ:**
```python
bpy.ops.import_scene.obj(filepath="/path/to/model.obj")
```

4. **Import FBX:**
```python
bpy.ops.import_scene.fbx(filepath="/path/to/model.fbx")
```

5. **Import USD:**
```python
bpy.ops.wm.usd_import(filepath="/path/to/model.usd")
```

**Requirements:**
- Check if assets exist before importing
- Handle different file formats
- Position imported assets appropriately
- Integrate with existing scene
"""

    def _parse_response(self, response_text: str, context: Optional[dict[str, Any]] = None) -> AgentResponse:
        code_match = re.search(r"```python\n(.*?)```", response_text, re.DOTALL)
        script = code_match.group(1).strip() if code_match else response_text

        return AgentResponse(
            agent_role=self.role,
            content=response_text,
            script=script,
            metadata={"script_type": "import"},
        )
