"""
Prompt Interpreter - Advanced NLP for Scene Understanding
==========================================================

This module analyzes natural language prompts to extract:
- Scene objects and their attributes
- Spatial relationships and positioning
- Visual style and aesthetic preferences
- Mood, atmosphere, and lighting hints
- Scene composition and camera angles

Uses pattern matching, keyword analysis, and semantic understanding
to create structured scene graphs from free-form text.

Author: VoxelWeaver Team
Version: 1.0.0
"""

import re
from typing import List, Dict, Any, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum

from utils.logger import get_logger

logger = get_logger(__name__)


class ObjectType(Enum):
    """Common 3D object categories."""
    FURNITURE = "furniture"
    ARCHITECTURE = "architecture"
    NATURE = "nature"
    VEHICLE = "vehicle"
    CHARACTER = "character"
    PROP = "prop"
    LIGHTING = "lighting"
    EFFECT = "effect"
    UNKNOWN = "unknown"


class SpatialRelation(Enum):
    """Spatial relationship types."""
    ON = "on"
    UNDER = "under"
    ABOVE = "above"
    BELOW = "below"
    BESIDE = "beside"
    NEXT_TO = "next_to"
    NEAR = "near"
    FAR_FROM = "far_from"
    IN_FRONT = "in_front"
    BEHIND = "behind"
    INSIDE = "inside"
    OUTSIDE = "outside"
    AROUND = "around"
    BETWEEN = "between"


@dataclass
class SceneObject:
    """Parsed object from prompt."""
    name: str
    type: ObjectType = ObjectType.UNKNOWN
    attributes: List[str] = field(default_factory=list)
    material: Optional[str] = None
    color: Optional[str] = None
    size: Optional[str] = None
    quantity: int = 1
    confidence: float = 1.0


@dataclass
class SpatialRelationship:
    """Spatial relationship between objects."""
    relation: SpatialRelation
    object1: str
    object2: str
    distance: Optional[float] = None
    confidence: float = 1.0


@dataclass
class SceneGraph:
    """Structured representation of scene."""
    objects: List[SceneObject] = field(default_factory=list)
    relationships: List[SpatialRelationship] = field(default_factory=list)
    style: Optional[str] = None
    mood: Optional[str] = None
    time_of_day: Optional[str] = None
    weather: Optional[str] = None
    camera_angle: Optional[str] = None
    lighting_hints: List[str] = field(default_factory=list)
    raw_prompt: str = ""


