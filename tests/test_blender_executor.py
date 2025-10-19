"""Tests for Blender script execution."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch
from src.voxel.blender.executor import BlenderExecutor
from src.voxel.core.config import Config


@pytest.fixture
def mock_config():
    """Create a mock configuration."""
    config = Mock(spec=Config)
    config.blender_path = Path("/usr/bin/blender")
    return config


def test_executor_initialization_invalid_path():
    """Test that executor raises error for invalid Blender path."""
    config = Mock(spec=Config)
    config.blender_path = Path("/nonexistent/blender")

    with pytest.raises(FileNotFoundError):
        BlenderExecutor(config)


@patch('pathlib.Path.exists')
def test_executor_initialization(mock_exists, mock_config):
    """Test executor initialization with valid path."""
    mock_exists.return_value = True
    executor = BlenderExecutor(mock_config)
    assert executor.blender_path == mock_config.blender_path


@patch('pathlib.Path.exists')
@patch('subprocess.run')
def test_execute_script_success(mock_run, mock_exists, mock_config):
    """Test successful script execution."""
    mock_exists.return_value = True
    mock_run.return_value = Mock(
        returncode=0,
        stdout="Script executed",
        stderr=""
    )

    executor = BlenderExecutor(mock_config)
    script_path = Path("/tmp/test_script.py")

    result = executor.execute_script(script_path)

    assert result.success is True
    assert result.stdout == "Script executed"
    assert result.execution_time >= 0


@patch('pathlib.Path.exists')
@patch('subprocess.run')
def test_execute_script_failure(mock_run, mock_exists, mock_config):
    """Test failed script execution."""
    mock_exists.return_value = True
    mock_run.return_value = Mock(
        returncode=1,
        stdout="",
        stderr="Error in script"
    )

    executor = BlenderExecutor(mock_config)
    script_path = Path("/tmp/test_script.py")

    result = executor.execute_script(script_path)

    assert result.success is False
    assert "Error in script" in result.stderr
