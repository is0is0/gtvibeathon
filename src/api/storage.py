"""
Storage Manager for Voxel API
Handles file uploads, downloads, and temporary URL generation.
"""

import os
import secrets
import shutil
import mimetypes
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, BinaryIO
import logging

logger = logging.getLogger(__name__)


class StorageManager:
    """
    Manages file storage operations for the Voxel API.
    Handles uploads, downloads, temporary URLs, and file cleanup.
    """

    def __init__(
        self,
        base_storage_path: str = "data/storage",
        temp_url_expire_minutes: int = 60,
        max_file_size_mb: int = 500,
    ):
        """
        Initialize storage manager.

        Args:
            base_storage_path: Base directory for file storage
            temp_url_expire_minutes: Expiration time for temporary download URLs
            max_file_size_mb: Maximum allowed file size in megabytes
        """
        self.base_storage_path = Path(base_storage_path)
        self.temp_url_expire_minutes = temp_url_expire_minutes
        self.max_file_size_bytes = max_file_size_mb * 1024 * 1024

        # Create storage directories
        self.uploads_path = self.base_storage_path / "uploads"
        self.projects_path = self.base_storage_path / "projects"
        self.temp_path = self.base_storage_path / "temp"

        for path in [self.uploads_path, self.projects_path, self.temp_path]:
            path.mkdir(parents=True, exist_ok=True)

        # Temporary URL storage (in-memory for simplicity, use Redis in production)
        self.temp_urls: Dict[str, Dict[str, Any]] = {}

        logger.info(f"StorageManager initialized at {self.base_storage_path}")

    # ==================== FILE UPLOAD OPERATIONS ====================

    def save_upload(
        self,
        file_id: str,
        filename: str,
        file_data: BinaryIO,
        user_id: str,
        project_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Save an uploaded file.

        Args:
            file_id: Unique file identifier
            filename: Original filename
            file_data: File binary data (file-like object)
            user_id: User who uploaded the file
            project_id: Associated project ID (optional)

        Returns:
            Dictionary with file metadata

        Raises:
            ValueError: If file is too large
        """
        # Determine storage location
        if project_id:
            storage_dir = self.projects_path / project_id / "uploads"
        else:
            storage_dir = self.uploads_path / user_id

        storage_dir.mkdir(parents=True, exist_ok=True)

        # Generate safe filename
        safe_filename = self._sanitize_filename(filename)
        file_path = storage_dir / f"{file_id}_{safe_filename}"

        # Save file with size check
        file_size = 0
        with open(file_path, "wb") as f:
            while True:
                chunk = file_data.read(8192)  # Read in 8KB chunks
                if not chunk:
                    break

                file_size += len(chunk)
                if file_size > self.max_file_size_bytes:
                    # Delete partial file and raise error
                    f.close()
                    file_path.unlink(missing_ok=True)
                    raise ValueError(
                        f"File too large. Maximum size is {self.max_file_size_bytes / 1024 / 1024}MB"
                    )

                f.write(chunk)

        # Detect MIME type
        mime_type, _ = mimetypes.guess_type(safe_filename)

        metadata = {
            "file_id": file_id,
            "filename": safe_filename,
            "original_filename": filename,
            "file_path": str(file_path),
            "file_size": file_size,
            "mime_type": mime_type,
            "user_id": user_id,
            "project_id": project_id,
            "uploaded_at": datetime.utcnow().isoformat(),
        }

        logger.info(f"Saved upload: {safe_filename} ({file_size} bytes)")
        return metadata

    def save_file(
        self,
        file_id: str,
        filename: str,
        content: bytes,
        user_id: str,
        project_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Save file content directly (alternative to save_upload).

        Args:
            file_id: Unique file identifier
            filename: Filename
            content: File content as bytes
            user_id: User ID
            project_id: Project ID (optional)

        Returns:
            File metadata dictionary
        """
        # Check size
        if len(content) > self.max_file_size_bytes:
            raise ValueError(
                f"File too large. Maximum size is {self.max_file_size_bytes / 1024 / 1024}MB"
            )

        # Determine storage location
        if project_id:
            storage_dir = self.projects_path / project_id / "uploads"
        else:
            storage_dir = self.uploads_path / user_id

        storage_dir.mkdir(parents=True, exist_ok=True)

        # Save file
        safe_filename = self._sanitize_filename(filename)
        file_path = storage_dir / f"{file_id}_{safe_filename}"

        with open(file_path, "wb") as f:
            f.write(content)

        # Detect MIME type
        mime_type, _ = mimetypes.guess_type(safe_filename)

        metadata = {
            "file_id": file_id,
            "filename": safe_filename,
            "original_filename": filename,
            "file_path": str(file_path),
            "file_size": len(content),
            "mime_type": mime_type,
            "user_id": user_id,
            "project_id": project_id,
            "uploaded_at": datetime.utcnow().isoformat(),
        }

        logger.info(f"Saved file: {safe_filename} ({len(content)} bytes)")
        return metadata

    # ==================== PROJECT OUTPUT OPERATIONS ====================

    def save_project_output(
        self,
        project_id: str,
        filename: str,
        content: bytes,
        asset_type: str = "render",
    ) -> Dict[str, Any]:
        """
        Save a project output file (render, model, etc.).

        Args:
            project_id: Project identifier
            filename: Output filename
            content: File content
            asset_type: Type of asset (render, model, script, etc.)

        Returns:
            File metadata dictionary
        """
        # Create project output directory
        output_dir = self.projects_path / project_id / "outputs" / asset_type
        output_dir.mkdir(parents=True, exist_ok=True)

        safe_filename = self._sanitize_filename(filename)
        file_path = output_dir / safe_filename

        # Save file
        with open(file_path, "wb") as f:
            f.write(content)

        # Detect MIME type
        mime_type, _ = mimetypes.guess_type(safe_filename)

        metadata = {
            "filename": safe_filename,
            "file_path": str(file_path),
            "file_size": len(content),
            "mime_type": mime_type,
            "asset_type": asset_type,
            "project_id": project_id,
            "created_at": datetime.utcnow().isoformat(),
        }

        logger.info(f"Saved project output: {project_id}/{asset_type}/{safe_filename}")
        return metadata

    def copy_to_project(
        self,
        source_path: str,
        project_id: str,
        filename: str,
        asset_type: str = "render",
    ) -> Dict[str, Any]:
        """
        Copy an existing file to project outputs.

        Args:
            source_path: Source file path
            project_id: Project identifier
            filename: Destination filename
            asset_type: Type of asset

        Returns:
            File metadata dictionary
        """
        source = Path(source_path)
        if not source.exists():
            raise FileNotFoundError(f"Source file not found: {source_path}")

        # Create destination directory
        output_dir = self.projects_path / project_id / "outputs" / asset_type
        output_dir.mkdir(parents=True, exist_ok=True)

        safe_filename = self._sanitize_filename(filename)
        dest_path = output_dir / safe_filename

        # Copy file
        shutil.copy2(source, dest_path)

        # Get file info
        file_size = dest_path.stat().st_size
        mime_type, _ = mimetypes.guess_type(safe_filename)

        metadata = {
            "filename": safe_filename,
            "file_path": str(dest_path),
            "file_size": file_size,
            "mime_type": mime_type,
            "asset_type": asset_type,
            "project_id": project_id,
            "created_at": datetime.utcnow().isoformat(),
        }

        logger.info(f"Copied to project: {safe_filename} ({file_size} bytes)")
        return metadata

    # ==================== FILE RETRIEVAL OPERATIONS ====================

    def get_file_path(self, file_path: str) -> Optional[Path]:
        """
        Get a file path if it exists.

        Args:
            file_path: File path string

        Returns:
            Path object if file exists, None otherwise
        """
        path = Path(file_path)
        if path.exists() and path.is_file():
            return path
        return None

    def read_file(self, file_path: str) -> Optional[bytes]:
        """
        Read file content.

        Args:
            file_path: File path string

        Returns:
            File content as bytes, or None if not found
        """
        path = self.get_file_path(file_path)
        if path:
            with open(path, "rb") as f:
                return f.read()
        return None

    def get_project_asset(
        self,
        project_id: str,
        filename: str,
        asset_type: str = "render",
    ) -> Optional[Path]:
        """
        Get path to a project asset.

        Args:
            project_id: Project identifier
            filename: Asset filename
            asset_type: Type of asset

        Returns:
            Path to asset if exists, None otherwise
        """
        asset_path = self.projects_path / project_id / "outputs" / asset_type / filename
        if asset_path.exists():
            return asset_path
        return None

    # ==================== TEMPORARY URL OPERATIONS ====================

    def create_download_link(
        self,
        file_path: str,
        expires_minutes: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Create a temporary download link for a file.

        Args:
            file_path: Path to file
            expires_minutes: Custom expiration time (optional)

        Returns:
            Dictionary with download_token, url, and expires_at
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Generate secure token
        download_token = secrets.token_urlsafe(32)

        # Calculate expiration
        expires_minutes = expires_minutes or self.temp_url_expire_minutes
        expires_at = datetime.utcnow() + timedelta(minutes=expires_minutes)

        # Store temporary URL metadata
        self.temp_urls[download_token] = {
            "file_path": str(path),
            "filename": path.name,
            "expires_at": expires_at,
            "created_at": datetime.utcnow(),
        }

        logger.info(f"Created download link for {path.name} (expires: {expires_at})")

        return {
            "download_token": download_token,
            "url": f"/api/download/{download_token}",
            "filename": path.name,
            "expires_at": expires_at.isoformat(),
        }

    def verify_download_token(self, download_token: str) -> Optional[Dict[str, Any]]:
        """
        Verify a download token and return file metadata.

        Args:
            download_token: Download token string

        Returns:
            File metadata if token is valid, None otherwise
        """
        if download_token not in self.temp_urls:
            logger.warning(f"Invalid download token: {download_token[:10]}...")
            return None

        metadata = self.temp_urls[download_token]

        # Check expiration
        if datetime.utcnow() > metadata["expires_at"]:
            logger.warning("Download token has expired")
            del self.temp_urls[download_token]  # Clean up expired token
            return None

        return metadata

    def cleanup_expired_tokens(self):
        """Remove expired download tokens."""
        now = datetime.utcnow()
        expired = [token for token, meta in self.temp_urls.items() if now > meta["expires_at"]]

        for token in expired:
            del self.temp_urls[token]

        if expired:
            logger.info(f"Cleaned up {len(expired)} expired download tokens")

    # ==================== FILE DELETION OPERATIONS ====================

    def delete_file(self, file_path: str) -> bool:
        """
        Delete a file.

        Args:
            file_path: Path to file

        Returns:
            True if successful, False otherwise
        """
        try:
            path = Path(file_path)
            if path.exists():
                path.unlink()
                logger.info(f"Deleted file: {file_path}")
                return True
            return False
        except Exception as e:
            logger.error(f"File deletion failed: {e}")
            return False

    def delete_project_files(self, project_id: str) -> bool:
        """
        Delete all files associated with a project.

        Args:
            project_id: Project identifier

        Returns:
            True if successful
        """
        try:
            project_dir = self.projects_path / project_id
            if project_dir.exists():
                shutil.rmtree(project_dir)
                logger.info(f"Deleted project files: {project_id}")
            return True
        except Exception as e:
            logger.error(f"Project deletion failed: {e}")
            return False

    def cleanup_temp_files(self, max_age_hours: int = 24):
        """
        Delete temporary files older than specified age.

        Args:
            max_age_hours: Maximum age in hours
        """
        now = datetime.utcnow()
        max_age = timedelta(hours=max_age_hours)

        deleted_count = 0
        for temp_file in self.temp_path.iterdir():
            if temp_file.is_file():
                file_age = now - datetime.fromtimestamp(temp_file.stat().st_mtime)
                if file_age > max_age:
                    temp_file.unlink()
                    deleted_count += 1

        if deleted_count > 0:
            logger.info(f"Cleaned up {deleted_count} temporary files")

    # ==================== UTILITY FUNCTIONS ====================

    def _sanitize_filename(self, filename: str) -> str:
        """
        Sanitize filename to prevent directory traversal and other issues.

        Args:
            filename: Original filename

        Returns:
            Sanitized filename
        """
        # Remove path separators and parent directory references
        filename = os.path.basename(filename)
        filename = filename.replace("..", "")

        # Remove potentially dangerous characters
        dangerous_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
        for char in dangerous_chars:
            filename = filename.replace(char, "_")

        # Ensure filename is not empty
        if not filename:
            filename = "unnamed_file"

        return filename

    def get_file_info(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata about a file.

        Args:
            file_path: Path to file

        Returns:
            File metadata dictionary or None
        """
        path = Path(file_path)
        if not path.exists():
            return None

        stat = path.stat()
        mime_type, _ = mimetypes.guess_type(path.name)

        return {
            "filename": path.name,
            "file_path": str(path),
            "file_size": stat.st_size,
            "mime_type": mime_type,
            "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
            "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
        }

    def get_storage_stats(self) -> Dict[str, Any]:
        """
        Get storage usage statistics.

        Returns:
            Dictionary with storage statistics
        """
        def get_dir_size(path: Path) -> int:
            """Calculate total size of directory."""
            total = 0
            for item in path.rglob("*"):
                if item.is_file():
                    total += item.stat().st_size
            return total

        return {
            "uploads_size": get_dir_size(self.uploads_path),
            "projects_size": get_dir_size(self.projects_path),
            "temp_size": get_dir_size(self.temp_path),
            "total_size": get_dir_size(self.base_storage_path),
            "max_file_size": self.max_file_size_bytes,
        }


# ==================== EXAMPLE USAGE ====================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Initialize storage manager
    storage = StorageManager("data/test_storage")

    # Save a test file
    test_content = b"Hello, this is test content!"
    metadata = storage.save_file(
        file_id="file_123",
        filename="test.txt",
        content=test_content,
        user_id="user_456",
    )
    print(f"Saved file: {metadata}")

    # Save project output
    render_data = b"PNG_IMAGE_DATA_HERE"
    output_meta = storage.save_project_output(
        project_id="proj_789",
        filename="render.png",
        content=render_data,
        asset_type="render",
    )
    print(f"\nSaved project output: {output_meta}")

    # Create download link
    download_link = storage.create_download_link(metadata["file_path"])
    print(f"\nDownload link: {download_link}")

    # Verify token
    verified = storage.verify_download_token(download_link["download_token"])
    print(f"Token verified: {verified}")

    # Get storage stats
    stats = storage.get_storage_stats()
    print(f"\nStorage stats: {stats}")

    # Cleanup
    storage.cleanup_expired_tokens()
    storage.cleanup_temp_files()
