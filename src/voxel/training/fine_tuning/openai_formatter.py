"""
OpenAI Fine-Tuning Formatter - Converts datasets to OpenAI's fine-tuning format.
Formats training examples for GPT model fine-tuning.
"""

import logging
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class OpenAIFineTuningExample:
    """
    Fine-tuning example in OpenAI's format.

    Format:
    {
        "messages": [
            {"role": "system", "content": "system prompt"},
            {"role": "user", "content": "user message"},
            {"role": "assistant", "content": "assistant response"}
        ]
    }
    """
    messages: List[Dict[str, str]]


class OpenAIFormatter:
    """
    Formats training data for OpenAI GPT fine-tuning.

    OpenAI fine-tuning format documentation:
    https://platform.openai.com/docs/guides/fine-tuning
    """

    # System prompts for different agent roles
    SYSTEM_PROMPTS = {
        "geometry": """You are an expert Blender Python programmer specializing in 3D geometry. Generate clean, efficient Python code using bpy to create objects, apply modifiers, and manipulate meshes. Always include necessary imports and error handling.""",

        "material": """You are an expert in Blender's shader system. Create sophisticated material setups using Principled BSDF, node networks, and procedural textures. Write clear Python code that leverages Blender's material nodes effectively.""",

        "lighting": """You are a Blender lighting specialist. Set up professional lighting using area lights, sun lamps, HDR environments, and world settings. Generate Python code that creates cinematic illumination.""",

        "animation": """You are a Blender animation expert. Create keyframe animations, modify F-curves, apply easing, and set up complex motion. Write Python code that produces smooth, professional animations.""",

        "scene": """You are a Blender scene composition expert. Organize objects into collections, configure render settings (Cycles/Eevee), and create complete scene setups. Generate well-structured Python code for scene management.""",
    }

    def __init__(
        self,
        dataset_dir: Path = Path("./training_data/datasets"),
        output_dir: Path = Path("./training_data/fine_tuning/openai")
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

        logger.info(f"OpenAIFormatter initialized (output={output_dir})")

    def format_dataset(self, split: str = "train") -> Dict[str, Any]:
        """
        Format a dataset split for OpenAI GPT fine-tuning.

        Args:
            split: Dataset split (train, val, test)

        Returns:
            Statistics about formatting
        """
        input_file = self.dataset_dir / f"{split}.jsonl"

        if not input_file.exists():
            logger.error(f"Dataset file not found: {input_file}")
            return {"error": "file_not_found"}

        logger.info(f"Formatting {split} dataset for OpenAI...")

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
        output_file = self.output_dir / f"{split}_openai.jsonl"
        self._save_formatted_dataset(formatted_examples, output_file)

        stats = {
            "split": split,
            "total_examples": len(formatted_examples),
            "output_file": str(output_file),
            "format": "openai_fine_tuning"
        }

        logger.info(f"Formatted {len(formatted_examples)} examples for OpenAI")
        return stats

    def _format_example(self, example: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Format a single example for OpenAI.

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

        # Format in OpenAI's fine-tuning format
        formatted = {
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt
                },
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
            "format": "openai_fine_tuning",
            "ready_for_upload": True
        }

    def validate_format(self, formatted_file: Path) -> Dict[str, Any]:
        """
        Validate formatted dataset meets OpenAI's requirements.

        Args:
            formatted_file: Path to formatted JSONL file

        Returns:
            Validation results
        """
        issues = []
        valid_count = 0
        total_tokens = 0

        with open(formatted_file, 'r') as f:
            for line_num, line in enumerate(f, 1):
                try:
                    example = json.loads(line)

                    # Check required fields
                    if 'messages' not in example:
                        issues.append(f"Line {line_num}: Missing 'messages' field")
                        continue

                    messages = example['messages']

                    if not isinstance(messages, list):
                        issues.append(f"Line {line_num}: 'messages' must be a list")
                        continue

                    if len(messages) != 3:
                        issues.append(f"Line {line_num}: 'messages' must have exactly 3 entries (system, user, assistant)")
                        continue

                    # Check message roles
                    expected_roles = ['system', 'user', 'assistant']
                    actual_roles = [msg.get('role') for msg in messages]

                    if actual_roles != expected_roles:
                        issues.append(f"Line {line_num}: Invalid message roles. Expected {expected_roles}, got {actual_roles}")
                        continue

                    # Check content exists
                    for idx, msg in enumerate(messages):
                        if 'content' not in msg or not msg['content']:
                            issues.append(f"Line {line_num}: Message {idx} missing content")
                            break
                    else:
                        valid_count += 1

                        # Estimate tokens (rough approximation: 4 chars = 1 token)
                        for msg in messages:
                            total_tokens += len(msg['content']) // 4

                except json.JSONDecodeError:
                    issues.append(f"Line {line_num}: Invalid JSON")

        # Estimate cost (GPT-4 fine-tuning: ~$0.008 per 1K tokens)
        estimated_cost = (total_tokens / 1000) * 0.008

        return {
            "valid": len(issues) == 0,
            "valid_examples": valid_count,
            "total_lines": line_num if 'line_num' in locals() else 0,
            "estimated_tokens": total_tokens,
            "estimated_cost_usd": round(estimated_cost, 2),
            "issues": issues[:10]  # First 10 issues
        }

    def estimate_training_cost(self, split: str = "train", epochs: int = 3) -> Dict[str, Any]:
        """
        Estimate fine-tuning cost for a dataset.

        Args:
            split: Dataset split
            epochs: Number of training epochs

        Returns:
            Cost estimation
        """
        formatted_file = self.output_dir / f"{split}_openai.jsonl"

        if not formatted_file.exists():
            return {"error": "formatted_file_not_found"}

        validation = self.validate_format(formatted_file)

        total_tokens = validation.get('estimated_tokens', 0)
        training_tokens = total_tokens * epochs

        # OpenAI pricing (as of 2025)
        # GPT-4: $0.008 per 1K tokens
        # GPT-3.5-turbo: $0.0016 per 1K tokens
        gpt4_cost = (training_tokens / 1000) * 0.008
        gpt35_cost = (training_tokens / 1000) * 0.0016

        return {
            "examples": validation.get('valid_examples', 0),
            "total_tokens": total_tokens,
            "training_tokens": training_tokens,
            "epochs": epochs,
            "estimated_cost": {
                "gpt4_usd": round(gpt4_cost, 2),
                "gpt35_turbo_usd": round(gpt35_cost, 2)
            }
        }


def main():
    """Example usage."""
    formatter = OpenAIFormatter()

    # Format all splits
    stats = formatter.format_all_splits()
    print(f"Formatting complete: {stats}")

    # Validate
    validation = formatter.validate_format(
        Path("./training_data/fine_tuning/openai/train_openai.jsonl")
    )
    print(f"Validation: {validation}")

    # Estimate cost
    cost = formatter.estimate_training_cost(epochs=3)
    print(f"Training cost estimate: {cost}")


if __name__ == "__main__":
    main()
