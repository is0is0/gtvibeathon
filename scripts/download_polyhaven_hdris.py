"""
Poly Haven HDRI Downloader
===========================
Pulls HDRIs from the Poly Haven API, downloads them in chosen resolution,
and saves metadata for training datasets. Optionally registers with Voxel AssetRegistry.

Features:
- Multi-resolution support (1k, 2k, 4k, 8k, 16k)
- Resume capability for interrupted downloads
- Progress tracking with download speeds
- Automatic retry with exponential backoff
- Optional integration with Voxel AssetRegistry
- Category and tag extraction from metadata
- Statistics and summary report

License: CC0 content from Poly Haven (https://polyhaven.com)
"""

import os
import sys
import json
import time
import hashlib
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime

import requests
from tqdm import tqdm

# Add parent directory to path for Voxel imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    from subsystems.asset_registry import AssetRegistry, AssetType
    VOXEL_AVAILABLE = True
except ImportError:
    VOXEL_AVAILABLE = False
    print("⚠️  Voxel AssetRegistry not available. Assets won't be registered.")


# ==================== CONFIGURATION ====================

API_LIST = "https://api.polyhaven.com/assets?type=hdris"
API_FILES = "https://api.polyhaven.com/files/{}"
API_INFO = "https://api.polyhaven.com/info/{}"

DEFAULT_SAVE_DIR = "data/polyhaven_hdri_dataset"
DEFAULT_RESOLUTION = "2k"
DELAY_BETWEEN_REQUESTS = 1.5  # Polite delay (seconds)
MAX_RETRIES = 3
RETRY_DELAY = 5  # Initial retry delay in seconds


# ==================== DOWNLOAD STATE ====================

class DownloadState:
    """Track download progress and allow resuming."""

    def __init__(self, state_file: str):
        self.state_file = state_file
        self.completed: List[str] = []
        self.failed: List[str] = []
        self.skipped: List[str] = []
        self.load()

    def load(self):
        """Load previous download state."""
        if os.path.exists(self.state_file):
            with open(self.state_file, 'r') as f:
                data = json.load(f)
                self.completed = data.get('completed', [])
                self.failed = data.get('failed', [])
                self.skipped = data.get('skipped', [])

    def save(self):
        """Save current download state."""
        with open(self.state_file, 'w') as f:
            json.dump({
                'completed': self.completed,
                'failed': self.failed,
                'skipped': self.skipped,
                'last_updated': datetime.utcnow().isoformat(),
            }, f, indent=2)

    def mark_completed(self, name: str):
        if name not in self.completed:
            self.completed.append(name)
        self.save()

    def mark_failed(self, name: str):
        if name not in self.failed:
            self.failed.append(name)
        self.save()

    def mark_skipped(self, name: str):
        if name not in self.skipped:
            self.skipped.append(name)
        self.save()

    def is_completed(self, name: str) -> bool:
        return name in self.completed

    def get_summary(self) -> Dict:
        return {
            'completed': len(self.completed),
            'failed': len(self.failed),
            'skipped': len(self.skipped),
            'total': len(self.completed) + len(self.failed) + len(self.skipped),
        }


# ==================== API FUNCTIONS ====================

def get_hdr_list() -> List[str]:
    """Fetch the list of all HDRI asset names from Poly Haven."""
    try:
        resp = requests.get(API_LIST, timeout=10)
        resp.raise_for_status()
        return list(resp.json().keys())
    except Exception as e:
        print(f"❌ Failed to fetch HDRI list: {e}")
        return []


def get_hdr_info(name: str) -> Optional[Dict]:
    """Fetch detailed info about an HDRI (categories, tags, etc.)."""
    try:
        resp = requests.get(API_INFO.format(name), timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"⚠️  Failed to fetch info for {name}: {e}")
        return None


def get_hdr_files(name: str) -> Optional[Dict]:
    """Fetch file download URLs for an HDRI."""
    try:
        resp = requests.get(API_FILES.format(name), timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"⚠️  Failed to fetch files for {name}: {e}")
        return None


# ==================== DOWNLOAD FUNCTIONS ====================

def calculate_file_hash(file_path: str) -> str:
    """Calculate SHA256 hash of a file."""
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            sha256.update(chunk)
    return sha256.hexdigest()


