"""Tests for script management."""

import pytest
from pathlib import Path
import tempfile
import shutil
from agency3d.blender.script_manager import ScriptManager


@pytest.fixture
def temp_output_dir():
    """Create a temporary output directory."""
    temp_dir = Path(tempfile.mkdtemp())
    yield temp_dir
    shutil.rmtree(temp_dir)


def test_script_manager_initialization(temp_output_dir):
    """Test ScriptManager initialization."""
    manager = ScriptManager(temp_output_dir)
    assert manager.output_dir == temp_output_dir
    assert temp_output_dir.exists()


def test_create_session_dir(temp_output_dir):
    """Test session directory creation."""
    manager = ScriptManager(temp_output_dir)
    session_dir = manager.create_session_dir("test_session")

    assert session_dir.exists()
    assert (session_dir / "scripts").exists()
    assert (session_dir / "renders").exists()
    assert (session_dir / "logs").exists()


def test_save_script(temp_output_dir):
    """Test saving a script file."""
    manager = ScriptManager(temp_output_dir)
    session_dir = manager.create_session_dir("test_session")

    script_content = "import bpy\nprint('Hello')"
    script_path = manager.save_script(
        script_content,
        "test_script",
        session_dir
    )

    assert script_path.exists()
    assert script_path.read_text() == script_content


def test_combine_scripts(temp_output_dir):
    """Test combining multiple scripts."""
    manager = ScriptManager(temp_output_dir)
    session_dir = manager.create_session_dir("test_session")

    # Create test scripts
    script1 = manager.save_script("# Script 1", "script1", session_dir)
    script2 = manager.save_script("# Script 2", "script2", session_dir)

    # Combine them
    combined = manager.combine_scripts(
        [script1, script2],
        "combined",
        session_dir
    )

    assert combined.exists()
    content = combined.read_text()
    assert "Script 1" in content
    assert "Script 2" in content


def test_save_concept(temp_output_dir):
    """Test saving scene concept."""
    manager = ScriptManager(temp_output_dir)
    session_dir = manager.create_session_dir("test_session")

    concept = "# Test Concept\nA test scene"
    concept_path = manager.save_concept(concept, session_dir)

    assert concept_path.exists()
    assert concept_path.read_text() == concept
