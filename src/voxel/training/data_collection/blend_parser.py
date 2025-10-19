"""
Blend File Parser - Extracts training data from .blend files.
Parses Blender files to extract objects, materials, modifiers, node trees, and Python scripts.
"""

import logging
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import hashlib

logger = logging.getLogger(__name__)


@dataclass
class BlendObject:
    """Represents an object extracted from a .blend file."""
    name: str
    type: str  # MESH, CURVE, LIGHT, CAMERA, etc.
    location: tuple
    rotation: tuple
    scale: tuple
    modifiers: List[str]
    materials: List[str]
    vertices_count: int = 0
    faces_count: int = 0


@dataclass
class BlendMaterial:
    """Represents a material extracted from a .blend file."""
    name: str
    use_nodes: bool
    nodes: List[Dict[str, Any]]  # Node tree structure
    node_count: int = 0
    has_textures: bool = False
    shader_type: Optional[str] = None  # Principled, Emission, Glass, etc.


@dataclass
class BlendSceneData:
    """Complete data extracted from a .blend file."""
    filename: str
    file_hash: str
    blender_version: str
    objects: List[BlendObject]
    materials: List[BlendMaterial]
    scripts: List[str]  # Python scripts found in file
    collections: List[str]
    render_settings: Dict[str, Any]
    metadata: Dict[str, Any]


class BlendFileParser:
    """
    Parses .blend files to extract structured training data.

    Uses blender_file library for binary parsing without requiring Blender.
    Falls back to Blender Python API if needed for complex parsing.
    """

    def __init__(self, output_dir: Path = Path("./training_data/parsed")):
        """
        Initialize parser.

        Args:
            output_dir: Directory to save parsed data
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.checkpoint_dir = self.output_dir.parent / "checkpoints"
        self.checkpoint_dir.mkdir(exist_ok=True)
        self.checkpoint_file = self.checkpoint_dir / "parsing_checkpoint.json"

        # Track parsed files
        self.parsed_hashes = set()
        self._load_checkpoint()

        logger.info(f"BlendFileParser initialized (output={output_dir})")

    def _load_checkpoint(self):
        """Load parsing checkpoint if exists."""
        if self.checkpoint_file.exists():
            try:
                with open(self.checkpoint_file, 'r') as f:
                    checkpoint = json.load(f)
                    self.parsed_hashes = set(checkpoint.get('parsed_hashes', []))
                logger.info(f"Loaded checkpoint: {len(self.parsed_hashes)} files already parsed")
            except Exception as e:
                logger.warning(f"Could not load checkpoint: {e}")

    def save_checkpoint(self, files_parsed: int, errors: List[str] = None):
        """Save parsing checkpoint."""
        from datetime import datetime

        checkpoint = {
            "task": "parsing",
            "status": "in_progress",
            "last_updated": datetime.now().isoformat(),
            "progress": {
                "files_parsed": files_parsed,
                "total_parsed_hashes": len(self.parsed_hashes),
                "errors": len(errors) if errors else 0
            },
            "state": {
                "parsed_hashes": list(self.parsed_hashes)
            },
            "errors": errors or [],
            "next_steps": [
                "Resume parsing remaining files",
                "Run: parser.parse_directory(Path('blend_files'))"
            ]
        }

        with open(self.checkpoint_file, 'w') as f:
            json.dump(checkpoint, f, indent=2)

        logger.info(f"Checkpoint saved: {files_parsed} files parsed")

    def parse_file(self, blend_path: Path) -> Optional[BlendSceneData]:
        """
        Parse a single .blend file.

        Args:
            blend_path: Path to .blend file

        Returns:
            BlendSceneData or None if parsing failed
        """
        file_hash = self._hash_file(blend_path)

        if file_hash in self.parsed_hashes:
            logger.info(f"Skipping already parsed file: {blend_path.name}")
            return None

        logger.info(f"Parsing: {blend_path.name}")

        try:
            # Try parsing with blender_file library first (fast, no Blender needed)
            scene_data = self._parse_with_blender_file(blend_path)

            if scene_data:
                # Save parsed data
                self._save_parsed_data(scene_data)
                self.parsed_hashes.add(file_hash)
                return scene_data
            else:
                # Fallback to Blender Python API (slow, requires Blender)
                logger.warning(f"blender_file failed for {blend_path.name}, trying Blender API")
                scene_data = self._parse_with_blender_api(blend_path)

                if scene_data:
                    self._save_parsed_data(scene_data)
                    self.parsed_hashes.add(file_hash)
                    return scene_data

        except Exception as e:
            logger.error(f"Error parsing {blend_path.name}: {e}")
            return None

        return None

    def _parse_with_blender_file(self, blend_path: Path) -> Optional[BlendSceneData]:
        """
        Parse using blender_file library (fast, limited).

        This is a placeholder - actual implementation would use blender_file library.
        For now, returns mock data structure.
        """
        try:
            # TODO: Implement actual blender_file parsing
            # from blender_file import BlendFile
            # blend = BlendFile(blend_path)
            # ...

            # For now, create mock structure to demonstrate data format
            file_hash = self._hash_file(blend_path)

            scene_data = BlendSceneData(
                filename=blend_path.name,
                file_hash=file_hash,
                blender_version="unknown",
                objects=[],
                materials=[],
                scripts=[],
                collections=[],
                render_settings={},
                metadata={
                    "file_size": blend_path.stat().st_size,
                    "parsing_method": "blender_file_library"
                }
            )

            return scene_data

        except Exception as e:
            logger.error(f"blender_file parsing failed: {e}")
            return None

    def _parse_with_blender_api(self, blend_path: Path) -> Optional[BlendSceneData]:
        """
        Parse using Blender Python API (slower, requires Blender installed).

        This generates a Blender Python script and executes it.
        """
        try:
            # Generate parsing script
            script = self._generate_parsing_script(blend_path)

            # Execute with Blender (requires Blender in PATH)
            # For now, placeholder
            logger.warning("Blender API parsing not yet implemented")
            return None

        except Exception as e:
            logger.error(f"Blender API parsing failed: {e}")
            return None

    def _generate_parsing_script(self, blend_path: Path) -> str:
        """Generate Blender Python script to extract data."""
        return f"""