def download_file_with_retry(
    url: str,
    output_path: str,
    max_retries: int = MAX_RETRIES,
) -> Tuple[bool, Optional[str]]:
    """
    Download a file with retry logic and progress bar.

    Returns:
        (success: bool, error_message: Optional[str])
    """
    for attempt in range(max_retries):
        try:
            # Get file size first
            head = requests.head(url, timeout=10)
            total_size = int(head.headers.get('content-length', 0))

            # Download with progress bar
            with requests.get(url, stream=True, timeout=30) as r:
                r.raise_for_status()

                with open(output_path, 'wb') as f:
                    with tqdm(
                        total=total_size,
                        unit='B',
                        unit_scale=True,
                        unit_divisor=1024,
                        desc=f"  Downloading",
                        leave=False,
                    ) as pbar:
                        for chunk in r.iter_content(chunk_size=8192):
                            f.write(chunk)
                            pbar.update(len(chunk))

            return True, None

        except Exception as e:
            if attempt < max_retries - 1:
                wait_time = RETRY_DELAY * (2 ** attempt)  # Exponential backoff
                print(f"  ⚠️  Attempt {attempt + 1} failed, retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                return False, str(e)

    return False, "Max retries exceeded"


def download_hdr(
    name: str,
    resolution: str,
    save_dir: str,
    state: DownloadState,
    registry: Optional[AssetRegistry] = None,
) -> bool:
    """
    Download a single HDR and its metadata.

    Returns:
        True if successful, False otherwise
    """
    # Check if already completed
    if state.is_completed(name):
        print(f"✅ {name} - already completed")
        return True

    # Paths
    hdr_path = os.path.join(save_dir, "images", f"{name}.hdr")
    meta_path = os.path.join(save_dir, "metadata", f"{name}.json")

    # Skip if file exists and is valid
    if os.path.exists(hdr_path):
        try:
            file_size = os.path.getsize(hdr_path)
            if file_size > 1000:  # Ensure it's not corrupted (> 1KB)
                print(f"✅ {name} - file exists, skipping")
                state.mark_skipped(name)
                return True
        except Exception:
            pass  # File exists but can't read, will re-download

    try:
        # Get file URLs
        files_meta = get_hdr_files(name)
        if not files_meta:
            state.mark_failed(name)
            return False

        # Check if HDR is available in desired resolution
        if "hdri" not in files_meta or resolution not in files_meta["hdri"]:
            print(f"⚠️  {name} - No HDR at {resolution} resolution")
            state.mark_skipped(name)
            return False

        hdr_url = files_meta["hdri"][resolution]["url"]

        # Get additional info (categories, tags)
        info = get_hdr_info(name)

        # Download HDR file
        print(f"📥 {name}")
        success, error = download_file_with_retry(hdr_url, hdr_path)

        if not success:
            print(f"❌ {name} - Download failed: {error}")
            state.mark_failed(name)
            return False

        # Calculate hash for integrity
        file_hash = calculate_file_hash(hdr_path)
        file_size = os.path.getsize(hdr_path)

        # Combine metadata
        combined_meta = {
            "name": name,
            "resolution": resolution,
            "source": "polyhaven",
            "url": f"https://polyhaven.com/a/{name}",
            "downloaded_at": datetime.utcnow().isoformat(),
            "file_path": os.path.abspath(hdr_path),
            "file_size": file_size,
            "file_hash": file_hash,
            "files": files_meta,
        }

        # Add info data if available
        if info:
            combined_meta["categories"] = info.get("categories", [])
            combined_meta["tags"] = info.get("tags", [])
            combined_meta["author"] = info.get("author", {})
            combined_meta["description"] = info.get("name", "")

        # Save metadata JSON
        with open(meta_path, "w") as f:
            json.dump(combined_meta, f, indent=2)

        # Register with Voxel AssetRegistry if available
        if registry and VOXEL_AVAILABLE:
            try:
                tags = info.get("tags", []) if info else []
                categories = info.get("categories", []) if info else []

                registry.add_asset(
                    name=name,
                    path=hdr_path,
                    asset_type=AssetType.HDRI,
                    description=f"HDRI from Poly Haven - {resolution} resolution",
                    tags=tags + categories + ["polyhaven", resolution],
                    category="lighting",
                    metadata=combined_meta,
                )
            except Exception as e:
                print(f"  ⚠️  Failed to register with AssetRegistry: {e}")

        print(f"✅ {name} - Downloaded ({file_size / 1024 / 1024:.1f} MB)")
        state.mark_completed(name)
        return True

    except Exception as e:
        print(f"❌ {name} - Error: {e}")
        state.mark_failed(name)
        return False


# ==================== MAIN ====================

def main():
    parser = argparse.ArgumentParser(
        description="Download HDRIs from Poly Haven with optional Voxel integration"
    )
    parser.add_argument(
        "--resolution",
        default=DEFAULT_RESOLUTION,
        choices=["1k", "2k", "4k", "8k", "16k"],
        help="HDRI resolution to download (default: 2k)",
    )
    parser.add_argument(
        "--output-dir",
        default=DEFAULT_SAVE_DIR,
        help=f"Output directory (default: {DEFAULT_SAVE_DIR})",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit number of HDRIs to download (for testing)",
    )
    parser.add_argument(
        "--register",
        action="store_true",
        help="Register downloaded HDRIs with Voxel AssetRegistry",
    )
    parser.add_argument(
        "--registry-path",
        default="data/voxel_assets.db",
        help="Path to Voxel AssetRegistry database",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=DELAY_BETWEEN_REQUESTS,
        help=f"Delay between requests in seconds (default: {DELAY_BETWEEN_REQUESTS})",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Resume previous download session",
    )

    args = parser.parse_args()

    # Setup directories
    save_dir = args.output_dir
    os.makedirs(save_dir, exist_ok=True)
    os.makedirs(f"{save_dir}/images", exist_ok=True)
    os.makedirs(f"{save_dir}/metadata", exist_ok=True)

    # Initialize download state
    state_file = os.path.join(save_dir, "download_state.json")
    state = DownloadState(state_file)

    if args.resume:
        summary = state.get_summary()
        print(f"📂 Resuming previous session:")
        print(f"   Completed: {summary['completed']}")
        print(f"   Failed: {summary['failed']}")
        print(f"   Skipped: {summary['skipped']}")
        print()

    # Initialize AssetRegistry if requested
    registry = None
    if args.register and VOXEL_AVAILABLE:
        try:
            registry = AssetRegistry(args.registry_path)
            print(f"✅ Connected to Voxel AssetRegistry at {args.registry_path}\n")
        except Exception as e:
            print(f"⚠️  Failed to initialize AssetRegistry: {e}")
            print("   Continuing without registry integration.\n")

    # Fetch HDRI list
    print("🔍 Fetching HDRI list from Poly Haven...")
    hdr_names = get_hdr_list()

    if not hdr_names:
        print("❌ No HDRIs found. Exiting.")
        return

    # Apply limit if specified
    if args.limit:
        hdr_names = hdr_names[:args.limit]

    # Filter out already completed
    if args.resume:
        hdr_names = [name for name in hdr_names if not state.is_completed(name)]

    print(f"📦 Found {len(hdr_names)} HDRIs to download at {args.resolution} resolution")
    print(f"💾 Saving to: {os.path.abspath(save_dir)}")
    print(f"⏱️  Delay between requests: {args.delay}s")
    print()

    # Download each HDRI
    start_time = time.time()

    for i, name in enumerate(hdr_names, 1):
        print(f"[{i}/{len(hdr_names)}] ", end="")
        download_hdr(name, args.resolution, save_dir, state, registry)

        # Polite delay (except for last item)
        if i < len(hdr_names):
            time.sleep(args.delay)

    # Final summary
    elapsed_time = time.time() - start_time
    summary = state.get_summary()

    print("\n" + "=" * 60)
    print("📊 DOWNLOAD SUMMARY")
    print("=" * 60)
    print(f"✅ Completed:  {summary['completed']}")
    print(f"⏭️  Skipped:    {summary['skipped']}")
    print(f"❌ Failed:     {summary['failed']}")
    print(f"⏱️  Total time: {elapsed_time:.1f}s ({elapsed_time / 60:.1f} min)")
    print(f"💾 Output:     {os.path.abspath(save_dir)}")

    if registry:
        print(f"📚 Assets registered in: {args.registry_path}")

    print("=" * 60)

    # Show failed items if any
    if state.failed:
        print("\n⚠️  Failed downloads:")
        for name in state.failed:
            print(f"   - {name}")
        print(f"\nRun with --resume to retry failed downloads.")

    print("\n✨ All done!")


if __name__ == "__main__":
    main()
