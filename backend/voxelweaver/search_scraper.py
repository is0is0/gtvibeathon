"""
Search Scraper Module
---------------------
Gathers reference data from online 3D model repositories.

This module searches public 3D model databases to find reference geometries,
dimensions, and metadata to improve scene generation accuracy.
"""

import logging
import json
import hashlib
import time
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import pickle

logger = logging.getLogger(__name__)


@dataclass
class ModelReference:
    """Reference to a 3D model."""
    name: str
    source: str  # Source repository/website
    url: str
    format: str  # File format (obj, fbx, glb, etc.)
    dimensions: Dict[str, float]  # width, height, depth in meters
    category: str
    tags: List[str] = field(default_factory=list)
    license: str = "unknown"
    thumbnail_url: Optional[str] = None
    download_url: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'name': self.name,
            'source': self.source,
            'url': self.url,
            'format': self.format,
            'dimensions': self.dimensions,
            'category': self.category,
            'tags': self.tags,
            'license': self.license,
            'thumbnail_url': self.thumbnail_url,
            'download_url': self.download_url,
            'metadata': self.metadata
        }


@dataclass
class SearchResult:
    """Search results container."""
    query: str
    models: List[ModelReference]
    total_results: int
    search_time: float
    timestamp: datetime
    cached: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'query': self.query,
            'models': [model.to_dict() for model in self.models],
            'total_results': self.total_results,
            'search_time': self.search_time,
            'timestamp': self.timestamp.isoformat(),
            'cached': self.cached
        }


class SearchCache:
    """Simple file-based cache for search results."""

    def __init__(self, cache_dir: Path, ttl_hours: int = 24):
        """
        Initialize search cache.

        Args:
            cache_dir: Directory to store cache files
            ttl_hours: Time-to-live for cached results in hours
        """
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl = timedelta(hours=ttl_hours)

    def _get_cache_key(self, query: str) -> str:
        """Generate cache key from query."""
        return hashlib.md5(query.lower().encode()).hexdigest()

    def _get_cache_path(self, query: str) -> Path:
        """Get cache file path for query."""
        key = self._get_cache_key(query)
        return self.cache_dir / f"{key}.cache"

    def get(self, query: str) -> Optional[SearchResult]:
        """
        Get cached search results.

        Args:
            query: Search query

        Returns:
            Cached SearchResult or None
        """
        cache_path = self._get_cache_path(query)

        if not cache_path.exists():
            return None

        try:
            # Check if cache is expired
            mtime = datetime.fromtimestamp(cache_path.stat().st_mtime)
            if datetime.now() - mtime > self.ttl:
                logger.debug(f"Cache expired for query: {query}")
                cache_path.unlink()
                return None

            # Load cached result
            with open(cache_path, 'rb') as f:
                result = pickle.load(f)
                result.cached = True
                logger.info(f"Cache hit for query: {query}")
                return result

        except Exception as e:
            logger.warning(f"Failed to load cache: {e}")
            return None

    def set(self, query: str, result: SearchResult) -> None:
        """
        Cache search results.

        Args:
            query: Search query
            result: Search results to cache
        """
        cache_path = self._get_cache_path(query)

        try:
            with open(cache_path, 'wb') as f:
                pickle.dump(result, f)
            logger.debug(f"Cached results for query: {query}")

        except Exception as e:
            logger.warning(f"Failed to cache results: {e}")

    def clear(self) -> None:
        """Clear all cached results."""
        for cache_file in self.cache_dir.glob("*.cache"):
            cache_file.unlink()
        logger.info("Cache cleared")


