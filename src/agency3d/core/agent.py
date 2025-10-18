"""Base agent class for all AI agents in the system."""

import logging
from abc import ABC, abstractmethod
from typing import Any, Optional

from pydantic import BaseModel, Field

from agency3d.core.models import AgentResponse, AgentRole, Message

logger = logging.getLogger(__name__)


class AgentConfig(BaseModel):
    """Configuration for an AI agent."""

    provider: str = Field(default="anthropic", description="AI provider")
    model: str = Field(default="claude-3-5-sonnet-20241022", description="Model name")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=4000, ge=100)
    api_key: str = Field(default="", description="API key for the provider")


class Agent(ABC):
    """Base class for all agents in the 3DAgency system."""

    def __init__(self, role: AgentRole, config: AgentConfig):
        """
        Initialize the agent.

        Args:
            role: The role of this agent
            config: Configuration for the agent
        """
        self.role = role
        self.config = config
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
