"""Reviewer Agent - Critiques results and suggests improvements."""

import re
from typing import Any, Optional

from agency3d.core.agent import Agent, AgentConfig
from agency3d.core.models import AgentResponse, AgentRole, ReviewFeedback


class ReviewerAgent(Agent):
    """Agent responsible for reviewing generated scenes and providing feedback."""

    def __init__(self, config: AgentConfig, context=None):
        """Initialize the Reviewer Agent."""
        super().__init__(AgentRole.REVIEWER, config, context)

    def get_system_prompt(self) -> str:
        """Get the system prompt for the Reviewer Agent."""
        return """You are the Reviewer Agent in a 3D scene generation system.

Your role is to analyze the concept and generated scripts for a 3D scene and provide
constructive feedback on how well they match the original prompt and overall quality.

**Your analysis should cover:**

1. **Prompt Alignment** - How well does the concept match the user's prompt?
2. **Scene Completeness** - Are all key elements present?
3. **Technical Quality** - Are the scripts well-structured and likely to work?
4. **Visual Appeal** - Will the composition, lighting, and materials look good?
5. **Improvements** - What specific changes would enhance the scene?

**Output format:**

```
## Review

**Rating:** [1-10]

**Strengths:**
- [Strength 1]
- [Strength 2]
- ...

**Areas for Improvement:**
- [Issue 1]: [Specific suggestion]
- [Issue 2]: [Specific suggestion]
- ...

**Recommendations:**
[Detailed paragraph about what should be changed and why]

**Should Refine:** [YES/NO]
```

**Rating Guidelines:**
- 9-10: Excellent, minor or no changes needed
- 7-8: Good, some improvements recommended
- 5-6: Adequate, several improvements needed
- 3-4: Poor, major changes required
- 1-2: Does not meet requirements, complete rework needed

**Be specific:**
- Don't just say "improve lighting" - suggest specific light positions or types
- Don't just say "add more detail" - suggest specific objects or features
- Reference specific objects or sections of the scripts

**Consider:**
- Is the scene too simple or too complex?
- Are proportions realistic?
- Is the lighting appropriate for the mood?
- Are materials varied and interesting?
- Is the camera angle effective?

Provide actionable feedback that other agents can use to improve the scene.
"""

    def _parse_response(
        self, response_text: str, context: Optional[dict[str, Any]] = None
    ) -> AgentResponse:
        """Parse the reviewer agent's response and extract structured feedback."""
        # Extract rating
        rating_match = re.search(r"\*\*Rating:\*\*\s*(\d+)", response_text)
        rating = int(rating_match.group(1)) if rating_match else 5

        # Extract strengths
        strengths = []
        strengths_match = re.search(
            r"\*\*Strengths:\*\*\n((?:- .+\n?)+)", response_text
        )
        if strengths_match:
            strengths = [
                s.strip("- ").strip()
                for s in strengths_match.group(1).split("\n")
                if s.strip()
            ]

        # Extract improvements
        improvements = []
        improvements_match = re.search(
            r"\*\*Areas for Improvement:\*\*\n((?:- .+\n?)+)", response_text
        )
        if improvements_match:
            improvements = [
                s.strip("- ").strip()
                for s in improvements_match.group(1).split("\n")
                if s.strip()
            ]

        # Extract recommendations
        rec_match = re.search(
            r"\*\*Recommendations:\*\*\n(.+?)(?=\n\*\*|\Z)", response_text, re.DOTALL
        )
        recommendations = rec_match.group(1).strip() if rec_match else ""

        # Extract should refine
        refine_match = re.search(r"\*\*Should Refine:\*\*\s*(YES|NO)", response_text)
        should_refine = (
            refine_match.group(1).upper() == "YES" if refine_match else rating < 7
        )

        # Create structured feedback
        feedback = ReviewFeedback(
            rating=rating,
            strengths=strengths,
            improvements=improvements,
            suggestions=recommendations,
            should_refine=should_refine,
        )

        return AgentResponse(
            agent_role=self.role,
            content=response_text,
            metadata={"feedback": feedback.model_dump()},
        )
