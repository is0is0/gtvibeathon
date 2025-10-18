"""
Proportion Analyzer Module
--------------------------
Determines real-world dimensions and normalizes object scales.

This module ensures all objects in a scene have correct proportions relative
to each other and are scaled appropriately for Blender's unit system.
"""

import logging
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class RealWorldDimensions:
    """Real-world dimensions for common objects (in meters)."""

    # Furniture
    TABLE_HEIGHT = 0.75
    CHAIR_HEIGHT = 0.85
    CHAIR_SEAT_HEIGHT = 0.45
    SOFA_HEIGHT = 0.85
    SOFA_WIDTH = 2.0
    BED_HEIGHT = 0.6
    BED_WIDTH = 1.6  # Double bed
    DESK_HEIGHT = 0.75

    # Appliances
    REFRIGERATOR_HEIGHT = 1.8
    TV_WIDTH_55_INCH = 1.23
    MICROWAVE_WIDTH = 0.5

    # Lighting
    FLOOR_LAMP_HEIGHT = 1.5
    TABLE_LAMP_HEIGHT = 0.5

    # Decoration
    VASE_HEIGHT = 0.3
    PLANT_POT_HEIGHT = 0.4
    PICTURE_FRAME_WIDTH = 0.5

    # Architectural
    DOOR_HEIGHT = 2.0
    DOOR_WIDTH = 0.9
    WINDOW_HEIGHT = 1.5
    WINDOW_WIDTH = 1.2
    CEILING_HEIGHT = 2.7

    # Human scale reference
    HUMAN_HEIGHT = 1.75
    HUMAN_ARM_REACH = 0.75


