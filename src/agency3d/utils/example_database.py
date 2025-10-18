"""Example database for RAG (Retrieval-Augmented Generation) and fine-tuning."""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class ExampleScene:
    """Represents an example scene for learning."""
    prompt: str
    concept: str
    builder_script: str
    texture_script: str
    render_script: str
    animation_script: str
    rigging_script: Optional[str] = None
    compositing_script: Optional[str] = None
    sequence_script: Optional[str] = None
    tags: List[str] = None
    quality_score: float = 0.0
    created_at: str = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()


@dataclass
class Pattern:
    """Represents a reusable pattern extracted from scenes."""
    pattern_type: str  # 'material', 'geometry', 'lighting', 'animation'
    description: str
    node_types: List[str]
    usage_context: str
    success_rate: float = 0.0
    usage_count: int = 0


class ExampleDatabase:
    """Database for storing and retrieving scene examples and patterns."""
    
    def __init__(self, db_path: Path = Path("./data/example_database.json")):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.examples: List[ExampleScene] = []
        self.patterns: List[Pattern] = []
        self._load_database()
    
    def _load_database(self) -> None:
        """Load examples and patterns from database file."""
        if self.db_path.exists():
            try:
                with open(self.db_path, 'r') as f:
                    data = json.load(f)
                    self.examples = [ExampleScene(**ex) for ex in data.get('examples', [])]
                    self.patterns = [Pattern(**p) for p in data.get('patterns', [])]
                logger.info(f"Loaded {len(self.examples)} examples and {len(self.patterns)} patterns")
            except Exception as e:
                logger.error(f"Error loading database: {e}")
                self.examples = []
                self.patterns = []
        else:
            self.examples = []
            self.patterns = []
    
    def _save_database(self) -> None:
        """Save examples and patterns to database file."""
        try:
            data = {
                'examples': [asdict(ex) for ex in self.examples],
                'patterns': [asdict(p) for p in self.patterns]
            }
            with open(self.db_path, 'w') as f:
                json.dump(data, f, indent=2)
            logger.info("Database saved successfully")
        except Exception as e:
            logger.error(f"Error saving database: {e}")
    
    def add_example(self, example: ExampleScene) -> None:
        """Add a new example scene to the database."""
        self.examples.append(example)
        self._extract_patterns(example)
        self._save_database()
        logger.info(f"Added example: {example.prompt[:50]}...")
    
    def find_similar_examples(self, prompt: str, k: int = 3) -> List[ExampleScene]:
        """Find similar examples based on prompt similarity."""
        # Simple keyword-based similarity (could be enhanced with embeddings)
        prompt_lower = prompt.lower()
        prompt_words = set(prompt_lower.split())
        
        scored_examples = []
        for example in self.examples:
            example_words = set(example.prompt.lower().split())
            # Calculate Jaccard similarity
            intersection = len(prompt_words.intersection(example_words))
            union = len(prompt_words.union(example_words))
            similarity = intersection / union if union > 0 else 0
            
            # Boost score for quality examples
            score = similarity + (example.quality_score * 0.1)
            scored_examples.append((score, example))
        
        # Sort by score and return top k
        scored_examples.sort(key=lambda x: x[0], reverse=True)
        return [ex[1] for ex in scored_examples[:k]]
    
    def find_examples_by_tags(self, tags: List[str]) -> List[ExampleScene]:
        """Find examples that match specific tags."""
        matching_examples = []
        for example in self.examples:
            if any(tag in example.tags for tag in tags):
                matching_examples.append(example)
        return matching_examples
    
    def get_high_quality_examples(self, min_score: float = 0.7) -> List[ExampleScene]:
        """Get examples with quality score above threshold."""
        return [ex for ex in self.examples if ex.quality_score >= min_score]
    
    def _extract_patterns(self, example: ExampleScene) -> None:
        """Extract reusable patterns from an example scene."""
        # Extract material patterns
        if example.texture_script:
            material_patterns = self._extract_material_patterns(example.texture_script)
            for pattern in material_patterns:
                self._add_or_update_pattern(pattern)
        
        # Extract geometry patterns
        if example.builder_script:
            geometry_patterns = self._extract_geometry_patterns(example.builder_script)
            for pattern in geometry_patterns:
                self._add_or_update_pattern(pattern)
        
        # Extract animation patterns
        if example.animation_script:
            animation_patterns = self._extract_animation_patterns(example.animation_script)
            for pattern in animation_patterns:
                self._add_or_update_pattern(pattern)
    
    def _extract_material_patterns(self, texture_script: str) -> List[Pattern]:
        """Extract material patterns from texture script."""
        patterns = []
        
        # Look for common shader node patterns
        if "PrincipledBSDF" in texture_script:
            patterns.append(Pattern(
                pattern_type="material",
                description="Principled BSDF material setup",
                node_types=["PrincipledBSDF", "ImageTexture", "Mapping"],
                usage_context="realistic materials"
            ))
        
        if "Emission" in texture_script:
            patterns.append(Pattern(
                pattern_type="material",
                description="Emission material for glowing objects",
                node_types=["Emission", "ColorRamp", "NoiseTexture"],
                usage_context="glowing, neon, or light-emitting materials"
            ))
        
        if "Glass" in texture_script or "Transparent" in texture_script:
            patterns.append(Pattern(
                pattern_type="material",
                description="Glass/transparent material setup",
                node_types=["GlassBSDF", "TransparentBSDF", "Fresnel"],
                usage_context="transparent or glass materials"
            ))
        
        return patterns
    
    def _extract_geometry_patterns(self, builder_script: str) -> List[Pattern]:
        """Extract geometry patterns from builder script."""
        patterns = []
        
        # Look for modifier patterns
        if "Array" in builder_script:
            patterns.append(Pattern(
                pattern_type="geometry",
                description="Array modifier for repetitive objects",
                node_types=["Array"],
                usage_context="creating multiple instances of objects"
            ))
        
        if "Subdivision" in builder_script:
            patterns.append(Pattern(
                pattern_type="geometry",
                description="Subdivision surface for smooth geometry",
                node_types=["SubdivisionSurface"],
                usage_context="smooth, organic shapes"
            ))
        
        if "Boolean" in builder_script:
            patterns.append(Pattern(
                pattern_type="geometry",
                description="Boolean operations for complex shapes",
                node_types=["Boolean"],
                usage_context="cutting, joining, or intersecting objects"
            ))
        
        return patterns
    
    def _extract_animation_patterns(self, animation_script: str) -> List[Pattern]:
        """Extract animation patterns from animation script."""
        patterns = []
        
        # Look for easing patterns
        if "BEZIER" in animation_script:
            patterns.append(Pattern(
                pattern_type="animation",
                description="Bezier easing for smooth animation",
                node_types=["BEZIER"],
                usage_context="smooth, natural movement"
            ))
        
        if "SINE" in animation_script:
            patterns.append(Pattern(
                pattern_type="animation",
                description="Sine easing for oscillating motion",
                node_types=["SINE"],
                usage_context="bouncing, swaying, or oscillating movement"
            ))
        
        if "rotation_euler" in animation_script:
            patterns.append(Pattern(
                pattern_type="animation",
                description="Rotation animation pattern",
                node_types=["rotation_euler"],
                usage_context="rotating objects"
            ))
        
        return patterns
    
    def _add_or_update_pattern(self, new_pattern: Pattern) -> None:
        """Add new pattern or update existing one."""
        for i, existing_pattern in enumerate(self.patterns):
            if (existing_pattern.pattern_type == new_pattern.pattern_type and
                existing_pattern.description == new_pattern.description):
                # Update existing pattern
                existing_pattern.usage_count += 1
                existing_pattern.success_rate = (existing_pattern.success_rate + 1.0) / 2
                return
        
        # Add new pattern
        self.patterns.append(new_pattern)
    
    def get_relevant_patterns(self, prompt: str, pattern_type: str = None) -> List[Pattern]:
        """Get patterns relevant to the given prompt."""
        prompt_lower = prompt.lower()
        relevant_patterns = []
        
        for pattern in self.patterns:
            if pattern_type and pattern.pattern_type != pattern_type:
                continue
            
            # Check if pattern description matches prompt keywords
            if any(word in prompt_lower for word in pattern.description.lower().split()):
                relevant_patterns.append(pattern)
        
        # Sort by success rate and usage count
        relevant_patterns.sort(key=lambda p: (p.success_rate, p.usage_count), reverse=True)
        return relevant_patterns
    
    def update_quality_score(self, example_id: int, score: float) -> None:
        """Update quality score for an example."""
        if 0 <= example_id < len(self.examples):
            self.examples[example_id].quality_score = score
            self._save_database()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics."""
        return {
            "total_examples": len(self.examples),
            "total_patterns": len(self.patterns),
            "average_quality": sum(ex.quality_score for ex in self.examples) / len(self.examples) if self.examples else 0,
            "pattern_types": list(set(p.pattern_type for p in self.patterns)),
            "most_used_patterns": sorted(self.patterns, key=lambda p: p.usage_count, reverse=True)[:5]
        }
    
    def create_enhanced_prompt(self, original_prompt: str, agent_role: str) -> str:
        """Create an enhanced prompt with relevant examples and patterns."""
        # Find similar examples
        similar_examples = self.find_similar_examples(original_prompt, k=2)
        
        # Find relevant patterns
        relevant_patterns = self.get_relevant_patterns(original_prompt, agent_role)
        
        enhanced_prompt = f"Original prompt: {original_prompt}\n\n"
        
        if similar_examples:
            enhanced_prompt += "Similar successful examples:\n"
            for i, example in enumerate(similar_examples, 1):
                enhanced_prompt += f"{i}. {example.prompt} (Quality: {example.quality_score:.2f})\n"
                if agent_role == "builder" and example.builder_script:
                    enhanced_prompt += f"   Key techniques: {self._extract_key_techniques(example.builder_script)}\n"
                elif agent_role == "texture" and example.texture_script:
                    enhanced_prompt += f"   Key techniques: {self._extract_key_techniques(example.texture_script)}\n"
            enhanced_prompt += "\n"
        
        if relevant_patterns:
            enhanced_prompt += "Relevant patterns to consider:\n"
            for pattern in relevant_patterns[:3]:
                enhanced_prompt += f"- {pattern.description} (Success rate: {pattern.success_rate:.2f})\n"
            enhanced_prompt += "\n"
        
        enhanced_prompt += "Use these examples and patterns as inspiration while creating something unique for the original prompt."
        
        return enhanced_prompt
    
    def _extract_key_techniques(self, script: str) -> str:
        """Extract key techniques from a script."""
        techniques = []
        
        # Look for common techniques
        if "Array" in script:
            techniques.append("Array modifier")
        if "Subdivision" in script:
            techniques.append("Subdivision surface")
        if "Boolean" in script:
            techniques.append("Boolean operations")
        if "PrincipledBSDF" in script:
            techniques.append("Principled BSDF")
        if "Emission" in script:
            techniques.append("Emission materials")
        if "BEZIER" in script:
            techniques.append("Bezier easing")
        
        return ", ".join(techniques[:3])  # Return top 3 techniques
