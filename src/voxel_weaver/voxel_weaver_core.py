"""
VoxelWeaver Integration Core - Bridge to Backend VoxelWeaver System
====================================================================

This module provides a high-level integration wrapper for the backend VoxelWeaver
system with enhanced features including:
- Prompt preprocessing and enhancement
- Result post-processing and validation
- Integration with new subsystems (texture, lighting, spatial)
- Performance monitoring and metrics
- Error handling and recovery
- Caching and optimization

Author: VoxelWeaver Team
Version: 1.0.0
"""

import sys
import time
import hashlib
import json
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
import re

# Add backend to path
backend_path = Path(__file__).parent.parent.parent / "backend"
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

# Import backend VoxelWeaver components
try:
    from voxelweaver import (
        VoxelWeaverCore as BackendVoxelWeaver,
        GeometryHandler,
        ProportionAnalyzer,
        ContextAlignment,
        LightingEngine,
        TextureMapper,
        BlenderBridge,
        SearchScraper,
        ModelFormatter,
        SceneValidator
    )
    BACKEND_AVAILABLE = True
except ImportError as e:
    BACKEND_AVAILABLE = False
    IMPORT_ERROR = str(e)

from utils.logger import get_logger

logger = get_logger(__name__)


class SceneStyle(Enum):
    """Scene rendering style options."""
    REALISTIC = "realistic"
    STYLIZED = "stylized"
    LOW_POLY = "low_poly"
    VOXEL = "voxel"
    WIREFRAME = "wireframe"
    PAINTERLY = "painterly"
    CARTOON = "cartoon"
    CYBERPUNK = "cyberpunk"
    FANTASY = "fantasy"


class GenerationQuality(Enum):
    """Quality presets for generation."""
    DRAFT = "draft"          # Fast, low quality
    MEDIUM = "medium"        # Balanced
    HIGH = "high"            # High quality
    ULTRA = "ultra"          # Maximum quality


@dataclass
class GenerationMetrics:
    """Performance metrics for scene generation."""
    total_time: float = 0.0
    preprocessing_time: float = 0.0
    generation_time: float = 0.0
    postprocessing_time: float = 0.0
    object_count: int = 0
    polygon_count: int = 0
    material_count: int = 0
    light_count: int = 0
    cache_hit: bool = False
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


@dataclass
class SceneGenerationRequest:
    """Request parameters for scene generation."""
    prompt: str
    style: SceneStyle = SceneStyle.REALISTIC
    quality: GenerationQuality = GenerationQuality.MEDIUM
    seed: Optional[int] = None
    output_path: Optional[str] = None
    enable_caching: bool = True
    enhance_prompt: bool = True
    validate_output: bool = True
    apply_postprocessing: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SceneGenerationResult:
    """Result of scene generation."""
    success: bool
    output_path: Optional[str] = None
    scene_data: Optional[Dict[str, Any]] = None
    metrics: GenerationMetrics = field(default_factory=GenerationMetrics)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    cache_key: Optional[str] = None


