"""
Quality Metrics - Evaluates fine-tuned models against base models.
Measures improvement in code quality, accuracy, and Blender-specific knowledge.
"""

import logging
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import re

logger = logging.getLogger(__name__)


@dataclass
class EvaluationResult:
    """Result of evaluating a model on a test example."""
    example_id: str
    prompt: str
    expected_output: str
    actual_output: str
    scores: Dict[str, float]  # code_quality, accuracy, blender_knowledge, etc.
    overall_score: float
    passed: bool


class QualityMetrics:
    """
    Evaluates fine-tuned models for quality improvements.
    Compares against base models and test dataset.
    """

    def __init__(
        self,
        test_dataset: Path = Path("./training_data/datasets/test.jsonl"),
        output_dir: Path = Path("./training_data/evaluation")
    ):
        """
        Initialize quality metrics.

        Args:
            test_dataset: Path to test dataset
            output_dir: Directory to save evaluation results
        """
        self.test_dataset = Path(test_dataset)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"QualityMetrics initialized (test={test_dataset})")

    def evaluate_model(
        self,
        model_id: str,
        provider: str,
        num_examples: int = 100
    ) -> Dict[str, Any]:
        """
        Evaluate a fine-tuned model.

        Args:
            model_id: Fine-tuned model ID
            provider: "anthropic" or "openai"
            num_examples: Number of test examples to evaluate

        Returns:
            Evaluation results
        """
        logger.info(f"Evaluating model {model_id}...")

        if not self.test_dataset.exists():
            logger.error(f"Test dataset not found: {self.test_dataset}")
            return {"error": "test_dataset_not_found"}

        # Load test examples
        test_examples = self._load_test_examples(num_examples)

        # Run evaluation
        results = []
        for idx, example in enumerate(test_examples):
            logger.info(f"Evaluating example {idx+1}/{len(test_examples)}")

            result = self._evaluate_example(
                example=example,
                model_id=model_id,
                provider=provider
            )

            results.append(result)

        # Calculate aggregate metrics
        metrics = self._calculate_aggregate_metrics(results)

        # Save results
        self._save_results(model_id, results, metrics)

        logger.info(f"Evaluation complete: {metrics}")

        return metrics

    def _load_test_examples(self, num_examples: int) -> List[Dict[str, Any]]:
        """Load test examples from dataset."""
        examples = []

        with open(self.test_dataset, 'r') as f:
            for idx, line in enumerate(f):
                if idx >= num_examples:
                    break

                example = json.loads(line)
                examples.append(example)

        logger.info(f"Loaded {len(examples)} test examples")
        return examples

    def _evaluate_example(
        self,
        example: Dict[str, Any],
        model_id: str,
        provider: str
    ) -> EvaluationResult:
        """Evaluate a single example."""
        prompt = example.get('prompt', '')
        expected = example.get('completion', '')

        # Get model response
        try:
            actual = self._get_model_response(prompt, model_id, provider)
        except Exception as e:
            logger.error(f"Error getting model response: {e}")
            actual = ""

        # Calculate scores
        scores = {
            "code_syntax": self._score_code_syntax(actual),
            "blender_api": self._score_blender_api_usage(actual),
            "completeness": self._score_completeness(actual, expected),
            "similarity": self._score_similarity(actual, expected)
        }

        overall = sum(scores.values()) / len(scores)

        return EvaluationResult(
            example_id=str(hash(prompt)),
            prompt=prompt,
            expected_output=expected,
            actual_output=actual,
            scores=scores,
            overall_score=overall,
            passed=overall >= 0.7
        )

    def _get_model_response(
        self,
        prompt: str,
        model_id: str,
        provider: str
    ) -> str:
        """Get response from fine-tuned model."""
        if provider == "anthropic":
            import anthropic
            import os

            client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

            message = client.messages.create(
                model=model_id,
                max_tokens=1024,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            return message.content[0].text

        elif provider == "openai":
            import openai
            import os

            openai.api_key = os.getenv("OPENAI_API_KEY")

            response = openai.ChatCompletion.create(
                model=model_id,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1024
            )

            return response.choices[0].message.content

        else:
            raise ValueError(f"Unknown provider: {provider}")

    def _score_code_syntax(self, code: str) -> float:
        """Score code syntax correctness."""
        try:
            # Check for Python code block
            if "```python" in code:
                code_match = re.search(r"```python\n(.*?)```", code, re.DOTALL)
                if code_match:
                    code = code_match.group(1)

            # Try to compile the code
            compile(code, '<string>', 'exec')
            return 1.0

        except SyntaxError:
            return 0.0
        except Exception:
            return 0.5  # Code exists but may have runtime issues

    def _score_blender_api_usage(self, code: str) -> float:
        """Score correct Blender API usage."""
        score = 0.0

        # Check for bpy import
        if "import bpy" in code:
            score += 0.3

        # Check for common bpy patterns
        patterns = [
            r'bpy\.ops\.\w+',  # Operations
            r'bpy\.data\.\w+',  # Data access
            r'bpy\.context\.\w+',  # Context access
        ]

        for pattern in patterns:
            if re.search(pattern, code):
                score += 0.2

        # Check for proper object creation
        if "primitive" in code.lower() or "add" in code.lower():
            score += 0.1

        return min(1.0, score)

    def _score_completeness(self, actual: str, expected: str) -> float:
        """Score how complete the response is."""
        if not actual:
            return 0.0

        # Simple heuristic: length ratio
        actual_len = len(actual)
        expected_len = len(expected)

        if expected_len == 0:
            return 0.5

        ratio = min(actual_len / expected_len, 1.5)  # Cap at 1.5x expected length

        # Normalize to 0-1 range
        if ratio < 0.5:
            return ratio / 0.5 * 0.5  # 0-0.5 maps to 0-0.25
        elif ratio > 1.5:
            return 0.5  # Too verbose
        else:
            return 0.5 + (ratio - 0.5) / 1.0 * 0.5  # 0.5-1.5 maps to 0.5-1.0

    def _score_similarity(self, actual: str, expected: str) -> float:
        """Score similarity to expected output."""
        if not actual or not expected:
            return 0.0

        # Extract code if in markdown
        actual_code = self._extract_code(actual)
        expected_code = self._extract_code(expected)

        # Simple word overlap
        actual_words = set(actual_code.lower().split())
        expected_words = set(expected_code.lower().split())

        if not expected_words:
            return 0.5

        overlap = len(actual_words & expected_words)
        total = len(expected_words)

        return overlap / total if total > 0 else 0.0

    def _extract_code(self, text: str) -> str:
        """Extract code from markdown if present."""
        match = re.search(r"```python\n(.*?)```", text, re.DOTALL)
        if match:
            return match.group(1)
        return text

    def _calculate_aggregate_metrics(self, results: List[EvaluationResult]) -> Dict[str, Any]:
        """Calculate aggregate metrics from all results."""
        if not results:
            return {}

        total = len(results)
        passed = sum(1 for r in results if r.passed)

        # Average scores
        avg_scores = {}
        for score_name in results[0].scores.keys():
            avg_scores[score_name] = sum(r.scores[score_name] for r in results) / total

        overall_avg = sum(r.overall_score for r in results) / total

        return {
            "total_examples": total,
            "passed": passed,
            "pass_rate": passed / total,
            "average_scores": avg_scores,
            "overall_average": overall_avg,
            "grade": self._assign_grade(overall_avg)
        }

    def _assign_grade(self, score: float) -> str:
        """Assign letter grade based on score."""
        if score >= 0.9:
            return "A"
        elif score >= 0.8:
            return "B"
        elif score >= 0.7:
            return "C"
        elif score >= 0.6:
            return "D"
        else:
            return "F"

    def _save_results(
        self,
        model_id: str,
        results: List[EvaluationResult],
        metrics: Dict[str, Any]
    ):
        """Save evaluation results to file."""
        output_file = self.output_dir / f"eval_{model_id.replace('/', '_')}.json"

        data = {
            "model_id": model_id,
            "metrics": metrics,
            "individual_results": [
                {
                    "example_id": r.example_id,
                    "prompt": r.prompt[:100] + "...",  # Truncate
                    "scores": r.scores,
                    "overall_score": r.overall_score,
                    "passed": r.passed
                }
                for r in results
            ]
        }

        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)

        logger.info(f"Saved evaluation results to {output_file}")

    def compare_models(self, model_ids: List[str], provider: str) -> Dict[str, Any]:
        """
        Compare multiple models.

        Args:
            model_ids: List of model IDs to compare
            provider: Provider name

        Returns:
            Comparison results
        """
        logger.info(f"Comparing {len(model_ids)} models...")

        comparisons = {}

        for model_id in model_ids:
            metrics = self.evaluate_model(model_id, provider, num_examples=50)
            comparisons[model_id] = metrics

        # Find best model
        best_model = max(
            comparisons.items(),
            key=lambda x: x[1].get('overall_average', 0)
        )

        return {
            "models": comparisons,
            "best_model": best_model[0],
            "best_score": best_model[1].get('overall_average', 0)
        }


def main():
    """Example usage."""
    metrics = QualityMetrics()

    # Evaluate a model
    # results = metrics.evaluate_model(
    #     model_id="ft:gpt-3.5-turbo:custom-model",
    #     provider="openai",
    #     num_examples=100
    # )
    # print(f"Evaluation results: {results}")


if __name__ == "__main__":
    main()