class PromptInterpreter:
    """
    Advanced NLP system for prompt analysis and scene understanding.

    This class extracts structured information from natural language
    prompts to guide 3D scene generation.

    Example:
        >>> interpreter = PromptInterpreter()
        >>> scene_graph = interpreter.parse_prompt(
        ...     "A cozy living room with a red sofa next to a fireplace"
        ... )
        >>> print(f"Found {len(scene_graph.objects)} objects")
        >>> print(f"Style: {scene_graph.style}")
    """

    # Object keyword patterns (object_name: (category, keywords))
    OBJECT_PATTERNS = {
        # Furniture
        'sofa': (ObjectType.FURNITURE, ['sofa', 'couch', 'settee']),
        'chair': (ObjectType.FURNITURE, ['chair', 'seat', 'stool']),
        'table': (ObjectType.FURNITURE, ['table', 'desk', 'surface']),
        'bed': (ObjectType.FURNITURE, ['bed', 'mattress', 'bunk']),
        'shelf': (ObjectType.FURNITURE, ['shelf', 'shelves', 'bookshelf']),
        'cabinet': (ObjectType.FURNITURE, ['cabinet', 'cupboard', 'wardrobe']),
        'lamp': (ObjectType.FURNITURE, ['lamp', 'light', 'lantern']),

        # Architecture
        'wall': (ObjectType.ARCHITECTURE, ['wall', 'partition']),
        'door': (ObjectType.ARCHITECTURE, ['door', 'doorway', 'entrance']),
        'window': (ObjectType.ARCHITECTURE, ['window', 'windowsill']),
        'floor': (ObjectType.ARCHITECTURE, ['floor', 'flooring', 'ground']),
        'ceiling': (ObjectType.ARCHITECTURE, ['ceiling', 'roof']),
        'stairs': (ObjectType.ARCHITECTURE, ['stairs', 'staircase', 'steps']),
        'column': (ObjectType.ARCHITECTURE, ['column', 'pillar', 'post']),
        'fireplace': (ObjectType.ARCHITECTURE, ['fireplace', 'hearth']),

        # Nature
        'tree': (ObjectType.NATURE, ['tree', 'trees', 'oak', 'pine']),
        'flower': (ObjectType.NATURE, ['flower', 'flowers', 'blossom']),
        'grass': (ObjectType.NATURE, ['grass', 'lawn', 'meadow']),
        'rock': (ObjectType.NATURE, ['rock', 'rocks', 'boulder', 'stone']),
        'water': (ObjectType.NATURE, ['water', 'pond', 'lake', 'river']),
        'mountain': (ObjectType.NATURE, ['mountain', 'mountains', 'hill']),
        'cloud': (ObjectType.NATURE, ['cloud', 'clouds']),

        # Vehicles
        'car': (ObjectType.VEHICLE, ['car', 'automobile', 'vehicle']),
        'bike': (ObjectType.VEHICLE, ['bike', 'bicycle', 'motorcycle']),
        'boat': (ObjectType.VEHICLE, ['boat', 'ship', 'vessel']),
        'plane': (ObjectType.VEHICLE, ['plane', 'airplane', 'aircraft']),

        # Props
        'book': (ObjectType.PROP, ['book', 'books', 'novel']),
        'cup': (ObjectType.PROP, ['cup', 'mug', 'glass']),
        'plate': (ObjectType.PROP, ['plate', 'dish', 'platter']),
        'vase': (ObjectType.PROP, ['vase', 'pot', 'urn']),
        'painting': (ObjectType.PROP, ['painting', 'picture', 'artwork']),
        'rug': (ObjectType.PROP, ['rug', 'carpet', 'mat']),
        'curtain': (ObjectType.PROP, ['curtain', 'curtains', 'drapes']),
    }

    # Style keywords
    STYLE_KEYWORDS = {
        'realistic': ['realistic', 'photorealistic', 'lifelike', 'accurate'],
        'stylized': ['stylized', 'artistic', 'expressive', 'unique'],
        'low_poly': ['low poly', 'geometric', 'faceted', 'minimalist'],
        'cartoon': ['cartoon', 'cartoony', 'animated', 'toon'],
        'cyberpunk': ['cyberpunk', 'neon', 'futuristic', 'high-tech'],
        'fantasy': ['fantasy', 'magical', 'mystical', 'ethereal'],
        'medieval': ['medieval', 'gothic', 'castle', 'knight'],
        'modern': ['modern', 'contemporary', 'minimalist', 'sleek'],
        'vintage': ['vintage', 'retro', 'antique', 'classic'],
    }

    # Mood keywords
    MOOD_KEYWORDS = {
        'cozy': ['cozy', 'warm', 'comfortable', 'inviting'],
        'dark': ['dark', 'gloomy', 'ominous', 'sinister'],
        'bright': ['bright', 'cheerful', 'sunny', 'vibrant'],
        'mysterious': ['mysterious', 'enigmatic', 'cryptic'],
        'peaceful': ['peaceful', 'calm', 'serene', 'tranquil'],
        'dramatic': ['dramatic', 'intense', 'powerful', 'striking'],
        'romantic': ['romantic', 'dreamy', 'soft', 'gentle'],
    }

    # Time of day keywords
    TIME_KEYWORDS = {
        'morning': ['morning', 'dawn', 'sunrise'],
        'noon': ['noon', 'midday', 'afternoon'],
        'evening': ['evening', 'dusk', 'twilight'],
        'night': ['night', 'nighttime', 'midnight'],
        'sunset': ['sunset', 'golden hour'],
    }

    # Color keywords
    COLOR_KEYWORDS = [
        'red', 'blue', 'green', 'yellow', 'orange', 'purple', 'pink',
        'black', 'white', 'gray', 'grey', 'brown', 'gold', 'silver',
        'cyan', 'magenta', 'crimson', 'navy', 'emerald', 'amber'
    ]

    # Material keywords
    MATERIAL_KEYWORDS = [
        'wood', 'wooden', 'metal', 'metallic', 'glass', 'stone', 'brick',
        'fabric', 'leather', 'plastic', 'ceramic', 'marble', 'concrete',
        'steel', 'iron', 'copper', 'brass', 'gold', 'silver'
    ]

    # Size keywords
    SIZE_KEYWORDS = {
        'tiny': 0.3,
        'small': 0.7,
        'medium': 1.0,
        'large': 1.5,
        'huge': 2.5,
        'massive': 4.0,
    }

    # Spatial relation patterns
    SPATIAL_PATTERNS = {
        SpatialRelation.ON: [r'\bon\b', r'\bon top of\b', r'\batop\b'],
        SpatialRelation.UNDER: [r'\bunder\b', r'\bbeneath\b', r'\bunderneath\b'],
        SpatialRelation.ABOVE: [r'\babove\b', r'\bover\b'],
        SpatialRelation.BESIDE: [r'\bbeside\b', r'\bnext to\b', r'\bnear\b'],
        SpatialRelation.BEHIND: [r'\bbehind\b', r'\bin back of\b'],
        SpatialRelation.IN_FRONT: [r'\bin front of\b', r'\bbefore\b'],
        SpatialRelation.INSIDE: [r'\binside\b', r'\bin\b', r'\bwithin\b'],
        SpatialRelation.AROUND: [r'\baround\b', r'\bsurrounding\b'],
        SpatialRelation.BETWEEN: [r'\bbetween\b'],
    }

    def __init__(self):
        """Initialize prompt interpreter."""
        self.logger = get_logger(__name__)

    def parse_prompt(self, prompt: str) -> SceneGraph:
        """
        Parse natural language prompt into structured scene graph.

        Args:
            prompt: Natural language scene description

        Returns:
            SceneGraph with extracted information

        Example:
            >>> scene = interpreter.parse_prompt(
            ...     "A dark medieval castle with stone walls and wooden doors"
            ... )
        """
        self.logger.info(f"Parsing prompt: '{prompt}'")

        scene_graph = SceneGraph(raw_prompt=prompt)

        # Extract all components
        scene_graph.objects = self.identify_objects(prompt)
        scene_graph.relationships = self.analyze_relationships(prompt, scene_graph.objects)
        scene_graph.style = self.extract_style(prompt)
        scene_graph.mood = self.extract_mood(prompt)
        scene_graph.time_of_day = self.extract_time_of_day(prompt)
        scene_graph.lighting_hints = self.extract_lighting_hints(prompt)
        scene_graph.camera_angle = self.extract_camera_angle(prompt)

        self.logger.info(
            f"Parsed scene: {len(scene_graph.objects)} objects, "
            f"{len(scene_graph.relationships)} relationships"
        )

        return scene_graph

    def identify_objects(self, prompt: str) -> List[SceneObject]:
        """
        Identify objects mentioned in prompt.

        Args:
            prompt: Scene description

        Returns:
            List of identified objects

        Example:
            >>> objects = interpreter.identify_objects(
            ...     "A red sofa and blue chair"
            ... )
        """
        prompt_lower = prompt.lower()
        objects = []
        seen_objects = set()

        # Extract quantities
        quantity_pattern = r'(\d+|a couple of|a few|several|many)\s+(\w+)'
        quantity_matches = re.finditer(quantity_pattern, prompt_lower)

        quantity_map = {}
        for match in quantity_matches:
            qty_str, obj_name = match.groups()
            qty = self._parse_quantity(qty_str)
            quantity_map[obj_name] = qty

        # Identify objects by pattern matching
        for obj_name, (obj_type, keywords) in self.OBJECT_PATTERNS.items():
            for keyword in keywords:
                pattern = r'\b' + re.escape(keyword) + r'\b'
                if re.search(pattern, prompt_lower):
                    if obj_name not in seen_objects:
                        # Extract attributes for this object
                        obj = SceneObject(
                            name=obj_name,
                            type=obj_type,
                            quantity=quantity_map.get(obj_name, 1)
                        )

                        # Extract color
                        obj.color = self._find_attribute_near(
                            prompt_lower, keyword, self.COLOR_KEYWORDS
                        )

                        # Extract material
                        obj.material = self._find_attribute_near(
                            prompt_lower, keyword, self.MATERIAL_KEYWORDS
                        )

                        # Extract size
                        size_keyword = self._find_attribute_near(
                            prompt_lower, keyword, list(self.SIZE_KEYWORDS.keys())
                        )
                        if size_keyword:
                            obj.size = size_keyword

                        # Extract other adjectives as attributes
                        obj.attributes = self._extract_adjectives_near(
                            prompt_lower, keyword
                        )

                        objects.append(obj)
                        seen_objects.add(obj_name)
                        break

        self.logger.debug(f"Identified {len(objects)} objects")
        return objects

    def analyze_relationships(
        self,
        prompt: str,
        objects: List[SceneObject]
    ) -> List[SpatialRelationship]:
        """
        Analyze spatial relationships between objects.

        Args:
            prompt: Scene description
            objects: List of identified objects

        Returns:
            List of spatial relationships

        Example:
            >>> relationships = interpreter.analyze_relationships(
            ...     "sofa next to table", objects
            ... )
        """
        prompt_lower = prompt.lower()
        relationships = []

        # Create object name map
        obj_names = [obj.name for obj in objects]

        # Find spatial relationships
        for relation_type, patterns in self.SPATIAL_PATTERNS.items():
            for pattern in patterns:
                # Look for "object1 [relation] object2" patterns
                for i, obj1 in enumerate(obj_names):
                    for j, obj2 in enumerate(obj_names):
                        if i == j:
                            continue

                        # Create pattern to match "obj1 relation obj2"
                        full_pattern = (
                            r'\b' + re.escape(obj1) +
                            r'\s+' + pattern +
                            r'\s+' + re.escape(obj2) + r'\b'
                        )

                        if re.search(full_pattern, prompt_lower):
                            relationship = SpatialRelationship(
                                relation=relation_type,
                                object1=obj1,
                                object2=obj2,
                                confidence=0.9
                            )
                            relationships.append(relationship)

        self.logger.debug(f"Found {len(relationships)} spatial relationships")
        return relationships

    def extract_style(self, prompt: str) -> Optional[str]:
        """
        Extract visual style from prompt.

        Args:
            prompt: Scene description

        Returns:
            Style identifier or None

        Example:
            >>> style = interpreter.extract_style("cyberpunk city")
            >>> print(style)  # "cyberpunk"
        """
        prompt_lower = prompt.lower()

        for style, keywords in self.STYLE_KEYWORDS.items():
            for keyword in keywords:
                if keyword in prompt_lower:
                    self.logger.debug(f"Detected style: {style}")
                    return style

        return None

    def extract_mood(self, prompt: str) -> Optional[str]:
        """
        Extract mood/atmosphere from prompt.

        Args:
            prompt: Scene description

        Returns:
            Mood identifier or None
        """
        prompt_lower = prompt.lower()

        for mood, keywords in self.MOOD_KEYWORDS.items():
            for keyword in keywords:
                if keyword in prompt_lower:
                    self.logger.debug(f"Detected mood: {mood}")
                    return mood

        return None

    def extract_time_of_day(self, prompt: str) -> Optional[str]:
        """Extract time of day from prompt."""
        prompt_lower = prompt.lower()

        for time, keywords in self.TIME_KEYWORDS.items():
            for keyword in keywords:
                if keyword in prompt_lower:
                    self.logger.debug(f"Detected time: {time}")
                    return time

        return None

    def extract_lighting_hints(self, prompt: str) -> List[str]:
        """
        Extract lighting hints from prompt.

        Args:
            prompt: Scene description

        Returns:
            List of lighting-related keywords
        """
        lighting_keywords = [
            'bright', 'dark', 'shadowy', 'illuminated', 'lit', 'glowing',
            'neon', 'fluorescent', 'candlelit', 'moonlit', 'sunlit',
            'spotlight', 'ambient', 'dramatic lighting', 'soft light'
        ]

        prompt_lower = prompt.lower()
        hints = []

        for keyword in lighting_keywords:
            if keyword in prompt_lower:
                hints.append(keyword)

        self.logger.debug(f"Found {len(hints)} lighting hints")
        return hints

    def extract_camera_angle(self, prompt: str) -> Optional[str]:
        """Extract camera angle/perspective hints."""
        camera_keywords = {
            'aerial': ['aerial view', 'top down', 'bird\'s eye'],
            'low': ['low angle', 'looking up', 'worm\'s eye'],
            'eye_level': ['eye level', 'straight on', 'front view'],
            'close_up': ['close up', 'closeup', 'tight shot'],
            'wide': ['wide angle', 'wide shot', 'establishing'],
        }

        prompt_lower = prompt.lower()

        for angle, keywords in camera_keywords.items():
            for keyword in keywords:
                if keyword in prompt_lower:
                    self.logger.debug(f"Detected camera angle: {angle}")
                    return angle

        return None

    def generate_scene_graph(self, prompt: str) -> Dict[str, Any]:
        """
        Generate complete scene graph representation.

        Args:
            prompt: Scene description

        Returns:
            Dictionary representation of scene graph

        Example:
            >>> graph = interpreter.generate_scene_graph(
            ...     "A cozy bedroom with a bed and nightstand"
            ... )
        """
        scene_graph = self.parse_prompt(prompt)

        return {
            'objects': [
                {
                    'name': obj.name,
                    'type': obj.type.value,
                    'attributes': obj.attributes,
                    'material': obj.material,
                    'color': obj.color,
                    'size': obj.size,
                    'quantity': obj.quantity
                }
                for obj in scene_graph.objects
            ],
            'relationships': [
                {
                    'relation': rel.relation.value,
                    'object1': rel.object1,
                    'object2': rel.object2,
                    'confidence': rel.confidence
                }
                for rel in scene_graph.relationships
            ],
            'metadata': {
                'style': scene_graph.style,
                'mood': scene_graph.mood,
                'time_of_day': scene_graph.time_of_day,
                'camera_angle': scene_graph.camera_angle,
                'lighting_hints': scene_graph.lighting_hints
            }
        }

    # Helper methods

    def _parse_quantity(self, quantity_str: str) -> int:
        """Parse quantity string to integer."""
        quantity_map = {
            'a couple of': 2,
            'a few': 3,
            'several': 5,
            'many': 10,
        }

        if quantity_str in quantity_map:
            return quantity_map[quantity_str]

        try:
            return int(quantity_str)
        except ValueError:
            return 1

    def _find_attribute_near(
        self,
        text: str,
        target: str,
        attributes: List[str],
        window: int = 50
    ) -> Optional[str]:
        """Find attribute word near target word."""
        # Find target position
        match = re.search(r'\b' + re.escape(target) + r'\b', text)
        if not match:
            return None

        pos = match.start()

        # Look in window before and after
        start = max(0, pos - window)
        end = min(len(text), pos + len(target) + window)
        context = text[start:end]

        # Check for attributes in context
        for attr in attributes:
            if re.search(r'\b' + re.escape(attr) + r'\b', context):
                return attr

        return None

    def _extract_adjectives_near(
        self,
        text: str,
        target: str,
        window: int = 50
    ) -> List[str]:
        """Extract adjectives near target word."""
        # Common adjectives to look for
        adjectives = [
            'beautiful', 'elegant', 'rustic', 'modern', 'vintage',
            'ornate', 'simple', 'complex', 'intricate', 'plain',
            'luxurious', 'comfortable', 'sturdy', 'delicate',
            'antique', 'contemporary', 'traditional'
        ]

        match = re.search(r'\b' + re.escape(target) + r'\b', text)
        if not match:
            return []

        pos = match.start()
        start = max(0, pos - window)
        end = min(len(text), pos + len(target) + window)
        context = text[start:end]

        found = []
        for adj in adjectives:
            if re.search(r'\b' + re.escape(adj) + r'\b', context):
                found.append(adj)

        return found