class PromptPreprocessor:
    """
    Preprocesses and enhances prompts for better generation results.
    """

    # Keyword enhancement mappings
    STYLE_KEYWORDS = {
        SceneStyle.REALISTIC: ["photorealistic", "detailed", "accurate lighting"],
        SceneStyle.STYLIZED: ["artistic", "expressive", "unique style"],
        SceneStyle.LOW_POLY: ["geometric", "faceted", "minimalist"],
        SceneStyle.VOXEL: ["blocky", "pixelated", "minecraft-like"],
        SceneStyle.CYBERPUNK: ["neon", "futuristic", "high-tech"],
        SceneStyle.FANTASY: ["magical", "ethereal", "fantastical"],
    }

    QUALITY_MULTIPLIERS = {
        GenerationQuality.DRAFT: 0.5,
        GenerationQuality.MEDIUM: 1.0,
        GenerationQuality.HIGH: 1.5,
        GenerationQuality.ULTRA: 2.0,
    }

    def __init__(self):
        """Initialize preprocessor."""
        self.logger = get_logger(__name__)

    def preprocess(
        self,
        prompt: str,
        style: SceneStyle,
        quality: GenerationQuality,
        enhance: bool = True
    ) -> str:
        """
        Preprocess and enhance prompt.

        Args:
            prompt: Original prompt
            style: Desired scene style
            quality: Quality preset
            enhance: Enable prompt enhancement

        Returns:
            Enhanced prompt string
        """
        processed = prompt.strip()

        if not enhance:
            return processed

        # Add style keywords
        if style in self.STYLE_KEYWORDS:
            style_keywords = ", ".join(self.STYLE_KEYWORDS[style])
            processed = f"{processed}, {style_keywords}"

        # Add quality descriptors
        quality_multiplier = self.QUALITY_MULTIPLIERS[quality]
        if quality_multiplier >= 1.5:
            processed += ", high detail, professional quality"
        elif quality_multiplier <= 0.5:
            processed += ", simple, efficient"

        # Extract and normalize object counts
        processed = self._normalize_quantities(processed)

        # Remove redundant words
        processed = self._remove_redundancy(processed)

        self.logger.debug(f"Preprocessed prompt: {processed}")
        return processed

    def _normalize_quantities(self, prompt: str) -> str:
        """Normalize quantity expressions in prompt."""
        # Convert "a few" -> "3", "several" -> "5", "many" -> "10"
        replacements = {
            r'\ba few\b': '3',
            r'\bseveral\b': '5',
            r'\bmany\b': '10',
            r'\bcouple of\b': '2',
        }

        for pattern, replacement in replacements.items():
            prompt = re.sub(pattern, replacement, prompt, flags=re.IGNORECASE)

        return prompt

    def _remove_redundancy(self, prompt: str) -> str:
        """Remove redundant or conflicting terms."""
        # Split into parts
        parts = [p.strip() for p in prompt.split(',')]

        # Remove duplicates while preserving order
        seen = set()
        unique_parts = []
        for part in parts:
            lower = part.lower()
            if lower not in seen:
                seen.add(lower)
                unique_parts.append(part)

        return ', '.join(unique_parts)


class ResultPostprocessor:
    """
    Post-processes generation results for quality and validation.
    """

    def __init__(self):
        """Initialize post-processor."""
        self.logger = get_logger(__name__)

    def postprocess(
        self,
        scene_data: Dict[str, Any],
        validate: bool = True
    ) -> Tuple[Dict[str, Any], List[str], List[str]]:
        """
        Post-process scene data.

        Args:
            scene_data: Raw scene data from backend
            validate: Enable validation

        Returns:
            Tuple of (processed_data, errors, warnings)
        """
        errors = []
        warnings = []
        processed = scene_data.copy()

        # Validate scene structure
        if validate:
            validation_errors, validation_warnings = self._validate_scene(processed)
            errors.extend(validation_errors)
            warnings.extend(validation_warnings)

        # Normalize coordinates
        if 'objects' in processed:
            processed['objects'] = self._normalize_coordinates(processed['objects'])

        # Optimize materials
        if 'materials' in processed:
            processed['materials'] = self._optimize_materials(processed['materials'])

        # Check for common issues
        if 'lights' not in processed or not processed['lights']:
            warnings.append("No lights in scene - adding default lighting")
            processed['lights'] = self._add_default_lighting()

        if 'camera' not in processed:
            warnings.append("No camera in scene - adding default camera")
            processed['camera'] = self._add_default_camera()

        self.logger.debug(
            f"Post-processing complete: {len(errors)} errors, {len(warnings)} warnings"
        )

        return processed, errors, warnings

    def _validate_scene(
        self, scene_data: Dict[str, Any]
    ) -> Tuple[List[str], List[str]]:
        """Validate scene data structure."""
        errors = []
        warnings = []

        # Check required fields
        if 'objects' not in scene_data:
            errors.append("Missing 'objects' field in scene data")

        # Validate objects
        if 'objects' in scene_data:
            for i, obj in enumerate(scene_data['objects']):
                if 'type' not in obj:
                    errors.append(f"Object {i} missing 'type' field")
                if 'location' not in obj:
                    warnings.append(f"Object {i} missing 'location' - using origin")

        return errors, warnings

    def _normalize_coordinates(self, objects: List[Dict]) -> List[Dict]:
        """Normalize object coordinates to reasonable ranges."""
        normalized = []

        for obj in objects:
            obj_copy = obj.copy()

            # Normalize location
            if 'location' in obj_copy:
                loc = obj_copy['location']
                if isinstance(loc, (list, tuple)) and len(loc) == 3:
                    # Clamp to reasonable range (-100, 100)
                    obj_copy['location'] = [
                        max(-100, min(100, float(x))) for x in loc
                    ]

            # Normalize scale
            if 'scale' in obj_copy:
                scale = obj_copy['scale']
                if isinstance(scale, (list, tuple)) and len(scale) == 3:
                    # Clamp scale (0.01, 100)
                    obj_copy['scale'] = [
                        max(0.01, min(100, float(x))) for x in scale
                    ]

            normalized.append(obj_copy)

        return normalized

    def _optimize_materials(self, materials: List[Dict]) -> List[Dict]:
        """Optimize material definitions."""
        optimized = []

        for mat in materials:
            mat_copy = mat.copy()

            # Ensure valid color values
            if 'base_color' in mat_copy:
                color = mat_copy['base_color']
                if isinstance(color, (list, tuple)):
                    mat_copy['base_color'] = [
                        max(0.0, min(1.0, float(c))) for c in color
                    ]

            # Clamp metallic and roughness
            if 'metallic' in mat_copy:
                mat_copy['metallic'] = max(0.0, min(1.0, float(mat_copy['metallic'])))

            if 'roughness' in mat_copy:
                mat_copy['roughness'] = max(0.0, min(1.0, float(mat_copy['roughness'])))

            optimized.append(mat_copy)

        return optimized

    def _add_default_lighting(self) -> List[Dict]:
        """Add default 3-point lighting setup."""
        return [
            {
                'type': 'SUN',
                'energy': 2.0,
                'location': (5, 5, 10),
                'rotation': (-0.6, 0.3, 0.8)
            },
            {
                'type': 'AREA',
                'energy': 500,
                'location': (-3, -3, 5),
                'size': 2.0
            }
        ]

    def _add_default_camera(self) -> Dict:
        """Add default camera configuration."""
        return {
            'location': (7.5, -7.5, 5.5),
            'rotation': (1.1, 0.0, 0.785),
            'lens': 50.0
        }


