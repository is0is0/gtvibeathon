"""
Spatial Validator
----------------
Physics-aware spatial validation and automatic correction.

Validates scene geometry for spacing, proportions, overlaps, and physics consistency.
Automatically fixes issues like floating objects, collisions, and improper spacing.
"""

import math
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class BoundingBox:
    """3D axis-aligned bounding box."""
    min_point: Tuple[float, float, float]  # (x, y, z) minimum corner
    max_point: Tuple[float, float, float]  # (x, y, z) maximum corner

    @property
    def center(self) -> Tuple[float, float, float]:
        """Calculate center point of bounding box."""
        return (
            (self.min_point[0] + self.max_point[0]) / 2,
            (self.min_point[1] + self.max_point[1]) / 2,
            (self.min_point[2] + self.max_point[2]) / 2
        )

    @property
    def size(self) -> Tuple[float, float, float]:
        """Calculate size (width, depth, height) of bounding box."""
        return (
            self.max_point[0] - self.min_point[0],
            self.max_point[1] - self.min_point[1],
            self.max_point[2] - self.min_point[2]
        )

    @property
    def volume(self) -> float:
        """Calculate volume of bounding box."""
        size = self.size
        return size[0] * size[1] * size[2]


@dataclass
class ValidationIssue:
    """Represents a validation issue found in the scene."""
    type: str  # 'overlap', 'floating', 'spacing', 'scale', 'alignment'
    severity: str  # 'error', 'warning', 'info'
    description: str
    objects_involved: List[str] = field(default_factory=list)
    suggested_fix: Optional[str] = None
    auto_fixable: bool = True


