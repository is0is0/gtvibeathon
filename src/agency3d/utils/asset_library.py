"""Asset Library Manager - Manages reusable 3D assets."""

from pathlib import Path
import json
import shutil
from typing import Optional, List, Dict, Any


class AssetLibrary:
    """Manages a library of reusable 3D assets."""

    def __init__(self, library_path: Path):
        self.library_path = Path(library_path)
        self.library_path.mkdir(parents=True, exist_ok=True)

        self.index_file = self.library_path / "index.json"
        self.index = self._load_index()

    def _load_index(self) -> Dict[str, Any]:
        """Load the asset index."""
        if self.index_file.exists():
            return json.loads(self.index_file.read_text())
        return {"assets": [], "version": "1.0"}

    def _save_index(self) -> None:
        """Save the asset index."""
        self.index_file.write_text(json.dumps(self.index, indent=2))

    def add_asset(
        self,
        name: str,
        asset_type: str,
        file_path: Path,
        tags: List[str] = None,
        metadata: Dict[str, Any] = None
    ) -> None:
        """Add an asset to the library."""
        asset_id = f"{asset_type}_{name}".replace(" ", "_")
        asset_dir = self.library_path / asset_id
        asset_dir.mkdir(exist_ok=True)

        # Copy asset file
        dest_path = asset_dir / file_path.name
        shutil.copy2(file_path, dest_path)

        # Add to index
        asset_entry = {
            "id": asset_id,
            "name": name,
            "type": asset_type,
            "path": str(dest_path.relative_to(self.library_path)),
            "tags": tags or [],
            "metadata": metadata or {}
        }

        # Update or add entry
        existing = next((a for a in self.index["assets"] if a["id"] == asset_id), None)
        if existing:
            self.index["assets"].remove(existing)
        self.index["assets"].append(asset_entry)

        self._save_index()

    def find_assets(
        self,
        asset_type: Optional[str] = None,
        tags: Optional[List[str]] = None,
        name_pattern: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Find assets matching criteria."""
        results = self.index["assets"]

        if asset_type:
            results = [a for a in results if a["type"] == asset_type]

        if tags:
            results = [a for a in results if any(t in a["tags"] for t in tags)]

        if name_pattern:
            results = [a for a in results if name_pattern.lower() in a["name"].lower()]

        return results

    def get_asset_path(self, asset_id: str) -> Optional[Path]:
        """Get the file path for an asset."""
        asset = next((a for a in self.index["assets"] if a["id"] == asset_id), None)
        if asset:
            return self.library_path / asset["path"]
        return None

    def import_to_scene_script(self, asset_id: str) -> str:
        """Generate a Blender script to import this asset."""
        asset_path = self.get_asset_path(asset_id)
        if not asset_path:
            return ""

        if asset_path.suffix == ".blend":
            return f"""
import bpy

# Import from blend file
with bpy.data.libraries.load("{asset_path}", link=False) as (data_from, data_to):
    data_to.objects = data_from.objects

# Add to scene
for obj in data_to.objects:
    if obj is not None:
        bpy.context.collection.objects.link(obj)
"""
        return ""

    def list_all_assets(self) -> List[str]:
        """List all asset names."""
        return [a["name"] for a in self.index["assets"]]