import bpy
import json

# Load blend file
bpy.ops.wm.open_mainfile(filepath="{blend_path}")

data = {{
    "filename": "{blend_path.name}",
    "blender_version": bpy.app.version_string,
    "objects": [],
    "materials": [],
    "collections": []
}}

# Extract objects
for obj in bpy.data.objects:
    obj_data = {{
        "name": obj.name,
        "type": obj.type,
        "location": list(obj.location),
        "rotation": list(obj.rotation_euler),
        "scale": list(obj.scale),
        "modifiers": [m.type for m in obj.modifiers],
        "materials": [m.name for m in obj.data.materials] if hasattr(obj.data, 'materials') else []
    }}

    if obj.type == 'MESH':
        obj_data["vertices_count"] = len(obj.data.vertices)
        obj_data["faces_count"] = len(obj.data.polygons)

    data["objects"].append(obj_data)

# Extract materials
for mat in bpy.data.materials:
    mat_data = {{
        "name": mat.name,
        "use_nodes": mat.use_nodes,
        "nodes": []
    }}

    if mat.use_nodes:
        for node in mat.node_tree.nodes:
            mat_data["nodes"].append({{
                "type": node.type,
                "name": node.name
            }})

    data["materials"].append(mat_data)

# Save to JSON
with open("{blend_path.parent / 'parsed' / (blend_path.stem + '.json')}", 'w') as f:
    json.dump(data, f, indent=2)
"""

    def _hash_file(self, file_path: Path) -> str:
        """Calculate file hash."""
        hasher = hashlib.md5()
        with open(file_path, 'rb') as f:
            hasher.update(f.read(8192))  # First 8KB for speed
        return hasher.hexdigest()

    def _save_parsed_data(self, scene_data: BlendSceneData):
        """Save parsed scene data to JSON."""
        output_file = self.output_dir / f"{Path(scene_data.filename).stem}.json"

        with open(output_file, 'w') as f:
            json.dump(asdict(scene_data), f, indent=2)

        logger.info(f"Saved parsed data: {output_file.name}")

    def parse_directory(self, blend_dir: Path) -> Dict[str, Any]:
        """
        Parse all .blend files in a directory.

        Args:
            blend_dir: Directory containing .blend files

        Returns:
            Statistics about parsing
        """
        logger.info(f"Parsing directory: {blend_dir}")

        blend_files = list(blend_dir.glob("**/*.blend"))
        logger.info(f"Found {len(blend_files)} .blend files")

        parsed_count = 0
        errors = []

        for idx, blend_file in enumerate(blend_files):
            logger.info(f"Processing [{idx+1}/{len(blend_files)}]: {blend_file.name}")

            scene_data = self.parse_file(blend_file)

            if scene_data:
                parsed_count += 1
            else:
                errors.append(f"Failed to parse: {blend_file.name}")

            # Save checkpoint every 10 files
            if (idx + 1) % 10 == 0:
                self.save_checkpoint(parsed_count, errors)

        # Final checkpoint
        self.save_checkpoint(parsed_count, errors)

        stats = {
            "total_files": len(blend_files),
            "parsed_successfully": parsed_count,
            "failed": len(errors),
            "errors": errors
        }

        logger.info(f"Parsing complete: {stats}")
        return stats


def main():
    """Example usage."""
    parser = BlendFileParser()

    # Parse directory
    stats = parser.parse_directory(Path("./training_data/blend_files"))
    print(f"Parsing complete: {stats}")


if __name__ == "__main__":
    main()
