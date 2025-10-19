"""
Context Alignment - Spatial positioning and collision detection system.
Ensures objects are positioned coherently without overlaps.
"""

import logging
import math
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class PlacementStrategy(str, Enum):
    """Strategies for object placement."""
    GRID = "grid"  # Arrange in grid pattern
    RANDOM = "random"  # Random non-overlapping positions
    CIRCULAR = "circular"  # Arrange in circle
    LINEAR = "linear"  # Line arrangement
    CLUSTERED = "clustered"  # Grouped placement
    PHYSICS_BASED = "physics_based"  # Use physics simulation


@dataclass
class BoundingBox:
    """3D bounding box for collision detection."""
    min_x: float
    max_x: float
    min_y: float
    max_y: float
    min_z: float
    max_z: float

    @property
    def width(self) -> float:
        return self.max_x - self.min_x

    @property
    def height(self) -> float:
        return self.max_z - self.min_z

    @property
    def depth(self) -> float:
        return self.max_y - self.min_y

    @property
    def center(self) -> Tuple[float, float, float]:
        return (
            (self.min_x + self.max_x) / 2,
            (self.min_y + self.max_y) / 2,
            (self.min_z + self.max_z) / 2
        )

    def intersects(self, other: 'BoundingBox', tolerance: float = 0.0) -> bool:
        """Check if this box intersects another box."""
        return not (
            self.max_x + tolerance < other.min_x or
            self.min_x - tolerance > other.max_x or
            self.max_y + tolerance < other.min_y or
            self.min_y - tolerance > other.max_y or
            self.max_z + tolerance < other.min_z or
            self.min_z - tolerance > other.max_z
        )


@dataclass
class AlignedObject:
    """Object with aligned spatial position."""
    name: str
    position: Tuple[float, float, float]  # x, y, z
    rotation: Tuple[float, float, float]  # rx, ry, rz in radians
    scale: Tuple[float, float, float]  # sx, sy, sz
    bounding_box: BoundingBox
    original_position: Optional[Tuple[float, float, float]] = None
    was_adjusted: bool = False
    adjustment_reason: str = ""


