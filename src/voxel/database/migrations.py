"""
Database migration utilities for Voxel.

This module provides database schema migration functionality.
"""

import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy import text, inspect
from sqlalchemy.exc import SQLAlchemyError

from .models import Base
from .manager import DatabaseManager

logger = logging.getLogger(__name__)


class MigrationManager:
    """Database migration manager."""

    def __init__(self, db_manager: DatabaseManager):
        """Initialize migration manager."""
        self.db_manager = db_manager
        self.migrations_dir = Path("database/migrations")

    def create_migration(self, name: str, description: str) -> str:
        """Create a new migration file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{name}.sql"
        filepath = self.migrations_dir / filename

        # Create migrations directory if it doesn't exist
        self.migrations_dir.mkdir(parents=True, exist_ok=True)

        # Create migration file
        migration_content = f"""-- Migration: {name}
-- Description: {description}
-- Created: {datetime.now().isoformat()}

-- Add your SQL commands here
-- Example:
-- ALTER TABLE projects ADD COLUMN new_field VARCHAR(255);
-- CREATE INDEX idx_projects_new_field ON projects(new_field);
"""
        
        with open(filepath, 'w') as f:
            f.write(migration_content)
        
        logger.info(f"Created migration: {filename}")
        return str(filepath)

    def get_pending_migrations(self) -> List[Path]:
        """Get list of pending migration files."""
        if not self.migrations_dir.exists():
            return []
        
        migration_files = sorted(self.migrations_dir.glob("*.sql"))
        return migration_files

    def run_migration(self, migration_file: Path) -> bool:
        """Run a specific migration file."""
        try:
            with open(migration_file, 'r') as f:
                sql_commands = f.read()
            
            with self.db_manager.get_session() as session:
                # Split commands by semicolon and execute each
                commands = [cmd.strip() for cmd in sql_commands.split(';') if cmd.strip()]
                for command in commands:
                    if command and not command.startswith('--'):
                        session.execute(text(command))
                
                session.commit()
            
            logger.info(f"Successfully ran migration: {migration_file.name}")
            return True
            
        except SQLAlchemyError as e:
            logger.error(f"Failed to run migration {migration_file.name}: {e}")
            return False

    def run_all_pending_migrations(self) -> Dict[str, Any]:
        """Run all pending migrations."""
        pending_migrations = self.get_pending_migrations()
        results = {
            "total_migrations": len(pending_migrations),
            "successful": 0,
            "failed": 0,
            "errors": []
        }

        for migration_file in pending_migrations:
            if self.run_migration(migration_file):
                results["successful"] += 1
            else:
                results["failed"] += 1
                results["errors"].append(f"Failed to run {migration_file.name}")

        logger.info(f"Migration results: {results}")
        return results

    def get_database_schema(self) -> Dict[str, Any]:
        """Get current database schema information."""
        try:
            with self.db_manager.get_session() as session:
                inspector = inspect(session.bind)
                
                tables = inspector.get_table_names()
                schema_info = {
                    "tables": {},
                    "total_tables": len(tables)
                }
                
                for table_name in tables:
                    columns = inspector.get_columns(table_name)
                    indexes = inspector.get_indexes(table_name)
                    foreign_keys = inspector.get_foreign_keys(table_name)
                    
                    schema_info["tables"][table_name] = {
                        "columns": [
                            {
                                "name": col["name"],
                                "type": str(col["type"]),
                                "nullable": col["nullable"],
                                "primary_key": col.get("primary_key", False)
                            }
                            for col in columns
                        ],
                        "indexes": [
                            {
                                "name": idx["name"],
                                "columns": idx["column_names"],
                                "unique": idx["unique"]
                            }
                            for idx in indexes
                        ],
                        "foreign_keys": [
                            {
                                "name": fk["name"],
                                "constrained_columns": fk["constrained_columns"],
                                "referred_table": fk["referred_table"],
                                "referred_columns": fk["referred_columns"]
                            }
                            for fk in foreign_keys
                        ]
                    }
                
                return schema_info
                
        except SQLAlchemyError as e:
            logger.error(f"Failed to get database schema: {e}")
            return {"error": str(e)}

    def check_schema_consistency(self) -> Dict[str, Any]:
        """Check if database schema matches expected models."""
        try:
            # Get current schema
            current_schema = self.get_database_schema()
            
            # Get expected tables from models
            expected_tables = set(Base.metadata.tables.keys())
            current_tables = set(current_schema.get("tables", {}).keys())
            
            missing_tables = expected_tables - current_tables
            extra_tables = current_tables - expected_tables
            
            return {
                "consistent": len(missing_tables) == 0 and len(extra_tables) == 0,
                "missing_tables": list(missing_tables),
                "extra_tables": list(extra_tables),
                "expected_tables": list(expected_tables),
                "current_tables": list(current_tables)
            }
            
        except Exception as e:
            logger.error(f"Failed to check schema consistency: {e}")
            return {"error": str(e)}

    def backup_database(self, backup_path: Optional[str] = None) -> str:
        """Create a backup of the database."""
        if not backup_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"database/backup_{timestamp}.db"
        
        backup_file = Path(backup_path)
        backup_file.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            # For SQLite, we can simply copy the database file
            if "sqlite" in self.db_manager.database_url:
                import shutil
                db_path = self.db_manager.database_url.replace("sqlite:///", "")
                shutil.copy2(db_path, backup_file)
                logger.info(f"Database backed up to: {backup_file}")
                return str(backup_file)
            else:
                logger.warning("Backup not implemented for non-SQLite databases")
                return ""
                
        except Exception as e:
            logger.error(f"Failed to backup database: {e}")
            return ""

    def restore_database(self, backup_path: str) -> bool:
        """Restore database from backup."""
        try:
            if "sqlite" in self.db_manager.database_url:
                import shutil
                db_path = self.db_manager.database_url.replace("sqlite:///", "")
                shutil.copy2(backup_path, db_path)
                logger.info(f"Database restored from: {backup_path}")
                return True
            else:
                logger.warning("Restore not implemented for non-SQLite databases")
                return False
                
        except Exception as e:
            logger.error(f"Failed to restore database: {e}")
            return False