class SearchScraper:
    """
    Searches online 3D model repositories for reference data.

    This class searches public 3D model databases to find reference
    geometries and metadata to improve scene generation.

    Example:
        >>> scraper = SearchScraper()
        >>> results = scraper.search_references("modern office chair")
        >>> print(f"Found {len(results['models'])} references")
    """

    def __init__(
        self,
        cache_dir: Optional[Path] = None,
        enable_cache: bool = True,
        max_results: int = 10
    ):
        """
        Initialize search scraper.

        Args:
            cache_dir: Directory for caching results
            enable_cache: Whether to enable caching
            max_results: Maximum results per search
        """
        self.cache_dir = cache_dir or Path.home() / ".voxelweaver" / "cache"
        self.enable_cache = enable_cache
        self.max_results = max_results

        if enable_cache:
            self.cache = SearchCache(self.cache_dir)
        else:
            self.cache = None

        # Source repositories (in production, these would be actual APIs)
        self.sources = {
            'sketchfab': 'https://sketchfab.com',
            'turbosquid': 'https://turbosquid.com',
            'cgtrader': 'https://cgtrader.com',
            'free3d': 'https://free3d.com',
            'thingiverse': 'https://thingiverse.com'
        }

        # Standard object dimensions database
        self.dimension_database = self._load_dimension_database()

        logger.info(f"SearchScraper initialized (cache: {enable_cache})")

    def _load_dimension_database(self) -> Dict[str, Dict[str, float]]:
        """
        Load database of standard object dimensions.

        Returns:
            Dictionary of object dimensions
        """
        return {
            # Furniture
            "chair": {"width": 0.5, "depth": 0.5, "height": 0.85},
            "table": {"width": 1.2, "depth": 0.8, "height": 0.75},
            "desk": {"width": 1.4, "depth": 0.7, "height": 0.75},
            "sofa": {"width": 2.0, "depth": 0.9, "height": 0.85},
            "bed": {"width": 1.6, "depth": 2.0, "height": 0.6},
            "nightstand": {"width": 0.5, "depth": 0.4, "height": 0.6},
            "bookshelf": {"width": 0.8, "depth": 0.3, "height": 2.0},
            "coffee_table": {"width": 1.2, "depth": 0.6, "height": 0.45},

            # Appliances
            "refrigerator": {"width": 0.7, "depth": 0.7, "height": 1.8},
            "oven": {"width": 0.6, "depth": 0.6, "height": 0.9},
            "microwave": {"width": 0.5, "depth": 0.4, "height": 0.3},
            "dishwasher": {"width": 0.6, "depth": 0.6, "height": 0.85},
            "washing_machine": {"width": 0.6, "depth": 0.6, "height": 0.85},

            # Electronics
            "tv_55": {"width": 1.23, "depth": 0.08, "height": 0.71},
            "monitor": {"width": 0.6, "depth": 0.2, "height": 0.4},
            "laptop": {"width": 0.35, "depth": 0.25, "height": 0.02},

            # Lighting
            "floor_lamp": {"width": 0.3, "depth": 0.3, "height": 1.5},
            "table_lamp": {"width": 0.25, "depth": 0.25, "height": 0.5},
            "ceiling_light": {"width": 0.4, "depth": 0.4, "height": 0.2},

            # Decoration
            "vase": {"width": 0.2, "depth": 0.2, "height": 0.3},
            "plant_pot": {"width": 0.3, "depth": 0.3, "height": 0.4},
            "picture_frame": {"width": 0.5, "depth": 0.05, "height": 0.7},
            "rug": {"width": 2.0, "depth": 1.5, "height": 0.01},

            # Architectural
            "door": {"width": 0.9, "depth": 0.05, "height": 2.0},
            "window": {"width": 1.2, "depth": 0.15, "height": 1.5},
        }

    def search_references(
        self,
        prompt: str,
        category: Optional[str] = None,
        max_results: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Search for reference models based on prompt.

        This is the main entry point for reference searching. It parses
        the prompt and searches multiple sources for relevant models.

        Args:
            prompt: Search query or scene description
            category: Optional category filter
            max_results: Maximum results to return (overrides default)

        Returns:
            Dictionary containing:
                - models: List of model references
                - dimensions: Dimension data
                - metadata: Search metadata

        Example:
            >>> scraper = SearchScraper()
            >>> results = scraper.search_references("modern kitchen")
            >>> for model in results['models']:
            ...     print(f"{model['name']}: {model['dimensions']}")
        """
        logger.info(f"Searching references for: {prompt}")

        start_time = time.time()
        max_results = max_results or self.max_results

        # Check cache
        if self.cache:
            cached_result = self.cache.get(prompt)
            if cached_result:
                return self._format_search_result(cached_result)

        # Extract object keywords from prompt
        keywords = self._extract_keywords(prompt)

        # Search for models
        models = []
        for keyword in keywords:
            keyword_models = self._search_keyword(keyword, category)
            models.extend(keyword_models)

            if len(models) >= max_results:
                break

        models = models[:max_results]

        # Create search result
        search_time = time.time() - start_time
        result = SearchResult(
            query=prompt,
            models=models,
            total_results=len(models),
            search_time=search_time,
            timestamp=datetime.now()
        )

        # Cache result
        if self.cache:
            self.cache.set(prompt, result)

        logger.info(f"Found {len(models)} references in {search_time:.2f}s")

        return self._format_search_result(result)

    def _extract_keywords(self, prompt: str) -> List[str]:
        """
        Extract object keywords from prompt.

        Args:
            prompt: Scene description

        Returns:
            List of object keywords
        """
        # Simple keyword extraction (can be enhanced with NLP)
        prompt_lower = prompt.lower()
        keywords = []

        # Check against dimension database
        for object_name in self.dimension_database.keys():
            # Handle multi-word names
            check_name = object_name.replace('_', ' ')
            if check_name in prompt_lower or object_name in prompt_lower:
                keywords.append(object_name)

        # If no keywords found, extract nouns (simplified)
        if not keywords:
            common_objects = [
                'chair', 'table', 'sofa', 'bed', 'lamp', 'desk',
                'shelf', 'cabinet', 'door', 'window', 'plant',
                'picture', 'tv', 'computer', 'phone'
            ]
            for obj in common_objects:
                if obj in prompt_lower:
                    keywords.append(obj)

        logger.debug(f"Extracted keywords: {keywords}")
        return keywords if keywords else ['generic_object']

    def _search_keyword(
        self,
        keyword: str,
        category: Optional[str] = None
    ) -> List[ModelReference]:
        """
        Search for models matching a keyword.

        Args:
            keyword: Object keyword
            category: Optional category filter

        Returns:
            List of model references
        """
        models = []

        # In production, this would query actual APIs
        # For now, generate mock references from dimension database

        if keyword in self.dimension_database:
            dimensions = self.dimension_database[keyword]

            # Create mock reference
            model = ModelReference(
                name=f"{keyword.replace('_', ' ').title()} Model",
                source='dimension_database',
                url=f'https://example.com/models/{keyword}',
                format='obj',
                dimensions=dimensions,
                category=category or 'generic',
                tags=[keyword, category or 'object'],
                license='CC0',
                thumbnail_url=None,
                download_url=None,
                metadata={
                    'verified': True,
                    'quality': 'high',
                    'poly_count': 5000
                }
            )

            models.append(model)

            # Add a few variations
            for i, variant in enumerate(['standard', 'modern', 'classic'][:2]):
                variant_dims = dimensions.copy()
                # Slight variations in dimensions
                variant_dims['width'] *= (0.9 + i * 0.1)
                variant_dims['depth'] *= (0.95 + i * 0.05)

                variant_model = ModelReference(
                    name=f"{variant.title()} {keyword.replace('_', ' ').title()}",
                    source='dimension_database',
                    url=f'https://example.com/models/{keyword}_{variant}',
                    format='glb',
                    dimensions=variant_dims,
                    category=category or 'generic',
                    tags=[keyword, variant, category or 'object'],
                    license='CC-BY',
                    thumbnail_url=None,
                    download_url=None,
                    metadata={
                        'verified': True,
                        'quality': 'medium',
                        'poly_count': 3000
                    }
                )

                models.append(variant_model)

        return models

    def _format_search_result(self, result: SearchResult) -> Dict[str, Any]:
        """
        Format search result for output.

        Args:
            result: SearchResult instance

        Returns:
            Formatted dictionary
        """
        # Extract unique dimensions
        dimensions_map = {}
        for model in result.models:
            key = model.name.lower().split()[0]
            if key not in dimensions_map:
                dimensions_map[key] = model.dimensions

        return {
            'models': [model.to_dict() for model in result.models],
            'dimensions': dimensions_map,
            'metadata': {
                'query': result.query,
                'total_results': result.total_results,
                'search_time': result.search_time,
                'timestamp': result.timestamp.isoformat(),
                'cached': result.cached
            }
        }

    def get_dimensions(self, object_name: str) -> Optional[Dict[str, float]]:
        """
        Get standard dimensions for an object.

        Args:
            object_name: Object name or type

        Returns:
            Dimensions dictionary or None

        Example:
            >>> scraper = SearchScraper()
            >>> dims = scraper.get_dimensions("chair")
            >>> print(f"Chair dimensions: {dims}")
        """
        object_key = object_name.lower().replace(' ', '_')

        if object_key in self.dimension_database:
            return self.dimension_database[object_key].copy()

        # Try partial match
        for key, dims in self.dimension_database.items():
            if object_key in key or key in object_key:
                return dims.copy()

        logger.warning(f"No dimensions found for: {object_name}")
        return None

    def download_model(
        self,
        model: ModelReference,
        output_dir: Path
    ) -> Optional[Path]:
        """
        Download a model file.

        Args:
            model: Model reference to download
            output_dir: Directory to save model

        Returns:
            Path to downloaded file or None

        Example:
            >>> scraper = SearchScraper()
            >>> results = scraper.search_references("chair")
            >>> if results['models']:
            ...     path = scraper.download_model(
            ...         results['models'][0],
            ...         Path("models")
            ...     )
        """
        logger.info(f"Downloading model: {model.name}")

        if not model.download_url:
            logger.warning(f"No download URL for model: {model.name}")
            return None

        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"{model.name.replace(' ', '_')}.{model.format}"

        # In production, this would actually download the file
        # For now, just log the attempt
        logger.info(f"Would download from: {model.download_url}")
        logger.info(f"To: {output_path}")

        return output_path

    def clear_cache(self) -> None:
        """
        Clear search cache.

        Example:
            >>> scraper = SearchScraper()
            >>> scraper.clear_cache()
        """
        if self.cache:
            self.cache.clear()
            logger.info("Search cache cleared")
        else:
            logger.warning("Cache is not enabled")


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    scraper = SearchScraper(enable_cache=True, max_results=5)

    # Test searches
    test_queries = [
        "modern living room with sofa and coffee table",
        "office desk with chair",
        "bedroom with bed and nightstand"
    ]

    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"Searching: {query}")
        print('='*60)

        results = scraper.search_references(query)

        print(f"\nFound {results['metadata']['total_results']} models")
        print(f"Search time: {results['metadata']['search_time']:.3f}s")
        print(f"Cached: {results['metadata']['cached']}")

        print(f"\nModels:")
        for model in results['models'][:3]:  # Show first 3
            print(f"\n  - {model['name']}")
            print(f"    Source: {model['source']}")
            print(f"    Format: {model['format']}")
            print(f"    Dimensions: {model['dimensions']}")
            print(f"    Tags: {', '.join(model['tags'])}")

        print(f"\nDimension database:")
        for name, dims in results['dimensions'].items():
            print(f"  - {name}: {dims}")

    # Test dimension lookup
    print(f"\n{'='*60}")
    print("Testing dimension lookup")
    print('='*60)

    objects = ["chair", "table", "lamp", "refrigerator"]
    for obj in objects:
        dims = scraper.get_dimensions(obj)
        if dims:
            print(f"\n{obj.title()}:")
            print(f"  Width: {dims['width']}m")
            print(f"  Depth: {dims['depth']}m")
            print(f"  Height: {dims['height']}m")
