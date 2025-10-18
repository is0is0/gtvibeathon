"""Pattern matcher for automatically applying scene analysis patterns."""

import logging
import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path

from agency3d.utils.example_database import ExampleDatabase, Pattern

logger = logging.getLogger(__name__)


@dataclass
class SceneAnalysis:
    """Represents analysis of a generated scene."""
    scene_id: str
    prompt: str
    materials: List[Dict[str, Any]]
    geometry: List[Dict[str, Any]]
    lighting: List[Dict[str, Any]]
    animation: List[Dict[str, Any]]
    quality_score: float
    suggestions: List[str]
    created_at: str


@dataclass
class PatternMatch:
    """Represents a pattern match with confidence score."""
    pattern: Pattern
    confidence: float
    context: str
    suggested_application: str


class PatternMatcher:
    """Matches patterns from scene analysis and suggests applications."""
    
    def __init__(self, example_db: ExampleDatabase):
        self.example_db = example_db
        self.analysis_history: List[SceneAnalysis] = []
        self.pattern_cache: Dict[str, List[Pattern]] = {}
    
    def analyze_scene(self, scene_data: Dict[str, Any]) -> SceneAnalysis:
        """Analyze a generated scene and extract patterns."""
        analysis = SceneAnalysis(
            scene_id=scene_data.get('scene_id', 'unknown'),
            prompt=scene_data.get('prompt', ''),
            materials=self._analyze_materials(scene_data.get('materials', [])),
            geometry=self._analyze_geometry(scene_data.get('geometry', [])),
            lighting=self._analyze_lighting(scene_data.get('lighting', [])),
            animation=self._analyze_animation(scene_data.get('animation', [])),
            quality_score=scene_data.get('quality_score', 0.0),
            suggestions=[],
            created_at=scene_data.get('created_at', '')
        )
        
        # Generate suggestions based on analysis
        analysis.suggestions = self._generate_suggestions(analysis)
        
        self.analysis_history.append(analysis)
        return analysis
    
    def _analyze_materials(self, materials: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze material usage patterns."""
        analyzed = []
        for material in materials:
            analysis = {
                'name': material.get('name', ''),
                'node_types': material.get('node_types', []),
                'complexity': len(material.get('node_types', [])),
                'shader_type': material.get('shader_type', 'unknown'),
                'texture_usage': material.get('texture_usage', False),
                'procedural': material.get('procedural', False),
                'emission': 'Emission' in material.get('node_types', []),
                'transparency': any(node in material.get('node_types', []) for node in ['GlassBSDF', 'TransparentBSDF']),
                'metallic': material.get('metallic', False),
                'roughness': material.get('roughness', 0.5)
            }
            analyzed.append(analysis)
        return analyzed
    
    def _analyze_geometry(self, geometry: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze geometry patterns."""
        analyzed = []
        for obj in geometry:
            analysis = {
                'name': obj.get('name', ''),
                'type': obj.get('type', 'unknown'),
                'modifiers': obj.get('modifiers', []),
                'vertex_count': obj.get('vertex_count', 0),
                'face_count': obj.get('face_count', 0),
                'has_array': 'Array' in obj.get('modifiers', []),
                'has_subdivision': 'SubdivisionSurface' in obj.get('modifiers', []),
                'has_boolean': 'Boolean' in obj.get('modifiers', []),
                'complexity_score': self._calculate_geometry_complexity(obj)
            }
            analyzed.append(analysis)
        return analyzed
    
    def _analyze_lighting(self, lighting: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze lighting setup patterns."""
        analyzed = []
        for light in lighting:
            analysis = {
                'name': light.get('name', ''),
                'type': light.get('type', 'unknown'),
                'energy': light.get('energy', 1.0),
                'color': light.get('color', (1, 1, 1)),
                'size': light.get('size', 0.1),
                'is_key_light': light.get('is_key_light', False),
                'is_fill_light': light.get('is_fill_light', False),
                'is_rim_light': light.get('is_rim_light', False),
                'has_shadows': light.get('shadows', True),
                'lighting_quality': self._assess_lighting_quality(light)
            }
            analyzed.append(analysis)
        return analyzed
    
    def _analyze_animation(self, animation: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze animation patterns."""
        analyzed = []
        for anim in animation:
            analysis = {
                'object_name': anim.get('object_name', ''),
                'property': anim.get('property', ''),
                'easing_type': anim.get('easing_type', 'BEZIER'),
                'duration': anim.get('duration', 0),
                'keyframes': anim.get('keyframes', []),
                'is_camera': anim.get('is_camera', False),
                'is_rotation': 'rotation' in anim.get('property', ''),
                'is_location': 'location' in anim.get('property', ''),
                'is_scale': 'scale' in anim.get('property', ''),
                'complexity': len(anim.get('keyframes', []))
            }
            analyzed.append(analysis)
        return analyzed
    
    def _calculate_geometry_complexity(self, obj: Dict[str, Any]) -> float:
        """Calculate complexity score for geometry object."""
        score = 0.0
        
        # Base complexity from vertex count
        vertex_count = obj.get('vertex_count', 0)
        if vertex_count > 10000:
            score += 3.0
        elif vertex_count > 1000:
            score += 2.0
        elif vertex_count > 100:
            score += 1.0
        
        # Modifier complexity
        modifiers = obj.get('modifiers', [])
        score += len(modifiers) * 0.5
        
        # Special modifiers add more complexity
        if 'Array' in modifiers:
            score += 1.0
        if 'SubdivisionSurface' in modifiers:
            score += 1.5
        if 'Boolean' in modifiers:
            score += 2.0
        
        return min(score, 10.0)  # Cap at 10
    
    def _assess_lighting_quality(self, light: Dict[str, Any]) -> float:
        """Assess lighting quality based on setup."""
        score = 0.0
        
        # Energy level appropriateness
        energy = light.get('energy', 1.0)
        if 0.5 <= energy <= 5.0:
            score += 1.0
        
        # Color temperature
        color = light.get('color', (1, 1, 1))
        if not all(c == 1.0 for c in color):  # Non-white light
            score += 0.5
        
        # Size appropriateness
        size = light.get('size', 0.1)
        if 0.05 <= size <= 2.0:
            score += 0.5
        
        # Shadow settings
        if light.get('shadows', True):
            score += 1.0
        
        return min(score, 5.0)  # Cap at 5
    
    def _generate_suggestions(self, analysis: SceneAnalysis) -> List[str]:
        """Generate improvement suggestions based on analysis."""
        suggestions = []
        
        # Material suggestions
        if not analysis.materials:
            suggestions.append("Consider adding materials to enhance visual appeal")
        else:
            avg_complexity = sum(m['complexity'] for m in analysis.materials) / len(analysis.materials)
            if avg_complexity < 3:
                suggestions.append("Materials could be more complex - try adding more shader nodes")
            
            if not any(m['emission'] for m in analysis.materials):
                suggestions.append("Consider adding emission materials for glowing effects")
        
        # Geometry suggestions
        if not analysis.geometry:
            suggestions.append("Scene needs more geometry objects")
        else:
            high_complexity_objects = [g for g in analysis.geometry if g['complexity_score'] > 5]
            if len(high_complexity_objects) < len(analysis.geometry) * 0.3:
                suggestions.append("Add more complex geometry with modifiers")
        
        # Lighting suggestions
        if len(analysis.lighting) < 2:
            suggestions.append("Add more lights for better illumination")
        else:
            key_lights = [l for l in analysis.lighting if l['is_key_light']]
            if not key_lights:
                suggestions.append("Add a key light for better subject illumination")
        
        # Animation suggestions
        if analysis.animation:
            simple_animations = [a for a in analysis.animation if a['complexity'] < 3]
            if len(simple_animations) > len(analysis.animation) * 0.5:
                suggestions.append("Add more complex animations with multiple keyframes")
        
        return suggestions
    
    def find_matching_patterns(self, prompt: str, analysis: SceneAnalysis) -> List[PatternMatch]:
        """Find patterns that match the current scene analysis."""
        matches = []
        
        # Get relevant patterns from database
        relevant_patterns = self.example_db.get_relevant_patterns(prompt)
        
        for pattern in relevant_patterns:
            confidence = self._calculate_pattern_confidence(pattern, analysis)
            if confidence > 0.3:  # Threshold for relevance
                match = PatternMatch(
                    pattern=pattern,
                    confidence=confidence,
                    context=self._get_pattern_context(pattern, analysis),
                    suggested_application=self._suggest_application(pattern, analysis)
                )
                matches.append(match)
        
        # Sort by confidence
        matches.sort(key=lambda m: m.confidence, reverse=True)
        return matches
    
    def _calculate_pattern_confidence(self, pattern: Pattern, analysis: SceneAnalysis) -> float:
        """Calculate confidence score for pattern match."""
        confidence = 0.0
        
        # Check material patterns
        if pattern.pattern_type == "material":
            for material in analysis.materials:
                if any(node in material['node_types'] for node in pattern.node_types):
                    confidence += 0.3
                if pattern.description.lower() in material.get('name', '').lower():
                    confidence += 0.2
        
        # Check geometry patterns
        elif pattern.pattern_type == "geometry":
            for obj in analysis.geometry:
                if any(mod in obj['modifiers'] for mod in pattern.node_types):
                    confidence += 0.3
                if pattern.description.lower() in obj.get('name', '').lower():
                    confidence += 0.2
        
        # Check animation patterns
        elif pattern.pattern_type == "animation":
            for anim in analysis.animation:
                if pattern.description.lower() in anim.get('easing_type', '').lower():
                    confidence += 0.3
                if any(prop in anim.get('property', '') for prop in pattern.node_types):
                    confidence += 0.2
        
        # Boost confidence based on pattern success rate
        confidence += pattern.success_rate * 0.2
        
        return min(confidence, 1.0)
    
    def _get_pattern_context(self, pattern: Pattern, analysis: SceneAnalysis) -> str:
        """Get context for why a pattern matches."""
        context_parts = []
        
        if pattern.pattern_type == "material":
            matching_materials = [m for m in analysis.materials 
                                if any(node in m['node_types'] for node in pattern.node_types)]
            if matching_materials:
                context_parts.append(f"Found in {len(matching_materials)} materials")
        
        elif pattern.pattern_type == "geometry":
            matching_objects = [g for g in analysis.geometry 
                              if any(mod in g['modifiers'] for mod in pattern.node_types)]
            if matching_objects:
                context_parts.append(f"Found in {len(matching_objects)} objects")
        
        elif pattern.pattern_type == "animation":
            matching_animations = [a for a in analysis.animation 
                                 if pattern.description.lower() in a.get('easing_type', '').lower()]
            if matching_animations:
                context_parts.append(f"Found in {len(matching_animations)} animations")
        
        return "; ".join(context_parts) if context_parts else "General match"
    
    def _suggest_application(self, pattern: Pattern, analysis: SceneAnalysis) -> str:
        """Suggest how to apply the pattern."""
        if pattern.pattern_type == "material":
            return f"Apply {pattern.description} to enhance material realism"
        elif pattern.pattern_type == "geometry":
            return f"Use {pattern.description} to create more complex geometry"
        elif pattern.pattern_type == "animation":
            return f"Apply {pattern.description} for smoother animation"
        else:
            return f"Consider using {pattern.description} pattern"
    
    def get_enhanced_prompt(self, original_prompt: str, analysis: SceneAnalysis) -> str:
        """Get enhanced prompt with pattern-based suggestions."""
        matches = self.find_matching_patterns(original_prompt, analysis)
        
        enhanced_prompt = f"Original prompt: {original_prompt}\n\n"
        
        if matches:
            enhanced_prompt += "Based on similar successful scenes, consider:\n"
            for i, match in enumerate(matches[:3], 1):
                enhanced_prompt += f"{i}. {match.suggested_application} (Confidence: {match.confidence:.2f})\n"
            enhanced_prompt += "\n"
        
        if analysis.suggestions:
            enhanced_prompt += "Scene analysis suggestions:\n"
            for i, suggestion in enumerate(analysis.suggestions, 1):
                enhanced_prompt += f"{i}. {suggestion}\n"
            enhanced_prompt += "\n"
        
        enhanced_prompt += "Use these insights to improve the scene while maintaining the original vision."
        
        return enhanced_prompt
    
    def get_pattern_statistics(self) -> Dict[str, Any]:
        """Get statistics about pattern matching."""
        if not self.analysis_history:
            return {"total_analyses": 0}
        
        total_analyses = len(self.analysis_history)
        avg_quality = sum(a.quality_score for a in self.analysis_history) / total_analyses
        
        pattern_usage = {}
        for analysis in self.analysis_history:
            matches = self.find_matching_patterns(analysis.prompt, analysis)
            for match in matches:
                pattern_name = match.pattern.description
                pattern_usage[pattern_name] = pattern_usage.get(pattern_name, 0) + 1
        
        return {
            "total_analyses": total_analyses,
            "average_quality": avg_quality,
            "most_used_patterns": sorted(pattern_usage.items(), key=lambda x: x[1], reverse=True)[:5],
            "total_patterns_available": len(self.example_db.patterns)
        }
