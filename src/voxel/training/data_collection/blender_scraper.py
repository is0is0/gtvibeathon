"""
Blender File Scraper - Collects real Blender files from public repositories.
Scrapes GitHub, BlendSwap, and other sources for training data.
"""

import logging
import asyncio
import aiohttp
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import json
import hashlib

logger = logging.getLogger(__name__)


@dataclass
class BlenderFileMetadata:
    """Metadata for a scraped Blender file."""
    url: str
    source: str  # github, blendswap, etc.
    filename: str
    file_hash: str
    size_bytes: int
    author: Optional[str] = None
    description: Optional[str] = None
    tags: List[str] = None
    license: Optional[str] = None
    stars: int = 0
    downloads: int = 0
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []


class BlenderFileScraper:
    """
    Scrapes Blender files from public repositories for ML training.
    """

    # GitHub API endpoints
    GITHUB_API = "https://api.github.com"
    GITHUB_SEARCH = f"{GITHUB_API}/search/repositories"
    GITHUB_CODE_SEARCH = f"{GITHUB_API}/search/code"

    # Search queries for different types of Blender content
    SEARCH_QUERIES = [
        "blender .blend language:Python",
        "blender tutorial .blend",
        "blender materials .blend",
        "blender models .blend",
        "blender animation .blend",
        "blender procedural .blend",
        "blender game assets .blend",
        "blender architecture .blend",
        "blender characters .blend",
    ]

    def __init__(
        self,
        github_token: Optional[str] = None,
        output_dir: Path = Path("./training_data"),
        max_files: int = 1000,
        rate_limit_delay: float = 1.0,
        checkpoint_interval: int = 10
    ):
        """
        Initialize scraper.

        Args:
            github_token: GitHub personal access token for higher rate limits
            output_dir: Directory to save scraped data
            max_files: Maximum number of files to scrape
            rate_limit_delay: Delay between API calls (seconds)
            checkpoint_interval: Save checkpoint every N files
        """
        self.github_token = github_token
        self.output_dir = Path(output_dir)
        self.max_files = max_files
        self.rate_limit_delay = rate_limit_delay
        self.checkpoint_interval = checkpoint_interval

        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.checkpoint_dir = self.output_dir / "checkpoints"
        self.checkpoint_dir.mkdir(exist_ok=True)
        self.metadata_file = self.output_dir / "scraped_metadata.json"
        self.checkpoint_file = self.checkpoint_dir / "scraping_checkpoint.json"

        # Track scraped files to avoid duplicates
        self.scraped_hashes = set()
        self.current_query_index = 0
        self.files_found = 0

        if self.metadata_file.exists():
            self._load_existing_metadata()

        logger.info(f"BlenderScraper initialized (max_files={max_files}, output={output_dir})")

    def _load_existing_metadata(self):
        """Load existing metadata to avoid re-scraping."""
        try:
            with open(self.metadata_file, 'r') as f:
                data = json.load(f)
                for item in data:
                    self.scraped_hashes.add(item.get('file_hash'))
            logger.info(f"Loaded {len(self.scraped_hashes)} existing file hashes")
        except Exception as e:
            logger.warning(f"Could not load existing metadata: {e}")

    async def scrape_github(self, max_repos: int = 100, start_index: int = 0) -> List[BlenderFileMetadata]:
        """
        Scrape Blender files from GitHub.

        Args:
            max_repos: Maximum number of repositories to search
            start_index: Starting query index for resume

        Returns:
            List of file metadata
        """
        logger.info(f"Starting GitHub scrape from query {start_index}...")
        files = []
        errors = []

        headers = {}
        if self.github_token:
            headers["Authorization"] = f"token {self.github_token}"

        async with aiohttp.ClientSession(headers=headers) as session:
            for idx, query in enumerate(self.SEARCH_QUERIES[start_index:], start=start_index):
                if len(files) >= self.max_files:
                    break

                logger.info(f"Searching GitHub [{idx+1}/{len(self.SEARCH_QUERIES)}]: {query}")
                self.current_query_index = idx

                # Search for repositories
                params = {
                    "q": query,
                    "sort": "stars",
                    "order": "desc",
                    "per_page": 30
                }

                try:
                    async with session.get(self.GITHUB_SEARCH, params=params) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            repos = data.get("items", [])
                            logger.info(f"Found {len(repos)} repositories")

                            # Search each repo for .blend files
                            for repo in repos[:10]:  # Top 10 repos per query
                                repo_files = await self._search_repo_for_blend_files(
                                    session, repo
                                )
                                files.extend(repo_files)

                                if len(files) >= self.max_files:
                                    break
                        elif resp.status == 403:
                            error_msg = f"GitHub rate limit exceeded at query {idx}"
                            logger.warning(error_msg)
                            errors.append(error_msg)
                            # Save checkpoint before waiting
                            self.save_checkpoint(idx, errors)
                            await asyncio.sleep(60)  # Wait 1 minute
                        else:
                            error_msg = f"GitHub API error: {resp.status} at query {idx}"
                            logger.warning(error_msg)
                            errors.append(error_msg)

                    await asyncio.sleep(self.rate_limit_delay)

                except Exception as e:
                    error_msg = f"Error searching GitHub query {idx}: {e}"
                    logger.error(error_msg)
                    errors.append(error_msg)

                # Save checkpoint after each query
                self.files_found = len(files)
                self.save_checkpoint(idx + 1, errors)

        logger.info(f"GitHub scrape complete: {len(files)} files found")
        return files

    async def _search_repo_for_blend_files(
        self,
        session: aiohttp.ClientSession,
        repo: Dict[str, Any]
    ) -> List[BlenderFileMetadata]:
        """Search a specific repository for .blend files."""
        files = []
        repo_name = repo.get("full_name")

        # Search for .blend files in this repo
        params = {
            "q": f"extension:blend repo:{repo_name}",
            "per_page": 10
        }

        try:
            async with session.get(self.GITHUB_CODE_SEARCH, params=params) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    items = data.get("items", [])

                    for item in items:
                        metadata = BlenderFileMetadata(
                            url=item.get("html_url", ""),
                            source="github",
                            filename=item.get("name", ""),
                            file_hash=item.get("sha", ""),
                            size_bytes=0,  # Would need additional API call
                            author=repo.get("owner", {}).get("login"),
                            description=repo.get("description", ""),
                            tags=[],
                            license=repo.get("license", {}).get("name") if repo.get("license") else None,
                            stars=repo.get("stargazers_count", 0),
                            created_at=repo.get("created_at"),
                            updated_at=repo.get("updated_at")
                        )

                        if metadata.file_hash not in self.scraped_hashes:
                            files.append(metadata)
                            self.scraped_hashes.add(metadata.file_hash)

                await asyncio.sleep(self.rate_limit_delay)

        except Exception as e:
            logger.error(f"Error searching repo {repo_name}: {e}")

        return files

    async def download_file(
        self,
        metadata: BlenderFileMetadata,
        session: aiohttp.ClientSession
    ) -> Optional[Path]:
        """
        Download a Blender file.

        Args:
            metadata: File metadata
            session: aiohttp session

        Returns:
            Path to downloaded file or None
        """
        # Convert GitHub URL to raw download URL
        if metadata.source == "github":
            download_url = metadata.url.replace(
                "github.com",
                "raw.githubusercontent.com"
            ).replace("/blob/", "/")
        else:
            download_url = metadata.url

        output_path = self.output_dir / "blend_files" / metadata.filename
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if output_path.exists():
            logger.info(f"File already exists: {metadata.filename}")
            return output_path

        try:
            logger.info(f"Downloading: {metadata.filename}")
            async with session.get(download_url) as resp:
                if resp.status == 200:
                    content = await resp.read()

                    with open(output_path, 'wb') as f:
                        f.write(content)

                    logger.info(f"Downloaded: {metadata.filename} ({len(content)} bytes)")
                    return output_path
                else:
                    logger.warning(f"Download failed: {resp.status}")
                    return None

        except Exception as e:
            logger.error(f"Error downloading {metadata.filename}: {e}")
            return None

    async def scrape_all(self, start_index: int = 0) -> Dict[str, Any]:
        """
        Run complete scraping pipeline.

        Args:
            start_index: Query index to start from (for resume)

        Returns:
            Statistics about scraping run
        """
        logger.info(f"Starting complete scraping pipeline from index {start_index}...")
        start_time = time.time()

        # Scrape GitHub
        github_files = await self.scrape_github(start_index=start_index)

        # Save metadata
        all_metadata = github_files
        self._save_metadata(all_metadata)

        # Download files (optional, can be large)
        # Uncomment to enable downloads:
        # async with aiohttp.ClientSession() as session:
        #     for metadata in all_metadata[:100]:  # Download first 100
        #         await self.download_file(metadata, session)
        #         await asyncio.sleep(self.rate_limit_delay)

        elapsed = time.time() - start_time

        stats = {
            "total_files_found": len(all_metadata),
            "github_files": len(github_files),
            "unique_files": len(self.scraped_hashes),
            "elapsed_seconds": elapsed,
            "output_directory": str(self.output_dir)
        }

        logger.info(f"Scraping complete: {stats}")
        return stats

    def _save_metadata(self, metadata_list: List[BlenderFileMetadata]):
        """Save metadata to JSON file."""
        data = []
        for meta in metadata_list:
            data.append({
                "url": meta.url,
                "source": meta.source,
                "filename": meta.filename,
                "file_hash": meta.file_hash,
                "size_bytes": meta.size_bytes,
                "author": meta.author,
                "description": meta.description,
                "tags": meta.tags,
                "license": meta.license,
                "stars": meta.stars,
                "downloads": meta.downloads,
                "created_at": meta.created_at,
                "updated_at": meta.updated_at
            })

        with open(self.metadata_file, 'w') as f:
            json.dump(data, f, indent=2)

        logger.info(f"Saved metadata for {len(data)} files")

    def get_high_quality_files(self, min_stars: int = 10) -> List[BlenderFileMetadata]:
        """Get high-quality files based on stars."""
        if not self.metadata_file.exists():
            return []

        with open(self.metadata_file, 'r') as f:
            data = json.load(f)

        high_quality = []
        for item in data:
            if item.get('stars', 0) >= min_stars:
                high_quality.append(BlenderFileMetadata(**item))

        return high_quality

    def save_checkpoint(self, query_index: int, errors: List[str] = None):
        """
        Save scraping checkpoint for resume capability.

        Args:
            query_index: Current query being processed
            errors: List of error messages
        """
        from datetime import datetime

        checkpoint = {
            "task": "scraping",
            "status": "in_progress",
            "started_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "progress": {
                "total_queries": len(self.SEARCH_QUERIES),
                "completed_queries": query_index,
                "current_query": self.SEARCH_QUERIES[query_index] if query_index < len(self.SEARCH_QUERIES) else "complete",
                "files_found": self.files_found,
                "unique_hashes": len(self.scraped_hashes),
                "errors": len(errors) if errors else 0
            },
            "state": {
                "scraped_hashes": list(self.scraped_hashes),
                "current_query_index": query_index,
                "max_files": self.max_files
            },
            "errors": errors or [],
            "next_steps": [
                f"Resume from query index {query_index}",
                "Run: BlenderFileScraper.from_checkpoint('checkpoint_file.json')",
                "Then: await scraper.resume_scraping()"
            ]
        }

        with open(self.checkpoint_file, 'w') as f:
            json.dump(checkpoint, f, indent=2)

        logger.info(f"Checkpoint saved: query {query_index}/{len(self.SEARCH_QUERIES)}, {self.files_found} files")

    @classmethod
    def from_checkpoint(cls, checkpoint_path: Path) -> 'BlenderFileScraper':
        """
        Resume scraping from a checkpoint file.

        Args:
            checkpoint_path: Path to checkpoint JSON file

        Returns:
            BlenderFileScraper instance with restored state
        """
        with open(checkpoint_path, 'r') as f:
            checkpoint = json.load(f)

        state = checkpoint.get('state', {})

        # Create instance
        scraper = cls(
            output_dir=Path(checkpoint_path).parent.parent,
            max_files=state.get('max_files', 1000)
        )

        # Restore state
        scraper.scraped_hashes = set(state.get('scraped_hashes', []))
        scraper.current_query_index = state.get('current_query_index', 0)
        scraper.files_found = checkpoint.get('progress', {}).get('files_found', 0)

        logger.info(f"Resumed from checkpoint: query {scraper.current_query_index}, {scraper.files_found} files")

        return scraper

    async def resume_scraping(self) -> Dict[str, Any]:
        """
        Resume scraping from checkpoint.

        Returns:
            Scraping statistics
        """
        logger.info(f"Resuming scraping from query {self.current_query_index}")

        # Continue from where we left off
        return await self.scrape_all(start_index=self.current_query_index)


async def main():
    """Example usage."""
    import os

    # Get GitHub token from environment
    github_token = os.getenv("GITHUB_TOKEN")

    scraper = BlenderFileScraper(
        github_token=github_token,
        output_dir=Path("./training_data/blender_files"),
        max_files=500
    )

    stats = await scraper.scrape_all()
    print(f"Scraping complete: {stats}")


if __name__ == "__main__":
    asyncio.run(main())
