"""
Claude Fine-Tuning Formatter - Converts datasets to Anthropic's fine-tuning format.
Formats training examples for Claude model fine-tuning.
"""

import logging
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ClaudeFineTuningExample:
    """
    Fine-tuning example in Claude's format.

    Format:
    {
        "system": "system prompt",
        "messages": [
            {"role": "user", "content": "user message"},
            {"role": "assistant", "content": "assistant response"}
        ]
    }
    """
    system: str
    messages: List[Dict[str, str]]


class ClaudeFormatter:
    """
    Formats training data for Claude fine-tuning.

    Anthropic fine-tuning format documentation:
    https://docs.anthropic.com/claude/docs/fine-tuning
    """

    # System prompts for different agent roles
    SYSTEM_PROMPTS = {
        "geometry": """You are a Blender geometry expert. Generate precise Python code for creating 3D objects, applying modifiers, and manipulating mesh geometry. Always use bpy.ops and bpy.data correctly.""",

        "material": """You are a Blender material expert. Create shader node networks, PBR materials, and procedural textures using Blender's node system. Output clean, efficient Python code.""",

        "lighting": """You are a Blender lighting expert. Set up professional lighting rigs, HDR environments, and realistic illumination using area lights, sun lamps, and world settings.""",

        "animation": """You are a Blender animation expert. Create keyframe animations, use F-curves, and set up complex motion using Blender's animation system.""",

        "scene": """You are a Blender scene expert. Organize objects into collections, set up render settings, and create complete scene compositions.""",
    }

    def __init__(
        self,
        dataset_dir: Path = Path("./training_data/datasets"),
        output_dir: Path = Path("./training_data/fine_tuning/claude")
    ):
        """
        Initialize formatter.

        Args:
            dataset_dir: Directory with raw datasets
            output_dir: Directory to save formatted data
        """
        self.dataset_dir = Path(dataset_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"ClaudeFormatter initialized (output={output_dir})")

    def format_dataset(self, split: str = "train") -> Dict[str, Any]:
        """
        Format a dataset split for Claude fine-tuning.

        Args:
            split: Dataset split (train, val, test)

        Returns:
            Statistics about formatting
        """
        input_file = self.dataset_dir / f"{split}.jsonl"

        if not input_file.exists():
            logger.error(f"Dataset file not found: {input_file}")
            return {"error": "file_not_found"}

        logger.info(f"Formatting {split} dataset for Claude...")

        formatted_examples = []

        with open(input_file, 'r') as f:
            for line_num, line in enumerate(f, 1):
                try:
                    example = json.loads(line)
                    formatted = self._format_example(example)

                    if formatted:
                        formatted_examples.append(formatted)

                except Exception as e:
                    logger.error(f"Error formatting line {line_num}: {e}")

        # Save formatted dataset
        output_file = self.output_dir / f"{split}_claude.jsonl"
        self._save_formatted_dataset(formatted_examples, output_file)

        stats = {
            "split": split,
            "total_examples": len(formatted_examples),
            "output_file": str(output_file),
            "format": "claude_fine_tuning"
        }

        logger.info(f"Formatted {len(formatted_examples)} examples for Claude")
        return stats

    def _format_example(self, example: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Format a single example for Claude.

        Args:
            example: Raw training example

        Returns:
            Formatted example or None
        """
        prompt = example.get('prompt')
        completion = example.get('completion')
        category = example.get('category', 'geometry')

        if not prompt or not completion:
            return None

        # Get appropriate system prompt
        system_prompt = self.SYSTEM_PROMPTS.get(category, self.SYSTEM_PROMPTS['geometry'])

        # Format in Claude's fine-tuning format
        formatted = {
            "system": system_prompt,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                },
                {
                    "role": "assistant",
                    "content": completion
                }
            ]
        }

        return formatted

    def _save_formatted_dataset(self, examples: List[Dict[str, Any]], output_file: Path):
        """Save formatted examples to JSONL file."""
        with open(output_file, 'w') as f:
            for example in examples:
                f.write(json.dumps(example) + '\n')

        logger.info(f"Saved {len(examples)} formatted examples to {output_file}")

    def format_all_splits(self) -> Dict[str, Any]:
        """Format all dataset splits (train, val, test)."""
        stats = {
            "train": self.format_dataset("train"),
            "val": self.format_dataset("val"),
            "test": self.format_dataset("test")
        }

        total_examples = sum(s.get('total_examples', 0) for s in stats.values())

        logger.info(f"Formatted all splits: {total_examples} total examples")

        return {
            "splits": stats,
            "total_examples": total_examples,
            "format": "claude_fine_tuning",
            "ready_for_upload": True
        }

    def validate_format(self, formatted_file: Path) -> Dict[str, Any]:
        """
        Validate formatted dataset meets Claude's requirements.

        Args:
            formatted_file: Path to formatted JSONL file

        Returns:
            Validation results
        """
        issues = []
        valid_count = 0

        with open(formatted_file, 'r') as f:
            for line_num, line in enumerate(f, 1):
                try:
                    example = json.loads(line)

                    # Check required fields
                    if 'system' not in example:
                        issues.append(f"Line {line_num}: Missing 'system' field")
                    if 'messages' not in example:
                        issues.append(f"Line {line_num}: Missing 'messages' field")
                    elif not isinstance(example['messages'], list):
                        issues.append(f"Line {line_num}: 'messages' must be a list")
                    elif len(example['messages']) != 2:
                        issues.append(f"Line {line_num}: 'messages' must have exactly 2 entries")
                    else:
                        # Check message format
                        for msg in example['messages']:
                            if 'role' not in msg or 'content' not in msg:
                                issues.append(f"Line {line_num}: Invalid message format")
                                break
                        else:
                            valid_count += 1

                except json.JSONDecodeError:
                    issues.append(f"Line {line_num}: Invalid JSON")

        return {
            "valid": len(issues) == 0,
            "valid_examples": valid_count,
            "total_lines": line_num,
            "issues": issues[:10]  # First 10 issues
        }


def main():
    """Example usage."""
    formatter = ClaudeFormatter()

    # Format all splits
    stats = formatter.format_all_splits()
    print(f"Formatting complete: {stats}")

    # Validate
    validation = formatter.validate_format(
        Path("./training_data/fine_tuning/claude/train_claude.jsonl")
    )
    print(f"Validation: {validation}")


if __name__ == "__main__":
    main()