class ProportionAnalyzer:
    """
    Analyzes and normalizes object proportions for realistic scenes.

    This class ensures all objects are scaled correctly relative to each
    other and to real-world measurements.

    Example:
        >>> analyzer = ProportionAnalyzer()
        >>> objects = [{"name": "table", "vertices": [...], ...}]
        >>> scaled = analyzer.normalize(objects, references={})
        >>> print(f"Scaled {len(scaled)} objects")
    """

    def __init__(self):
        """Initialize the proportion analyzer."""
        self.dimensions = RealWorldDimensions()
        self.scale_database = self._build_scale_database()
        logger.info("ProportionAnalyzer initialized")

    def _build_scale_database(self) -> Dict[str, Dict[str, float]]:
        """
        Build database of real-world object dimensions.

        Returns:
            Dictionary mapping object types to their dimensions
        """
        return {
            "table": {
                "height": self.dimensions.TABLE_HEIGHT,
                "width": 1.2,
                "depth": 0.8
            },
            "chair": {
                "height": self.dimensions.CHAIR_HEIGHT,
                "width": 0.5,
                "depth": 0.5,
                "seat_height": self.dimensions.CHAIR_SEAT_HEIGHT
            },
            "sofa": {
                "height": self.dimensions.SOFA_HEIGHT,
                "width": self.dimensions.SOFA_WIDTH,
                "depth": 0.9
            },
            "bed": {
                "height": self.dimensions.BED_HEIGHT,
                "width": self.dimensions.BED_WIDTH,
                "length": 2.0
            },
            "lamp": {
                "height": self.dimensions.FLOOR_LAMP_HEIGHT,
                "base_radius": 0.15
            },
            "door": {
                "height": self.dimensions.DOOR_HEIGHT,
                "width": self.dimensions.DOOR_WIDTH
            },
            "window": {
                "height": self.dimensions.WINDOW_HEIGHT,
                "width": self.dimensions.WINDOW_WIDTH
            }
        }

    def normalize(
        self,
        objects: List[Dict[str, Any]],
        references: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Normalize object scales to real-world proportions.

        Args:
            objects: List of geometry objects to normalize
            references: Reference data with scale information

        Returns:
            List of normalized objects with correct scales

        Example:
            >>> analyzer = ProportionAnalyzer()
            >>> objects = [{"name": "table", "vertices": np.array([[...]])}]
            >>> normalized = analyzer.normalize(objects, {})
        """
        logger.info(f"Normalizing proportions for {len(objects)} objects")

        normalized_objects = []

        for obj in objects:
            try:
                # Get target dimensions
                target_dims = self._get_target_dimensions(obj, references)

                # Calculate current dimensions
                current_dims = self._calculate_current_dimensions(obj)

                # Calculate scale factor
                scale_factor = self._calculate_scale_factor(current_dims, target_dims)

                # Apply scaling
                scaled_obj = self._apply_scale(obj, scale_factor)

                # Add scale metadata
                scaled_obj['metadata'] = scaled_obj.get('metadata', {})
                scaled_obj['metadata']['scale_factor'] = scale_factor
                scaled_obj['metadata']['target_dimensions'] = target_dims
                scaled_obj['metadata']['real_world_size'] = target_dims

                normalized_objects.append(scaled_obj)
                logger.info(f"Normalized {obj.get('name', 'object')}: scale factor = {scale_factor:.3f}")

            except Exception as e:
                logger.error(f"Failed to normalize {obj.get('name', 'unknown')}: {e}")
                # Keep original object if normalization fails
                normalized_objects.append(obj)

        return normalized_objects

    def _get_target_dimensions(
        self,
        obj: Dict[str, Any],
        references: Dict[str, Any]
    ) -> Dict[str, float]:
        """
        Get target real-world dimensions for an object.

        Args:
            obj: Object to get dimensions for
            references: Reference data

        Returns:
            Dictionary of target dimensions
        """
        object_name = obj.get('name', '').lower()

        # Check if we have reference dimensions
        if references and 'dimensions' in references:
            ref_dims = references['dimensions'].get(object_name)
            if ref_dims:
                return ref_dims

        # Check scale database
        for key, dims in self.scale_database.items():
            if key in object_name:
                return dims

        # Default dimensions based on metadata
        metadata = obj.get('metadata', {})
        if 'size' in metadata:
            size = metadata['size']
            return {
                "width": size[0],
                "depth": size[1] if len(size) > 1 else size[0],
                "height": size[2] if len(size) > 2 else size[0]
            }

        # Fallback to 1m cube
        return {"width": 1.0, "depth": 1.0, "height": 1.0}

    def _calculate_current_dimensions(self, obj: Dict[str, Any]) -> Dict[str, float]:
        """
        Calculate current object dimensions from vertices.

        Args:
            obj: Object with vertices

        Returns:
            Dictionary of current dimensions
        """
        vertices = obj.get('vertices')

        if vertices is None or len(vertices) == 0:
            return {"width": 1.0, "depth": 1.0, "height": 1.0}

        # Convert to numpy array if needed
        if not isinstance(vertices, np.ndarray):
            vertices = np.array(vertices)

        # Calculate bounding box
        min_point = vertices.min(axis=0)
        max_point = vertices.max(axis=0)
        size = max_point - min_point

        return {
            "width": float(size[0]),
            "depth": float(size[1]) if len(size) > 1 else float(size[0]),
            "height": float(size[2]) if len(size) > 2 else float(size[0])
        }

    def _calculate_scale_factor(
        self,
        current: Dict[str, float],
        target: Dict[str, float]
    ) -> float:
        """
        Calculate uniform scale factor.

        Args:
            current: Current dimensions
            target: Target dimensions

        Returns:
            Scale factor to apply
        """
        # Use the dimension that's most important for the object type
        # Default to height if available, otherwise use average

        if 'height' in target and 'height' in current and current['height'] > 0:
            return target['height'] / current['height']

        # Calculate average scale factor from all dimensions
        scales = []
        for dim in ['width', 'depth', 'height']:
            if dim in target and dim in current and current[dim] > 0:
                scales.append(target[dim] / current[dim])

        return np.mean(scales) if scales else 1.0

    def _apply_scale(
        self,
        obj: Dict[str, Any],
        scale_factor: float
    ) -> Dict[str, Any]:
        """
        Apply scale factor to object vertices.

        Args:
            obj: Object to scale
            scale_factor: Scale factor to apply

        Returns:
            Scaled object
        """
        scaled_obj = obj.copy()

        # Scale vertices
        if 'vertices' in scaled_obj and scaled_obj['vertices'] is not None:
            vertices = scaled_obj['vertices']
            if not isinstance(vertices, np.ndarray):
                vertices = np.array(vertices)

            scaled_obj['vertices'] = vertices * scale_factor

        return scaled_obj

    def analyze_scene_proportions(
        self,
        objects: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analyze proportions of all objects in a scene.

        Args:
            objects: List of objects to analyze

        Returns:
            Analysis report with proportion statistics
        """
        logger.info(f"Analyzing scene proportions for {len(objects)} objects")

        analysis = {
            "total_objects": len(objects),
            "objects": [],
            "scale_consistency": 0.0,
            "warnings": []
        }

        for obj in objects:
            obj_analysis = {
                "name": obj.get('name', 'unknown'),
                "current_size": self._calculate_current_dimensions(obj),
                "metadata": obj.get('metadata', {})
            }

            analysis["objects"].append(obj_analysis)

        # Check for proportion inconsistencies
        analysis["warnings"] = self._check_proportion_consistency(objects)

        return analysis

    def _check_proportion_consistency(
        self,
        objects: List[Dict[str, Any]]
    ) -> List[str]:
        """
        Check for proportion inconsistencies in the scene.

        Args:
            objects: List of objects to check

        Returns:
            List of warning messages
        """
        warnings = []

        # Example checks
        for i, obj1 in enumerate(objects):
            for obj2 in objects[i+1:]:
                # Check if a chair is larger than a table
                if ('chair' in obj1.get('name', '').lower() and
                    'table' in obj2.get('name', '').lower()):

                    dims1 = self._calculate_current_dimensions(obj1)
                    dims2 = self._calculate_current_dimensions(obj2)

                    if dims1.get('height', 0) > dims2.get('height', 0):
                        warnings.append(
                            f"Warning: Chair appears taller than table "
                            f"({dims1['height']:.2f}m vs {dims2['height']:.2f}m)"
                        )

        return warnings


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    analyzer = ProportionAnalyzer()

    # Create test objects
    test_objects = [
        {
            "name": "table",
            "vertices": np.array([
                [-0.6, -0.4, 0], [0.6, -0.4, 0],
                [0.6, 0.4, 0], [-0.6, 0.4, 0]
            ])
        },
        {
            "name": "chair",
            "vertices": np.array([
                [-0.25, -0.25, 0], [0.25, -0.25, 0],
                [0.25, 0.25, 0.5], [-0.25, 0.25, 0.5]
            ])
        }
    ]

    # Normalize
    normalized = analyzer.normalize(test_objects, {})

    print(f"\nNormalized {len(normalized)} objects:")
    for obj in normalized:
        print(f"  - {obj['name']}")
        print(f"    Scale factor: {obj['metadata'].get('scale_factor', 1.0):.3f}")
        print(f"    Target size: {obj['metadata'].get('target_dimensions', {})}")
