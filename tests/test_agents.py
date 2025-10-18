"""Tests for AI agents."""

import pytest
from unittest.mock import Mock, patch
from agency3d.agents import ConceptAgent, BuilderAgent, TextureAgent
from agency3d.core.agent import AgentConfig
from agency3d.core.models import AgentRole


@pytest.fixture
def agent_config():
    """Create a test agent configuration."""
    return AgentConfig(
        provider="anthropic",
        model="claude-3-5-sonnet-20241022",
        api_key="test_key"
    )


def test_concept_agent_initialization(agent_config):
    """Test that ConceptAgent initializes correctly."""
    agent = ConceptAgent(agent_config)
    assert agent.role == AgentRole.CONCEPT
    assert agent.config == agent_config
    assert len(agent.conversation_history) == 0


def test_concept_agent_system_prompt(agent_config):
    """Test that ConceptAgent has appropriate system prompt."""
    agent = ConceptAgent(agent_config)
    prompt = agent.get_system_prompt()
    assert "scene concept" in prompt.lower()
    assert len(prompt) > 100


def test_builder_agent_initialization(agent_config):
    """Test that BuilderAgent initializes correctly."""
    agent = BuilderAgent(agent_config)
    assert agent.role == AgentRole.BUILDER
    assert "blender" in agent.get_system_prompt().lower()


def test_texture_agent_initialization(agent_config):
    """Test that TextureAgent initializes correctly."""
    agent = TextureAgent(agent_config)
    assert agent.role == AgentRole.TEXTURE
    assert "material" in agent.get_system_prompt().lower()


@patch('agency3d.core.agent.Anthropic')
def test_agent_generate_response(mock_anthropic, agent_config):
    """Test agent response generation."""
    # Mock the Anthropic client
    mock_client = Mock()
    mock_response = Mock()
    mock_response.content = [Mock(text="Test response")]
    mock_client.messages.create.return_value = mock_response
    mock_anthropic.return_value = mock_client

    agent = ConceptAgent(agent_config)
    response = agent.generate_response("Create a simple scene")

    assert response.agent_role == AgentRole.CONCEPT
    assert response.content == "Test response"
    assert len(agent.conversation_history) == 2  # user + assistant


def test_agent_reset(agent_config):
    """Test that agent reset clears history."""
    agent = ConceptAgent(agent_config)
    agent.conversation_history.append(Mock())
    agent.conversation_history.append(Mock())

    agent.reset()
    assert len(agent.conversation_history) == 0
