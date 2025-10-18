"""
Prompt Interpreter
-----------------
NLP-based prompt analysis for extracting structured 3D scene data.

Converts natural language descriptions into structured data for scene generation,
including objects, materials, lighting preferences, scene type, and style.
"""

import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class SceneElement:
    """Represents a single element in the scene."""
    name: str
    category: str = "object"
    attributes: Dict[str, Any] = field(default_factory=dict)
    position: Optional[str] = None  # e.g., "foreground", "background", "center"
    modifiers: List[str] = field(default_factory=list)  # e.g., ["large", "wooden", "vintage"]


class PromptInterpreter:
    """
    Interprets natural language prompts into structured 3D scene data.

    Uses keyword matching, pattern recognition, and basic NLP techniques
    to extract objects, materials, lighting, style, mood, and spatial relationships.
    """

    # Category keywords for object classification
    OBJECT_CATEGORIES = {
        'furniture': ['chair', 'table', 'desk', 'sofa', 'couch', 'bed', 'shelf', 'bookshelf',
                      'cabinet', 'dresser', 'nightstand', 'bench', 'stool', 'ottoman'],
        'lighting': ['lamp', 'light', 'chandelier', 'sconce', 'lantern', 'candle', 'spotlight'],
        'decor': ['plant', 'vase', 'picture', 'painting', 'sculpture', 'rug', 'curtain',
                  'mirror', 'clock', 'pillow', 'cushion', 'poster', 'frame'],
        'electronics': ['tv', 'television', 'computer', 'monitor', 'phone', 'iphone', 'laptop',
                        'speaker', 'camera', 'tablet', 'keyboard', 'mouse'],
        'nature': ['tree', 'flower', 'grass', 'rock', 'stone', 'water', 'sky', 'cloud',
                   'mountain', 'hill', 'river', 'lake', 'ocean', 'forest'],
        'architecture': ['building', 'house', 'wall', 'door', 'window', 'roof', 'floor',
                         'ceiling', 'column', 'pillar', 'arch', 'stairs', 'bridge'],
        'vehicle': ['car', 'truck', 'bike', 'bicycle', 'motorcycle', 'boat', 'ship', 'plane'],
        'character': ['person', 'human', 'character', 'figure', 'avatar'],
        'food': ['apple', 'fruit', 'food', 'cup', 'mug', 'plate', 'bowl', 'bottle', 'glass']
    }

    # Material keywords
    MATERIAL_KEYWORDS = {
        'wood': ['wooden', 'wood', 'timber', 'oak', 'pine', 'mahogany'],
        'metal': ['metal', 'metallic', 'steel', 'iron', 'bronze', 'copper', 'gold', 'silver'],
        'glass': ['glass', 'transparent', 'crystal', 'clear'],
        'fabric': ['fabric', 'cloth', 'textile', 'leather', 'velvet', 'cotton'],
        'stone': ['stone', 'marble', 'granite', 'concrete', 'brick'],
        'plastic': ['plastic', 'acrylic', 'polymer']
    }

    # Lighting keywords
    LIGHTING_KEYWORDS = {
        'warm': ['warm', 'cozy', 'golden', 'amber', 'candlelight', 'firelight'],
        'cool': ['cool', 'cold', 'blue', 'icy', 'moonlight'],
        'bright': ['bright', 'brilliant', 'intense', 'vivid', 'radiant'],
        'dim': ['dim', 'dark', 'shadowy', 'moody', 'subtle'],
        'natural': ['natural', 'daylight', 'sunlight', 'outdoor'],
        'dramatic': ['dramatic', 'cinematic', 'theatrical', 'spotlight'],
        'soft': ['soft', 'diffuse', 'gentle', 'ambient']
    }

    # Style keywords
    STYLE_KEYWORDS = {
        'realistic': ['realistic', 'photorealistic', 'real', 'lifelike', 'accurate'],
        'stylized': ['stylized', 'artistic', 'abstract', 'non-realistic'],
        'modern': ['modern', 'contemporary', 'minimalist', 'sleek', 'clean'],
        'vintage': ['vintage', 'retro', 'antique', 'old-fashioned', 'classic'],
        'industrial': ['industrial', 'urban', 'mechanical', 'factory'],
        'rustic': ['rustic', 'rural', 'countryside', 'farmhouse'],
        'futuristic': ['futuristic', 'sci-fi', 'cyberpunk', 'high-tech', 'advanced'],
        'fantasy': ['fantasy', 'magical', 'mystical', 'enchanted'],
        'minimalist': ['minimalist', 'simple', 'sparse', 'basic']
    }

    # Mood keywords
    MOOD_KEYWORDS = {
        'cozy': ['cozy', 'comfortable', 'homey', 'inviting', 'snug'],
        'dramatic': ['dramatic', 'intense', 'powerful', 'striking'],
        'peaceful': ['peaceful', 'calm', 'serene', 'tranquil', 'relaxing'],
        'energetic': ['energetic', 'vibrant', 'lively', 'dynamic', 'active'],
        'mysterious': ['mysterious', 'enigmatic', 'secretive', 'hidden'],
        'elegant': ['elegant', 'sophisticated', 'refined', 'graceful'],
        'playful': ['playful', 'fun', 'whimsical', 'cheerful']
    }

    # Spatial relationship keywords
    SPATIAL_KEYWORDS = {
        'on': ['on', 'atop', 'above'],
        'under': ['under', 'beneath', 'below'],
        'beside': ['beside', 'next to', 'adjacent to', 'near'],
        'in front of': ['in front of', 'before', 'ahead of'],
        'behind': ['behind', 'back of'],
        'inside': ['inside', 'within', 'in'],
        'around': ['around', 'surrounding', 'encircling']
    }

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize prompt interpreter.

        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.confidence_threshold = self.config.get('confidence_threshold', 0.5)
        logger.info("Prompt Interpreter initialized")

    def parse_prompt(self, prompt: str) -> Dict[str, Any]:
        """
        Parse natural language prompt into structured data.

        Args:
            prompt: Natural language scene description

        Returns:
            Dictionary containing:
                - objects: List of SceneElement objects
                - materials: Detected materials
                - lighting: Lighting preferences
                - style: Visual style
                - mood: Atmosphere descriptors
                - original_prompt: Original input

        Example:
            >>> interpreter = PromptInterpreter()
            >>> result = interpreter.parse_prompt("A cozy living room with a wooden table")
            >>> print(result['objects'])
            [SceneElement(name='living room', category='architecture', ...),
             SceneElement(name='table', category='furniture', modifiers=['wooden'])]
        """
        logger.info(f"Parsing prompt: {prompt}")

        # Validate prompt
        if not prompt or not prompt.strip():
            logger.warning("Empty prompt provided")
            return self._create_default_scene()

        # Clean prompt
        prompt_clean = self._clean_prompt(prompt)

        # Extract objects and their attributes
        objects = self._extract_objects(prompt_clean)
        logger.debug(f"Extracted {len(objects)} objects")

        # Extract materials
        materials = self._extract_materials(prompt_clean)
        logger.debug(f"Detected materials: {materials}")

        # Extract lighting preferences
        lighting = self._extract_lighting(prompt_clean)
        logger.debug(f"Lighting style: {lighting}")

        # Extract style
        style = self._extract_style_from_prompt(prompt_clean)
        logger.debug(f"Style: {style}")

        # Extract mood
        mood = self.extract_mood(prompt_clean)
        logger.debug(f"Mood: {mood}")

        result = {
            'objects': objects,
            'materials': materials,
            'lighting': lighting,
            'style': style,
            'mood': mood,
            'original_prompt': prompt,
            'confidence': self._calculate_confidence(objects, materials, lighting)
        }

        logger.info(f"Prompt parsing complete: {len(objects)} objects, confidence: {result['confidence']:.2f}")

        return result

    def extract_style(self, prompt: str, default_style: str = "realistic") -> str:
        """
        Extract visual style from prompt.

        Args:
            prompt: Natural language prompt
            default_style: Default style if none detected

        Returns:
            Detected style string
        """
        logger.debug(f"Extracting style from prompt (default: {default_style})")

        prompt_lower = prompt.lower()

        # Check for style keywords
        for style, keywords in self.STYLE_KEYWORDS.items():
            for keyword in keywords:
                if keyword in prompt_lower:
                    logger.debug(f"Style detected: {style} (keyword: {keyword})")
                    return style

        logger.debug(f"No style detected, using default: {default_style}")
        return default_style

    def extract_mood(self, prompt: str) -> Dict[str, float]:
        """
        Extract mood and atmosphere from prompt.

        Args:
            prompt: Natural language prompt

        Returns:
            Dictionary of mood descriptors with confidence scores
        """
        logger.debug("Extracting mood from prompt")

        prompt_lower = prompt.lower()
        moods = {}

        # Check for mood keywords
        for mood, keywords in self.MOOD_KEYWORDS.items():
            for keyword in keywords:
                if keyword in prompt_lower:
                    # Simple confidence based on keyword length (longer = more specific)
                    confidence = min(1.0, len(keyword) / 10.0)
                    moods[mood] = confidence
                    logger.debug(f"Mood detected: {mood} (confidence: {confidence:.2f})")

        # If no mood detected, infer from other keywords
        if not moods:
            moods = self._infer_mood_from_context(prompt_lower)

        return moods

    def analyze_relationships(self, objects: List[SceneElement]) -> Dict[str, Any]:
        """
        Analyze spatial relationships between objects.

        Args:
            objects: List of scene elements

        Returns:
            Dictionary of spatial relationships
        """
        logger.debug(f"Analyzing relationships between {len(objects)} objects")

        relationships = {}

        # For now, use simple heuristics based on object categories
        for obj in objects:
            relationships[obj.name] = {
                'category': obj.category,
                'position': obj.position or 'center',
                'related_objects': []
            }

            # Furniture typically sits on floor
            if obj.category == 'furniture':
                relationships[obj.name]['support'] = 'floor'

            # Decor typically placed on/near furniture
            if obj.category == 'decor' and any(o.category == 'furniture' for o in objects):
                furniture = [o.name for o in objects if o.category == 'furniture']
                relationships[obj.name]['related_objects'] = furniture

        logger.debug(f"Found {len(relationships)} relationships")

        return relationships

    def generate_scene_graph(self, interpreted_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate hierarchical scene graph from interpreted data.

        Args:
            interpreted_data: Parsed prompt data

        Returns:
            Hierarchical scene graph structure
        """
        logger.debug("Generating scene graph")

        objects = interpreted_data.get('objects', [])

        # Create scene graph with hierarchy
        scene_graph = {
            'root': {
                'type': 'scene',
                'style': interpreted_data.get('style', 'realistic'),
                'mood': interpreted_data.get('mood', {}),
                'children': []
            }
        }

        # Group objects by category
        by_category = {}
        for obj in objects:
            category = obj.category
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(obj)

        # Add category groups to scene graph
        for category, items in by_category.items():
            category_node = {
                'type': 'group',
                'name': f'{category}_group',
                'children': [
                    {
                        'type': 'object',
                        'name': item.name,
                        'category': item.category,
                        'attributes': item.attributes,
                        'modifiers': item.modifiers,
                        'position': item.position
                    }
                    for item in items
                ]
            }
            scene_graph['root']['children'].append(category_node)

        logger.debug(f"Scene graph generated with {len(by_category)} category groups")

        return scene_graph

    # Private helper methods

    def _clean_prompt(self, prompt: str) -> str:
        """Clean and normalize prompt text."""
        # Remove extra whitespace
        prompt = re.sub(r'\s+', ' ', prompt.strip())
        return prompt

    def _extract_objects(self, prompt: str) -> List[SceneElement]:
        """Extract objects from prompt using keyword matching."""
        prompt_lower = prompt.lower()
        objects = []
        words = re.findall(r'\b\w+\b', prompt_lower)

        # Track which words we've already processed
        processed_indices = set()

        # Look for multi-word objects first (e.g., "wooden table")
        for i, word in enumerate(words):
            if i in processed_indices:
                continue

            # Check for modifier + object pattern
            if i < len(words) - 1:
                modifier = word
                next_word = words[i + 1]

                # Check if next word is a known object
                for category, obj_list in self.OBJECT_CATEGORIES.items():
                    if next_word in obj_list:
                        # Found object with modifier
                        objects.append(SceneElement(
                            name=next_word,
                            category=category,
                            modifiers=[modifier],
                            attributes={'material': self._get_material_from_modifier(modifier)}
                        ))
                        processed_indices.add(i)
                        processed_indices.add(i + 1)
                        logger.debug(f"Found object: {next_word} (modifier: {modifier}, category: {category})")
                        break

        # Look for standalone objects
        for i, word in enumerate(words):
            if i in processed_indices:
                continue

            for category, obj_list in self.OBJECT_CATEGORIES.items():
                if word in obj_list:
                    objects.append(SceneElement(
                        name=word,
                        category=category
                    ))
                    processed_indices.add(i)
                    logger.debug(f"Found object: {word} (category: {category})")
                    break

        # If no objects found, try to infer from scene type
        if not objects:
            logger.warning("No specific objects found, inferring from scene type")
            objects = self._infer_objects_from_scene_type(prompt_lower)

        return objects

    def _extract_materials(self, prompt: str) -> List[str]:
        """Extract material keywords from prompt."""
        prompt_lower = prompt.lower()
        materials = []

        for material, keywords in self.MATERIAL_KEYWORDS.items():
            for keyword in keywords:
                if keyword in prompt_lower:
                    if material not in materials:
                        materials.append(material)
                        logger.debug(f"Material detected: {material} (keyword: {keyword})")

        return materials

    def _extract_lighting(self, prompt: str) -> str:
        """Extract lighting preference from prompt."""
        prompt_lower = prompt.lower()

        # Check for lighting keywords
        for lighting_type, keywords in self.LIGHTING_KEYWORDS.items():
            for keyword in keywords:
                if keyword in prompt_lower:
                    logger.debug(f"Lighting detected: {lighting_type} (keyword: {keyword})")
                    return lighting_type

        # Default lighting
        logger.debug("No specific lighting detected, using 'natural'")
        return 'natural'

    def _extract_style_from_prompt(self, prompt: str) -> str:
        """Extract style from prompt."""
        return self.extract_style(prompt, default_style='realistic')

    def _infer_mood_from_context(self, prompt: str) -> Dict[str, float]:
        """Infer mood from contextual clues if no explicit mood keywords."""
        moods = {}

        # Infer from lighting
        if any(word in prompt for word in ['sunset', 'sunrise', 'golden hour']):
            moods['peaceful'] = 0.7
            moods['warm'] = 0.6

        # Infer from style
        if any(word in prompt for word in ['futuristic', 'cyberpunk', 'neon']):
            moods['energetic'] = 0.6
            moods['dramatic'] = 0.5

        # Infer from scene type
        if any(word in prompt for word in ['bedroom', 'living room', 'home']):
            moods['cozy'] = 0.6

        if any(word in prompt for word in ['office', 'studio', 'workspace']):
            moods['focused'] = 0.6

        return moods if moods else {'neutral': 0.5}

    def _get_material_from_modifier(self, modifier: str) -> Optional[str]:
        """Get material type from modifier word."""
        for material, keywords in self.MATERIAL_KEYWORDS.items():
            if modifier in keywords:
                return material
        return None

    def _infer_objects_from_scene_type(self, prompt: str) -> List[SceneElement]:
        """Infer typical objects based on scene type."""
        objects = []

        # Living room
        if 'living room' in prompt:
            objects.extend([
                SceneElement(name='sofa', category='furniture'),
                SceneElement(name='table', category='furniture'),
                SceneElement(name='lamp', category='lighting')
            ])

        # Bedroom
        elif 'bedroom' in prompt:
            objects.extend([
                SceneElement(name='bed', category='furniture'),
                SceneElement(name='nightstand', category='furniture'),
                SceneElement(name='lamp', category='lighting')
            ])

        # Office
        elif 'office' in prompt or 'workspace' in prompt:
            objects.extend([
                SceneElement(name='desk', category='furniture'),
                SceneElement(name='chair', category='furniture'),
                SceneElement(name='computer', category='electronics')
            ])

        # Kitchen
        elif 'kitchen' in prompt:
            objects.extend([
                SceneElement(name='table', category='furniture'),
                SceneElement(name='cabinet', category='furniture')
            ])

        # Outdoor/nature
        elif any(word in prompt for word in ['outdoor', 'forest', 'nature', 'landscape']):
            objects.extend([
                SceneElement(name='tree', category='nature'),
                SceneElement(name='grass', category='nature'),
                SceneElement(name='sky', category='nature')
            ])

        logger.debug(f"Inferred {len(objects)} objects from scene type")
        return objects

    def _calculate_confidence(
        self,
        objects: List[SceneElement],
        materials: List[str],
        lighting: str
    ) -> float:
        """Calculate confidence score for parsing."""
        # Simple confidence calculation
        confidence = 0.0

        # Objects found
        if objects:
            confidence += 0.5 * min(1.0, len(objects) / 3.0)

        # Materials found
        if materials:
            confidence += 0.2 * min(1.0, len(materials) / 2.0)

        # Lighting found
        if lighting and lighting != 'natural':
            confidence += 0.3

        return min(1.0, confidence)

    def _create_default_scene(self) -> Dict[str, Any]:
        """Create default scene for empty prompts."""
        logger.warning("Creating default scene")

        return {
            'objects': [
                SceneElement(name='cube', category='object'),
                SceneElement(name='sphere', category='object'),
                SceneElement(name='plane', category='architecture')
            ],
            'materials': [],
            'lighting': 'natural',
            'style': 'realistic',
            'mood': {'neutral': 0.5},
            'original_prompt': '',
            'confidence': 0.3
        }


# Example usage and testing
if __name__ == "__main__":
    from utils.logger import setup_logging

    # Setup logging
    setup_logging(level="DEBUG", console=True)

    # Create interpreter
    interpreter = PromptInterpreter()

    # Test prompts
    test_prompts = [
        "A cozy living room with a wooden table and a warm lamp",
        "A futuristic cityscape at sunset with neon lights",
        "A realistic iPhone against a sunset backdrop",
        "A minimalist bedroom with modern furniture",
        "A mystical forest with glowing crystals and dramatic lighting"
    ]

    print("\n" + "="*80)
    print("PROMPT INTERPRETER - TEST SUITE")
    print("="*80 + "\n")

    for i, prompt in enumerate(test_prompts, 1):
        print(f"\n{'='*80}")
        print(f"Test {i}: {prompt}")
        print("="*80)

        result = interpreter.parse_prompt(prompt)

        print(f"\n📦 Objects ({len(result['objects'])}):")
        for obj in result['objects']:
            modifiers = f" ({', '.join(obj.modifiers)})" if obj.modifiers else ""
            print(f"  - {obj.name} [{obj.category}]{modifiers}")

        print(f"\n🎨 Materials: {', '.join(result['materials']) if result['materials'] else 'None'}")
        print(f"💡 Lighting: {result['lighting']}")
        print(f"🎭 Style: {result['style']}")
        print(f"🌟 Mood: {', '.join(f'{k} ({v:.2f})' for k, v in result['mood'].items())}")
        print(f"📊 Confidence: {result['confidence']:.2%}")

        # Generate scene graph
        scene_graph = interpreter.generate_scene_graph(result)
        print(f"\n🌳 Scene Graph: {len(scene_graph['root']['children'])} category groups")

    print("\n" + "="*80)
    print("TEST SUITE COMPLETE")
    print("="*80 + "\n")
