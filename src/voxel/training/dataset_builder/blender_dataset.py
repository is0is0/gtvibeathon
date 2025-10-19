"""
Blender Dataset Builder - Converts parsed .blend data into ML training examples.
Creates prompt-completion pairs for fine-tuning Claude and GPT models.
"""

import logging
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import random

logger = logging.getLogger(__name__)


@dataclass
class TrainingExample:
    """A single training example (prompt-completion pair)."""
    prompt: str
    completion: str
    metadata: Dict[str, Any]
    category: str  # geometry, material, lighting, animation, etc.
    difficulty: str  # basic, intermediate, advanced
    quality_score: float  # 0.0 to 1.0


class BlenderDatasetBuilder:
    """
    Builds training datasets from parsed Blender files.
    Creates diverse prompt-completion pairs for different agent specializations.
    """

    # Templates for generating prompts
    GEOMETRY_PROMPTS = [
        "Create a {object_type} with {modifier_count} modifiers",
        "Build a {object_type} positioned at {location}",
        "Generate a {object_type} with {vertices_count} vertices",
        "Model a {object_type} using {modifiers}",
    ]

    MATERIAL_PROMPTS = [
        "Create a {shader_type} material for {object_type}",
        "Set up a material with {node_count} shader nodes",
        "Build a {material_type} material using nodes",
        "Generate PBR material for {object_type}",
    ]

    SCENE_PROMPTS = [
        "Create a scene with {object_count} objects",
        "Build a {collection_name} collection",
        "Set up a scene for {render_engine}",
        "Generate a scene with {lighting_type} lighting",
    ]

    def __init__(
        self,
        parsed_data_dir: Path = Path("./training_data/parsed"),
        output_dir: Path = Path("./training_data/datasets"),
        min_quality_score: float = 0.5
    ):
        """
        Initialize dataset builder.

        Args:
            parsed_data_dir: Directory with parsed .blend data
            output_dir: Directory to save datasets
            min_quality_score: Minimum quality score for examples
        """
        self.parsed_data_dir = Path(parsed_data_dir)
        self.output_dir = Path(output_dir)
        self.min_quality_score = min_quality_score

        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.checkpoint_dir = self.output_dir.parent / "checkpoints"
        self.checkpoint_dir.mkdir(exist_ok=True)
        self.checkpoint_file = self.checkpoint_dir / "dataset_checkpoint.json"

        self.examples = []
        self._load_checkpoint()

        logger.info(f"DatasetBuilder initialized (min_quality={min_quality_score})")

    def _load_checkpoint(self):
        """Load dataset building checkpoint."""
        if self.checkpoint_file.exists():
            try:
                with open(self.checkpoint_file, 'r') as f:
                    checkpoint = json.load(f)
                    # Could load partial examples if needed
                logger.info("Loaded dataset checkpoint")
            except Exception as e:
                logger.warning(f"Could not load checkpoint: {e}")

    def save_checkpoint(self, files_processed: int, errors: List[str] = None):
        """Save dataset building checkpoint."""
        from datetime import datetime

        checkpoint = {
            "task": "dataset_building",
            "status": "in_progress",
            "last_updated": datetime.now().isoformat(),
            "progress": {
                "files_processed": files_processed,
                "examples_generated": len(self.examples),
                "errors": len(errors) if errors else 0
            },
            "stats": {
                "by_category": self._count_by_category(),
                "by_difficulty": self._count_by_difficulty()
            },
            "errors": errors or []
        }

        with open(self.checkpoint_file, 'w') as f:
            json.dump(checkpoint, f, indent=2)

        logger.info(f"Checkpoint saved: {len(self.examples)} examples generated")

    def build_dataset(self) -> Dict[str, Any]:
        """
        Build complete training dataset from parsed files.

        Returns:
            Statistics about dataset creation
        """
        logger.info("Building training dataset...")

        parsed_files = list(self.parsed_data_dir.glob("*.json"))
        logger.info(f"Found {len(parsed_files)} parsed files")

        errors = []

        for idx, parsed_file in enumerate(parsed_files):
            try:
                with open(parsed_file, 'r') as f:
                    scene_data = json.load(f)

                # Generate examples from this scene
                examples = self._generate_examples_from_scene(scene_data)
                self.examples.extend(examples)

                logger.info(f"[{idx+1}/{len(parsed_files)}] Generated {len(examples)} examples from {parsed_file.name}")

                # Checkpoint every 10 files
                if (idx + 1) % 10 == 0:
                    self.save_checkpoint(idx + 1, errors)

            except Exception as e:
                error_msg = f"Error processing {parsed_file.name}: {e}"
                logger.error(error_msg)
                errors.append(error_msg)

        # Final checkpoint
        self.save_checkpoint(len(parsed_files), errors)

        # Filter by quality
        high_quality = [ex for ex in self.examples if ex.quality_score >= self.min_quality_score]

        # Split into train/val/test
        train, val, test = self._split_dataset(high_quality)

        # Save datasets
        self._save_dataset(train, "train")
        self._save_dataset(val, "val")
        self._save_dataset(test, "test")

        stats = {
            "total_examples": len(self.examples),
            "high_quality": len(high_quality),
            "train_size": len(train),
            "val_size": len(val),
            "test_size": len(test),
            "by_category": self._count_by_category(),
            "by_difficulty": self._count_by_difficulty(),
            "errors": errors
        }

        logger.info(f"Dataset complete: {stats}")
        return stats

    def _generate_examples_from_scene(self, scene_data: Dict[str, Any]) -> List[TrainingExample]:
        """Generate multiple training examples from a single scene."""
        examples = []

        # Generate geometry examples
        for obj in scene_data.get('objects', []):
            examples.extend(self._generate_geometry_examples(obj, scene_data))

        # Generate material examples
        for material in scene_data.get('materials', []):
            examples.extend(self._generate_material_examples(material, scene_data))

        # Generate scene-level examples
        examples.extend(self._generate_scene_examples(scene_data))

        return examples

    def _generate_geometry_examples(
        self,
        obj: Dict[str, Any],
        scene_data: Dict[str, Any]
    ) -> List[TrainingExample]:
        """Generate geometry-specific training examples."""
        examples = []

        obj_type = obj.get('type', 'MESH')
        obj_name = obj.get('name', 'object')
        modifiers = obj.get('modifiers', [])
        location = obj.get('location', [0, 0, 0])
        vertices = obj.get('vertices_count', 0)

        # Example 1: Basic object creation
        if obj_type == 'MESH':
            prompt = f"Create a {obj_name.lower()} object in Blender"
            completion = self._generate_object_creation_code(obj)

            examples.append(TrainingExample(
                prompt=prompt,
                completion=completion,
                metadata={"object": obj_name, "type": obj_type},
                category="geometry",
                difficulty="basic" if len(modifiers) == 0 else "intermediate",
                quality_score=self._calculate_quality_score(obj, scene_data)
            ))

        # Example 2: With modifiers
        if modifiers:
            prompt = f"Create a {obj_type.lower()} with {', '.join(modifiers[:3])} modifiers"
            completion = self._generate_object_with_modifiers_code(obj)

            examples.append(TrainingExample(
                prompt=prompt,
                completion=completion,
                metadata={"object": obj_name, "modifiers": modifiers},
                category="geometry",
                difficulty="intermediate" if len(modifiers) <= 2 else "advanced",
                quality_score=self._calculate_quality_score(obj, scene_data)
            ))

        return examples

    def _generate_material_examples(
        self,
        material: Dict[str, Any],
        scene_data: Dict[str, Any]
    ) -> List[TrainingExample]:
        """Generate material-specific training examples."""
        examples = []

        mat_name = material.get('name', 'Material')
        use_nodes = material.get('use_nodes', False)
        nodes = material.get('nodes', [])

        if use_nodes and nodes:
            # Detect shader type
            shader_type = self._detect_shader_type(nodes)

            prompt = f"Create a {shader_type} material using shader nodes"
            completion = self._generate_material_code(material)

            examples.append(TrainingExample(
                prompt=prompt,
                completion=completion,
                metadata={"material": mat_name, "shader": shader_type, "nodes": len(nodes)},
                category="material",
                difficulty="intermediate" if len(nodes) < 5 else "advanced",
                quality_score=0.8 if len(nodes) > 3 else 0.6
            ))

        return examples

    def _generate_scene_examples(self, scene_data: Dict[str, Any]) -> List[TrainingExample]:
        """Generate scene-level training examples."""
        examples = []

        objects = scene_data.get('objects', [])
        collections = scene_data.get('collections', [])

        if len(objects) > 3:
            prompt = f"Create a scene with {len(objects)} objects"
            completion = self._generate_scene_setup_code(scene_data)

            examples.append(TrainingExample(
                prompt=prompt,
                completion=completion,
                metadata={"object_count": len(objects)},
                category="scene",
                difficulty="intermediate" if len(objects) < 10 else "advanced",
                quality_score=0.7
            ))

        return examples

    def _generate_object_creation_code(self, obj: Dict[str, Any]) -> str:
        """Generate Blender Python code for object creation."""
        obj_type = obj.get('type', 'MESH').lower()
        name = obj.get('name', 'Object')
        location = obj.get('location', [0, 0, 0])

        if obj_type == 'mesh':
            return f"""import bpy

# Create mesh object
bpy.ops.mesh.primitive_cube_add(location=({location[0]}, {location[1]}, {location[2]}))
obj = bpy.context.active_object
obj.name = '{name}'
"""
        else:
            return f"""import bpy

# Create {obj_type} object
bpy.ops.object.{obj_type}_add(location=({location[0]}, {location[1]}, {location[2]}))
obj = bpy.context.active_object
obj.name = '{name}'
"""

    def _generate_object_with_modifiers_code(self, obj: Dict[str, Any]) -> str:
        """Generate code for object with modifiers."""
        base_code = self._generate_object_creation_code(obj)
        modifiers = obj.get('modifiers', [])

        modifier_code = "\n# Add modifiers\n"
        for mod in modifiers:
            if mod == 'SUBSURF':
                modifier_code += "mod = obj.modifiers.new('Subdivision', 'SUBSURF')\nmod.levels = 2\n"
            elif mod == 'BEVEL':
                modifier_code += "mod = obj.modifiers.new('Bevel', 'BEVEL')\nmod.width = 0.05\n"
            elif mod == 'ARRAY':
                modifier_code += "mod = obj.modifiers.new('Array', 'ARRAY')\nmod.count = 3\n"

        return base_code + modifier_code

    def _generate_material_code(self, material: Dict[str, Any]) -> str:
        """Generate code for material creation."""
        mat_name = material.get('name', 'Material')
        nodes = material.get('nodes', [])

        code = f"""import bpy

# Create material
mat = bpy.data.materials.new(name='{mat_name}')
mat.use_nodes = True
nodes = mat.node_tree.nodes
links = mat.node_tree.links
nodes.clear()

# Add shader nodes
"""

        # Add principal BSDF by default
        code += """bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
output = nodes.new(type='ShaderNodeOutputMaterial')
links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
"""

        return code

    def _generate_scene_setup_code(self, scene_data: Dict[str, Any]) -> str:
        """Generate code for complete scene setup."""
        return """import bpy

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Scene setup code here
# (Would be populated with actual objects from scene_data)
"""

    def _detect_shader_type(self, nodes: List[Dict[str, Any]]) -> str:
        """Detect shader type from node list."""
        node_types = [n.get('type', '') for n in nodes]

        if 'ShaderNodeBsdfPrincipled' in node_types:
            return "PBR"
        elif 'ShaderNodeBsdfGlass' in node_types:
            return "Glass"
        elif 'ShaderNodeEmission' in node_types:
            return "Emission"
        else:
            return "Custom"

    def _calculate_quality_score(self, obj: Dict[str, Any], scene_data: Dict[str, Any]) -> float:
        """Calculate quality score for an example."""
        score = 0.5  # Base score

        # Bonus for modifiers
        modifiers = obj.get('modifiers', [])
        score += min(0.2, len(modifiers) * 0.1)

        # Bonus for complexity
        vertices = obj.get('vertices_count', 0)
        if vertices > 100:
            score += 0.1
        if vertices > 1000:
            score += 0.1

        # Bonus for materials
        materials = obj.get('materials', [])
        if materials:
            score += 0.1

        return min(1.0, score)

    def _split_dataset(
        self,
        examples: List[TrainingExample],
        train_ratio: float = 0.8,
        val_ratio: float = 0.1
    ) -> tuple:
        """Split dataset into train/val/test sets."""
        random.shuffle(examples)

        n = len(examples)
        train_end = int(n * train_ratio)
        val_end = train_end + int(n * val_ratio)

        train = examples[:train_end]
        val = examples[train_end:val_end]
        test = examples[val_end:]

        return train, val, test

    def _save_dataset(self, examples: List[TrainingExample], split: str):
        """Save dataset split to file."""
        output_file = self.output_dir / f"{split}.jsonl"

        with open(output_file, 'w') as f:
            for example in examples:
                data = {
                    "prompt": example.prompt,
                    "completion": example.completion,
                    "metadata": example.metadata,
                    "category": example.category,
                    "difficulty": example.difficulty,
                    "quality_score": example.quality_score
                }
                f.write(json.dumps(data) + '\n')

        logger.info(f"Saved {len(examples)} examples to {output_file}")

    def _count_by_category(self) -> Dict[str, int]:
        """Count examples by category."""
        counts = {}
        for ex in self.examples:
            counts[ex.category] = counts.get(ex.category, 0) + 1
        return counts

    def _count_by_difficulty(self) -> Dict[str, int]:
        """Count examples by difficulty."""
        counts = {}
        for ex in self.examples:
            counts[ex.difficulty] = counts.get(ex.difficulty, 0) + 1
        return counts


def main():
    """Example usage."""
    builder = BlenderDatasetBuilder()
    stats = builder.build_dataset()
    print(f"Dataset built: {stats}")


if __name__ == "__main__":
    main()
