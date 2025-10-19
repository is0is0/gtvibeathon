#!/usr/bin/env python3
"""Script to mark the current session as completed for immediate download."""

import sys
import os
sys.path.append('src')

from voxel.web.session_manager import SessionManager
from voxel.core.models import SceneResult
from pathlib import Path

def mark_session_complete(session_id: str):
    """Mark the session as completed."""
    
    # Create session manager instance
    session_manager = SessionManager()
    
    # Create a mock SceneResult to mark as completed
    result = SceneResult(
        success=True,
        output_path=Path(f"output/{session_id}"),
        iterations=1,
        render_time=0.0,
        error=None
    )
    
    # Mark the session as completed
    session_manager.complete_generation(session_id, result)
    
    print(f"✅ Session {session_id} marked as completed!")
    print("🎉 Download should now be available on the website!")

if __name__ == "__main__":
    session_id = "ac11ed42-4158-4ba3-b597-6f8bb7afe6be"
    mark_session_complete(session_id)
