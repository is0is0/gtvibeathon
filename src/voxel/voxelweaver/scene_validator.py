"""
Scene Validator - Quality assurance for generated 3D scenes.
Validates scene coherence, realism, and technical quality.
"""

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class ValidationLevel(str, Enum):
    """Validation strictness levels."""
    BASIC = "basic"  # Basic checks only
    STANDARD = "standard"  # Standard quality checks
    STRICT = "strict"  # Strict validation
    PRODUCTION = "production"  # Production-ready quality


class IssueLevel(str, Enum):
    """Issue severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class ValidationIssue:
    """A validation issue found in the scene."""
    category: str  # geometry, materials, lighting, etc.
    level: IssueLevel
    message: str
    object_name: Optional[str] = None
    suggestion: Optional[str] = None


class SceneValidator:
    """
    Validates generated 3D scenes for quality and coherence.
    """

    def __init__(self, validation_level: ValidationLevel = ValidationLevel.STANDARD):
        """
        Initialize scene validator.

        Args:
            validation_level: Level of validation strictness
        """
        self.validation_level = validation_level
        logger.info(f"SceneValidator initialized (level={validation_level.value})")

    def validate(self, scene_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate a scene.

        Args:
            scene_data: Scene metadata and configuration

        Returns:
            Validation results with issues and overall score
        """
        logger.info("Validating scene...")

        issues = []

        # Run validation checks
        issues.extend(self._validate_geometry(scene_data))
        issues.extend(self._validate_materials(scene_data))
        issues.extend(self._validate_lighting(scene_data))
        issues.extend(self._validate_proportions(scene_data))
        issues.extend(self._validate_coherence(scene_data))
        issues.extend(self._validate_technical(scene_data))

        # Calculate quality score
        quality_score = self._calculate_quality_score(issues)

        # Determine if scene passes
        passes = self._determine_pass(issues, quality_score)

        result = {
            "validated": True,
            "validation_level": self.validation_level.value,
            "passes": passes,
            "quality_score": quality_score,
            "issues_count": len(issues),
            "issues": [self._issue_to_dict(issue) for issue in issues],
            "critical_count": sum(1 for i in issues if i.level == IssueLevel.CRITICAL),
            "error_count": sum(1 for i in issues if i.level == IssueLevel.ERROR),
            "warning_count": sum(1 for i in issues if i.level == IssueLevel.WARNING),
            "recommendations": self._generate_recommendations(issues, scene_data)
        }

        logger.info(f"Validation complete. Score: {quality_score:.2f}, Passes: {passes}")

        return result

    def _validate_geometry(self, scene_data: Dict[str, Any]) -> List[ValidationIssue]:
        """Validate geometry-related aspects."""
        issues = []

        # Check if geometry hints exist
        geometry_hints = scene_data.get("geometry_hints", {})

        if not geometry_hints:
            issues.append(ValidationIssue(
                category="geometry",
                level=IssueLevel.WARNING,
                message="No geometry hints provided",
                suggestion="Add geometry guidance for better scene coherence"
            ))
        else:
            # Check vertex count
            total_verts = geometry_hints.get("total_vertex_estimate", 0)

            if total_verts > 5000000:
                issues.append(ValidationIssue(
                    category="geometry",
                    level=IssueLevel.ERROR,
                    message=f"Extremely high vertex count: {total_verts:,}",
                    suggestion="Reduce complexity or use instancing/LOD"
                ))
            elif total_verts > 1000000:
                issues.append(ValidationIssue(
                    category="geometry",
                    level=IssueLevel.WARNING,
                    message=f"High vertex count: {total_verts:,}",
                    suggestion="Consider optimizing geometry for better performance"
                ))

            # Check object count
            object_count = geometry_hints.get("objects_count", 0)

            if object_count < 1:
                issues.append(ValidationIssue(
                    category="geometry",
                    level=IssueLevel.CRITICAL,
                    message="No objects in scene",
                    suggestion="Scene must contain at least one object"
                ))
            elif object_count > 100:
                issues.append(ValidationIssue(
                    category="geometry",
                    level=IssueLevel.WARNING,
                    message=f"Very high object count: {object_count}",
                    suggestion="Consider using collections or instances"
                ))

        return issues

    def _validate_materials(self, scene_data: Dict[str, Any]) -> List[ValidationIssue]:
        """Validate material setup."""
        issues = []

        texture_suggestions = scene_data.get("texture_suggestions", {})

        if not texture_suggestions:
            issues.append(ValidationIssue(
                category="materials",
                level=IssueLevel.INFO,
                message="No material suggestions provided",
                suggestion="Add material guidance for better visual quality"
            ))
        else:
            materials = texture_suggestions.get("materials", [])

            if not materials:
                issues.append(ValidationIssue(
                    category="materials",
                    level=IssueLevel.WARNING,
                    message="No materials defined",
                    suggestion="Add at least basic materials to objects"
                ))

            # Check for mixed material types
            material_types = set()
            for mat in materials:
                mat_type = mat.get("material_type")
                if mat_type:
                    material_types.add(mat_type)

            if "glass" in material_types:
                issues.append(ValidationIssue(
                    category="materials",
                    level=IssueLevel.INFO,
                    message="Glass materials detected",
                    suggestion="Ensure caustics are enabled for realistic glass rendering"
                ))

        return issues

    def _validate_lighting(self, scene_data: Dict[str, Any]) -> List[ValidationIssue]:
        """Validate lighting setup."""
        issues = []

        lighting_config = scene_data.get("lighting_config", {})

        if not lighting_config:
            issues.append(ValidationIssue(
                category="lighting",
                level=IssueLevel.ERROR,
                message="No lighting configuration",
                suggestion="Add lighting setup for proper scene illumination"
            ))
        else:
            lights = lighting_config.get("lights", [])

            if not lights:
                issues.append(ValidationIssue(
                    category="lighting",
                    level=IssueLevel.ERROR,
                    message="No lights in scene",
                    suggestion="Add at least one light source"
                ))
            elif len(lights) < 2:
                issues.append(ValidationIssue(
                    category="lighting",
                    level=IssueLevel.WARNING,
                    message="Only one light source",
                    suggestion="Consider adding fill/rim lights for better illumination"
                ))

            # Check for ambient lighting
            ambient = lighting_config.get("ambient", {})
            if not ambient or not ambient.get("enabled"):
                issues.append(ValidationIssue(
                    category="lighting",
                    level=IssueLevel.INFO,
                    message="No ambient lighting",
                    suggestion="Add ambient/environment lighting for realism"
                ))

        return issues

    def _validate_proportions(self, scene_data: Dict[str, Any]) -> List[ValidationIssue]:
        """Validate object proportions."""
        issues = []

        proportions = scene_data.get("proportions", {})

        if not proportions:
            issues.append(ValidationIssue(
                category="proportions",
                level=IssueLevel.WARNING,
                message="No proportion analysis available",
                suggestion="Add proportion validation for realistic scaling"
            ))
        else:
            realism_score = proportions.get("realism_score", 0.5)

            if realism_score < 0.5:
                issues.append(ValidationIssue(
                    category="proportions",
                    level=IssueLevel.ERROR,
                    message=f"Low realism score: {realism_score:.2f}",
                    suggestion="Review object dimensions for real-world accuracy"
                ))
            elif realism_score < 0.7:
                issues.append(ValidationIssue(
                    category="proportions",
                    level=IssueLevel.WARNING,
                    message=f"Below standard realism: {realism_score:.2f}",
                    suggestion="Adjust object proportions to match references"
                ))

            # Check for proportion issues
            proportion_issues = proportions.get("issues", [])
            for issue_msg in proportion_issues[:5]:  # Top 5 issues
                issues.append(ValidationIssue(
                    category="proportions",
                    level=IssueLevel.INFO,
                    message=issue_msg
                ))

        return issues

    def _validate_coherence(self, scene_data: Dict[str, Any]) -> List[ValidationIssue]:
        """Validate overall scene coherence."""
        issues = []

        coherence_score = scene_data.get("coherence_score", 0.0)

        if coherence_score < 0.5:
            issues.append(ValidationIssue(
                category="coherence",
                level=IssueLevel.ERROR,
                message=f"Low coherence score: {coherence_score:.2f}",
                suggestion="Review VoxelWeaver processing for better scene integration"
            ))
        elif coherence_score < 0.7:
            issues.append(ValidationIssue(
                category="coherence",
                level=IssueLevel.WARNING,
                message=f"Below standard coherence: {coherence_score:.2f}",
                suggestion="Improve scene element integration"
            ))

        # Check for references
        references = scene_data.get("references", [])
        if not references and scene_data.get("config", {}).get("search_references"):
            issues.append(ValidationIssue(
                category="coherence",
                level=IssueLevel.INFO,
                message="No external references found",
                suggestion="Enable reference search for better quality"
            ))

        return issues

    def _validate_technical(self, scene_data: Dict[str, Any]) -> List[ValidationIssue]:
        """Validate technical aspects."""
        issues = []

        config = scene_data.get("config", {})

        # Check voxel resolution
        voxel_res = config.get("voxel_resolution")
        if voxel_res:
            if voxel_res < 0.001:
                issues.append(ValidationIssue(
                    category="technical",
                    level=IssueLevel.WARNING,
                    message=f"Extremely fine voxel resolution: {voxel_res}m",
                    suggestion="May cause performance issues"
                ))
            elif voxel_res > 1.0:
                issues.append(ValidationIssue(
                    category="technical",
                    level=IssueLevel.WARNING,
                    message=f"Very coarse voxel resolution: {voxel_res}m",
                    suggestion="May result in blocky geometry"
                ))

        # Check for validation being enabled
        if not config.get("validate_scene", True):
            issues.append(ValidationIssue(
                category="technical",
                level=IssueLevel.INFO,
                message="Scene validation was disabled in config",
                suggestion="Enable validation for quality assurance"
            ))

        return issues

    def _calculate_quality_score(self, issues: List[ValidationIssue]) -> float:
        """Calculate overall quality score from issues."""
        if not issues:
            return 1.0

        # Penalty weights
        penalties = {
            IssueLevel.CRITICAL: 0.3,
            IssueLevel.ERROR: 0.15,
            IssueLevel.WARNING: 0.05,
            IssueLevel.INFO: 0.01
        }

        total_penalty = 0.0
        for issue in issues:
            total_penalty += penalties.get(issue.level, 0.0)

        score = max(0.0, 1.0 - total_penalty)

        return round(score, 2)

    def _determine_pass(self, issues: List[ValidationIssue], quality_score: float) -> bool:
        """Determine if scene passes validation."""
        # Critical issues always fail
        if any(i.level == IssueLevel.CRITICAL for i in issues):
            return False

        # Level-based thresholds
        thresholds = {
            ValidationLevel.BASIC: 0.3,
            ValidationLevel.STANDARD: 0.6,
            ValidationLevel.STRICT: 0.8,
            ValidationLevel.PRODUCTION: 0.9
        }

        threshold = thresholds.get(self.validation_level, 0.6)

        return quality_score >= threshold

    def _generate_recommendations(
        self,
        issues: List[ValidationIssue],
        scene_data: Dict[str, Any]
    ) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []

        # Collect suggestions from issues
        for issue in issues:
            if issue.suggestion and issue.suggestion not in recommendations:
                recommendations.append(issue.suggestion)

        # Add general recommendations
        if scene_data.get("coherence_score", 0) < 0.8:
            recommendations.append("Use VoxelWeaver reference search for improved coherence")

        return recommendations[:10]  # Top 10 recommendations

    def _issue_to_dict(self, issue: ValidationIssue) -> Dict[str, Any]:
        """Convert ValidationIssue to dictionary."""
        return {
            "category": issue.category,
            "level": issue.level.value,
            "message": issue.message,
            "object_name": issue.object_name,
            "suggestion": issue.suggestion
        }

    def quick_check(self, scene_data: Dict[str, Any]) -> bool:
        """Quick pass/fail check without detailed validation."""
        # Must have objects
        if not scene_data.get("geometry_hints", {}).get("objects_count", 0):
            return False

        # Must have lighting
        if not scene_data.get("lighting_config", {}).get("lights"):
            return False

        # Must have decent coherence
        if scene_data.get("coherence_score", 0) < 0.5:
            return False

        return True
