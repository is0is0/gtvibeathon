"""
Context Alignment Module
------------------------
Handles spatial positioning and collision detection for scene objects.

This module positions objects in 3D space without overlaps using grid-based
placement algorithms, collision detection, and hierarchical scene organization.
"""

import logging
import numpy as np
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class PlacementStrategy(Enum):
    """Strategies for object placement."""
    GRID = "grid"  # Grid-based placement
    RADIAL = "radial"  # Radial arrangement around center
    LINEAR = "linear"  # Linear arrangement
    CLUSTERED = "clustered"  # Grouped by category
    CUSTOM = "custom"  # Custom positions from metadata


@dataclass
class BoundingBox:
    """3D axis-aligned bounding box."""
    min_point: np.ndarray  # [x, y, z]
    max_point: np.ndarray  # [x, y, z]

    @property
    def center(self) -> np.ndarray:
        """Get bounding box center."""
        return (self.min_point + self.max_point) / 2

    @property
    def size(self) -> np.ndarray:
        """Get bounding box dimensions."""
        return self.max_point - self.min_point

    @property
    def volume(self) -> float:
        """Get bounding box volume."""
        size = self.size
        return float(size[0] * size[1] * size[2])

    def intersects(self, other: 'BoundingBox', margin: float = 0.0) -> bool:
        """
        Check if this bounding box intersects another.

        Args:
            other: Other bounding box to check
            margin: Safety margin to add around boxes

        Returns:
            True if boxes intersect
        """
        # Expand boxes by margin
        min1 = self.min_point - margin
        max1 = self.max_point + margin
        min2 = other.min_point - margin
        max2 = other.max_point + margin

        # Check overlap on all axes
        return (min1[0] <= max2[0] and max1[0] >= min2[0] and
                min1[1] <= max2[1] and max1[1] >= min2[1] and
                min1[2] <= max2[2] and max1[2] >= min2[2])


@dataclass
class PlacedObject:
    """Represents an object with position and bounding box."""
    name: str
    position: np.ndarray  # [x, y, z]
    rotation: np.ndarray  # [rx, ry, rz] in radians
    bounding_box: BoundingBox
    category: str
    metadata: Dict[str, Any]


@dataclass
class SpatialGrid:
    """3D spatial grid for efficient collision checking."""
    grid_size: float
    cells: Dict[Tuple[int, int, int], List[PlacedObject]]

    def __init__(self, grid_size: float = 1.0):
        """
        Initialize spatial grid.

        Args:
            grid_size: Size of each grid cell
        """
        self.grid_size = grid_size
        self.cells = {}

    def _get_cell_coords(self, position: np.ndarray) -> Tuple[int, int, int]:
        """Get grid cell coordinates for a position."""
        return (
            int(position[0] / self.grid_size),
            int(position[1] / self.grid_size),
            int(position[2] / self.grid_size)
        )

    def _get_cell_range(self, bbox: BoundingBox) -> List[Tuple[int, int, int]]:
        """Get all grid cells that a bounding box occupies."""
        min_cell = self._get_cell_coords(bbox.min_point)
        max_cell = self._get_cell_coords(bbox.max_point)

        cells = []
        for x in range(min_cell[0], max_cell[0] + 1):
            for y in range(min_cell[1], max_cell[1] + 1):
                for z in range(min_cell[2], max_cell[2] + 1):
                    cells.append((x, y, z))

        return cells

    def add_object(self, obj: PlacedObject) -> None:
        """Add object to spatial grid."""
        cells = self._get_cell_range(obj.bounding_box)
        for cell in cells:
            if cell not in self.cells:
                self.cells[cell] = []
            self.cells[cell].append(obj)

    def get_nearby_objects(self, bbox: BoundingBox) -> List[PlacedObject]:
        """Get all objects near a bounding box."""
        nearby = set()
        cells = self._get_cell_range(bbox)

        for cell in cells:
            if cell in self.cells:
                nearby.update(self.cells[cell])

        return list(nearby)