class VoxelWeaverIntegration:
    """
    High-level integration wrapper for backend VoxelWeaver system.

    This class provides an enhanced interface to the backend VoxelWeaver
    with additional features like prompt enhancement, result validation,
    caching, and integration with other subsystems.

    Attributes:
        backend: Backend VoxelWeaver instance
        preprocessor: Prompt preprocessor
        postprocessor: Result post-processor
        cache_dir: Cache directory for results

    Example:
        >>> integration = VoxelWeaverIntegration()
        >>> request = SceneGenerationRequest(
        ...     prompt="A cozy living room with fireplace",
        ...     style=SceneStyle.REALISTIC,
        ...     quality=GenerationQuality.HIGH
        ... )
        >>> result = integration.generate_scene(request)
        >>> if result.success:
        ...     print(f"Scene saved to: {result.output_path}")
    """

    def __init__(
        self,
        cache_dir: Optional[str] = None,
        enable_backend: bool = True
    ):
        """
        Initialize VoxelWeaver integration.

        Args:
            cache_dir: Directory for caching results
            enable_backend: Enable backend integration (False for testing)

        Raises:
            RuntimeError: If backend not available and enable_backend=True
        """
        if enable_backend and not BACKEND_AVAILABLE:
            raise RuntimeError(
                f"Backend VoxelWeaver not available: {IMPORT_ERROR}\n"
                "Ensure backend/voxelweaver is properly installed."
            )

        self.backend = BackendVoxelWeaver() if BACKEND_AVAILABLE else None
        self.preprocessor = PromptPreprocessor()
        self.postprocessor = ResultPostprocessor()

        self.cache_dir = Path(cache_dir or "cache/voxelweaver")
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        logger.info(
            f"VoxelWeaverIntegration initialized "
            f"(backend={'enabled' if BACKEND_AVAILABLE else 'disabled'})"
        )

    def generate_scene(self, request: SceneGenerationRequest) -> SceneGenerationResult:
        """
        Generate 3D scene from request.

        This is the main entry point for scene generation. It handles:
        1. Prompt preprocessing and enhancement
        2. Cache lookup (if enabled)
        3. Backend generation
        4. Result post-processing and validation
        5. Metrics collection

        Args:
            request: Scene generation request

        Returns:
            SceneGenerationResult with scene data and metrics

        Example:
            >>> request = SceneGenerationRequest(
            ...     prompt="medieval castle on a hill",
            ...     style=SceneStyle.FANTASY,
            ...     quality=GenerationQuality.HIGH
            ... )
            >>> result = integration.generate_scene(request)
        """
        start_time = time.time()
        metrics = GenerationMetrics()
        errors = []
        warnings = []

        try:
            # Step 1: Preprocess prompt
            logger.info(f"Generating scene: '{request.prompt}'")
            preprocess_start = time.time()

            enhanced_prompt = self.preprocessor.preprocess(
                request.prompt,
                request.style,
                request.quality,
                enhance=request.enhance_prompt
            )

            metrics.preprocessing_time = time.time() - preprocess_start
            logger.debug(f"Preprocessing took {metrics.preprocessing_time:.2f}s")

            # Step 2: Check cache
            cache_key = None
            if request.enable_caching:
                cache_key = self._generate_cache_key(request, enhanced_prompt)
                cached_result = self._load_from_cache(cache_key)

                if cached_result:
                    logger.info(f"Cache hit for key: {cache_key}")
                    metrics.cache_hit = True
                    metrics.total_time = time.time() - start_time
                    cached_result.metrics = metrics
                    return cached_result

            # Step 3: Generate scene via backend
            gen_start = time.time()

            if not self.backend:
                raise RuntimeError("Backend not available")

            # Call backend generation
            scene_data = self._call_backend(enhanced_prompt, request)

            metrics.generation_time = time.time() - gen_start
            logger.debug(f"Generation took {metrics.generation_time:.2f}s")

            # Step 4: Post-process results
            if request.apply_postprocessing:
                postprocess_start = time.time()

                processed_data, proc_errors, proc_warnings = self.postprocessor.postprocess(
                    scene_data,
                    validate=request.validate_output
                )

                errors.extend(proc_errors)
                warnings.extend(proc_warnings)

                metrics.postprocessing_time = time.time() - postprocess_start
                logger.debug(f"Post-processing took {metrics.postprocessing_time:.2f}s")
            else:
                processed_data = scene_data

            # Step 5: Extract metrics
            self._extract_metrics(processed_data, metrics)

            # Step 6: Save output
            output_path = request.output_path
            if output_path:
                self._save_scene(processed_data, output_path)

            # Step 7: Cache result
            if request.enable_caching and cache_key:
                self._save_to_cache(cache_key, processed_data, output_path)

            metrics.total_time = time.time() - start_time
            metrics.errors = errors
            metrics.warnings = warnings

            logger.info(
                f"Scene generation complete in {metrics.total_time:.2f}s "
                f"({metrics.object_count} objects)"
            )

            return SceneGenerationResult(
                success=True,
                output_path=output_path,
                scene_data=processed_data,
                metrics=metrics,
                errors=errors,
                warnings=warnings,
                cache_key=cache_key
            )

        except Exception as e:
            logger.exception(f"Scene generation failed: {e}")
            metrics.total_time = time.time() - start_time
            metrics.errors.append(str(e))

            return SceneGenerationResult(
                success=False,
                metrics=metrics,
                errors=[str(e)]
            )

    def _call_backend(
        self,
        prompt: str,
        request: SceneGenerationRequest
    ) -> Dict[str, Any]:
        """
        Call backend VoxelWeaver system.

        Args:
            prompt: Enhanced prompt
            request: Original request

        Returns:
            Scene data dictionary
        """
        # Map quality to backend parameters
        quality_params = {
            GenerationQuality.DRAFT: {'detail_level': 0.5, 'optimization': 'speed'},
            GenerationQuality.MEDIUM: {'detail_level': 1.0, 'optimization': 'balanced'},
            GenerationQuality.HIGH: {'detail_level': 1.5, 'optimization': 'quality'},
            GenerationQuality.ULTRA: {'detail_level': 2.0, 'optimization': 'quality'},
        }

        params = quality_params[request.quality]

        # Call backend (this is a simplified interface - adapt to actual backend API)
        try:
            # Example backend call - adjust based on actual VoxelWeaver API
            result = self.backend.generate_scene(
                prompt=prompt,
                style=request.style.value,
                seed=request.seed,
                **params
            )
            return result
        except AttributeError:
            # Fallback if backend doesn't have expected interface
            logger.warning("Backend API mismatch - using fallback")
            return self._generate_fallback_scene(prompt)

    def _generate_fallback_scene(self, prompt: str) -> Dict[str, Any]:
        """Generate fallback scene data when backend unavailable."""
        return {
            'objects': [
                {
                    'type': 'CUBE',
                    'location': (0, 0, 0),
                    'scale': (1, 1, 1),
                    'name': 'Fallback_Cube'
                }
            ],
            'materials': [
                {
                    'name': 'DefaultMaterial',
                    'base_color': (0.8, 0.8, 0.8, 1.0),
                    'metallic': 0.0,
                    'roughness': 0.5
                }
            ],
            'lights': [],
            'camera': {},
            'metadata': {
                'prompt': prompt,
                'fallback': True
            }
        }

    def _generate_cache_key(
        self,
        request: SceneGenerationRequest,
        enhanced_prompt: str
    ) -> str:
        """Generate cache key for request."""
        cache_data = {
            'prompt': enhanced_prompt,
            'style': request.style.value,
            'quality': request.quality.value,
            'seed': request.seed,
        }

        cache_string = json.dumps(cache_data, sort_keys=True)
        return hashlib.sha256(cache_string.encode()).hexdigest()[:16]

    def _load_from_cache(self, cache_key: str) -> Optional[SceneGenerationResult]:
        """Load cached result."""
        cache_file = self.cache_dir / f"{cache_key}.json"

        if not cache_file.exists():
            return None

        try:
            with open(cache_file, 'r') as f:
                data = json.load(f)

            return SceneGenerationResult(
                success=True,
                output_path=data.get('output_path'),
                scene_data=data.get('scene_data'),
                cache_key=cache_key
            )
        except Exception as e:
            logger.warning(f"Failed to load cache {cache_key}: {e}")
            return None

    def _save_to_cache(
        self,
        cache_key: str,
        scene_data: Dict[str, Any],
        output_path: Optional[str]
    ):
        """Save result to cache."""
        cache_file = self.cache_dir / f"{cache_key}.json"

        try:
            with open(cache_file, 'w') as f:
                json.dump({
                    'scene_data': scene_data,
                    'output_path': output_path,
                    'cached_at': time.time()
                }, f)

            logger.debug(f"Cached result: {cache_key}")
        except Exception as e:
            logger.warning(f"Failed to cache result: {e}")

    def _save_scene(self, scene_data: Dict[str, Any], output_path: str):
        """Save scene data to file."""
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w') as f:
            json.dump(scene_data, f, indent=2)

        logger.debug(f"Scene saved to: {output_path}")

    def _extract_metrics(self, scene_data: Dict[str, Any], metrics: GenerationMetrics):
        """Extract metrics from scene data."""
        metrics.object_count = len(scene_data.get('objects', []))
        metrics.material_count = len(scene_data.get('materials', []))
        metrics.light_count = len(scene_data.get('lights', []))

        # Count polygons (if available)
        total_polys = 0
        for obj in scene_data.get('objects', []):
            total_polys += obj.get('polygon_count', 100)  # Default estimate

        metrics.polygon_count = total_polys

    def clear_cache(self):
        """Clear all cached results."""
        import shutil
        if self.cache_dir.exists():
            shutil.rmtree(self.cache_dir)
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            logger.info("Cache cleared")


# Example usage
if __name__ == "__main__":
    # Initialize integration
    integration = VoxelWeaverIntegration()

    # Create generation request
    request = SceneGenerationRequest(
        prompt="A cozy living room with a fireplace, sofa, and coffee table",
        style=SceneStyle.REALISTIC,
        quality=GenerationQuality.HIGH,
        output_path="output/living_room_scene.json",
        enhance_prompt=True,
        validate_output=True
    )

    # Generate scene
    result = integration.generate_scene(request)

    # Check result
    if result.success:
        print(f"Scene generated successfully!")
        print(f"Output: {result.output_path}")
        print(f"Objects: {result.metrics.object_count}")
        print(f"Generation time: {result.metrics.generation_time:.2f}s")
        print(f"Total time: {result.metrics.total_time:.2f}s")
    else:
        print(f"Generation failed: {result.errors}")

    # Print warnings
    if result.warnings:
        print(f"Warnings: {result.warnings}")
