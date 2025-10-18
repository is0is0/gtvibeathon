"""
HDR Agent - Generates HDR lighting and environment maps.
"""

import re
from typing import Optional, Dict, Any
from agency3d.core.agent import Agent
from agency3d.core.models import AgentResponse


class HDRAgent(Agent):
    """Agent responsible for generating HDR lighting and environment maps."""
    
    def __init__(self, context=None):
        super().__init__(
            role="hdr",
            system_prompt="""You are an HDR lighting and environment expert. Generate HDR lighting setups and environment maps.

Your task:
- Create HDR environment maps and lighting setups
- Generate realistic lighting conditions
- Support various lighting scenarios (indoor, outdoor, studio, etc.)
- Create equirectangular HDR maps
- Set up proper lighting parameters

Guidelines:
- Use realistic lighting values and color temperatures
- Consider different times of day and weather conditions
- Support both natural and artificial lighting
- Include proper exposure and tone mapping
- Optimize for real-time rendering when possible

Only output HDR lighting code in hdr blocks""",
            context=context
        )
    
    def _parse_response(self, response_text: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """Parse the HDR agent's response and extract HDR code."""
        # Extract HDR code block
        hdr_match = re.search(r"hdr\n(.*?)(?=\n\n|\Z)", response_text, re.DOTALL)
        hdr_code = hdr_match.group(1).strip() if hdr_match else response_text
        
        return AgentResponse(
            success=True,
            content=hdr_code,
            metadata={
                "agent_type": "hdr",
                "lighting_type": self._detect_lighting_type(hdr_code),
                "environment_type": self._detect_environment_type(hdr_code)
            }
        )
    
    def _detect_lighting_type(self, code: str) -> str:
        """Detect the type of lighting from the code."""
        code_lower = code.lower()
        if "sun" in code_lower or "daylight" in code_lower:
            return "natural"
        elif "studio" in code_lower or "artificial" in code_lower:
            return "studio"
        elif "night" in code_lower or "moon" in code_lower:
            return "night"
        else:
            return "mixed"
    
    def _detect_environment_type(self, code: str) -> str:
        """Detect the environment type from the code."""
        code_lower = code.lower()
        if "indoor" in code_lower or "room" in code_lower:
            return "indoor"
        elif "outdoor" in code_lower or "landscape" in code_lower:
            return "outdoor"
        elif "studio" in code_lower:
            return "studio"
        else:
            return "mixed"