class ContextAlignment:
    """
    Handles spatial positioning and collision detection for scene objects.

    This class positions objects in 3D space ensuring no overlaps, proper
    spacing, and logical arrangements based on object types and relationships.

    Example:
        >>> alignment = ContextAlignment()
        >>> objects = [{"name": "table", "vertices": [...], ...}]
        >>> positioned = alignment.align(objects)
        >>> print(f"Positioned {len(positioned)} objects")
    """

    def __init__(
        self,
        strategy: PlacementStrategy = PlacementStrategy.GRID,
        grid_spacing: float = 0.5,
        collision_margin: float = 0.1,
        ground_level: float = 0.0
    ):
        """
        Initialize context alignment system.

        Args:
            strategy: Default placement strategy
            grid_spacing: Spacing between grid positions (meters)
            collision_margin: Safety margin around objects (meters)
            ground_level: Y-coordinate of ground plane
        """
        self.strategy = strategy
        self.grid_spacing = grid_spacing
        self.collision_margin = collision_margin
        self.ground_level = ground_level
        self.spatial_grid = SpatialGrid(grid_size=2.0)

        # Object relationship rules
        self.placement_rules = self._initialize_placement_rules()

        logger.info(f"ContextAlignment initialized with {strategy.value} strategy")

    def _initialize_placement_rules(self) -> Dict[str, Dict[str, Any]]:
        """
        Initialize rules for object placement relationships.

        Returns:
            Dictionary of placement rules
        """
        return {
            "table": {
                "ground_offset": 0.0,
                "nearby_objects": ["chair", "lamp", "vase"],
                "spacing": 0.3
            },
            "chair": {
                "ground_offset": 0.0,
                "nearby_objects": ["table", "desk"],
                "spacing": 0.2
            },
            "sofa": {
                "ground_offset": 0.0,
                "nearby_objects": ["coffee_table", "lamp"],
                "spacing": 0.5
            },
            "lamp": {
                "ground_offset": 0.0,
                "nearby_objects": ["table", "sofa"],
                "spacing": 0.2
            },
            "bed": {
                "ground_offset": 0.0,
                "nearby_objects": ["nightstand", "lamp"],
                "spacing": 0.3
            },
            "wall": {
                "ground_offset": 0.0,
                "nearby_objects": ["door", "window", "picture"],
                "spacing": 0.0
            }
        }

    def align(
        self,
        objects: List[Dict[str, Any]],
        strategy: Optional[PlacementStrategy] = None
    ) -> List[Dict[str, Any]]:
        """
        Position objects in 3D space without collisions.

        This is the main entry point for spatial alignment. It analyzes
        object relationships and places them according to the chosen strategy.

        Args:
            objects: List of geometry objects to position
            strategy: Optional override for placement strategy

        Returns:
            List of positioned objects with position and rotation data

        Example:
            >>> alignment = ContextAlignment()
            >>> objects = [
            ...     {"name": "table", "vertices": np.array([...])},
            ...     {"name": "chair", "vertices": np.array([...])}
            ... ]
            >>> positioned = alignment.align(objects)
        """
        logger.info(f"Aligning {len(objects)} objects")

        if not objects:
            return []

        strategy = strategy or self.strategy

        # Reset spatial grid
        self.spatial_grid = SpatialGrid(grid_size=2.0)

        # Calculate bounding boxes
        objects_with_bounds = self._calculate_bounding_boxes(objects)

        # Categorize objects
        categorized = self._categorize_objects(objects_with_bounds)

        # Position objects based on strategy
        if strategy == PlacementStrategy.GRID:
            positioned = self._place_grid(categorized)
        elif strategy == PlacementStrategy.RADIAL:
            positioned = self._place_radial(categorized)
        elif strategy == PlacementStrategy.LINEAR:
            positioned = self._place_linear(categorized)
        elif strategy == PlacementStrategy.CLUSTERED:
            positioned = self._place_clustered(categorized)
        else:
            positioned = self._place_grid(categorized)  # Fallback

        # Create scene hierarchy
        positioned_with_hierarchy = self._create_hierarchy(positioned)

        logger.info(f"Successfully positioned {len(positioned_with_hierarchy)} objects")

        return positioned_with_hierarchy

    def _calculate_bounding_boxes(
        self,
        objects: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Calculate bounding boxes for all objects.

        Args:
            objects: List of objects

        Returns:
            Objects with bounding box data
        """
        logger.info("Calculating bounding boxes...")

        objects_with_bounds = []

        for obj in objects:
            vertices = obj.get('vertices')

            if vertices is None or len(vertices) == 0:
                logger.warning(f"Object {obj.get('name', 'unknown')} has no vertices")
                continue

            if not isinstance(vertices, np.ndarray):
                vertices = np.array(vertices)

            # Calculate axis-aligned bounding box
            min_point = vertices.min(axis=0)
            max_point = vertices.max(axis=0)

            obj_copy = obj.copy()
            obj_copy['bounding_box'] = {
                'min': min_point.tolist(),
                'max': max_point.tolist(),
                'center': ((min_point + max_point) / 2).tolist(),
                'size': (max_point - min_point).tolist()
            }

            objects_with_bounds.append(obj_copy)

        return objects_with_bounds

    def _categorize_objects(
        self,
        objects: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Categorize objects by type.

        Args:
            objects: List of objects

        Returns:
            Dictionary mapping categories to objects
        """
        categories = {}

        for obj in objects:
            # Get category from metadata or infer from name
            category = obj.get('metadata', {}).get('object_type', 'generic')
            if category == 'generic':
                category = obj.get('type', 'generic')

            if category not in categories:
                categories[category] = []

            categories[category].append(obj)

        logger.info(f"Categorized objects into {len(categories)} categories")
        return categories

    def _place_grid(
        self,
        categorized: Dict[str, List[Dict[str, Any]]]
    ) -> List[Dict[str, Any]]:
        """
        Place objects in a grid pattern.

        Args:
            categorized: Categorized objects

        Returns:
            List of positioned objects
        """
        logger.info("Placing objects in grid pattern...")

        positioned = []
        grid_x = 0
        grid_z = 0
        max_height_in_row = 0

        # Flatten categories
        all_objects = []
        for category, objs in categorized.items():
            all_objects.extend(objs)

        for obj in all_objects:
            bbox_data = obj.get('bounding_box', {})
            size = bbox_data.get('size', [1.0, 1.0, 1.0])

            # Position at grid location
            position = np.array([
                grid_x + size[0] / 2,
                self.ground_level + size[1] / 2,
                grid_z + size[2] / 2
            ])

            # Check for collisions and adjust
            position = self._find_valid_position(obj, position)

            # Create positioned object
            positioned_obj = self._create_positioned_object(obj, position)
            positioned.append(positioned_obj)

            # Update spatial grid
            self.spatial_grid.add_object(positioned_obj)

            # Update grid position
            max_height_in_row = max(max_height_in_row, size[2])
            grid_x += size[0] + self.grid_spacing

            # Move to next row if needed
            if grid_x > 10.0:  # Max row width
                grid_x = 0
                grid_z += max_height_in_row + self.grid_spacing
                max_height_in_row = 0

        return [self._positioned_to_dict(obj) for obj in positioned]

    def _place_radial(
        self,
        categorized: Dict[str, List[Dict[str, Any]]]
    ) -> List[Dict[str, Any]]:
        """
        Place objects in a radial pattern around center.

        Args:
            categorized: Categorized objects

        Returns:
            List of positioned objects
        """
        logger.info("Placing objects in radial pattern...")

        positioned = []
        all_objects = []
        for category, objs in categorized.items():
            all_objects.extend(objs)

        radius = 3.0
        angle_step = 2 * np.pi / len(all_objects) if all_objects else 0

        for i, obj in enumerate(all_objects):
            angle = i * angle_step

            bbox_data = obj.get('bounding_box', {})
            size = bbox_data.get('size', [1.0, 1.0, 1.0])

            # Position on circle
            position = np.array([
                radius * np.cos(angle),
                self.ground_level + size[1] / 2,
                radius * np.sin(angle)
            ])

            # Create positioned object with rotation towards center
            rotation = np.array([0, -angle, 0])
            positioned_obj = self._create_positioned_object(obj, position, rotation)
            positioned.append(positioned_obj)

            self.spatial_grid.add_object(positioned_obj)

        return [self._positioned_to_dict(obj) for obj in positioned]

    def _place_linear(
        self,
        categorized: Dict[str, List[Dict[str, Any]]]
    ) -> List[Dict[str, Any]]:
        """
        Place objects in a linear arrangement.

        Args:
            categorized: Categorized objects

        Returns:
            List of positioned objects
        """
        logger.info("Placing objects in linear pattern...")

        positioned = []
        all_objects = []
        for category, objs in categorized.items():
            all_objects.extend(objs)

        current_x = 0

        for obj in all_objects:
            bbox_data = obj.get('bounding_box', {})
            size = bbox_data.get('size', [1.0, 1.0, 1.0])

            position = np.array([
                current_x + size[0] / 2,
                self.ground_level + size[1] / 2,
                0
            ])

            positioned_obj = self._create_positioned_object(obj, position)
            positioned.append(positioned_obj)

            self.spatial_grid.add_object(positioned_obj)

            current_x += size[0] + self.grid_spacing

        return [self._positioned_to_dict(obj) for obj in positioned]

    def _place_clustered(
        self,
        categorized: Dict[str, List[Dict[str, Any]]]
    ) -> List[Dict[str, Any]]:
        """
        Place objects clustered by category.

        Args:
            categorized: Categorized objects

        Returns:
            List of positioned objects
        """
        logger.info("Placing objects in clustered pattern...")

        positioned = []
        cluster_x = 0

        for category, objects in categorized.items():
            cluster_z = 0
            max_width = 0

            for obj in objects:
                bbox_data = obj.get('bounding_box', {})
                size = bbox_data.get('size', [1.0, 1.0, 1.0])

                position = np.array([
                    cluster_x + size[0] / 2,
                    self.ground_level + size[1] / 2,
                    cluster_z + size[2] / 2
                ])

                positioned_obj = self._create_positioned_object(obj, position)
                positioned.append(positioned_obj)

                self.spatial_grid.add_object(positioned_obj)

                cluster_z += size[2] + self.grid_spacing
                max_width = max(max_width, size[0])

            # Move to next cluster
            cluster_x += max_width + self.grid_spacing * 2

        return [self._positioned_to_dict(obj) for obj in positioned]

    def _find_valid_position(
        self,
        obj: Dict[str, Any],
        initial_position: np.ndarray,
        max_attempts: int = 100
    ) -> np.ndarray:
        """
        Find a valid collision-free position for an object.

        Args:
            obj: Object to position
            initial_position: Initial position to try
            max_attempts: Maximum attempts to find valid position

        Returns:
            Valid position
        """
        bbox_data = obj.get('bounding_box', {})
        size = np.array(bbox_data.get('size', [1.0, 1.0, 1.0]))

        for attempt in range(max_attempts):
            test_bbox = BoundingBox(
                min_point=initial_position - size / 2,
                max_point=initial_position + size / 2
            )

            # Check for collisions
            nearby = self.spatial_grid.get_nearby_objects(test_bbox)
            has_collision = False

            for nearby_obj in nearby:
                if test_bbox.intersects(nearby_obj.bounding_box, self.collision_margin):
                    has_collision = True
                    break

            if not has_collision:
                return initial_position

            # Try offset position
            offset = np.array([
                np.random.uniform(-0.5, 0.5),
                0,
                np.random.uniform(-0.5, 0.5)
            ])
            initial_position += offset

        logger.warning(f"Could not find collision-free position for {obj.get('name')}")
        return initial_position

    def _create_positioned_object(
        self,
        obj: Dict[str, Any],
        position: np.ndarray,
        rotation: Optional[np.ndarray] = None
    ) -> PlacedObject:
        """
        Create a positioned object with bounding box.

        Args:
            obj: Original object
            position: World position
            rotation: Optional rotation (default: [0, 0, 0])

        Returns:
            PlacedObject instance
        """
        if rotation is None:
            rotation = np.array([0.0, 0.0, 0.0])

        bbox_data = obj.get('bounding_box', {})
        size = np.array(bbox_data.get('size', [1.0, 1.0, 1.0]))

        bbox = BoundingBox(
            min_point=position - size / 2,
            max_point=position + size / 2
        )

        category = obj.get('metadata', {}).get('object_type', 'generic')

        return PlacedObject(
            name=obj.get('name', 'object'),
            position=position,
            rotation=rotation,
            bounding_box=bbox,
            category=category,
            metadata=obj.get('metadata', {})
        )

    def _positioned_to_dict(self, placed_obj: PlacedObject) -> Dict[str, Any]:
        """
        Convert PlacedObject to dictionary.

        Args:
            placed_obj: PlacedObject instance

        Returns:
            Dictionary representation
        """
        return {
            'name': placed_obj.name,
            'position': placed_obj.position.tolist(),
            'rotation': placed_obj.rotation.tolist(),
            'bounding_box': {
                'min': placed_obj.bounding_box.min_point.tolist(),
                'max': placed_obj.bounding_box.max_point.tolist(),
                'center': placed_obj.bounding_box.center.tolist(),
                'size': placed_obj.bounding_box.size.tolist()
            },
            'category': placed_obj.category,
            'metadata': placed_obj.metadata
        }

    def _create_hierarchy(
        self,
        positioned: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Create scene hierarchy with parent-child relationships.

        Args:
            positioned: List of positioned objects

        Returns:
            Objects with hierarchy information
        """
        logger.info("Creating scene hierarchy...")

        # Group by category
        categories = {}
        for obj in positioned:
            category = obj.get('category', 'generic')
            if category not in categories:
                categories[category] = []
            categories[category].append(obj)

        # Add hierarchy metadata
        for obj in positioned:
            obj['hierarchy'] = {
                'parent': obj.get('category', 'generic') + '_group',
                'children': [],
                'level': 1
            }

        return positioned

    def check_collisions(
        self,
        objects: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Check for collisions between positioned objects.

        Args:
            objects: List of positioned objects

        Returns:
            List of collision reports

        Example:
            >>> alignment = ContextAlignment()
            >>> collisions = alignment.check_collisions(positioned_objects)
            >>> if collisions:
            ...     print(f"Found {len(collisions)} collisions")
        """
        logger.info("Checking for collisions...")

        collisions = []

        for i, obj1 in enumerate(objects):
            bbox1_data = obj1.get('bounding_box', {})
            bbox1 = BoundingBox(
                min_point=np.array(bbox1_data.get('min', [0, 0, 0])),
                max_point=np.array(bbox1_data.get('max', [1, 1, 1]))
            )

            for obj2 in objects[i + 1:]:
                bbox2_data = obj2.get('bounding_box', {})
                bbox2 = BoundingBox(
                    min_point=np.array(bbox2_data.get('min', [0, 0, 0])),
                    max_point=np.array(bbox2_data.get('max', [1, 1, 1]))
                )

                if bbox1.intersects(bbox2, self.collision_margin):
                    collisions.append({
                        'object1': obj1.get('name'),
                        'object2': obj2.get('name'),
                        'severity': 'overlap',
                        'overlap_volume': self._calculate_overlap_volume(bbox1, bbox2)
                    })

        logger.info(f"Found {len(collisions)} collisions")
        return collisions

    def _calculate_overlap_volume(
        self,
        bbox1: BoundingBox,
        bbox2: BoundingBox
    ) -> float:
        """Calculate volume of overlap between two bounding boxes."""
        overlap_min = np.maximum(bbox1.min_point, bbox2.min_point)
        overlap_max = np.minimum(bbox1.max_point, bbox2.max_point)

        overlap_size = overlap_max - overlap_min
        if np.all(overlap_size > 0):
            return float(np.prod(overlap_size))
        return 0.0


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    alignment = ContextAlignment(
        strategy=PlacementStrategy.GRID,
        grid_spacing=0.5,
        collision_margin=0.1
    )

    # Create test objects
    test_objects = [
        {
            "name": "table",
            "type": "furniture",
            "vertices": np.array([
                [-0.6, 0, -0.4], [0.6, 0, -0.4],
                [0.6, 0.75, -0.4], [-0.6, 0.75, -0.4],
                [-0.6, 0, 0.4], [0.6, 0, 0.4],
                [0.6, 0.75, 0.4], [-0.6, 0.75, 0.4]
            ]),
            "metadata": {"object_type": "furniture"}
        },
        {
            "name": "chair",
            "type": "furniture",
            "vertices": np.array([
                [-0.25, 0, -0.25], [0.25, 0, -0.25],
                [0.25, 0.85, -0.25], [-0.25, 0.85, -0.25],
                [-0.25, 0, 0.25], [0.25, 0, 0.25],
                [0.25, 0.85, 0.25], [-0.25, 0.85, 0.25]
            ]),
            "metadata": {"object_type": "furniture"}
        },
        {
            "name": "lamp",
            "type": "lighting",
            "vertices": np.array([
                [-0.15, 0, -0.15], [0.15, 0, -0.15],
                [0.15, 1.5, -0.15], [-0.15, 1.5, -0.15],
                [-0.15, 0, 0.15], [0.15, 0, 0.15],
                [0.15, 1.5, 0.15], [-0.15, 1.5, 0.15]
            ]),
            "metadata": {"object_type": "lighting"}
        }
    ]

    # Position objects
    positioned = alignment.align(test_objects, strategy=PlacementStrategy.GRID)

    print(f"\nPositioned {len(positioned)} objects:")
    for obj in positioned:
        print(f"  - {obj['name']}: position = {obj['position']}")
        print(f"    Bounding box size: {obj['bounding_box']['size']}")

    # Check for collisions
    collisions = alignment.check_collisions(positioned)
    if collisions:
        print(f"\nWarning: Found {len(collisions)} collisions:")
        for collision in collisions:
            print(f"  - {collision['object1']} <-> {collision['object2']}")
    else:
        print("\nNo collisions detected")
