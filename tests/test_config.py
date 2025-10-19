"""Tests for configuration management."""

import pytest
from pathlib import Path
from src.voxel.core.config import Config


def test_config_defaults():
    """Test that config has reasonable defaults."""
    config = Config()
    assert config.ai_provider in ["anthropic", "openai"]
    assert config.render_samples > 0
    assert config.max_iterations > 0


def test_config_validation():
    """Test config validation methods."""
    config = Config(
        blender_path=Path("/nonexistent/path"),
        anthropic_api_key="test_key",
        ai_provider="anthropic"
    )

    # Should raise for invalid Blender path
    with pytest.raises(ValueError, match="Blender executable not found"):
        config.validate_paths()


def test_config_from_env(monkeypatch):
    """Test loading config from environment variables."""
    monkeypatch.setenv("AI_PROVIDER", "openai")
    monkeypatch.setenv("RENDER_SAMPLES", "256")

    config = Config()
    assert config.ai_provider == "openai"
    assert config.render_samples == 256
