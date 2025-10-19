"""
Search and Scrape - External reference gathering for Blender scene generation.
Scrapes open-source Blender projects, assets, and real-world data for training.
"""

import re
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class ExternalReference:
    """A reference found from external sources."""
    source: str  # GitHub, OpenGameArt, Free3D, etc.
    object_type: str  # cube, sphere, tree, car, etc.
    url: str
    description: str
    dimensions: Optional[Dict[str, float]] = None  # width, height, depth in meters
    material_hints: List[str] = None
    technique: Optional[str] = None  # modeling technique used
    quality_score: float = 0.5  # 0.0 to 1.0

    def __post_init__(self):
        if self.material_hints is None:
            self.material_hints = []


class ReferenceSearcher:
    """
    Searches external sources for Blender references and real-world data.
    """

    # Real-world dimension databases
    DIMENSION_DATABASE = {
        # Common objects with real dimensions (in meters)
        "chair": {"width": 0.5, "height": 0.9, "depth": 0.5},
        "table": {"width": 1.2, "height": 0.75, "depth": 0.8},
        "desk": {"width": 1.4, "height": 0.75, "depth": 0.7},
        "door": {"width": 0.9, "height": 2.1, "depth": 0.05},
        "window": {"width": 1.2, "height": 1.5, "depth": 0.1},
        "bed": {"width": 1.5, "height": 0.6, "depth": 2.0},
        "sofa": {"width": 2.0, "height": 0.85, "depth": 0.9},
        "car": {"width": 1.8, "height": 1.5, "depth": 4.5},
        "tree": {"width": 2.0, "height": 8.0, "depth": 2.0},
        "bush": {"width": 1.0, "height": 1.2, "depth": 1.0},
        "human": {"width": 0.5, "height": 1.75, "depth": 0.3},
        "dog": {"width": 0.3, "height": 0.6, "depth": 0.8},
        "cat": {"width": 0.2, "height": 0.25, "depth": 0.4},
        "bird": {"width": 0.15, "height": 0.2, "depth": 0.2},
        "cup": {"width": 0.08, "height": 0.1, "depth": 0.08},
        "glass": {"width": 0.07, "height": 0.15, "depth": 0.07},
        "bottle": {"width": 0.07, "height": 0.25, "depth": 0.07},
        "lamp": {"width": 0.3, "height": 0.5, "depth": 0.3},
        "monitor": {"width": 0.6, "height": 0.4, "depth": 0.05},
        "keyboard": {"width": 0.45, "height": 0.03, "depth": 0.15},
        "mouse": {"width": 0.06, "height": 0.04, "depth": 0.11},
        "book": {"width": 0.15, "height": 0.23, "depth": 0.03},
        "building": {"width": 20.0, "height": 30.0, "depth": 15.0},
        "house": {"width": 10.0, "height": 6.0, "depth": 12.0},
        "room": {"width": 4.0, "height": 2.7, "depth": 5.0},
    }

    # Material suggestions based on object types
    MATERIAL_HINTS = {
        "chair": ["wood", "metal", "fabric", "leather"],
        "table": ["wood", "glass", "metal"],
        "car": ["metal", "glass", "rubber", "plastic"],
        "tree": ["bark", "leaves", "wood"],
        "glass": ["glass", "transparent"],
        "bird": ["feathers", "glass", "metal", "ceramic"],
        "fabric": ["cloth", "textile", "velvet", "silk"],
        "floor": ["wood", "tile", "carpet", "concrete"],
        "wall": ["paint", "wallpaper", "concrete", "brick"],
    }

    # Known Blender resource sources (simulated - in production would use API)
    SEARCH_SOURCES = [
        "GitHub:awesome-blender",
        "GitHub:blender-models",
        "OpenGameArt.org",
        "Free3D.com",
        "CGTrader.com",
        "BlendSwap.com",
        "Dimensions.com",  # Real-world dimensions
    ]

    def __init__(self, max_results: int = 50, enabled: bool = True):
        """
        Initialize the reference searcher.

        Args:
            max_results: Maximum number of references to fetch
            enabled: Whether search is enabled
        """
        self.max_results = max_results
        self.enabled = enabled
        self._cache: Dict[str, List[ExternalReference]] = {}

        logger.info(f"ReferenceSearcher initialized (enabled={enabled}, max={max_results})")

    def search_concept(self, concept: str, prompt: str) -> List[Dict[str, Any]]:
        """
        Search external sources for references matching the concept.

        Args:
            concept: Scene concept description
            prompt: Original user prompt

        Returns:
            List of external references with metadata
        """
        if not self.enabled:
            logger.info("Reference search disabled")
            return []

        logger.info(f"Searching external references for: {concept[:100]}...")

        # Extract objects from concept
        objects = self._extract_objects(concept)
        logger.info(f"Extracted {len(objects)} objects: {objects}")

        references = []
        for obj in objects[:10]:  # Limit to top 10 objects
            refs = self._search_object(obj)
            references.extend(refs)

        # Deduplicate and sort by quality
        references = self._deduplicate(references)
        references.sort(key=lambda r: r.quality_score, reverse=True)

        # Convert to dict for JSON serialization
        results = [self._reference_to_dict(r) for r in references[:self.max_results]]

        logger.info(f"Found {len(results)} total references")
        return results

    def _extract_objects(self, concept: str) -> List[str]:
        """Extract object names from concept description."""
        # Simple keyword extraction (in production, use NLP)
        concept_lower = concept.lower()

        found_objects = []

        # Check dimension database keys
        for obj_name in self.DIMENSION_DATABASE.keys():
            if obj_name in concept_lower:
                found_objects.append(obj_name)

        # Common 3D objects
        common_objects = [
            "cube", "sphere", "cylinder", "cone", "plane",
            "torus", "suzanne", "icosphere", "light", "camera"
        ]

        for obj in common_objects:
            if obj in concept_lower and obj not in found_objects:
                found_objects.append(obj)

        # Extract words that might be objects (nouns)
        words = re.findall(r'\b[a-z]{3,}\b', concept_lower)
        for word in words:
            if word not in found_objects and word not in ["the", "and", "with", "for", "scene"]:
                found_objects.append(word)

        return found_objects[:20]  # Limit to 20 objects

    def _search_object(self, object_name: str) -> List[ExternalReference]:
        """
        Search for a specific object across all sources.

        Args:
            object_name: Name of the object to search for

        Returns:
            List of references found
        """
        # Check cache first
        if object_name in self._cache:
            return self._cache[object_name]

        references = []

        # Search dimension database
        if object_name in self.DIMENSION_DATABASE:
            ref = ExternalReference(
                source="Dimensions.com",
                object_type=object_name,
                url=f"https://dimensions.com/{object_name}",
                description=f"Real-world dimensions for {object_name}",
                dimensions=self.DIMENSION_DATABASE[object_name],
                material_hints=self.MATERIAL_HINTS.get(object_name, []),
                technique="reference_dimensions",
                quality_score=0.9
            )
            references.append(ref)

        # Simulate GitHub search
        github_ref = ExternalReference(
            source="GitHub:blender-models",
            object_type=object_name,
            url=f"https://github.com/search?q=blender+{object_name}+.blend",
            description=f"Blender models of {object_name} from open-source projects",
            material_hints=self.MATERIAL_HINTS.get(object_name, ["generic"]),
            technique="mesh_modeling",
            quality_score=0.7
        )
        references.append(github_ref)

        # Simulate Free3D search
        free3d_ref = ExternalReference(
            source="Free3D.com",
            object_type=object_name,
            url=f"https://free3d.com/3d-models/{object_name}",
            description=f"Free 3D models of {object_name}",
            material_hints=self.MATERIAL_HINTS.get(object_name, ["textured"]),
            technique="mixed",
            quality_score=0.6
        )
        references.append(free3d_ref)

        # Simulate BlendSwap search
        blendswap_ref = ExternalReference(
            source="BlendSwap.com",
            object_type=object_name,
            url=f"https://blendswap.com/search?q={object_name}",
            description=f"Community Blender files for {object_name}",
            material_hints=self.MATERIAL_HINTS.get(object_name, []),
            technique="community_blend",
            quality_score=0.75
        )
        references.append(blendswap_ref)

        # Cache results
        self._cache[object_name] = references

        return references

    def _deduplicate(self, references: List[ExternalReference]) -> List[ExternalReference]:
        """Remove duplicate references."""
        seen = set()
        unique = []

        for ref in references:
            key = (ref.source, ref.object_type)
            if key not in seen:
                seen.add(key)
                unique.append(ref)

        return unique

    def _reference_to_dict(self, ref: ExternalReference) -> Dict[str, Any]:
        """Convert reference to dictionary."""
        return {
            "source": ref.source,
            "object_type": ref.object_type,
            "url": ref.url,
            "description": ref.description,
            "dimensions": ref.dimensions,
            "material_hints": ref.material_hints,
            "technique": ref.technique,
            "quality_score": ref.quality_score
        }

    def get_dimension_estimate(self, object_name: str) -> Optional[Dict[str, float]]:
        """
        Get estimated dimensions for an object.

        Args:
            object_name: Name of the object

        Returns:
            Dictionary with width, height, depth in meters
        """
        object_lower = object_name.lower()

        # Direct match
        if object_lower in self.DIMENSION_DATABASE:
            return self.DIMENSION_DATABASE[object_lower]

        # Partial match
        for key, dims in self.DIMENSION_DATABASE.items():
            if key in object_lower or object_lower in key:
                return dims

        # Default fallback (1 meter cube)
        logger.warning(f"No dimension data for '{object_name}', using default")
        return {"width": 1.0, "height": 1.0, "depth": 1.0}

    def get_material_suggestions(self, object_name: str) -> List[str]:
        """Get material suggestions for an object type."""
        object_lower = object_name.lower()

        # Direct match
        if object_lower in self.MATERIAL_HINTS:
            return self.MATERIAL_HINTS[object_lower]

        # Partial match
        for key, materials in self.MATERIAL_HINTS.items():
            if key in object_lower:
                return materials

        # Default materials
        return ["generic", "default"]
