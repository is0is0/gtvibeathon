"""Session manager for tracking generation sessions."""

import logging
import uuid
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from threading import Lock

logger = logging.getLogger(__name__)


class SessionManager:
    """Manages generation sessions and their state."""

    def __init__(self, output_dir: Path = Path("./output")):
        """Initialize the session manager."""
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.lock = Lock()
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Recover sessions from disk on startup
        self._recover_sessions_from_disk()

    def create_session(self) -> str:
        """
        Create a new session.

        Returns:
            Session ID
        """
        session_id = str(uuid.uuid4())

        with self.lock:
            self.sessions[session_id] = {
                'id': session_id,
                'created_at': datetime.now().isoformat(),
                'status': 'created',
                'uploads': []
            }

        self._persist_session(session_id)
        logger.info(f"Created session: {session_id}")
        return session_id

    def start_generation(
        self,
        session_id: Optional[str],
        prompt: str,
        agents: List[str],
        context: List[str]
    ) -> Dict[str, Any]:
        """
        Start a generation session.

        Args:
            session_id: Existing session ID or None to create new
            prompt: User's scene description
            agents: List of agent IDs to use
            context: List of context file paths

        Returns:
            Session data
        """
        if session_id is None or session_id not in self.sessions:
            session_id = self.create_session()

        with self.lock:
            self.sessions[session_id].update({
                'prompt': prompt,
                'agents': agents,
                'context': context,
                'status': 'pending',
                'started_at': datetime.now().isoformat(),
                'current_stage': 'initialization',
                'progress': []
            })

        self._persist_session(session_id)
        logger.info(f"Started generation for session: {session_id}")
        return self.sessions[session_id]

    def update_status(
        self,
        session_id: str,
        status: str,
        error: Optional[str] = None
    ) -> None:
        """
        Update session status.

        Args:
            session_id: Session identifier
            status: New status
            error: Optional error message
        """
        with self.lock:
            if session_id in self.sessions:
                self.sessions[session_id]['status'] = status
                self.sessions[session_id]['updated_at'] = datetime.now().isoformat()

                if error:
                    self.sessions[session_id]['error'] = error

        self._persist_session(session_id)
        logger.info(f"Session {session_id} status: {status}")

    def add_progress(
        self,
        session_id: str,
        stage: str,
        agent: str,
        message: str
    ) -> None:
        """
        Add progress update to session.

        Args:
            session_id: Session identifier
            stage: Current stage
            agent: Agent name
            message: Progress message
        """
        with self.lock:
            if session_id in self.sessions:
                progress_entry = {
                    'timestamp': datetime.now().isoformat(),
                    'stage': stage,
                    'agent': agent,
                    'message': message
                }

                if 'progress' not in self.sessions[session_id]:
                    self.sessions[session_id]['progress'] = []

                self.sessions[session_id]['progress'].append(progress_entry)
                self.sessions[session_id]['current_stage'] = stage

        self._persist_session(session_id)

    def complete_generation(
        self,
        session_id: str,
        result: Any
    ) -> None:
        """
        Mark generation as complete.

        Args:
            session_id: Session identifier
            result: SceneResult object
        """
        with self.lock:
            if session_id in self.sessions:
                self.sessions[session_id].update({
                    'status': 'completed' if result.success else 'failed',
                    'completed_at': datetime.now().isoformat(),
                    'output_path': str(result.session_dir) if result.session_dir else None,  # Store session directory
                    'result': {
                        'success': result.success,
                        'output_path': str(result.output_path) if result.output_path else None,  # Render image path
                        'session_dir': str(result.session_dir) if result.session_dir else None,  # Session directory
                        'iterations': result.iterations,
                        'render_time': result.render_time,
                        'error': result.error
                    }
                })

        self._persist_session(session_id)
        logger.info(f"Generation completed for session: {session_id}")

    def modify_agents(
        self,
        session_id: str,
        action: str,
        agent_ids: List[str]
    ) -> None:
        """
        Modify agents during generation.

        Args:
            session_id: Session identifier
            action: 'add' or 'remove'
            agent_ids: List of agent IDs
        """
        with self.lock:
            if session_id not in self.sessions:
                raise ValueError(f"Session not found: {session_id}")

            current_agents = self.sessions[session_id].get('agents', [])

            if action == 'add':
                for agent_id in agent_ids:
                    if agent_id not in current_agents:
                        current_agents.append(agent_id)
            elif action == 'remove':
                current_agents = [a for a in current_agents if a not in agent_ids]
            else:
                raise ValueError(f"Invalid action: {action}")

            self.sessions[session_id]['agents'] = current_agents

            # Log the modification
            if 'agent_modifications' not in self.sessions[session_id]:
                self.sessions[session_id]['agent_modifications'] = []

            self.sessions[session_id]['agent_modifications'].append({
                'timestamp': datetime.now().isoformat(),
                'action': action,
                'agents': agent_ids
            })

            logger.info(f"Modified agents for session {session_id}: {action} {agent_ids}")

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get session data.

        Args:
            session_id: Session identifier

        Returns:
            Session data or None
        """
        with self.lock:
            return self.sessions.get(session_id)

    def get_active_sessions(self) -> List[Dict[str, Any]]:
        """
        Get all active sessions.

        Returns:
            List of active session data
        """
        with self.lock:
            return [
                session for session in self.sessions.values()
                if session['status'] in ['pending', 'running']
            ]

    def cleanup_old_sessions(self, max_age_hours: int = 24) -> int:
        """
        Clean up old sessions.

        Args:
            max_age_hours: Maximum age in hours

        Returns:
            Number of sessions cleaned up
        """
        from datetime import timedelta

        cutoff = datetime.now() - timedelta(hours=max_age_hours)
        cleaned = 0

        with self.lock:
            sessions_to_remove = []

            for session_id, session in self.sessions.items():
                created_at = datetime.fromisoformat(session['created_at'])
                if created_at < cutoff and session['status'] in ['completed', 'failed']:
                    sessions_to_remove.append(session_id)

            for session_id in sessions_to_remove:
                del self.sessions[session_id]
                cleaned += 1

        if cleaned > 0:
            logger.info(f"Cleaned up {cleaned} old sessions")

        return cleaned

    def _persist_session(self, session_id: str) -> None:
        """
        Save session state to disk.

        Args:
            session_id: Session identifier
        """
        with self.lock:
            if session_id not in self.sessions:
                return

            session_dir = self.output_dir / session_id
            session_dir.mkdir(parents=True, exist_ok=True)

            state_file = session_dir / "session_state.json"

            try:
                with open(state_file, 'w') as f:
                    json.dump(self.sessions[session_id], f, indent=2, default=str)
                logger.debug(f"Persisted session state: {session_id}")
            except Exception as e:
                logger.error(f"Failed to persist session {session_id}: {e}")

    def _recover_sessions_from_disk(self) -> None:
        """
        Recover session state from disk on startup.
        This syncs in-memory state with what actually exists.
        """
        if not self.output_dir.exists():
            logger.info("No output directory found, starting fresh")
            return

        recovered = 0
        synced = 0

        for session_dir in self.output_dir.iterdir():
            if not session_dir.is_dir():
                continue

            session_id = session_dir.name
            state_file = session_dir / "session_state.json"

            # Try to load saved state
            if state_file.exists():
                try:
                    with open(state_file, 'r') as f:
                        session_data = json.load(f)

                    # Sync state with actual files
                    session_data = self._sync_session_with_files(session_id, session_data)

                    self.sessions[session_id] = session_data
                    recovered += 1
                    logger.info(f"Recovered session from disk: {session_id}")
                except Exception as e:
                    logger.error(f"Failed to recover session {session_id}: {e}")
                    # Fall back to file-based detection
                    self._detect_session_from_files(session_id)
                    synced += 1
            else:
                # No state file, try to detect from files
                self._detect_session_from_files(session_id)
                synced += 1

        logger.info(f"Session recovery complete: {recovered} recovered, {synced} synced from files")

    def _sync_session_with_files(self, session_id: str, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sync session state with actual files on disk.

        Args:
            session_id: Session identifier
            session_data: Current session data

        Returns:
            Updated session data
        """
        session_dir = self.output_dir / session_id

        # Check for completion markers
        blend_files = list(session_dir.glob("*.blend"))
        blend_file = blend_files[0] if blend_files else None
        renders = list((session_dir / "renders").glob("*.png")) if (session_dir / "renders").exists() else []
        scripts = list((session_dir / "scripts").glob("*.py")) if (session_dir / "scripts").exists() else []
        concept_file = session_dir / "concept.md"

        # If we have a render and blend file, generation was successful
        if renders and blend_file and blend_file.exists():
            session_data['status'] = 'completed'
            if 'result' not in session_data:
                session_data['result'] = {}

            session_data['result'].update({
                'success': True,
                'output_path': str(renders[-1]),  # Latest render
                'session_dir': str(session_dir)
            })
            session_data['output_path'] = str(session_dir)

            if 'completed_at' not in session_data:
                # Use latest file modification time
                latest_time = max(
                    renders[-1].stat().st_mtime if renders else 0,
                    blend_file.stat().st_mtime if blend_file.exists() else 0
                )
                session_data['completed_at'] = datetime.fromtimestamp(latest_time).isoformat()

        # If we have concept but no render, it's still in progress or failed
        elif concept_file.exists() and not renders:
            if session_data.get('status') not in ['failed', 'completed']:
                # Check how old it is - if > 30 minutes, probably failed
                age_minutes = (datetime.now().timestamp() - concept_file.stat().st_mtime) / 60
                if age_minutes > 30:
                    session_data['status'] = 'failed'
                    if 'result' not in session_data:
                        session_data['result'] = {}
                    session_data['result']['error'] = 'Generation timeout or crash (recovered from disk)'

        return session_data

    def _detect_session_from_files(self, session_id: str) -> None:
        """
        Detect session state purely from files when no state file exists.

        Args:
            session_id: Session identifier
        """
        session_dir = self.output_dir / session_id

        if not session_dir.exists():
            return

        # Build session data from files
        session_data = {
            'id': session_id,
            'created_at': datetime.fromtimestamp(session_dir.stat().st_ctime).isoformat(),
            'status': 'unknown',
            'recovered_from_disk': True
        }

        # Check for files
        blend_files = list(session_dir.glob("*.blend"))
        blend_file = blend_files[0] if blend_files else None
        renders = list((session_dir / "renders").glob("*.png")) if (session_dir / "renders").exists() else []
        concept_file = session_dir / "concept.md"

        # Try to extract prompt from concept
        if concept_file.exists():
            try:
                concept_text = concept_file.read_text()
                # Look for prompt in concept (usually at the top)
                lines = concept_text.split('\n')
                for line in lines[:10]:
                    if line.strip() and not line.startswith('#'):
                        session_data['prompt'] = line.strip()[:200]
                        break
            except:
                pass

        # Determine status from files
        if renders and blend_file and blend_file.exists():
            session_data['status'] = 'completed'
            session_data['completed_at'] = datetime.fromtimestamp(renders[-1].stat().st_mtime).isoformat()
            session_data['result'] = {
                'success': True,
                'output_path': str(renders[-1]),
                'session_dir': str(session_dir)
            }
            session_data['output_path'] = str(session_dir)
        else:
            session_data['status'] = 'incomplete'

        with self.lock:
            self.sessions[session_id] = session_data

        # Persist this detected state
        self._persist_session(session_id)

        logger.info(f"Detected session from files: {session_id} - {session_data['status']}")
