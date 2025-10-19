"""
Proportion Analyzer - Ensures realistic real-world proportions in generated scenes.
Validates scale relationships and suggests corrections for coherence.
"""

import re
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ProportionCheck:
    """Result of a proportion check."""
    object_name: str
    estimated_size: Dict[str, float]  # width, height, depth in meters
    reference_size: Optional[Dict[str, float]]  # real-world reference
    realism_score: float  # 0.0 to 1.0
    issues: List[str]
    suggestions: List[str]


class ProportionAnalyzer:
    """
    Analyzes scene concepts for realistic proportions and scale relationships.
    Ensures objects maintain real-world scale ratios.
    """

    # Real-world scale references (meters)
    SCALE_REFERENCES = {
        # Humans and animals
        "human": {"height": 1.75, "width": 0.5},
        "adult": {"height": 1.75, "width": 0.5},
        "child": {"height": 1.2, "width": 0.35},
        "baby": {"height": 0.7, "width": 0.3},
        "dog": {"height": 0.6, "length": 0.8},
        "cat": {"height": 0.25, "length": 0.45},
        "bird": {"height": 0.15, "wingspan": 0.3},
        "horse": {"height": 1.6, "length": 2.4},

        # Furniture
        "chair": {"height": 0.9, "width": 0.5, "depth": 0.5},
        "table": {"height": 0.75, "width": 1.2, "depth": 0.8},
        "desk": {"height": 0.75, "width": 1.4, "depth": 0.7},
        "sofa": {"height": 0.85, "width": 2.0, "depth": 0.9},
        "bed": {"height": 0.6, "width": 1.5, "length": 2.0},
        "shelf": {"height": 2.0, "width": 1.0, "depth": 0.3},
        "cabinet": {"height": 1.8, "width": 0.8, "depth": 0.5},

        # Architecture
        "door": {"height": 2.1, "width": 0.9, "thickness": 0.05},
        "window": {"height": 1.5, "width": 1.2},
        "room": {"height": 2.7, "width": 4.0, "length": 5.0},
        "ceiling": {"height": 2.7},
        "wall": {"height": 2.7, "thickness": 0.15},
        "floor": {"thickness": 0.05},
        "stair": {"height": 0.18, "depth": 0.28},  # per step

        # Vehicles
        "car": {"height": 1.5, "width": 1.8, "length": 4.5},
        "truck": {"height": 2.5, "width": 2.5, "length": 6.0},
        "bicycle": {"height": 1.1, "width": 0.6, "length": 1.8},
        "motorcycle": {"height": 1.2, "width": 0.8, "length": 2.2},

        # Nature
        "tree": {"height": 8.0, "width": 2.0},
        "small_tree": {"height": 3.0, "width": 1.5},
        "bush": {"height": 1.2, "width": 1.0},
        "grass": {"height": 0.05},
        "flower": {"height": 0.3, "width": 0.1},

        # Objects
        "cup": {"height": 0.1, "diameter": 0.08},
        "glass": {"height": 0.15, "diameter": 0.07},
        "bottle": {"height": 0.25, "diameter": 0.07},
        "plate": {"height": 0.02, "diameter": 0.25},
        "bowl": {"height": 0.08, "diameter": 0.15},
        "book": {"height": 0.23, "width": 0.15, "thickness": 0.03},
        "laptop": {"height": 0.02, "width": 0.35, "depth": 0.24},
        "monitor": {"height": 0.4, "width": 0.6, "depth": 0.05},
        "phone": {"height": 0.15, "width": 0.07, "depth": 0.008},
        "lamp": {"height": 0.5, "width": 0.3},
    }

    # Proportion ratios (for validation)
    PROPORTION_RATIOS = {
        # Height to width ratios
        "human": {"height_to_width": 3.5},  # 1.75m / 0.5m
        "door": {"height_to_width": 2.3},   # 2.1m / 0.9m
        "chair": {"height_to_width": 1.8},  # 0.9m / 0.5m
        "table": {"height_to_width": 0.625},  # 0.75m / 1.2m
    }

    def __init__(self):
        """Initialize the proportion analyzer."""
        logger.info("ProportionAnalyzer initialized")

    def analyze_concept(self, concept: str) -> Dict[str, Any]:
        """
        Analyze a scene concept for proportion issues.

        Args:
            concept: Scene concept description

        Returns:
            Analysis results with realism scores and suggestions
        """
        logger.info("Analyzing proportions in concept...")

        # Extract objects and their described dimensions
        objects = self._extract_objects_with_dimensions(concept)

        # Check each object against references
        checks = []
        for obj in objects:
            check = self._check_object_proportions(obj, concept)
            checks.append(check)

        # Calculate overall realism score
        realism_score = self._calculate_realism_score(checks)

        # Find scale relationships
        relationships = self._analyze_scale_relationships(objects, concept)

        result = {
            "objects_analyzed": len(objects),
            "proportion_checks": [self._check_to_dict(c) for c in checks],
            "realism_score": realism_score,
            "scale_relationships": relationships,
            "issues": self._collect_issues(checks),
            "suggestions": self._collect_suggestions(checks)
        }

        logger.info(f"Proportion analysis complete. Realism score: {realism_score:.2f}")

        return result

    def _extract_objects_with_dimensions(self, concept: str) -> List[Dict[str, Any]]:
        """Extract object names and any mentioned dimensions from concept."""
        objects = []

        # Pattern to match dimensions (e.g., "1.2m tall", "0.5 meters wide")
        dimension_pattern = r'(\d+\.?\d*)\s*(m|meters?|cm|centimeters?|mm|millimeters?)\s*(tall|wide|high|deep|long)'

        # Extract known object types
        concept_lower = concept.lower()
        for obj_name in self.SCALE_REFERENCES.keys():
            if obj_name in concept_lower:
                # Find context around this object
                obj_context = self._get_object_context(concept_lower, obj_name)

                # Look for dimensions in context
                dimensions = {}
                matches = re.finditer(dimension_pattern, obj_context)
                for match in matches:
                    value = float(match.group(1))
                    unit = match.group(2)
                    dimension_type = match.group(3)

                    # Convert to meters
                    if unit in ['cm', 'centimeter', 'centimeters']:
                        value /= 100
                    elif unit in ['mm', 'millimeter', 'millimeters']:
                        value /= 1000

                    dimensions[dimension_type] = value

                objects.append({
                    "name": obj_name,
                    "mentioned_dimensions": dimensions,
                    "context": obj_context
                })

        return objects

    def _get_object_context(self, text: str, object_name: str, window: int = 100) -> str:
        """Get text context around an object mention."""
        idx = text.find(object_name)
        if idx == -1:
            return ""

        start = max(0, idx - window)
        end = min(len(text), idx + len(object_name) + window)
        return text[start:end]

    def _check_object_proportions(self, obj: Dict[str, Any], concept: str) -> ProportionCheck:
        """
        Check if object proportions are realistic.

        Args:
            obj: Object dictionary with name and dimensions
            concept: Full concept text

        Returns:
            ProportionCheck result
        """
        obj_name = obj["name"]
        mentioned_dims = obj.get("mentioned_dimensions", {})

        # Get reference dimensions
        reference = self.SCALE_REFERENCES.get(obj_name, {})

        # Estimate size based on reference or mentioned dimensions
        estimated = self._estimate_size(obj_name, mentioned_dims, reference)

        # Calculate realism score
        realism, issues, suggestions = self._calculate_realism(
            obj_name, estimated, reference, mentioned_dims
        )

        return ProportionCheck(
            object_name=obj_name,
            estimated_size=estimated,
            reference_size=reference if reference else None,
            realism_score=realism,
            issues=issues,
            suggestions=suggestions
        )

    def _estimate_size(
        self,
        obj_name: str,
        mentioned_dims: Dict[str, float],
        reference: Dict[str, float]
    ) -> Dict[str, float]:
        """Estimate object size combining references and mentions."""
        estimated = {}

        # Start with reference dimensions
        if reference:
            estimated.update(reference)

        # Override with mentioned dimensions
        # Map dimension types
        dim_map = {
            "tall": "height",
            "high": "height",
            "wide": "width",
            "deep": "depth",
            "long": "length"
        }

        for mention_type, value in mentioned_dims.items():
            dimension = dim_map.get(mention_type, mention_type)
            estimated[dimension] = value

        # If no dimensions, use defaults
        if not estimated:
            estimated = {"width": 1.0, "height": 1.0, "depth": 1.0}

        return estimated

    def _calculate_realism(
        self,
        obj_name: str,
        estimated: Dict[str, float],
        reference: Dict[str, float],
        mentioned: Dict[str, float]
    ) -> Tuple[float, List[str], List[str]]:
        """
        Calculate realism score and identify issues.

        Returns:
            (score, issues, suggestions)
        """
        score = 1.0
        issues = []
        suggestions = []

        # If no reference, give medium score
        if not reference:
            return 0.7, [], [f"No reference data for {obj_name}, using generic proportions"]

        # Check each dimension against reference
        for dim, ref_value in reference.items():
            if dim in estimated:
                est_value = estimated[dim]
                ratio = est_value / ref_value if ref_value > 0 else 1.0

                # Check if ratio is reasonable (within 0.5x to 2x)
                if ratio < 0.5:
                    score -= 0.2
                    issues.append(f"{obj_name} {dim} too small ({est_value:.2f}m vs reference {ref_value:.2f}m)")
                    suggestions.append(f"Consider increasing {obj_name} {dim} to ~{ref_value:.2f}m")
                elif ratio > 2.0:
                    score -= 0.2
                    issues.append(f"{obj_name} {dim} too large ({est_value:.2f}m vs reference {ref_value:.2f}m)")
                    suggestions.append(f"Consider decreasing {obj_name} {dim} to ~{ref_value:.2f}m")
                elif ratio < 0.8 or ratio > 1.2:
                    score -= 0.1
                    issues.append(f"{obj_name} {dim} slightly off scale (ratio: {ratio:.2f}x)")

        return max(0.0, min(1.0, score)), issues, suggestions

    def _calculate_realism_score(self, checks: List[ProportionCheck]) -> float:
        """Calculate overall realism score from all checks."""
        if not checks:
            return 0.5

        total = sum(c.realism_score for c in checks)
        return total / len(checks)

    def _analyze_scale_relationships(
        self,
        objects: List[Dict[str, Any]],
        concept: str
    ) -> List[Dict[str, Any]]:
        """
        Analyze scale relationships between objects.
        E.g., "Is the chair appropriately sized for a human?"
        """
        relationships = []

        # Common relationships to check
        pairs = [
            ("human", "chair"),
            ("human", "table"),
            ("human", "door"),
            ("chair", "table"),
            ("car", "human"),
        ]

        obj_names = [o["name"] for o in objects]

        for obj1, obj2 in pairs:
            if obj1 in obj_names and obj2 in obj_names:
                ref1 = self.SCALE_REFERENCES.get(obj1, {})
                ref2 = self.SCALE_REFERENCES.get(obj2, {})

                if ref1 and ref2:
                    relationship = self._check_relationship(obj1, obj2, ref1, ref2)
                    relationships.append(relationship)

        return relationships

    def _check_relationship(
        self,
        obj1: str,
        obj2: str,
        ref1: Dict[str, float],
        ref2: Dict[str, float]
    ) -> Dict[str, Any]:
        """Check scale relationship between two objects."""
        # Example: chair height should be ~50% of human height
        expected_ratios = {
            ("human", "chair"): ("height", "height", 0.51),  # ~0.9m / 1.75m
            ("human", "table"): ("height", "height", 0.43),  # ~0.75m / 1.75m
            ("chair", "table"): ("height", "height", 0.83),  # ~0.9m / 0.75m (chair to table)
        }

        result = {
            "object_1": obj1,
            "object_2": obj2,
            "relationship": f"{obj1} to {obj2}",
            "is_realistic": True,
            "notes": []
        }

        # Check if we have expected ratio
        key = (obj1, obj2)
        if key in expected_ratios:
            dim1, dim2, expected_ratio = expected_ratios[key]

            if dim1 in ref1 and dim2 in ref2:
                actual_ratio = ref1[dim1] / ref2[dim2]
                deviation = abs(actual_ratio - expected_ratio)

                if deviation > 0.2:
                    result["is_realistic"] = False
                    result["notes"].append(
                        f"Scale mismatch: {obj1} {dim1} to {obj2} {dim2} ratio is {actual_ratio:.2f}, "
                        f"expected ~{expected_ratio:.2f}"
                    )

        return result

    def _collect_issues(self, checks: List[ProportionCheck]) -> List[str]:
        """Collect all issues from checks."""
        issues = []
        for check in checks:
            issues.extend(check.issues)
        return issues

    def _collect_suggestions(self, checks: List[ProportionCheck]) -> List[str]:
        """Collect all suggestions from checks."""
        suggestions = []
        for check in checks:
            suggestions.extend(check.suggestions)
        return suggestions

    def _check_to_dict(self, check: ProportionCheck) -> Dict[str, Any]:
        """Convert ProportionCheck to dictionary."""
        return {
            "object_name": check.object_name,
            "estimated_size": check.estimated_size,
            "reference_size": check.reference_size,
            "realism_score": check.realism_score,
            "issues": check.issues,
            "suggestions": check.suggestions
        }

    def get_scale_factor(self, object_name: str, target_dimension: str) -> Optional[float]:
        """
        Get recommended scale factor for an object.

        Args:
            object_name: Name of the object
            target_dimension: Dimension to scale (height, width, etc.)

        Returns:
            Recommended size in meters
        """
        ref = self.SCALE_REFERENCES.get(object_name.lower())
        if ref and target_dimension in ref:
            return ref[target_dimension]
        return None