class SpatialValidator:
    """
    Physics-aware spatial validation system.

    Validates and automatically corrects:
    - Bounding box collisions between objects
    - Minimum spacing thresholds
    - Object grounding (no floating objects)
    - Scene center alignment
    - Proportional relationships
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize spatial validator.

        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}

        # Configuration parameters
        self.min_distance = self.config.get('min_distance', 0.1)  # Minimum object spacing
        self.ground_tolerance = self.config.get('ground_tolerance', 0.01)  # Tolerance for grounding
        self.auto_fix = self.config.get('auto_fix', True)  # Automatically fix issues
        self.max_iterations = self.config.get('max_iterations', 10)  # Max fix iterations

        # Validation results
        self.issues = []
        self.fixes_applied = []

        logger.info(f"Spatial Validator initialized (auto_fix: {self.auto_fix}, min_distance: {self.min_distance})")

    def check(self, scene_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check scene for spatial validation issues.

        Args:
            scene_data: Scene data with objects

        Returns:
            Validation report with issues found
        """
        logger.info("Checking scene spatial validity")

        self.issues = []
        objects = scene_data.get('objects', [])

        if not objects:
            logger.warning("No objects to validate")
            return self._create_report('valid', "No objects in scene")

        # Calculate bounding boxes
        bboxes = self._calculate_bounding_boxes(objects)

        # Run validation checks
        self._check_overlaps(objects, bboxes)
        self._check_spacing(objects, bboxes)
        self._check_grounding(objects, bboxes)
        self._check_alignment(objects, bboxes)
        self._check_scale_relationships(objects, bboxes)

        # Determine overall status
        error_count = sum(1 for issue in self.issues if issue.severity == 'error')
        warning_count = sum(1 for issue in self.issues if issue.severity == 'warning')

        if error_count > 0:
            status = 'invalid'
        elif warning_count > 0:
            status = 'warning'
        else:
            status = 'valid'

        report = self._create_report(status, f"Found {len(self.issues)} issues")

        logger.info(f"Validation complete: {status} ({len(self.issues)} issues)")

        return report

    def apply(self, scene_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and automatically fix spatial issues.

        Args:
            scene_data: Scene data with objects

        Returns:
            Scene data with fixes applied
        """
        logger.info("Applying spatial validation with auto-fix")

        objects = scene_data.get('objects', [])
        if not objects:
            logger.warning("No objects to fix")
            return scene_data

        self.fixes_applied = []

        # Run validation
        report = self.check(scene_data)

        # Apply fixes if enabled
        if self.auto_fix and self.issues:
            logger.info(f"Auto-fixing {len(self.issues)} issues")

            # Iterate until no more issues or max iterations reached
            for iteration in range(self.max_iterations):
                logger.debug(f"Fix iteration {iteration + 1}/{self.max_iterations}")

                # Apply fixes
                fixed_count = self._apply_fixes(objects)

                if fixed_count == 0:
                    logger.debug("No more fixes needed")
                    break

                # Re-validate
                report = self.check(scene_data)
                if report['status'] == 'valid':
                    logger.info("All issues resolved")
                    break

            logger.info(f"Applied {len(self.fixes_applied)} fixes")

        scene_data['validation'] = {
            'status': report['status'],
            'issues': len(self.issues),
            'fixes_applied': len(self.fixes_applied),
            'report': report
        }

        return scene_data

    def validate_positions(self, scene_objects: List[Dict[str, Any]]) -> bool:
        """
        Validate object positions for spacing and collisions.

        Args:
            scene_objects: List of scene objects

        Returns:
            True if all positions are valid, False otherwise

        Example:
            >>> validator = SpatialValidator()
            >>> objects = [{'name': 'cube1', 'vertices': [...]}, ...]
            >>> is_valid = validator.validate_positions(objects)
        """
        logger.info(f"Validating positions of {len(scene_objects)} objects")

        # Calculate bounding boxes
        bboxes = self._calculate_bounding_boxes(scene_objects)

        # Check for overlaps
        has_overlaps = False
        for i, obj1 in enumerate(scene_objects):
            for j, obj2 in enumerate(scene_objects[i+1:], start=i+1):
                if self._check_bbox_collision(bboxes[i], bboxes[j]):
                    logger.warning(f"Overlap detected: {obj1.get('name', 'unknown')} and {obj2.get('name', 'unknown')}")
                    has_overlaps = True

        # Check minimum distances
        has_spacing_issues = False
        for i, obj1 in enumerate(scene_objects):
            for j, obj2 in enumerate(scene_objects[i+1:], start=i+1):
                distance = self._calculate_bbox_distance(bboxes[i], bboxes[j])
                if distance < self.min_distance:
                    logger.warning(f"Insufficient spacing: {obj1.get('name', 'unknown')} and {obj2.get('name', 'unknown')} ({distance:.3f}m)")
                    has_spacing_issues = True

        is_valid = not (has_overlaps or has_spacing_issues)
        logger.info(f"Position validation: {'VALID' if is_valid else 'INVALID'}")

        return is_valid

    def fix_overlaps(self, scene_objects: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Automatically fix overlapping objects by repositioning.

        Args:
            scene_objects: List of scene objects

        Returns:
            Modified list with overlaps fixed

        Example:
            >>> validator = SpatialValidator()
            >>> fixed_objects = validator.fix_overlaps(scene_objects)
        """
        logger.info(f"Fixing overlaps for {len(scene_objects)} objects")

        fixed_count = 0

        # Calculate bounding boxes
        bboxes = self._calculate_bounding_boxes(scene_objects)

        # Find and fix overlaps
        for i, obj1 in enumerate(scene_objects):
            for j, obj2 in enumerate(scene_objects[i+1:], start=i+1):
                if self._check_bbox_collision(bboxes[i], bboxes[j]):
                    # Resolve overlap by moving obj2
                    logger.debug(f"Resolving overlap between {obj1.get('name', 'unknown')} and {obj2.get('name', 'unknown')}")

                    # Calculate separation vector
                    separation = self._calculate_separation_vector(bboxes[i], bboxes[j])

                    # Move object2
                    self._move_object(scene_objects[j], separation)

                    # Recalculate bbox for moved object
                    bboxes[j] = self._calculate_object_bbox(scene_objects[j])

                    fixed_count += 1
                    self.fixes_applied.append(f"Moved {obj2.get('name', 'unknown')} to resolve overlap")

        logger.info(f"Fixed {fixed_count} overlaps")

        return scene_objects

    def validate_scene(self, scene_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate complete scene (legacy method for compatibility).

        Args:
            scene_data: Scene data

        Returns:
            Validation report
        """
        return self.check(scene_data)

    # Private helper methods

    def _calculate_bounding_boxes(self, objects: List[Dict[str, Any]]) -> List[BoundingBox]:
        """Calculate bounding boxes for all objects."""
        bboxes = []

        for obj in objects:
            bbox = self._calculate_object_bbox(obj)
            bboxes.append(bbox)

        return bboxes

    def _calculate_object_bbox(self, obj: Dict[str, Any]) -> BoundingBox:
        """
        Calculate bounding box for a single object.

        Example:
            For a cube with vertices at corners:
            vertices = [(-1,-1,-1), (1,-1,-1), (1,1,-1), (-1,1,-1),
                       (-1,-1,1), (1,-1,1), (1,1,1), (-1,1,1)]

            min_point = (-1, -1, -1)  # minimum x, y, z
            max_point = (1, 1, 1)      # maximum x, y, z

            center = ((−1+1)/2, (−1+1)/2, (−1+1)/2) = (0, 0, 0)
            size = (1−(−1), 1−(−1), 1−(−1)) = (2, 2, 2)
        """
        vertices = obj.get('vertices', [])

        if not vertices or len(vertices) == 0:
            # Default small bounding box at origin
            logger.debug(f"No vertices for {obj.get('name', 'unknown')}, using default bbox")
            return BoundingBox(
                min_point=(-0.5, -0.5, -0.5),
                max_point=(0.5, 0.5, 0.5)
            )

        # Find min and max coordinates
        min_x = min(v[0] for v in vertices)
        min_y = min(v[1] for v in vertices)
        min_z = min(v[2] for v in vertices)

        max_x = max(v[0] for v in vertices)
        max_y = max(v[1] for v in vertices)
        max_z = max(v[2] for v in vertices)

        return BoundingBox(
            min_point=(min_x, min_y, min_z),
            max_point=(max_x, max_y, max_z)
        )

    def _check_bbox_collision(self, bbox1: BoundingBox, bbox2: BoundingBox) -> bool:
        """
        Check if two bounding boxes overlap.

        Uses Separating Axis Theorem (SAT) for AABBs:
        Two boxes overlap if they overlap on ALL three axes (x, y, z)

        Example:
            Box1: min=(0,0,0), max=(2,2,2)
            Box2: min=(1,1,1), max=(3,3,3)

            X-axis: [0,2] overlaps [1,3] ✓ (1 < 2 and 0 < 3)
            Y-axis: [0,2] overlaps [1,3] ✓
            Z-axis: [0,2] overlaps [1,3] ✓

            Result: COLLISION (overlaps on all axes)
        """
        # Check overlap on X axis
        overlap_x = (bbox1.min_point[0] <= bbox2.max_point[0] and
                     bbox1.max_point[0] >= bbox2.min_point[0])

        # Check overlap on Y axis
        overlap_y = (bbox1.min_point[1] <= bbox2.max_point[1] and
                     bbox1.max_point[1] >= bbox2.min_point[1])

        # Check overlap on Z axis
        overlap_z = (bbox1.min_point[2] <= bbox2.max_point[2] and
                     bbox1.max_point[2] >= bbox2.min_point[2])

        # Collision if overlapping on ALL axes
        return overlap_x and overlap_y and overlap_z

    def _calculate_bbox_distance(self, bbox1: BoundingBox, bbox2: BoundingBox) -> float:
        """
        Calculate minimum distance between two bounding boxes.

        Example:
            Box1 center: (0, 0, 0), size: (2, 2, 2)
            Box2 center: (5, 0, 0), size: (2, 2, 2)

            Box1 extends to x=1, Box2 starts at x=4
            Distance = 4 - 1 = 3.0
        """
        # Calculate distance between centers
        center1 = bbox1.center
        center2 = bbox2.center

        # Calculate distance on each axis
        dx = abs(center2[0] - center1[0]) - (bbox1.size[0] + bbox2.size[0]) / 2
        dy = abs(center2[1] - center1[1]) - (bbox1.size[1] + bbox2.size[1]) / 2
        dz = abs(center2[2] - center1[2]) - (bbox1.size[2] + bbox2.size[2]) / 2

        # If negative, boxes overlap on that axis (distance is 0)
        dx = max(0, dx)
        dy = max(0, dy)
        dz = max(0, dz)

        # Euclidean distance
        distance = math.sqrt(dx**2 + dy**2 + dz**2)

        return distance

    def _calculate_separation_vector(
        self,
        bbox1: BoundingBox,
        bbox2: BoundingBox
    ) -> Tuple[float, float, float]:
        """
        Calculate vector to separate two overlapping boxes.

        Moves bbox2 away from bbox1 by the minimum overlap distance.

        Example:
            Box1: min=(0,0,0), max=(2,2,2)
            Box2: min=(1,1,1), max=(3,3,3)

            Overlap on X: 2 - 1 = 1.0
            Overlap on Y: 2 - 1 = 1.0
            Overlap on Z: 2 - 1 = 1.0

            Minimum overlap is X (or Y or Z, all equal)
            Separate along X: move Box2 by (1.1, 0, 0)
        """
        # Calculate overlap on each axis
        overlap_x = min(bbox1.max_point[0] - bbox2.min_point[0],
                       bbox2.max_point[0] - bbox1.min_point[0])
        overlap_y = min(bbox1.max_point[1] - bbox2.min_point[1],
                       bbox2.max_point[1] - bbox1.min_point[1])
        overlap_z = min(bbox1.max_point[2] - bbox2.min_point[2],
                       bbox2.max_point[2] - bbox1.min_point[2])

        # Find axis with minimum overlap (easiest to separate)
        min_overlap = min(overlap_x, overlap_y, overlap_z)

        # Add small buffer to ensure separation
        separation_distance = min_overlap + self.min_distance

        # Calculate separation vector along minimum overlap axis
        center1 = bbox1.center
        center2 = bbox2.center

        if min_overlap == overlap_x:
            # Separate along X axis
            direction = 1 if center2[0] > center1[0] else -1
            return (separation_distance * direction, 0, 0)
        elif min_overlap == overlap_y:
            # Separate along Y axis
            direction = 1 if center2[1] > center1[1] else -1
            return (0, separation_distance * direction, 0)
        else:
            # Separate along Z axis
            direction = 1 if center2[2] > center1[2] else -1
            return (0, 0, separation_distance * direction)

    def _move_object(self, obj: Dict[str, Any], offset: Tuple[float, float, float]) -> None:
        """
        Move object by offset vector.

        Example:
            Object at (0, 0, 0), offset = (1, 0, 0)
            All vertices move by (1, 0, 0)
            vertex (1, 1, 1) becomes (2, 1, 1)
        """
        vertices = obj.get('vertices', [])

        if not vertices:
            return

        # Move all vertices by offset
        for i, vertex in enumerate(vertices):
            vertices[i] = [
                vertex[0] + offset[0],
                vertex[1] + offset[1],
                vertex[2] + offset[2]
            ]

        logger.debug(f"Moved {obj.get('name', 'unknown')} by {offset}")

    def _check_overlaps(self, objects: List[Dict[str, Any]], bboxes: List[BoundingBox]) -> None:
        """Check for bounding box collisions."""
        for i, obj1 in enumerate(objects):
            for j, obj2 in enumerate(objects[i+1:], start=i+1):
                if self._check_bbox_collision(bboxes[i], bboxes[j]):
                    issue = ValidationIssue(
                        type='overlap',
                        severity='error',
                        description=f"Objects overlap",
                        objects_involved=[obj1.get('name', f'obj{i}'), obj2.get('name', f'obj{j}')],
                        suggested_fix="Reposition objects to eliminate overlap",
                        auto_fixable=True
                    )
                    self.issues.append(issue)
                    logger.warning(f"Overlap: {obj1.get('name', 'unknown')} ↔ {obj2.get('name', 'unknown')}")

    def _check_spacing(self, objects: List[Dict[str, Any]], bboxes: List[BoundingBox]) -> None:
        """Check minimum distance between objects."""
        for i, obj1 in enumerate(objects):
            for j, obj2 in enumerate(objects[i+1:], start=i+1):
                distance = self._calculate_bbox_distance(bboxes[i], bboxes[j])
                if 0 < distance < self.min_distance:
                    issue = ValidationIssue(
                        type='spacing',
                        severity='warning',
                        description=f"Insufficient spacing: {distance:.3f}m (minimum: {self.min_distance}m)",
                        objects_involved=[obj1.get('name', f'obj{i}'), obj2.get('name', f'obj{j}')],
                        suggested_fix="Increase distance between objects",
                        auto_fixable=True
                    )
                    self.issues.append(issue)

    def _check_grounding(self, objects: List[Dict[str, Any]], bboxes: List[BoundingBox]) -> None:
        """
        Check if objects are properly grounded (not floating).

        An object is considered grounded if its minimum Z coordinate is near 0.

        Example:
            Object with min_z = 2.5 is floating (should be at z=0)
            Object with min_z = 0.005 is grounded (within tolerance)
        """
        for i, obj in enumerate(objects):
            bbox = bboxes[i]
            min_z = bbox.min_point[2]

            # Check if object is floating (min_z > ground_tolerance)
            if min_z > self.ground_tolerance:
                issue = ValidationIssue(
                    type='floating',
                    severity='warning',
                    description=f"Object is floating (z={min_z:.3f}m above ground)",
                    objects_involved=[obj.get('name', f'obj{i}')],
                    suggested_fix=f"Move object down by {min_z:.3f}m to ground it",
                    auto_fixable=True
                )
                self.issues.append(issue)
                logger.warning(f"Floating object: {obj.get('name', 'unknown')} at z={min_z:.3f}")

    def _check_alignment(self, objects: List[Dict[str, Any]], bboxes: List[BoundingBox]) -> None:
        """Check scene center alignment."""
        if not objects:
            return

        # Calculate overall scene center
        all_centers = [bbox.center for bbox in bboxes]
        scene_center_x = sum(c[0] for c in all_centers) / len(all_centers)
        scene_center_y = sum(c[1] for c in all_centers) / len(all_centers)

        # Check if scene is roughly centered around origin
        max_offset = 10.0  # Maximum acceptable offset from origin

        if abs(scene_center_x) > max_offset or abs(scene_center_y) > max_offset:
            issue = ValidationIssue(
                type='alignment',
                severity='info',
                description=f"Scene center is offset from origin: ({scene_center_x:.2f}, {scene_center_y:.2f})",
                suggested_fix="Consider centering scene around origin",
                auto_fixable=False
            )
            self.issues.append(issue)

    def _check_scale_relationships(
        self,
        objects: List[Dict[str, Any]],
        bboxes: List[BoundingBox]
    ) -> None:
        """Check if object scales are proportional."""
        if len(objects) < 2:
            return

        # Calculate size ratios
        sizes = [max(bbox.size) for bbox in bboxes]
        max_size = max(sizes)
        min_size = min(sizes)

        # Check if size difference is too extreme
        if max_size > 0 and min_size > 0:
            ratio = max_size / min_size

            # Warn if ratio is too extreme (>100x)
            if ratio > 100:
                issue = ValidationIssue(
                    type='scale',
                    severity='info',
                    description=f"Extreme size variation: largest object is {ratio:.1f}x bigger than smallest",
                    suggested_fix="Consider adjusting object scales for better proportion",
                    auto_fixable=False
                )
                self.issues.append(issue)

    def _apply_fixes(self, objects: List[Dict[str, Any]]) -> int:
        """Apply automatic fixes for detected issues."""
        fixed_count = 0

        for issue in self.issues:
            if not issue.auto_fixable:
                continue

            if issue.type == 'overlap':
                # Fix overlaps by repositioning
                fixed_count += self._fix_overlap_issue(objects, issue)
            elif issue.type == 'floating':
                # Ground floating objects
                fixed_count += self._fix_floating_issue(objects, issue)
            elif issue.type == 'spacing':
                # Increase spacing
                fixed_count += self._fix_spacing_issue(objects, issue)

        return fixed_count

    def _fix_overlap_issue(self, objects: List[Dict[str, Any]], issue: ValidationIssue) -> int:
        """Fix overlap between two objects."""
        if len(issue.objects_involved) != 2:
            return 0

        # Find objects by name
        obj1 = next((o for o in objects if o.get('name') == issue.objects_involved[0]), None)
        obj2 = next((o for o in objects if o.get('name') == issue.objects_involved[1]), None)

        if not obj1 or not obj2:
            return 0

        # Calculate bboxes
        bbox1 = self._calculate_object_bbox(obj1)
        bbox2 = self._calculate_object_bbox(obj2)

        # Calculate separation
        separation = self._calculate_separation_vector(bbox1, bbox2)

        # Move second object
        self._move_object(obj2, separation)

        self.fixes_applied.append(f"Separated {issue.objects_involved[0]} and {issue.objects_involved[1]}")
        return 1

    def _fix_floating_issue(self, objects: List[Dict[str, Any]], issue: ValidationIssue) -> int:
        """Ground floating object."""
        if len(issue.objects_involved) != 1:
            return 0

        obj_name = issue.objects_involved[0]
        obj = next((o for o in objects if o.get('name') == obj_name), None)

        if not obj:
            return 0

        # Calculate bbox
        bbox = self._calculate_object_bbox(obj)

        # Move object down to ground
        offset = (0, 0, -bbox.min_point[2])
        self._move_object(obj, offset)

        self.fixes_applied.append(f"Grounded {obj_name}")
        return 1

    def _fix_spacing_issue(self, objects: List[Dict[str, Any]], issue: ValidationIssue) -> int:
        """Increase spacing between objects."""
        if len(issue.objects_involved) != 2:
            return 0

        # Find objects
        obj1 = next((o for o in objects if o.get('name') == issue.objects_involved[0]), None)
        obj2 = next((o for o in objects if o.get('name') == issue.objects_involved[1]), None)

        if not obj1 or not obj2:
            return 0

        # Calculate bboxes
        bbox1 = self._calculate_object_bbox(obj1)
        bbox2 = self._calculate_object_bbox(obj2)

        # Calculate current distance
        current_distance = self._calculate_bbox_distance(bbox1, bbox2)

        # Calculate needed separation
        needed_separation = self.min_distance - current_distance

        if needed_separation <= 0:
            return 0

        # Calculate direction vector between centers
        center1 = bbox1.center
        center2 = bbox2.center

        dx = center2[0] - center1[0]
        dy = center2[1] - center1[1]
        dz = center2[2] - center1[2]

        # Normalize
        length = math.sqrt(dx**2 + dy**2 + dz**2)
        if length > 0:
            dx /= length
            dy /= length
            dz /= length

        # Apply separation
        offset = (dx * needed_separation, dy * needed_separation, dz * needed_separation)
        self._move_object(obj2, offset)

        self.fixes_applied.append(f"Increased spacing between {issue.objects_involved[0]} and {issue.objects_involved[1]}")
        return 1

    def _create_report(self, status: str, message: str) -> Dict[str, Any]:
        """Create validation report."""
        return {
            'status': status,
            'message': message,
            'total_issues': len(self.issues),
            'issues_by_type': {
                'overlap': sum(1 for i in self.issues if i.type == 'overlap'),
                'floating': sum(1 for i in self.issues if i.type == 'floating'),
                'spacing': sum(1 for i in self.issues if i.type == 'spacing'),
                'alignment': sum(1 for i in self.issues if i.type == 'alignment'),
                'scale': sum(1 for i in self.issues if i.type == 'scale')
            },
            'issues_by_severity': {
                'error': sum(1 for i in self.issues if i.severity == 'error'),
                'warning': sum(1 for i in self.issues if i.severity == 'warning'),
                'info': sum(1 for i in self.issues if i.severity == 'info')
            },
            'issues': [
                {
                    'type': i.type,
                    'severity': i.severity,
                    'description': i.description,
                    'objects': i.objects_involved,
                    'fix': i.suggested_fix,
                    'auto_fixable': i.auto_fixable
                }
                for i in self.issues
            ],
            'fixes_applied': self.fixes_applied
        }


# Example usage and testing
if __name__ == "__main__":
    from utils.logger import setup_logging

    # Setup logging
    setup_logging(level="DEBUG", console=True)

    # Create validator
    validator = SpatialValidator(config={'auto_fix': True, 'min_distance': 0.5})

    print("\n" + "="*80)
    print("SPATIAL VALIDATOR - TEST SUITE")
    print("="*80 + "\n")

    # Test 1: Overlapping objects
    print("\n" + "="*80)
    print("Test 1: Detect Overlapping Objects")
    print("="*80 + "\n")

    overlapping_objects = [
        {
            'name': 'cube1',
            'vertices': [
                [-1, -1, 0], [1, -1, 0], [1, 1, 0], [-1, 1, 0],
                [-1, -1, 2], [1, -1, 2], [1, 1, 2], [-1, 1, 2]
            ]
        },
        {
            'name': 'cube2',
            'vertices': [
                [0, 0, 0], [2, 0, 0], [2, 2, 0], [0, 2, 0],
                [0, 0, 2], [2, 0, 2], [2, 2, 2], [0, 2, 2]
            ]
        }
    ]

    scene1 = {'objects': overlapping_objects}
    report1 = validator.check(scene1)
    print(f"Status: {report1['status']}")
    print(f"Issues: {report1['total_issues']}")
    for issue in report1['issues']:
        print(f"  - {issue['type']}: {issue['description']}")

    # Test 2: Floating objects
    print("\n" + "="*80)
    print("Test 2: Detect Floating Objects")
    print("="*80 + "\n")

    floating_object = [
        {
            'name': 'floating_cube',
            'vertices': [
                [-1, -1, 5], [1, -1, 5], [1, 1, 5], [-1, 1, 5],
                [-1, -1, 7], [1, -1, 7], [1, 1, 7], [-1, 1, 7]
            ]
        }
    ]

    scene2 = {'objects': floating_object}
    report2 = validator.check(scene2)
    print(f"Status: {report2['status']}")
    print(f"Floating issues: {report2['issues_by_type']['floating']}")

    # Test 3: Auto-fix overlaps
    print("\n" + "="*80)
    print("Test 3: Auto-Fix Overlaps")
    print("="*80 + "\n")

    fixed_scene = validator.apply(scene1)
    print(f"Fixes applied: {len(validator.fixes_applied)}")
    for fix in validator.fixes_applied:
        print(f"  - {fix}")

    # Test 4: Validate positions method
    print("\n" + "="*80)
    print("Test 4: Validate Positions")
    print("="*80 + "\n")

    valid_objects = [
        {
            'name': 'cube1',
            'vertices': [[-1, -1, 0], [1, -1, 0], [1, 1, 0], [-1, 1, 0],
                        [-1, -1, 2], [1, -1, 2], [1, 1, 2], [-1, 1, 2]]
        },
        {
            'name': 'cube2',
            'vertices': [[5, 5, 0], [7, 5, 0], [7, 7, 0], [5, 7, 0],
                        [5, 5, 2], [7, 5, 2], [7, 7, 2], [5, 7, 2]]
        }
    ]

    is_valid = validator.validate_positions(valid_objects)
    print(f"Positions valid: {is_valid}")

    print("\n" + "="*80)
    print("TEST SUITE COMPLETE")
    print("="*80 + "\n")
