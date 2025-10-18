"""
Scene Validator Module
----------------------
Performs quality assurance checks on generated scenes.

This module validates scene correctness, checks for overlaps, ensures proper
naming conventions, validates lighting exposure, and generates quality reports.
"""

import logging
import numpy as np
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)


class ValidationSeverity(Enum):
    """Severity levels for validation issues."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ValidationCategory(Enum):
    """Categories of validation checks."""
    GEOMETRY = "geometry"
    NAMING = "naming"
    LIGHTING = "lighting"
    MATERIALS = "materials"
    HIERARCHY = "hierarchy"
    PERFORMANCE = "performance"


@dataclass
class ValidationIssue:
    """Represents a validation issue."""
    severity: ValidationSeverity
    category: ValidationCategory
    message: str
    object_name: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'severity': self.severity.value,
            'category': self.category.value,
            'message': self.message,
            'object': self.object_name,
            'details': self.details
        }


@dataclass
class ValidationReport:
    """Complete validation report."""
    timestamp: datetime
    status: str  # 'pass', 'warning', 'fail'
    total_issues: int
    issues_by_severity: Dict[str, int]
    issues_by_category: Dict[str, int]
    issues: List[ValidationIssue]
    scene_statistics: Dict[str, Any]
    recommendations: List[str]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'timestamp': self.timestamp.isoformat(),
            'status': self.status,
            'total_issues': self.total_issues,
            'issues_by_severity': self.issues_by_severity,
            'issues_by_category': self.issues_by_category,
            'issues': [issue.to_dict() for issue in self.issues],
            'statistics': self.scene_statistics,
            'recommendations': self.recommendations
        }


class SceneValidator:
    """
    Performs quality assurance checks on generated scenes.

    This class validates scene data for correctness, quality, and best
    practices, generating detailed reports with issues and recommendations.

    Example:
        >>> validator = SceneValidator()
        >>> scene = {"objects": [...], "lighting": {...}}
        >>> result = validator.check(scene)
        >>> print(f"Status: {result['status']}")
    """

    def __init__(
        self,
        strict_naming: bool = True,
        max_overlap_volume: float = 0.001,
        min_lighting_exposure: float = 0.1,
        max_lighting_exposure: float = 10.0
    ):
        """
        Initialize scene validator.

        Args:
            strict_naming: Whether to enforce strict naming conventions
            max_overlap_volume: Maximum allowed overlap volume (m³)
            min_lighting_exposure: Minimum lighting exposure
            max_lighting_exposure: Maximum lighting exposure
        """
        self.strict_naming = strict_naming
        self.max_overlap_volume = max_overlap_volume
        self.min_lighting_exposure = min_lighting_exposure
        self.max_lighting_exposure = max_lighting_exposure

        # Naming convention rules
        self.naming_rules = {
            'allowed_chars': 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_',
            'max_length': 64,
            'min_length': 1,
            'reserved_names': ['temp', 'tmp', 'test', 'debug']
        }

        # Performance thresholds
        self.performance_thresholds = {
            'max_vertices_per_object': 100000,
            'max_faces_per_object': 50000,
            'max_objects': 1000,
            'max_lights': 20,
            'max_materials': 100
        }

        logger.info("SceneValidator initialized")

    def check(
        self,
        scene: Dict[str, Any],
        strict: bool = False
    ) -> Dict[str, Any]:
        """
        Validate a scene and generate quality report.

        This is the main entry point for scene validation. It performs
        comprehensive checks and returns a detailed report.

        Args:
            scene: Scene data to validate
            strict: Whether to use strict validation (fails on warnings)

        Returns:
            Dictionary containing:
                - status: 'pass', 'warning', or 'fail'
                - scene: Validated scene data
                - report: Detailed validation report
                - fixed_issues: List of auto-fixed issues

        Example:
            >>> validator = SceneValidator()
            >>> result = validator.check(scene_data)
            >>> if result['status'] == 'pass':
            ...     print("Scene is valid")
        """
        logger.info("Starting scene validation")

        issues: List[ValidationIssue] = []
        fixed_issues: List[str] = []

        # Validate objects
        if 'objects' in scene:
            object_issues = self._validate_objects(scene['objects'])
            issues.extend(object_issues)

        # Check for overlaps
        overlap_issues = self._check_overlaps(scene.get('objects', []))
        issues.extend(overlap_issues)

        # Validate naming
        naming_issues = self._validate_naming(scene.get('objects', []))
        issues.extend(naming_issues)

        # Validate lighting
        if 'lighting' in scene:
            lighting_issues = self._validate_lighting(scene['lighting'], scene.get('objects', []))
            issues.extend(lighting_issues)

        # Validate materials
        material_issues = self._validate_materials(scene.get('objects', []))
        issues.extend(material_issues)

        # Validate hierarchy
        hierarchy_issues = self._validate_hierarchy(scene.get('objects', []))
        issues.extend(hierarchy_issues)

        # Check performance
        performance_issues = self._check_performance(scene)
        issues.extend(performance_issues)

        # Generate statistics
        statistics = self._collect_statistics(scene)

        # Categorize issues
        issues_by_severity = {severity.value: 0 for severity in ValidationSeverity}
        issues_by_category = {category.value: 0 for category in ValidationCategory}

        for issue in issues:
            issues_by_severity[issue.severity.value] += 1
            issues_by_category[issue.category.value] += 1

        # Determine status
        has_critical = issues_by_severity[ValidationSeverity.CRITICAL.value] > 0
        has_errors = issues_by_severity[ValidationSeverity.ERROR.value] > 0
        has_warnings = issues_by_severity[ValidationSeverity.WARNING.value] > 0

        if has_critical or has_errors:
            status = 'fail'
        elif has_warnings and strict:
            status = 'fail'
        elif has_warnings:
            status = 'warning'
        else:
            status = 'pass'

        # Generate recommendations
        recommendations = self._generate_recommendations(issues, statistics)

        # Create report
        report = ValidationReport(
            timestamp=datetime.now(),
            status=status,
            total_issues=len(issues),
            issues_by_severity=issues_by_severity,
            issues_by_category=issues_by_category,
            issues=issues,
            scene_statistics=statistics,
            recommendations=recommendations
        )

        logger.info(f"Validation complete: {status} ({len(issues)} issues)")

        return {
            'status': status,
            'scene': scene,
            'report': report.to_dict(),
            'fixed_issues': fixed_issues
        }

    def _validate_objects(self, objects: List[Dict[str, Any]]) -> List[ValidationIssue]:
        """Validate object geometry and properties."""
        issues = []

        for obj in objects:
            name = obj.get('name', 'unnamed')

            # Check for vertices
            vertices = obj.get('vertices')
            if vertices is None or len(vertices) == 0:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    category=ValidationCategory.GEOMETRY,
                    message="Object has no vertices",
                    object_name=name
                ))

            # Check for faces
            faces = obj.get('faces')
            if faces is None or len(faces) == 0:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    category=ValidationCategory.GEOMETRY,
                    message="Object has no faces",
                    object_name=name
                ))

            # Check vertex/face counts
            if vertices is not None:
                vertex_count = len(vertices)
                if vertex_count > self.performance_thresholds['max_vertices_per_object']:
                    issues.append(ValidationIssue(
                        severity=ValidationSeverity.WARNING,
                        category=ValidationCategory.PERFORMANCE,
                        message=f"High vertex count: {vertex_count}",
                        object_name=name,
                        details={'vertex_count': vertex_count}
                    ))

            if faces is not None:
                face_count = len(faces)
                if face_count > self.performance_thresholds['max_faces_per_object']:
                    issues.append(ValidationIssue(
                        severity=ValidationSeverity.WARNING,
                        category=ValidationCategory.PERFORMANCE,
                        message=f"High face count: {face_count}",
                        object_name=name,
                        details={'face_count': face_count}
                    ))

            # Check for degenerate geometry
            if vertices is not None and faces is not None:
                degenerate = self._check_degenerate_geometry(vertices, faces)
                if degenerate:
                    issues.append(ValidationIssue(
                        severity=ValidationSeverity.WARNING,
                        category=ValidationCategory.GEOMETRY,
                        message="Object contains degenerate faces",
                        object_name=name,
                        details={'degenerate_faces': len(degenerate)}
                    ))

        return issues

    def _check_overlaps(self, objects: List[Dict[str, Any]]) -> List[ValidationIssue]:
        """Check for object overlaps and collisions."""
        issues = []

        for i, obj1 in enumerate(objects):
            bbox1 = obj1.get('bounding_box')
            if not bbox1:
                continue

            for obj2 in objects[i + 1:]:
                bbox2 = obj2.get('bounding_box')
                if not bbox2:
                    continue

                # Check intersection
                overlap_volume = self._calculate_overlap_volume(bbox1, bbox2)

                if overlap_volume > self.max_overlap_volume:
                    issues.append(ValidationIssue(
                        severity=ValidationSeverity.WARNING,
                        category=ValidationCategory.GEOMETRY,
                        message=f"Objects overlap: {obj1.get('name')} <-> {obj2.get('name')}",
                        object_name=obj1.get('name'),
                        details={
                            'object1': obj1.get('name'),
                            'object2': obj2.get('name'),
                            'overlap_volume': overlap_volume
                        }
                    ))

        return issues

    def _calculate_overlap_volume(
        self,
        bbox1: Dict[str, Any],
        bbox2: Dict[str, Any]
    ) -> float:
        """Calculate volume of overlap between two bounding boxes."""
        min1 = np.array(bbox1.get('min', [0, 0, 0]))
        max1 = np.array(bbox1.get('max', [1, 1, 1]))
        min2 = np.array(bbox2.get('min', [0, 0, 0]))
        max2 = np.array(bbox2.get('max', [1, 1, 1]))

        overlap_min = np.maximum(min1, min2)
        overlap_max = np.minimum(max1, max2)

        overlap_size = overlap_max - overlap_min

        if np.all(overlap_size > 0):
            return float(np.prod(overlap_size))

        return 0.0

    def _validate_naming(self, objects: List[Dict[str, Any]]) -> List[ValidationIssue]:
        """Validate object naming conventions."""
        issues = []
        seen_names: Set[str] = set()

        for obj in objects:
            name = obj.get('name', '')

            # Check if name exists
            if not name:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    category=ValidationCategory.NAMING,
                    message="Object has no name",
                    object_name=None
                ))
                continue

            # Check for duplicates
            if name in seen_names:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    category=ValidationCategory.NAMING,
                    message=f"Duplicate object name: {name}",
                    object_name=name
                ))

            seen_names.add(name)

            if self.strict_naming:
                # Check length
                if len(name) < self.naming_rules['min_length']:
                    issues.append(ValidationIssue(
                        severity=ValidationSeverity.WARNING,
                        category=ValidationCategory.NAMING,
                        message=f"Name too short: {name}",
                        object_name=name
                    ))

                if len(name) > self.naming_rules['max_length']:
                    issues.append(ValidationIssue(
                        severity=ValidationSeverity.WARNING,
                        category=ValidationCategory.NAMING,
                        message=f"Name too long: {name}",
                        object_name=name
                    ))

                # Check allowed characters
                for char in name:
                    if char not in self.naming_rules['allowed_chars']:
                        issues.append(ValidationIssue(
                            severity=ValidationSeverity.WARNING,
                            category=ValidationCategory.NAMING,
                            message=f"Invalid character in name: {char}",
                            object_name=name
                        ))
                        break

                # Check reserved names
                if name.lower() in self.naming_rules['reserved_names']:
                    issues.append(ValidationIssue(
                        severity=ValidationSeverity.WARNING,
                        category=ValidationCategory.NAMING,
                        message=f"Reserved name used: {name}",
                        object_name=name
                    ))

        return issues

    def _validate_lighting(
        self,
        lighting: Dict[str, Any],
        objects: List[Dict[str, Any]]
    ) -> List[ValidationIssue]:
        """Validate lighting setup and exposure."""
        issues = []

        lights = lighting.get('lights', [])

        # Check if scene has lights
        if not lights:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                category=ValidationCategory.LIGHTING,
                message="Scene has no lights"
            ))

        # Check light count
        if len(lights) > self.performance_thresholds['max_lights']:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                category=ValidationCategory.PERFORMANCE,
                message=f"Too many lights: {len(lights)}",
                details={'light_count': len(lights)}
            ))

        # Validate individual lights
        for i, light in enumerate(lights):
            name = light.get('name', f'Light_{i}')

            # Check energy/exposure
            energy = light.get('energy', 0)

            if energy < self.min_lighting_exposure:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    category=ValidationCategory.LIGHTING,
                    message=f"Light energy too low: {energy}",
                    object_name=name,
                    details={'energy': energy}
                ))

            if energy > self.max_lighting_exposure * 100:  # Adjusted threshold for lights
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    category=ValidationCategory.LIGHTING,
                    message=f"Light energy very high: {energy}",
                    object_name=name,
                    details={'energy': energy}
                ))

            # Check color validity
            color = light.get('color', [1, 1, 1])
            if not self._validate_color(color):
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    category=ValidationCategory.LIGHTING,
                    message=f"Invalid light color: {color}",
                    object_name=name
                ))

        # Check overall exposure
        total_exposure = sum(light.get('energy', 0) for light in lights)
        avg_exposure = total_exposure / len(lights) if lights else 0

        if avg_exposure < self.min_lighting_exposure:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                category=ValidationCategory.LIGHTING,
                message="Scene may be underexposed",
                details={'average_exposure': avg_exposure}
            ))

        return issues

    def _validate_materials(self, objects: List[Dict[str, Any]]) -> List[ValidationIssue]:
        """Validate materials and textures."""
        issues = []
        material_count = 0

        for obj in objects:
            name = obj.get('name', 'unnamed')
            material = obj.get('material')

            if not material:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.INFO,
                    category=ValidationCategory.MATERIALS,
                    message="Object has no material",
                    object_name=name
                ))
                continue

            material_count += 1

            # Validate material properties
            props = material.get('properties', {})

            # Check color validity
            base_color = props.get('base_color')
            if base_color and not self._validate_color(base_color):
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    category=ValidationCategory.MATERIALS,
                    message=f"Invalid base color: {base_color}",
                    object_name=name
                ))

            # Check value ranges
            metallic = props.get('metallic', 0)
            if not 0 <= metallic <= 1:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    category=ValidationCategory.MATERIALS,
                    message=f"Metallic value out of range: {metallic}",
                    object_name=name
                ))

            roughness = props.get('roughness', 0.5)
            if not 0 <= roughness <= 1:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    category=ValidationCategory.MATERIALS,
                    message=f"Roughness value out of range: {roughness}",
                    object_name=name
                ))

        # Check total material count
        if material_count > self.performance_thresholds['max_materials']:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                category=ValidationCategory.PERFORMANCE,
                message=f"Too many materials: {material_count}",
                details={'material_count': material_count}
            ))

        return issues

    def _validate_hierarchy(self, objects: List[Dict[str, Any]]) -> List[ValidationIssue]:
        """Validate scene hierarchy."""
        issues = []

        # Check for hierarchy information
        has_hierarchy = any('hierarchy' in obj for obj in objects)

        if not has_hierarchy:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.INFO,
                category=ValidationCategory.HIERARCHY,
                message="Scene has no hierarchy information"
            ))

        return issues

    def _check_performance(self, scene: Dict[str, Any]) -> List[ValidationIssue]:
        """Check scene performance characteristics."""
        issues = []

        objects = scene.get('objects', [])

        # Check total object count
        if len(objects) > self.performance_thresholds['max_objects']:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                category=ValidationCategory.PERFORMANCE,
                message=f"Very high object count: {len(objects)}",
                details={'object_count': len(objects)}
            ))

        # Calculate total geometry
        total_vertices = 0
        total_faces = 0

        for obj in objects:
            vertices = obj.get('vertices', [])
            faces = obj.get('faces', [])

            total_vertices += len(vertices) if vertices else 0
            total_faces += len(faces) if faces else 0

        # Check totals
        if total_vertices > 1000000:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                category=ValidationCategory.PERFORMANCE,
                message=f"Very high total vertex count: {total_vertices}",
                details={'total_vertices': total_vertices}
            ))

        if total_faces > 500000:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                category=ValidationCategory.PERFORMANCE,
                message=f"Very high total face count: {total_faces}",
                details={'total_faces': total_faces}
            ))

        return issues

    def _check_degenerate_geometry(
        self,
        vertices: Any,
        faces: Any
    ) -> List[int]:
        """Check for degenerate faces."""
        if not isinstance(vertices, np.ndarray):
            vertices = np.array(vertices)
        if not isinstance(faces, np.ndarray):
            faces = np.array(faces)

        degenerate_faces = []

        for i, face in enumerate(faces):
            # Check for duplicate vertices in face
            if len(face) != len(set(face)):
                degenerate_faces.append(i)

        return degenerate_faces

    def _validate_color(self, color: Any) -> bool:
        """Validate color value."""
        if not isinstance(color, (list, tuple)):
            return False

        if len(color) not in [3, 4]:
            return False

        return all(0 <= c <= 1 for c in color)

    def _collect_statistics(self, scene: Dict[str, Any]) -> Dict[str, Any]:
        """Collect scene statistics."""
        objects = scene.get('objects', [])
        lighting = scene.get('lighting', {})

        total_vertices = sum(len(obj.get('vertices', [])) for obj in objects)
        total_faces = sum(len(obj.get('faces', [])) for obj in objects)

        return {
            'object_count': len(objects),
            'total_vertices': total_vertices,
            'total_faces': total_faces,
            'light_count': len(lighting.get('lights', [])),
            'material_count': sum(1 for obj in objects if 'material' in obj),
            'has_hdri': lighting.get('hdri', {}).get('path') is not None,
            'has_hierarchy': any('hierarchy' in obj for obj in objects)
        }

    def _generate_recommendations(
        self,
        issues: List[ValidationIssue],
        statistics: Dict[str, Any]
    ) -> List[str]:
        """Generate recommendations based on issues and statistics."""
        recommendations = []

        # Check for common patterns
        error_count = sum(1 for issue in issues if issue.severity == ValidationSeverity.ERROR)
        warning_count = sum(1 for issue in issues if issue.severity == ValidationSeverity.WARNING)

        if error_count > 0:
            recommendations.append("Fix all errors before exporting the scene")

        if warning_count > 5:
            recommendations.append("Consider addressing warnings to improve scene quality")

        # Performance recommendations
        if statistics['total_vertices'] > 500000:
            recommendations.append("Consider optimizing meshes to reduce vertex count")

        if statistics['light_count'] > 10:
            recommendations.append("High light count may impact render performance")

        # Quality recommendations
        if not statistics['has_hdri']:
            recommendations.append("Consider adding HDRI environment for realistic lighting")

        if statistics['material_count'] < statistics['object_count'] * 0.5:
            recommendations.append("Many objects are missing materials")

        return recommendations


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    validator = SceneValidator(
        strict_naming=True,
        max_overlap_volume=0.001
    )

    # Create test scene
    test_scene = {
        "objects": [
            {
                "name": "table",
                "vertices": np.random.rand(100, 3).tolist(),
                "faces": np.random.randint(0, 100, (50, 3)).tolist(),
                "bounding_box": {
                    "min": [0, 0, 0],
                    "max": [1.2, 0.75, 0.8]
                },
                "material": {
                    "properties": {
                        "base_color": [0.6, 0.4, 0.3, 1.0],
                        "metallic": 0.0,
                        "roughness": 0.7
                    }
                }
            },
            {
                "name": "chair",
                "vertices": np.random.rand(80, 3).tolist(),
                "faces": np.random.randint(0, 80, (40, 3)).tolist(),
                "bounding_box": {
                    "min": [2, 0, 0],
                    "max": [2.5, 0.85, 0.5]
                },
                "material": {
                    "properties": {
                        "base_color": [0.5, 0.5, 0.5, 1.0],
                        "metallic": 0.2,
                        "roughness": 0.5
                    }
                }
            }
        ],
        "lighting": {
            "lights": [
                {
                    "name": "Sun",
                    "type": "SUN",
                    "energy": 5.0,
                    "color": [1.0, 1.0, 1.0]
                },
                {
                    "name": "Fill",
                    "type": "AREA",
                    "energy": 100.0,
                    "color": [1.0, 0.9, 0.8]
                }
            ],
            "hdri": {
                "path": "outdoor.hdr",
                "strength": 1.0
            }
        }
    }

    # Validate scene
    print("="*60)
    print("Validating test scene")
    print("="*60)

    result = validator.check(test_scene)

    print(f"\nValidation Status: {result['status'].upper()}")
    print(f"Total Issues: {result['report']['total_issues']}")

    print(f"\nIssues by Severity:")
    for severity, count in result['report']['issues_by_severity'].items():
        if count > 0:
            print(f"  {severity.upper()}: {count}")

    print(f"\nIssues by Category:")
    for category, count in result['report']['issues_by_category'].items():
        if count > 0:
            print(f"  {category.upper()}: {count}")

    print(f"\nScene Statistics:")
    for key, value in result['report']['statistics'].items():
        print(f"  {key}: {value}")

    if result['report']['issues']:
        print(f"\nIssues:")
        for issue in result['report']['issues'][:10]:  # Show first 10
            print(f"  [{issue['severity'].upper()}] {issue['message']}")
            if issue['object']:
                print(f"    Object: {issue['object']}")

    if result['report']['recommendations']:
        print(f"\nRecommendations:")
        for rec in result['report']['recommendations']:
            print(f"  - {rec}")
