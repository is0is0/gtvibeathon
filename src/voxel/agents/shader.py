"""
Shader Agent - Generates shader code from text prompts.
"""

import re
from typing import Optional, Dict, Any
from voxel.core.agent import Agent
from voxel.core.models import AgentResponse


class ShaderAgent(Agent):
    """Agent responsible for generating shader code from text descriptions."""
    
    def __init__(self, context=None):
        super().__init__(
            role="shader",
            system_prompt="""You are a shader programming expert. Generate high-quality shader code based on text descriptions.

Your task:
- Generate shader code (GLSL, HLSL, or similar) from text prompts
- Focus on visual effects, materials, lighting, and rendering
- Output clean, well-commented shader code
- Support various shader types: vertex, fragment, compute, etc.

Guidelines:
- Use proper shader syntax and conventions
- Include necessary uniforms and attributes
- Add comments explaining the code
- Optimize for performance when possible
- Support both forward and deferred rendering

Only output shader code in shader blocks""",
            context=context
        )
    
    def _parse_response(self, response_text: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """Parse the shader agent's response and extract shader code."""
        # Extract shader code block
        shader_match = re.search(r"shader\n(.*?)(?=\n\n|\Z)", response_text, re.DOTALL)
        shader_code = shader_match.group(1).strip() if shader_match else response_text
        
        return AgentResponse(
            success=True,
            content=shader_code,
            metadata={
                "agent_type": "shader",
                "shader_type": self._detect_shader_type(shader_code),
                "complexity": self._assess_complexity(shader_code)
            }
        )
    
    def _detect_shader_type(self, code: str) -> str:
        """Detect the type of shader from the code."""
        code_lower = code.lower()
        if "main()" in code_lower and "gl_position" in code_lower:
            return "vertex"
        elif "main()" in code_lower and ("gl_fragcolor" in code_lower or "fragcolor" in code_lower):
            return "fragment"
        elif "compute" in code_lower:
            return "compute"
        else:
            return "unknown"
    
    def _assess_complexity(self, code: str) -> str:
        """Assess the complexity of the shader code."""
        lines = len(code.split('\n'))
        if lines < 20:
            return "simple"
        elif lines < 50:
            return "medium"
        else:
            return "complex"
