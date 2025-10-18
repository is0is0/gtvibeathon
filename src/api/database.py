"""
Database Manager for Voxel API
Handles all database operations for users, projects, and assets.
Supports both SQLite (development) and PostgreSQL (production).
"""

import os
import json
import sqlite3
from datetime import datetime
from typing import Optional, List, Dict, Any
from pathlib import Path
import logging

from api.schemas import (
    UserProfile,
    ProjectSummary,
    ProjectDetails,
    GeneratedAsset,
    GenerationStageUpdate,
    ProjectStatus,
    ContextType,
    AgentType,
)

logger = logging.getLogger(__name__)


class DatabaseManager:
    """
    Manages database operations for the Voxel API.
    Provides a simple interface for CRUD operations on users, projects, and assets.
    """

    def __init__(self, db_path: str = "data/voxel.db", db_type: str = "sqlite"):
        """
        Initialize database manager.

        Args:
            db_path: Path to SQLite database file (for SQLite backend)
            db_type: Database type ('sqlite' or 'postgresql')
        """
        self.db_path = db_path
        self.db_type = db_type

        # Ensure data directory exists
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)

        if db_type == "sqlite":
            self._init_sqlite()
        else:
            raise NotImplementedError(f"Database type {db_type} not yet implemented")

        logger.info(f"DatabaseManager initialized with {db_type} at {db_path}")

    def _init_sqlite(self):
        """Initialize SQLite database with schema."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL,
                subscription_tier TEXT DEFAULT 'free',
                total_generations INTEGER DEFAULT 0,
                total_downloads INTEGER DEFAULT 0
            )
        """)

        # Projects table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                project_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                prompt TEXT NOT NULL,
                status TEXT NOT NULL,
                progress REAL DEFAULT 0.0,
                current_stage TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                completed_at TEXT,
                estimated_time REAL,
                error_message TEXT,
                FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE
            )
        """)

        # Project agents table (many-to-many)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS project_agents (
                project_id TEXT NOT NULL,
                agent_type TEXT NOT NULL,
                PRIMARY KEY (project_id, agent_type),
                FOREIGN KEY (project_id) REFERENCES projects (project_id) ON DELETE CASCADE
            )
        """)

        # Context files table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS context_files (
                file_id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                agent_type TEXT NOT NULL,
                filename TEXT NOT NULL,
                file_path TEXT NOT NULL,
                context_type TEXT NOT NULL,
                file_size INTEGER NOT NULL,
                uploaded_at TEXT NOT NULL,
                FOREIGN KEY (project_id) REFERENCES projects (project_id) ON DELETE CASCADE
            )
        """)

        # Generated assets table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS generated_assets (
                asset_id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                asset_type TEXT NOT NULL,
                filename TEXT NOT NULL,
                file_path TEXT NOT NULL,
                file_size INTEGER NOT NULL,
                preview_url TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (project_id) REFERENCES projects (project_id) ON DELETE CASCADE
            )
        """)

        # Generation stages table (for progress tracking)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS generation_stages (
                stage_id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id TEXT NOT NULL,
                stage_name TEXT NOT NULL,
                status TEXT NOT NULL,
                progress REAL DEFAULT 0.0,
                message TEXT,
                started_at TEXT,
                completed_at TEXT,
                FOREIGN KEY (project_id) REFERENCES projects (project_id) ON DELETE CASCADE
            )
        """)

        # Project settings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS project_settings (
                project_id TEXT PRIMARY KEY,
                mode TEXT NOT NULL,
                settings_json TEXT NOT NULL,
                FOREIGN KEY (project_id) REFERENCES projects (project_id) ON DELETE CASCADE
            )
        """)

        # Create indexes for faster queries
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_projects_user_id ON projects (user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_projects_status ON projects (status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_context_files_project ON context_files (project_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_assets_project ON generated_assets (project_id)")

        conn.commit()
        conn.close()
        logger.info("SQLite database schema initialized")

    def _get_connection(self):
        """Get database connection."""
        if self.db_type == "sqlite":
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # Enable column access by name
            return conn
        else:
            raise NotImplementedError(f"Database type {self.db_type} not supported")

    # ==================== USER OPERATIONS ====================

    def create_user(
        self,
        user_id: str,
        email: str,
        username: str,
        password_hash: str,
        subscription_tier: str = "free",
    ) -> bool:
        """
        Create a new user.

        Args:
            user_id: Unique user identifier
            email: User email address
            username: Username
            password_hash: Hashed password
            subscription_tier: Subscription level

        Returns:
            True if successful, False otherwise
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO users (user_id, email, username, password_hash, created_at, subscription_tier)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (user_id, email, username, password_hash, datetime.utcnow().isoformat(), subscription_tier),
            )

            conn.commit()
            conn.close()
            logger.info(f"Created user: {username} ({email})")
            return True
        except sqlite3.IntegrityError as e:
            logger.error(f"User creation failed: {e}")
            return False

    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email address."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        row = cursor.fetchone()
        conn.close()

        if row:
            return dict(row)
        return None

    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user by username."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        conn.close()

        if row:
            return dict(row)
        return None

    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            return dict(row)
        return None

    def verify_credentials(self, email: str, password_hash: str) -> Optional[Dict[str, Any]]:
        """
        Verify user credentials.

        Args:
            email: User email
            password_hash: Hashed password to verify

        Returns:
            User data if valid, None otherwise
        """
        user = self.get_user_by_email(email)
        if user and user["password_hash"] == password_hash:
            return user
        return None

    def update_user_stats(self, user_id: str, generations: int = 0, downloads: int = 0):
        """Update user statistics."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE users
            SET total_generations = total_generations + ?,
                total_downloads = total_downloads + ?
            WHERE user_id = ?
        """,
            (generations, downloads, user_id),
        )

        conn.commit()
        conn.close()

    # ==================== PROJECT OPERATIONS ====================

    def create_project(
        self,
        project_id: str,
        user_id: str,
        prompt: str,
        agents: List[str],
        settings: Dict[str, Any],
    ) -> bool:
        """
        Create a new project.

        Args:
            project_id: Unique project identifier
            user_id: User who owns the project
            prompt: Generation prompt
            agents: List of agent types to use
            settings: Project settings (mode and configuration)

        Returns:
            True if successful
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            now = datetime.utcnow().isoformat()

            # Create project
            cursor.execute(
                """
                INSERT INTO projects (
                    project_id, user_id, prompt, status, progress,
                    created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (project_id, user_id, prompt, "pending", 0.0, now, now),
            )

            # Add selected agents
            for agent in agents:
                cursor.execute(
                    "INSERT INTO project_agents (project_id, agent_type) VALUES (?, ?)",
                    (project_id, agent),
                )

            # Store settings
            cursor.execute(
                "INSERT INTO project_settings (project_id, mode, settings_json) VALUES (?, ?, ?)",
                (project_id, settings.get("mode", "automatic"), json.dumps(settings)),
            )

            conn.commit()
            conn.close()
            logger.info(f"Created project {project_id} for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Project creation failed: {e}")
            return False

    def get_project(self, project_id: str) -> Optional[ProjectDetails]:
        """
        Get complete project details.

        Args:
            project_id: Project identifier

        Returns:
            ProjectDetails object or None
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        # Get project
        cursor.execute("SELECT * FROM projects WHERE project_id = ?", (project_id,))
        project_row = cursor.fetchone()

        if not project_row:
            conn.close()
            return None

        project = dict(project_row)

        # Get agents
        cursor.execute("SELECT agent_type FROM project_agents WHERE project_id = ?", (project_id,))
        agents = [row["agent_type"] for row in cursor.fetchall()]

        # Get assets
        cursor.execute("SELECT * FROM generated_assets WHERE project_id = ?", (project_id,))
        asset_rows = cursor.fetchall()
        assets = [
            GeneratedAsset(
                asset_type=row["asset_type"],
                filename=row["filename"],
                url=f"/api/projects/{project_id}/assets/{row['filename']}",
                file_size=row["file_size"],
                preview_url=row["preview_url"],
                created_at=row["created_at"],
            )
            for row in asset_rows
        ]

        # Get generation stages
        cursor.execute(
            "SELECT * FROM generation_stages WHERE project_id = ? ORDER BY stage_id",
            (project_id,),
        )
        stage_rows = cursor.fetchall()
        stages = [
            GenerationStageUpdate(
                stage=row["stage_name"],
                status=row["status"],
                progress=row["progress"],
                message=row["message"],
            )
            for row in stage_rows
        ]

        # Get settings
        cursor.execute("SELECT settings_json FROM project_settings WHERE project_id = ?", (project_id,))
        settings_row = cursor.fetchone()
        settings = json.loads(settings_row["settings_json"]) if settings_row else {}

        conn.close()

        return ProjectDetails(
            project_id=project["project_id"],
            prompt=project["prompt"],
            agents=agents,
            settings=settings,
            status=ProjectStatus(project["status"]),
            progress=project["progress"],
            current_stage=project["current_stage"],
            assets=assets,
            stages=stages,
            created_at=project["created_at"],
            updated_at=project["updated_at"],
            completed_at=project["completed_at"],
            estimated_time=project["estimated_time"],
            error_message=project["error_message"],
        )

    def list_projects(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 20,
        status: Optional[str] = None,
    ) -> List[ProjectSummary]:
        """
        List user projects with pagination.

        Args:
            user_id: User identifier
            skip: Number of records to skip
            limit: Maximum number of records
            status: Filter by status (optional)

        Returns:
            List of ProjectSummary objects
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        query = "SELECT * FROM projects WHERE user_id = ?"
        params = [user_id]

        if status:
            query += " AND status = ?"
            params.append(status)

        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, skip])

        cursor.execute(query, params)
        rows = cursor.fetchall()

        projects = []
        for row in rows:
            project = dict(row)

            # Get preview asset (first image)
            cursor.execute(
                """
                SELECT filename FROM generated_assets
                WHERE project_id = ? AND asset_type IN ('render', 'preview')
                LIMIT 1
            """,
                (project["project_id"],),
            )
            preview_row = cursor.fetchone()
            preview_url = (
                f"/api/projects/{project['project_id']}/assets/{preview_row['filename']}"
                if preview_row
                else None
            )

            projects.append(
                ProjectSummary(
                    project_id=project["project_id"],
                    prompt=project["prompt"],
                    status=ProjectStatus(project["status"]),
                    preview_url=preview_url,
                    created_at=project["created_at"],
                    completed_at=project["completed_at"],
                )
            )

        conn.close()
        return projects

    def update_project_status(
        self,
        project_id: str,
        status: str,
        progress: Optional[float] = None,
        current_stage: Optional[str] = None,
        error_message: Optional[str] = None,
    ):
        """Update project status and progress."""
        conn = self._get_connection()
        cursor = conn.cursor()

        updates = ["status = ?", "updated_at = ?"]
        params = [status, datetime.utcnow().isoformat()]

        if progress is not None:
            updates.append("progress = ?")
            params.append(progress)

        if current_stage is not None:
            updates.append("current_stage = ?")
            params.append(current_stage)

        if error_message is not None:
            updates.append("error_message = ?")
            params.append(error_message)

        if status == "completed":
            updates.append("completed_at = ?")
            params.append(datetime.utcnow().isoformat())

        params.append(project_id)

        cursor.execute(f"UPDATE projects SET {', '.join(updates)} WHERE project_id = ?", params)

        conn.commit()
        conn.close()

    def delete_project(self, project_id: str) -> bool:
        """Delete a project and all associated data."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute("DELETE FROM projects WHERE project_id = ?", (project_id,))

            conn.commit()
            conn.close()
            logger.info(f"Deleted project {project_id}")
            return True
        except Exception as e:
            logger.error(f"Project deletion failed: {e}")
            return False

    def count_projects(self, user_id: str, status: Optional[str] = None) -> int:
        """Count user projects."""
        conn = self._get_connection()
        cursor = conn.cursor()

        query = "SELECT COUNT(*) as count FROM projects WHERE user_id = ?"
        params = [user_id]

        if status:
            query += " AND status = ?"
            params.append(status)

        cursor.execute(query, params)
        count = cursor.fetchone()["count"]
        conn.close()

        return count

    # ==================== CONTEXT FILE OPERATIONS ====================

    def save_context_file(
        self,
        file_id: str,
        project_id: str,
        agent_type: str,
        filename: str,
        file_path: str,
        context_type: str,
        file_size: int,
    ) -> bool:
        """Save context file metadata."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO context_files (
                    file_id, project_id, agent_type, filename, file_path,
                    context_type, file_size, uploaded_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    file_id,
                    project_id,
                    agent_type,
                    filename,
                    file_path,
                    context_type,
                    file_size,
                    datetime.utcnow().isoformat(),
                ),
            )

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Context file save failed: {e}")
            return False

    def get_context_file(self, file_id: str) -> Optional[Dict[str, Any]]:
        """Get context file metadata."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM context_files WHERE file_id = ?", (file_id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            return dict(row)
        return None

    def list_context_files(self, project_id: str) -> List[Dict[str, Any]]:
        """List all context files for a project."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM context_files WHERE project_id = ?", (project_id,))
        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    # ==================== ASSET OPERATIONS ====================

    def add_generated_asset(
        self,
        asset_id: str,
        project_id: str,
        asset_type: str,
        filename: str,
        file_path: str,
        file_size: int,
        preview_url: Optional[str] = None,
    ) -> bool:
        """Add a generated asset to a project."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO generated_assets (
                    asset_id, project_id, asset_type, filename, file_path,
                    file_size, preview_url, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    asset_id,
                    project_id,
                    asset_type,
                    filename,
                    file_path,
                    file_size,
                    preview_url,
                    datetime.utcnow().isoformat(),
                ),
            )

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Asset save failed: {e}")
            return False

    def get_asset(self, project_id: str, filename: str) -> Optional[Dict[str, Any]]:
        """Get asset metadata."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM generated_assets WHERE project_id = ? AND filename = ?",
            (project_id, filename),
        )
        row = cursor.fetchone()
        conn.close()

        if row:
            return dict(row)
        return None

    # ==================== STAGE OPERATIONS ====================

    def add_generation_stage(
        self,
        project_id: str,
        stage_name: str,
        status: str = "pending",
        progress: float = 0.0,
        message: Optional[str] = None,
    ) -> bool:
        """Add a generation stage for progress tracking."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO generation_stages (
                    project_id, stage_name, status, progress, message, started_at
                )
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (project_id, stage_name, status, progress, message, datetime.utcnow().isoformat()),
            )

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Stage add failed: {e}")
            return False

    def update_generation_stage(
        self,
        project_id: str,
        stage_name: str,
        status: str,
        progress: float,
        message: Optional[str] = None,
    ):
        """Update a generation stage."""
        conn = self._get_connection()
        cursor = conn.cursor()

        updates = ["status = ?", "progress = ?"]
        params = [status, progress]

        if message:
            updates.append("message = ?")
            params.append(message)

        if status == "completed":
            updates.append("completed_at = ?")
            params.append(datetime.utcnow().isoformat())

        params.extend([project_id, stage_name])

        cursor.execute(
            f"UPDATE generation_stages SET {', '.join(updates)} WHERE project_id = ? AND stage_name = ?",
            params,
        )

        conn.commit()
        conn.close()

    # ==================== STATISTICS ====================

    def get_user_statistics(self, user_id: str) -> Dict[str, Any]:
        """Get user statistics."""
        conn = self._get_connection()
        cursor = conn.cursor()

        # User info
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        user = dict(cursor.fetchone())

        # Project counts
        cursor.execute(
            """
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed,
                SUM(CASE WHEN status = 'processing' THEN 1 ELSE 0 END) as processing,
                SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed
            FROM projects
            WHERE user_id = ?
        """,
            (user_id,),
        )
        stats = dict(cursor.fetchone())

        conn.close()

        return {
            "user_id": user_id,
            "total_projects": stats["total"],
            "completed_projects": stats["completed"] or 0,
            "processing_projects": stats["processing"] or 0,
            "failed_projects": stats["failed"] or 0,
            "total_generations": user["total_generations"],
            "total_downloads": user["total_downloads"],
            "subscription_tier": user["subscription_tier"],
            "member_since": user["created_at"],
        }


# ==================== EXAMPLE USAGE ====================

if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)

    db = DatabaseManager("data/voxel_test.db")

    # Create test user
    db.create_user(
        user_id="user_123",
        email="test@example.com",
        username="testuser",
        password_hash="hashed_password_here",
    )

    # Create test project
    db.create_project(
        project_id="proj_456",
        user_id="user_123",
        prompt="A cozy bedroom with warm lighting",
        agents=["concept", "builder", "texture", "render"],
        settings={"mode": "automatic", "quality": "high"},
    )

    # Update project
    db.update_project_status("proj_456", "processing", progress=0.5, current_stage="texturing")

    # Add asset
    db.add_generated_asset(
        asset_id="asset_789",
        project_id="proj_456",
        asset_type="render",
        filename="final_render.png",
        file_path="output/renders/final_render.png",
        file_size=1024000,
    )

    # Get project details
    project = db.get_project("proj_456")
    print(f"\nProject: {project.prompt}")
    print(f"Status: {project.status}")
    print(f"Assets: {len(project.assets)}")

    # Get statistics
    stats = db.get_user_statistics("user_123")
    print(f"\nUser Statistics: {stats}")