# Example usage
if __name__ == "__main__":
    interpreter = PromptInterpreter()

    test_prompts = [
        "A cozy living room with a red sofa next to a fireplace",
        "Medieval castle throne room with stone walls and wooden chairs",
        "Cyberpunk city street at night with neon signs",
        "Peaceful forest clearing with several trees and rocks",
        "Modern kitchen with steel appliances and marble counters"
    ]

    for prompt in test_prompts:
        print(f"\n{'='*60}")
        print(f"Prompt: {prompt}")
        print(f"{'='*60}\n")

        scene_graph = interpreter.parse_prompt(prompt)

        print(f"Objects ({len(scene_graph.objects)}):")
        for obj in scene_graph.objects:
            print(f"  - {obj.name} ({obj.type.value})")
            if obj.color:
                print(f"    Color: {obj.color}")
            if obj.material:
                print(f"    Material: {obj.material}")
            if obj.attributes:
                print(f"    Attributes: {', '.join(obj.attributes)}")

        print(f"\nRelationships ({len(scene_graph.relationships)}):")
        for rel in scene_graph.relationships:
            print(f"  - {rel.object1} {rel.relation.value} {rel.object2}")

        print(f"\nMetadata:")
        print(f"  Style: {scene_graph.style}")
        print(f"  Mood: {scene_graph.mood}")
        print(f"  Time: {scene_graph.time_of_day}")
        print(f"  Lighting: {', '.join(scene_graph.lighting_hints) if scene_graph.lighting_hints else 'None'}")
