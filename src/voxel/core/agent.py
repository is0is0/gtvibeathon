"""Base agent class for all AI agents in the system."""

import logging
from abc import ABC, abstractmethod
from typing import Any, Optional, Dict, List, Callable
from datetime import datetime

from pydantic import BaseModel, Field

from voxel.core.models import AgentResponse, AgentRole, Message
from voxel.core.agent_context import AgentContext, ContextType

logger = logging.getLogger(__name__)


class AgentConfig(BaseModel):
    """Configuration for an AI agent."""

    provider: str = Field(default="anthropic", description="AI provider")
    model: str = Field(default="claude-3-5-sonnet-20241022", description="Model name")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=4000, ge=100)
    api_key: str = Field(default="", description="API key for the provider")


class Agent(ABC):
    """Base class for all agents in the Voxel system."""

    def __init__(self, role: AgentRole, config: AgentConfig, context: Optional[AgentContext] = None):
        """
        Initialize the agent.

        Args:
            role: The role of this agent
            config: Configuration for the agent
            context: Shared context for agent collaboration
        """
        self.role = role
        self.config = config
        self.context = context or AgentContext()
        self.conversation_history: list[Message] = []
        self._setup_client()

    def _setup_client(self) -> None:
        """Set up the AI client based on provider."""
        if self.config.provider == "anthropic":
            from anthropic import Anthropic

            self.client = Anthropic(api_key=self.config.api_key)
        elif self.config.provider == "openai":
            from openai import OpenAI

            self.client = OpenAI(api_key=self.config.api_key)
        else:
            raise ValueError(f"Unsupported AI provider: {self.config.provider}")

    @abstractmethod
    def get_system_prompt(self) -> str:
        """
        Get the system prompt for this agent.

        Returns:
            System prompt string
        """
        pass

    def add_message(self, message: Message) -> None:
        """Add a message to the conversation history."""
        self.conversation_history.append(message)

    def _call_anthropic(self, messages: list[dict[str, str]]) -> str:
        """Call Anthropic API."""
        response = self.client.messages.create(
            model=self.config.model,
            max_tokens=self.config.max_tokens,
            temperature=self.config.temperature,
            system=self.get_system_prompt(),
            messages=messages,
        )
        return response.content[0].text

    def _call_openai(self, messages: list[dict[str, str]]) -> str:
        """Call OpenAI API."""
        system_msg = {"role": "system", "content": self.get_system_prompt()}
        all_messages = [system_msg] + messages

        response = self.client.chat.completions.create(
            model=self.config.model,
            max_tokens=self.config.max_tokens,
            temperature=self.config.temperature,
            messages=all_messages,
        )
        return response.choices[0].message.content or ""

    def generate_response(self, user_message: str, context: Optional[dict[str, Any]] = None) -> AgentResponse:
        """
        Generate a response to a user message.

        Args:
            user_message: The user's message
            context: Optional context information

        Returns:
            AgentResponse with the agent's reply
        """
        # Add user message to history
        msg = Message(role="user", content=user_message)
        self.add_message(msg)

        # Prepare messages for API
        api_messages = [
            {"role": m.role.value, "content": m.content}
            for m in self.conversation_history
            if m.role.value != "system"
        ]

        # Call appropriate API
        try:
            if self.config.provider == "anthropic":
                response_text = self._call_anthropic(api_messages)
            elif self.config.provider == "openai":
                response_text = self._call_openai(api_messages)
            else:
                raise ValueError(f"Unsupported provider: {self.config.provider}")

            # Add response to history
            assistant_msg = Message(role="assistant", content=response_text)
            self.add_message(assistant_msg)

            # Parse response
            return self._parse_response(response_text, context)

        except Exception as e:
            logger.error(f"Error generating response: {e}")
            raise

    @abstractmethod
    def _parse_response(
        self, response_text: str, context: Optional[dict[str, Any]] = None
    ) -> AgentResponse:
        """
        Parse the raw response into an AgentResponse.

        Args:
            response_text: Raw text from the AI
            context: Optional context

        Returns:
            Parsed AgentResponse
        """
        pass

    def reset(self) -> None:
        """Reset the agent's conversation history."""
        self.conversation_history = []
    
    def add_context(self, context_type: ContextType, content: str, 
                   metadata: Optional[Dict[str, Any]] = None, 
                   confidence: float = 1.0, 
                   tags: Optional[set] = None) -> None:
        """Add context information to the shared context."""
        self.context.add_context(
            context_type=context_type,
            source_agent=self.role,
            content=content,
            metadata=metadata,
            confidence=confidence,
            tags=tags
        )
    
    def get_related_context(self, context_type: ContextType) -> list:
        """Get context from other agents that's relevant to this agent's work."""
        return self.context.get_related_context(self.role, context_type)
    
    def get_agent_insights(self, agent_role: AgentRole) -> Dict[str, Any]:
        """Get insights from a specific agent."""
        return self.context.get_agent_insights(agent_role)
    
    def set_agent_insights(self, insights: Dict[str, Any]) -> None:
        """Set insights from this agent."""
        self.context.set_agent_insights(self.role, insights)
    
    def add_collaboration_event(self, event_type: str, details: Dict[str, Any]) -> None:
        """Add a collaboration event."""
        self.context.add_collaboration_event(event_type, self.role, details)
    
    def get_enhanced_prompt(self, base_prompt: str, context_type: ContextType) -> str:
        """Get an enhanced prompt with relevant context from other agents."""
        related_context = self.get_related_context(context_type)
        
        if not related_context:
            return base_prompt
        
        enhanced_parts = [f"Original prompt: {base_prompt}"]
        enhanced_parts.append("\nRelevant context from other agents:")
        
        for item in related_context[:3]:  # Limit to top 3 most relevant
            enhanced_parts.append(f"- {item.source_agent.value}: {item.content}")
        
        enhanced_parts.append("\nUse this context to inform your work while maintaining the original vision.")
        
        return "\n".join(enhanced_parts)
    
    def share_asset(self, asset_name: str, asset: Any) -> None:
        """Share an asset with other agents."""
        self.context.set_shared_asset(asset_name, asset)
        self.add_collaboration_event("asset_shared", {"asset_name": asset_name, "asset_type": type(asset).__name__})
    
    def get_shared_asset(self, asset_name: str) -> Any:
        """Get a shared asset from other agents."""
        return self.context.get_shared_asset(asset_name)
    
    def setup_realtime_updates(self) -> None:
        """Set up real-time context updates for this agent."""
        def context_update_handler(update: Dict[str, Any]) -> None:
            """Handle real-time context updates."""
            logger.info(f"{self.role.value} received update: {update['context_type']} from {update['source_agent']}")
            # Agents can override this method to handle updates
            self._handle_context_update(update)
        
        self.context.register_observer(self.role, context_update_handler)
        logger.info(f"Set up real-time updates for {self.role.value}")
    
    def _handle_context_update(self, update: Dict[str, Any]) -> None:
        """Handle real-time context updates. Override in subclasses for specific behavior."""
        # Default implementation - agents can override this
        pass
    
    def subscribe_to_context_type(self, context_type: ContextType, 
                                callback: Callable[[Any], None]) -> None:
        """Subscribe to specific context type updates."""
        self.context.subscribe_to_context_type(self.role, context_type, callback)
    
    def get_latest_context(self, context_type: ContextType) -> Optional[Any]:
        """Get the latest context of a specific type."""
        return self.context.get_latest_context(self.role, context_type)
    
    def get_context_updates_since(self, since: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Get all context updates since a specific time."""
        return self.context.get_updates_since(self.role, since)
    
    def get_context_stream(self) -> List[Dict[str, Any]]:
        """Get a stream of all context updates relevant to this agent."""
        return self.context.get_context_stream(self.role)
