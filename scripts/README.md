# Voxel Scripts

Utility scripts for the Voxel AI 3D scene generation system.

---

## Poly Haven HDRI Downloader

Download high-quality HDRIs from [Poly Haven](https://polyhaven.com) for use in your Voxel projects.

### Features

- **Multi-resolution support**: Download in 1k, 2k, 4k, 8k, or 16k
- **Resume capability**: Interrupt and resume downloads
- **Progress tracking**: Visual progress bars with download speeds
- **Automatic retry**: Exponential backoff for failed downloads
- **Voxel integration**: Optional registration with AssetRegistry
- **Metadata extraction**: Categories, tags, and asset information
- **Integrity checking**: SHA256 hash verification

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Or install individually
pip install requests tqdm
```

### Usage

#### Basic Usage

Download all HDRIs at 2k resolution:

```bash
python download_polyhaven_hdris.py
```

#### Download Specific Resolution

```bash
# Available: 1k, 2k, 4k, 8k, 16k
python download_polyhaven_hdris.py --resolution 4k
```

#### Custom Output Directory

```bash
python download_polyhaven_hdris.py --output-dir /path/to/hdris
```

#### Test with Limited Downloads

```bash
python download_polyhaven_hdris.py --limit 5 --resolution 1k
```

#### Resume Interrupted Download

```bash
python download_polyhaven_hdris.py --resume
```

#### Register with Voxel AssetRegistry

```bash
python download_polyhaven_hdris.py --register --registry-path data/voxel_assets.db
```

#### Adjust Request Delay

```bash
# Be more polite (slower)
python download_polyhaven_hdris.py --delay 3.0

# Faster (less polite, use carefully)
python download_polyhaven_hdris.py --delay 0.5
```

### All Options

```
Options:
  --resolution {1k,2k,4k,8k,16k}
                        HDRI resolution to download (default: 2k)
  --output-dir DIR      Output directory (default: data/polyhaven_hdri_dataset)
  --limit N             Limit number of HDRIs to download (for testing)
  --register            Register downloaded HDRIs with Voxel AssetRegistry
  --registry-path PATH  Path to Voxel AssetRegistry database
  --delay SECONDS       Delay between requests in seconds (default: 1.5)
  --resume              Resume previous download session
  -h, --help            Show help message
```

### Output Structure

```
data/polyhaven_hdri_dataset/
├── images/
│   ├── abandoned_warehouse.hdr
│   ├── forest_path.hdr
│   └── ... (all HDRIs)
├── metadata/
│   ├── abandoned_warehouse.json
│   ├── forest_path.json
│   └── ... (all metadata)
└── download_state.json (resume tracking)
```

### Metadata Format

Each HDRI has a JSON file with:

```json
{
  "name": "forest_path",
  "resolution": "2k",
  "source": "polyhaven",
  "url": "https://polyhaven.com/a/forest_path",
  "downloaded_at": "2025-01-15T10:30:00Z",
  "file_path": "/absolute/path/to/forest_path.hdr",
  "file_size": 12582912,
  "file_hash": "sha256_hash_here",
  "categories": ["outdoor", "nature"],
  "tags": ["forest", "trees", "daylight"],
  "author": {
    "name": "Photographer Name",
    "link": "https://..."
  },
  "description": "Forest Path",
  "files": {
    "hdri": {
      "1k": {"url": "...", "size": 1048576},
      "2k": {"url": "...", "size": 4194304},
      "4k": {"url": "...", "size": 16777216}
    }
  }
}
```

### Examples

#### Download 10 HDRIs at 1k for testing

```bash
python download_polyhaven_hdris.py --resolution 1k --limit 10
```

#### Download all 4k HDRIs and register with Voxel

```bash
python download_polyhaven_hdris.py \
  --resolution 4k \
  --register \
  --registry-path ../data/voxel_assets.db \
  --output-dir ../data/hdris
```

#### Resume a failed download session

```bash
python download_polyhaven_hdris.py --resume
```

### Performance Tips

1. **Start with lower resolution** (1k or 2k) to test
2. **Use `--limit`** to download a few HDRIs first
3. **Check disk space** before downloading high resolutions:
   - 1k: ~1-2 MB per file
   - 2k: ~4-8 MB per file
   - 4k: ~16-32 MB per file
   - 8k: ~64-128 MB per file
   - 16k: ~256-512 MB per file
4. **Use `--resume`** if download is interrupted
5. **Be polite** to Poly Haven servers (don't reduce `--delay` too much)

### Using HDRIs in Voxel

Once downloaded, HDRIs can be used in your Voxel projects:

```python
from subsystems.lighting_ai import LightingAI

# Initialize lighting system
lighting = LightingAI()

# Use downloaded HDRI
lighting.setup_hdri_lighting(
    hdri_path="data/polyhaven_hdri_dataset/images/forest_path.hdr",
    rotation=45,
    strength=1.5
)
```

### Using with AssetRegistry

If registered with `--register`, you can search and retrieve HDRIs:

```python
from subsystems.asset_registry import AssetRegistry, AssetType

# Load registry
registry = AssetRegistry("data/voxel_assets.db")

# Search for outdoor HDRIs
outdoor_hdris = registry.search_assets(
    query="outdoor",
    asset_type=AssetType.HDRI,
    tags=["outdoor"]
)

# Get specific HDRI
forest = registry.get_asset("forest_path")
print(f"HDRI path: {forest.path}")
```

### Troubleshooting

**Download fails with timeout:**
- Check internet connection
- Increase `--delay` to reduce load
- Use `--resume` to continue

**"No HDR at [resolution] resolution":**
- Not all HDRIs are available in all resolutions
- Try a different resolution (2k is most common)

**Out of disk space:**
- Check available space before downloading
- Use lower resolution or `--limit`
- Estimate: ~500 HDRIs × 8MB (2k) = ~4GB

**Voxel AssetRegistry not found:**
- Make sure you're running from the project root
- Or install Voxel in development mode: `pip install -e .`

### License

All HDRIs from Poly Haven are **CC0** (public domain). You can use them for any purpose without attribution (though it's appreciated!).

**Attribution:**
- HDRIs: [Poly Haven](https://polyhaven.com) (CC0)
- Script: Part of the Voxel project

### Support

For issues or questions:
- Poly Haven: https://polyhaven.com
- Voxel project: https://github.com/yourusername/voxel

---

## Other Scripts

More utility scripts will be added here as the project grows.
