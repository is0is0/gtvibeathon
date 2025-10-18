"""Session manager for tracking generation sessions."""

import logging
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from threading import Lock

logger = logging.getLogger(__name__)


class SessionManager:
    """Manages generation sessions and their state."""

    def __init__(self):
        """Initialize the session manager."""
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.lock = Lock()

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
                    'result': {
                        'success': result.success,
                        'output_path': str(result.output_path) if result.output_path else None,
                        'iterations': result.iterations,
                        'render_time': result.render_time,
                        'error': result.error
                    }
                })

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