class ContextAligner:
    """
    Aligns objects spatially to prevent collisions and ensure coherent layout.
    """

    def __init__(self, collision_tolerance: float = 0.01):
        """
        Initialize context aligner.

        Args:
            collision_tolerance: Minimum gap between objects in meters
        """
        self.collision_tolerance = collision_tolerance
        logger.info(f"ContextAligner initialized (tolerance={collision_tolerance}m)")

    def align_objects(self, objects: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Align objects to prevent collisions.

        Args:
            objects: List of object definitions with positions, sizes, etc.

        Returns:
            Dictionary with aligned objects and collision report
        """
        logger.info(f"Aligning {len(objects)} objects...")

        # Convert to AlignedObject instances
        aligned_objects = []
        for obj_data in objects:
            aligned_obj = self._create_aligned_object(obj_data)
            aligned_objects.append(aligned_obj)

        # Detect collisions
        collisions = self._detect_collisions(aligned_objects)
        original_collision_count = len(collisions)

        logger.info(f"Detected {original_collision_count} initial collisions")

        # Resolve collisions
        if collisions:
            aligned_objects = self._resolve_collisions(aligned_objects, collisions)

            # Re-check collisions
            remaining_collisions = self._detect_collisions(aligned_objects)
            logger.info(f"Resolved {original_collision_count - len(remaining_collisions)} collisions")
        else:
            remaining_collisions = []

        # Calculate statistics
        adjusted_count = sum(1 for obj in aligned_objects if obj.was_adjusted)

        result = {
            "objects": [self._aligned_object_to_dict(obj) for obj in aligned_objects],
            "collisions_initial": original_collision_count,
            "collisions_remaining": len(remaining_collisions),
            "collisions_fixed": original_collision_count - len(remaining_collisions),
            "objects_adjusted": adjusted_count,
            "remaining_issues": [self._collision_to_dict(c) for c in remaining_collisions]
        }

        return result

    def _create_aligned_object(self, obj_data: Dict[str, Any]) -> AlignedObject:
        """Create AlignedObject from raw data."""
        # Extract or default values
        name = obj_data.get("name", "unnamed")
        position = obj_data.get("position", (0.0, 0.0, 0.0))
        rotation = obj_data.get("rotation", (0.0, 0.0, 0.0))
        scale = obj_data.get("scale", (1.0, 1.0, 1.0))

        # Get dimensions
        dimensions = obj_data.get("dimensions", {"width": 1.0, "height": 1.0, "depth": 1.0})
        width = dimensions.get("width", 1.0) * scale[0]
        height = dimensions.get("height", 1.0) * scale[2]
        depth = dimensions.get("depth", 1.0) * scale[1]

        # Create bounding box
        bbox = BoundingBox(
            min_x=position[0] - width / 2,
            max_x=position[0] + width / 2,
            min_y=position[1] - depth / 2,
            max_y=position[1] + depth / 2,
            min_z=position[2] - height / 2,
            max_z=position[2] + height / 2
        )

        return AlignedObject(
            name=name,
            position=position,
            rotation=rotation,
            scale=scale,
            bounding_box=bbox,
            original_position=position
        )

    def _detect_collisions(
        self,
        objects: List[AlignedObject]
    ) -> List[Tuple[AlignedObject, AlignedObject]]:
        """Detect all collisions between objects."""
        collisions = []

        for i, obj1 in enumerate(objects):
            for obj2 in objects[i + 1:]:
                if obj1.bounding_box.intersects(obj2.bounding_box, -self.collision_tolerance):
                    collisions.append((obj1, obj2))

        return collisions

    def _resolve_collisions(
        self,
        objects: List[AlignedObject],
        collisions: List[Tuple[AlignedObject, AlignedObject]]
    ) -> List[AlignedObject]:
        """Resolve collisions by adjusting object positions."""
        # Sort collisions by severity (amount of overlap)
        sorted_collisions = sorted(
            collisions,
            key=lambda c: self._calculate_overlap_volume(c[0], c[1]),
            reverse=True
        )

        for obj1, obj2 in sorted_collisions:
            # Find current objects in list (may have been moved)
            idx1 = next(i for i, o in enumerate(objects) if o.name == obj1.name)
            idx2 = next(i for i, o in enumerate(objects) if o.name == obj2.name)

            current_obj1 = objects[idx1]
            current_obj2 = objects[idx2]

            # Check if still colliding
            if not current_obj1.bounding_box.intersects(
                current_obj2.bounding_box,
                -self.collision_tolerance
            ):
                continue  # Already resolved

            # Move obj2 away from obj1
            new_position = self._calculate_separation_position(current_obj1, current_obj2)

            # Update obj2
            objects[idx2] = self._update_object_position(current_obj2, new_position, "collision_avoidance")

        return objects

    def _calculate_overlap_volume(self, obj1: AlignedObject, obj2: AlignedObject) -> float:
        """Calculate approximate overlap volume between two objects."""
        bbox1 = obj1.bounding_box
        bbox2 = obj2.bounding_box

        overlap_x = max(0, min(bbox1.max_x, bbox2.max_x) - max(bbox1.min_x, bbox2.min_x))
        overlap_y = max(0, min(bbox1.max_y, bbox2.max_y) - max(bbox1.min_y, bbox2.min_y))
        overlap_z = max(0, min(bbox1.max_z, bbox2.max_z) - max(bbox1.min_z, bbox2.min_z))

        return overlap_x * overlap_y * overlap_z

    def _calculate_separation_position(
        self,
        obj1: AlignedObject,
        obj2: AlignedObject
    ) -> Tuple[float, float, float]:
        """Calculate new position for obj2 to separate from obj1."""
        # Get centers
        c1 = obj1.bounding_box.center
        c2 = obj2.bounding_box.center

        # Calculate direction vector from obj1 to obj2
        dx = c2[0] - c1[0]
        dy = c2[1] - c1[1]
        dz = c2[2] - c1[2]

        # If objects are at same position, use default direction
        distance = math.sqrt(dx**2 + dy**2 + dz**2)
        if distance < 0.001:
            dx, dy, dz = 1.0, 0.0, 0.0
            distance = 1.0

        # Normalize direction
        dx /= distance
        dy /= distance
        dz /= distance

        # Calculate required separation distance
        required_dist = (
            (obj1.bounding_box.width + obj2.bounding_box.width) / 2 +
            (obj1.bounding_box.depth + obj2.bounding_box.depth) / 2
        ) / 2 + self.collision_tolerance

        # New position for obj2
        new_x = c1[0] + dx * required_dist
        new_y = c1[1] + dy * required_dist
        new_z = c2[2]  # Keep same height

        return (new_x, new_y, new_z)

    def _update_object_position(
        self,
        obj: AlignedObject,
        new_position: Tuple[float, float, float],
        reason: str
    ) -> AlignedObject:
        """Update object position and bounding box."""
        # Calculate offset
        offset_x = new_position[0] - obj.position[0]
        offset_y = new_position[1] - obj.position[1]
        offset_z = new_position[2] - obj.position[2]

        # Update bounding box
        new_bbox = BoundingBox(
            min_x=obj.bounding_box.min_x + offset_x,
            max_x=obj.bounding_box.max_x + offset_x,
            min_y=obj.bounding_box.min_y + offset_y,
            max_y=obj.bounding_box.max_y + offset_y,
            min_z=obj.bounding_box.min_z + offset_z,
            max_z=obj.bounding_box.max_z + offset_z
        )

        return AlignedObject(
            name=obj.name,
            position=new_position,
            rotation=obj.rotation,
            scale=obj.scale,
            bounding_box=new_bbox,
            original_position=obj.original_position or obj.position,
            was_adjusted=True,
            adjustment_reason=reason
        )

    def _aligned_object_to_dict(self, obj: AlignedObject) -> Dict[str, Any]:
        """Convert AlignedObject to dictionary."""
        return {
            "name": obj.name,
            "position": obj.position,
            "rotation": obj.rotation,
            "scale": obj.scale,
            "bounding_box": {
                "min": (obj.bounding_box.min_x, obj.bounding_box.min_y, obj.bounding_box.min_z),
                "max": (obj.bounding_box.max_x, obj.bounding_box.max_y, obj.bounding_box.max_z),
                "center": obj.bounding_box.center,
                "dimensions": (obj.bounding_box.width, obj.bounding_box.depth, obj.bounding_box.height)
            },
            "was_adjusted": obj.was_adjusted,
            "adjustment_reason": obj.adjustment_reason,
            "original_position": obj.original_position
        }

    def _collision_to_dict(self, collision: Tuple[AlignedObject, AlignedObject]) -> Dict[str, Any]:
        """Convert collision pair to dictionary."""
        obj1, obj2 = collision
        overlap = self._calculate_overlap_volume(obj1, obj2)

        return {
            "object_1": obj1.name,
            "object_2": obj2.name,
            "overlap_volume": overlap,
            "severity": "high" if overlap > 1.0 else "medium" if overlap > 0.1 else "low"
        }

    def place_objects_in_pattern(
        self,
        objects: List[Dict[str, Any]],
        strategy: PlacementStrategy = PlacementStrategy.GRID,
        spacing: float = 2.0
    ) -> List[Dict[str, Any]]:
        """
        Place objects in a specific pattern.

        Args:
            objects: List of objects to place
            strategy: Placement strategy to use
            spacing: Distance between objects

        Returns:
            List of objects with updated positions
        """
        logger.info(f"Placing {len(objects)} objects in {strategy.value} pattern")

        if strategy == PlacementStrategy.GRID:
            return self._place_grid(objects, spacing)
        elif strategy == PlacementStrategy.CIRCULAR:
            return self._place_circular(objects, spacing)
        elif strategy == PlacementStrategy.LINEAR:
            return self._place_linear(objects, spacing)
        else:
            logger.warning(f"Strategy {strategy} not implemented, using grid")
            return self._place_grid(objects, spacing)

    def _place_grid(self, objects: List[Dict[str, Any]], spacing: float) -> List[Dict[str, Any]]:
        """Place objects in grid pattern."""
        grid_size = math.ceil(math.sqrt(len(objects)))

        for i, obj in enumerate(objects):
            row = i // grid_size
            col = i % grid_size

            obj["position"] = (
                col * spacing - (grid_size * spacing) / 2,
                row * spacing - (grid_size * spacing) / 2,
                0.0
            )

        return objects

    def _place_circular(self, objects: List[Dict[str, Any]], radius: float) -> List[Dict[str, Any]]:
        """Place objects in circular pattern."""
        count = len(objects)
        angle_step = 2 * math.pi / count

        for i, obj in enumerate(objects):
            angle = i * angle_step
            obj["position"] = (
                radius * math.cos(angle),
                radius * math.sin(angle),
                0.0
            )

        return objects

    def _place_linear(self, objects: List[Dict[str, Any]], spacing: float) -> List[Dict[str, Any]]:
        """Place objects in line."""
        total_width = (len(objects) - 1) * spacing

        for i, obj in enumerate(objects):
            obj["position"] = (
                i * spacing - total_width / 2,
                0.0,
                0.0
            )

        return objects
