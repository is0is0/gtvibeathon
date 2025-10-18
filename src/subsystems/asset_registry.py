"""
Asset Registry
-------------
Comprehensive asset management system for caching and retrieving reusable
3D assets, textures, materials, lighting setups, and scene configurations.

Supports both JSON and SQLite storage backends for flexible deployment.
"""

import json
import sqlite3
import hashlib
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict, field
from enum import Enum
from utils.logger import get_logger

logger = get_logger(__name__)


class AssetType(str, Enum):
    """Supported asset types."""
    MODEL = "model"              # 3D models (.blend, .fbx, .obj, .gltf)
    TEXTURE = "texture"          # Image textures (.png, .jpg, .exr)
    MATERIAL = "material"        # Material definitions (JSON/Python)
    LIGHTING = "lighting"        # Lighting setups (JSON/Python)
    SCRIPT = "script"            # Blender Python scripts
    SCENE = "scene"              # Complete scene configurations
    HDRI = "hdri"                # HDRI environment maps
    COLLECTION = "collection"    # Asset collections/libraries


class StorageBackend(str, Enum):
    """Storage backend options."""
    JSON = "json"
    SQLITE = "sqlite"


@dataclass
class Asset:
    """Asset metadata and information."""
    name: str
    asset_type: AssetType
    path: str
    description: str = ""
    tags: List[str] = field(default_factory=list)
    category: str = "general"
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Automatically managed fields
    asset_id: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    file_size: Optional[int] = None
    checksum: Optional[str] = None
    version: str = "1.0.0"
    author: str = "unknown"
    license: str = "unknown"

    def __post_init__(self):
        """Generate ID and timestamps if not provided."""
        if not self.asset_id:
            self.asset_id = self._generate_id()
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.updated_at:
            self.updated_at = self.created_at

        # Calculate file info if path exists
        path_obj = Path(self.path)
        if path_obj.exists() and path_obj.is_file():
            self.file_size = path_obj.stat().st_size
            self.checksum = self._calculate_checksum(path_obj)

    def _generate_id(self) -> str:
        """Generate unique asset ID."""
        content = f"{self.name}:{self.asset_type}:{self.path}:{datetime.now().isoformat()}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def _calculate_checksum(self, path: Path) -> str:
        """Calculate file checksum for integrity verification."""
        try:
            sha256 = hashlib.sha256()
            with open(path, 'rb') as f:
                for chunk in iter(lambda: f.read(8192), b''):
                    sha256.update(chunk)
            return sha256.hexdigest()[:16]
        except Exception as e:
            logger.warning(f"Could not calculate checksum for {path}: {e}")
            return "unknown"

    def to_dict(self) -> Dict[str, Any]:
        """Convert asset to dictionary."""
        data = asdict(self)
        data['asset_type'] = self.asset_type.value
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Asset':
        """Create asset from dictionary."""
        if 'asset_type' in data and isinstance(data['asset_type'], str):
            data['asset_type'] = AssetType(data['asset_type'])
        return cls(**data)


class AssetRegistry:
    """
    Asset management system for caching and retrieving reusable assets.

    Features:
    - Multiple storage backends (JSON, SQLite)
    - Asset versioning and checksums
    - Category and tag-based organization
    - Full-text search capabilities
    - Asset collections and dependencies
    - Automatic metadata extraction
    """

    def __init__(
        self,
        storage_path: Optional[Union[str, Path]] = None,
        backend: StorageBackend = StorageBackend.JSON,
        auto_save: bool = True
    ):
        """
        Initialize Asset Registry.

        Args:
            storage_path: Path to storage file (JSON or SQLite database)
            backend: Storage backend to use
            auto_save: Automatically save changes
        """
        self.backend = backend
        self.auto_save = auto_save

        # Set default storage path
        if storage_path is None:
            storage_path = Path("data/asset_registry")
            storage_path.mkdir(parents=True, exist_ok=True)

            if backend == StorageBackend.JSON:
                storage_path = storage_path / "registry.json"
            else:
                storage_path = storage_path / "registry.db"

        self.storage_path = Path(storage_path)
        self.assets: Dict[str, Asset] = {}

        # Initialize storage
        if backend == StorageBackend.JSON:
            self._init_json_storage()
        else:
            self._init_sqlite_storage()

        logger.info(
            f"Asset Registry initialized (backend: {backend.value}, "
            f"path: {self.storage_path}, assets: {len(self.assets)})"
        )

    # Core asset management methods

    def add_asset(
        self,
        name: str,
        path: str,
        asset_type: Optional[Union[str, AssetType]] = None,
        **kwargs
    ) -> Asset:
        """
        Add new asset to registry.

        Args:
            name: Asset name
            path: Path to asset file
            asset_type: Type of asset (auto-detected if not provided)
            **kwargs: Additional asset metadata

        Returns:
            Created asset object
        """
        # Auto-detect asset type if not provided
        if asset_type is None:
            asset_type = self._detect_asset_type(path)
        elif isinstance(asset_type, str):
            asset_type = AssetType(asset_type)

        # Create asset
        asset = Asset(
            name=name,
            path=path,
            asset_type=asset_type,
            **kwargs
        )

        # Store asset
        self.assets[asset.asset_id] = asset

        if self.auto_save:
            self.save()

        logger.info(f"Added asset: {name} ({asset_type.value}) [ID: {asset.asset_id}]")

        return asset

    def get_asset(self, identifier: str) -> Optional[Asset]:
        """
        Get asset by ID or name.

        Args:
            identifier: Asset ID or name

        Returns:
            Asset object or None if not found
        """
        # Try direct ID lookup
        if identifier in self.assets:
            return self.assets[identifier]

        # Try name lookup
        for asset in self.assets.values():
            if asset.name == identifier:
                return asset

        logger.warning(f"Asset not found: {identifier}")
        return None

    def update_asset(
        self,
        identifier: str,
        **updates
    ) -> Optional[Asset]:
        """
        Update asset metadata.

        Args:
            identifier: Asset ID or name
            **updates: Fields to update

        Returns:
            Updated asset or None if not found
        """
        asset = self.get_asset(identifier)

        if asset is None:
            return None

        # Update fields
        for key, value in updates.items():
            if hasattr(asset, key):
                setattr(asset, key, value)

        # Update timestamp
        asset.updated_at = datetime.now().isoformat()

        if self.auto_save:
            self.save()

        logger.info(f"Updated asset: {asset.name} [ID: {asset.asset_id}]")

        return asset

    def remove_asset(self, identifier: str) -> bool:
        """
        Remove asset from registry.

        Args:
            identifier: Asset ID or name

        Returns:
            True if removed, False if not found
        """
        asset = self.get_asset(identifier)

        if asset is None:
            return False

        del self.assets[asset.asset_id]

        if self.auto_save:
            self.save()

        logger.info(f"Removed asset: {asset.name} [ID: {asset.asset_id}]")

        return True

    def list_assets(
        self,
        asset_type: Optional[Union[str, AssetType]] = None,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> List[Asset]:
        """
        List assets with optional filtering.

        Args:
            asset_type: Filter by asset type
            category: Filter by category
            tags: Filter by tags (assets must have ALL tags)

        Returns:
            List of matching assets
        """
        results = list(self.assets.values())

        # Filter by type
        if asset_type is not None:
            if isinstance(asset_type, str):
                asset_type = AssetType(asset_type)
            results = [a for a in results if a.asset_type == asset_type]

        # Filter by category
        if category is not None:
            results = [a for a in results if a.category == category]

        # Filter by tags
        if tags is not None:
            results = [
                a for a in results
                if all(tag in a.tags for tag in tags)
            ]

        logger.debug(f"Listed {len(results)} assets (filters: type={asset_type}, category={category}, tags={tags})")

        return results

    def search_assets(
        self,
        query: str,
        fields: Optional[List[str]] = None
    ) -> List[Asset]:
        """
        Search assets by text query.

        Args:
            query: Search query
            fields: Fields to search (default: name, description, tags)

        Returns:
            List of matching assets
        """
        if fields is None:
            fields = ['name', 'description', 'tags', 'category']

        query_lower = query.lower()
        results = []

        for asset in self.assets.values():
            match = False

            for field in fields:
                value = getattr(asset, field, None)

                if value is None:
                    continue

                # Handle different field types
                if isinstance(value, str):
                    if query_lower in value.lower():
                        match = True
                        break
                elif isinstance(value, list):
                    if any(query_lower in str(item).lower() for item in value):
                        match = True
                        break

            if match:
                results.append(asset)

        logger.debug(f"Search '{query}' found {len(results)} assets")

        return results

    def get_categories(self) -> List[str]:
        """
        Get list of all categories.

        Returns:
            List of unique categories
        """
        categories = set(asset.category for asset in self.assets.values())
        return sorted(categories)

    def get_tags(self) -> List[str]:
        """
        Get list of all tags.

        Returns:
            List of unique tags
        """
        tags = set()
        for asset in self.assets.values():
            tags.update(asset.tags)
        return sorted(tags)

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get registry statistics.

        Returns:
            Dictionary of statistics
        """
        stats = {
            'total_assets': len(self.assets),
            'by_type': {},
            'by_category': {},
            'total_size': 0,
            'categories': len(self.get_categories()),
            'tags': len(self.get_tags())
        }

        # Count by type
        for asset_type in AssetType:
            count = len([a for a in self.assets.values() if a.asset_type == asset_type])
            stats['by_type'][asset_type.value] = count

        # Count by category
        for category in self.get_categories():
            count = len([a for a in self.assets.values() if a.category == category])
            stats['by_category'][category] = count

        # Calculate total size
        stats['total_size'] = sum(
            asset.file_size or 0
            for asset in self.assets.values()
        )

        return stats

    def verify_assets(self) -> Dict[str, List[str]]:
        """
        Verify asset integrity (file existence and checksums).

        Returns:
            Dictionary with 'valid', 'missing', and 'modified' asset lists
        """
        result = {
            'valid': [],
            'missing': [],
            'modified': []
        }

        for asset in self.assets.values():
            path = Path(asset.path)

            if not path.exists():
                result['missing'].append(asset.asset_id)
                logger.warning(f"Missing asset file: {asset.name} at {asset.path}")
            elif asset.checksum and asset.checksum != "unknown":
                # Verify checksum
                current_checksum = asset._calculate_checksum(path)
                if current_checksum != asset.checksum:
                    result['modified'].append(asset.asset_id)
                    logger.warning(f"Modified asset file: {asset.name}")
                else:
                    result['valid'].append(asset.asset_id)
            else:
                result['valid'].append(asset.asset_id)

        logger.info(
            f"Asset verification: {len(result['valid'])} valid, "
            f"{len(result['missing'])} missing, {len(result['modified'])} modified"
        )

        return result

    # Storage operations

    def save(self) -> bool:
        """
        Save registry to storage.

        Returns:
            True if successful
        """
        try:
            if self.backend == StorageBackend.JSON:
                self._save_json()
            else:
                self._save_sqlite()

            logger.debug(f"Saved {len(self.assets)} assets to {self.storage_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to save registry: {e}")
            return False

    def load(self) -> bool:
        """
        Load registry from storage.

        Returns:
            True if successful
        """
        try:
            if self.backend == StorageBackend.JSON:
                self._load_json()
            else:
                self._load_sqlite()

            logger.info(f"Loaded {len(self.assets)} assets from {self.storage_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to load registry: {e}")
            return False

    def export_assets(
        self,
        output_path: Union[str, Path],
        asset_ids: Optional[List[str]] = None
    ) -> bool:
        """
        Export assets to JSON file.

        Args:
            output_path: Path to output file
            asset_ids: Specific assets to export (all if None)

        Returns:
            True if successful
        """
        try:
            # Select assets to export
            if asset_ids is None:
                assets_to_export = self.assets.values()
            else:
                assets_to_export = [
                    self.assets[aid] for aid in asset_ids
                    if aid in self.assets
                ]

            # Convert to dictionaries
            data = {
                'exported_at': datetime.now().isoformat(),
                'asset_count': len(assets_to_export),
                'assets': [asset.to_dict() for asset in assets_to_export]
            }

            # Write JSON
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)

            logger.info(f"Exported {len(assets_to_export)} assets to {output_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to export assets: {e}")
            return False

    def import_assets(
        self,
        input_path: Union[str, Path],
        overwrite: bool = False
    ) -> int:
        """
        Import assets from JSON file.

        Args:
            input_path: Path to input file
            overwrite: Overwrite existing assets with same ID

        Returns:
            Number of assets imported
        """
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            imported = 0

            for asset_data in data.get('assets', []):
                asset = Asset.from_dict(asset_data)

                # Check if asset exists
                if asset.asset_id in self.assets and not overwrite:
                    logger.debug(f"Skipping existing asset: {asset.name}")
                    continue

                self.assets[asset.asset_id] = asset
                imported += 1

            if self.auto_save:
                self.save()

            logger.info(f"Imported {imported} assets from {input_path}")
            return imported

        except Exception as e:
            logger.error(f"Failed to import assets: {e}")
            return 0

    # Private helper methods

    def _detect_asset_type(self, path: str) -> AssetType:
        """Auto-detect asset type from file extension."""
        ext = Path(path).suffix.lower()

        extension_map = {
            # Models
            '.blend': AssetType.MODEL,
            '.fbx': AssetType.MODEL,
            '.obj': AssetType.MODEL,
            '.gltf': AssetType.MODEL,
            '.glb': AssetType.MODEL,
            '.dae': AssetType.MODEL,
            '.stl': AssetType.MODEL,

            # Textures
            '.png': AssetType.TEXTURE,
            '.jpg': AssetType.TEXTURE,
            '.jpeg': AssetType.TEXTURE,
            '.tiff': AssetType.TEXTURE,
            '.tif': AssetType.TEXTURE,
            '.bmp': AssetType.TEXTURE,
            '.tga': AssetType.TEXTURE,

            # HDR
            '.exr': AssetType.HDRI,
            '.hdr': AssetType.HDRI,
            '.hdri': AssetType.HDRI,

            # Scripts
            '.py': AssetType.SCRIPT,

            # Configs
            '.json': AssetType.MATERIAL,
        }

        return extension_map.get(ext, AssetType.MODEL)

    def _init_json_storage(self):
        """Initialize JSON storage backend."""
        if self.storage_path.exists():
            self._load_json()
        else:
            # Create empty registry
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            self._save_json()

    def _init_sqlite_storage(self):
        """Initialize SQLite storage backend."""
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

        conn = sqlite3.connect(self.storage_path)
        cursor = conn.cursor()

        # Create assets table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS assets (
                asset_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                asset_type TEXT NOT NULL,
                path TEXT NOT NULL,
                description TEXT,
                category TEXT,
                tags TEXT,
                metadata TEXT,
                created_at TEXT,
                updated_at TEXT,
                file_size INTEGER,
                checksum TEXT,
                version TEXT,
                author TEXT,
                license TEXT
            )
        ''')

        # Create indices for common queries
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_name ON assets(name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_type ON assets(asset_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_category ON assets(category)')

        conn.commit()
        conn.close()

        # Load existing assets
        if self.storage_path.exists():
            self._load_sqlite()

    def _save_json(self):
        """Save to JSON file."""
        data = {
            'version': '1.0.0',
            'saved_at': datetime.now().isoformat(),
            'asset_count': len(self.assets),
            'assets': [asset.to_dict() for asset in self.assets.values()]
        }

        with open(self.storage_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

    def _load_json(self):
        """Load from JSON file."""
        with open(self.storage_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        self.assets.clear()

        for asset_data in data.get('assets', []):
            asset = Asset.from_dict(asset_data)
            self.assets[asset.asset_id] = asset

    def _save_sqlite(self):
        """Save to SQLite database."""
        conn = sqlite3.connect(self.storage_path)
        cursor = conn.cursor()

        for asset in self.assets.values():
            cursor.execute('''
                INSERT OR REPLACE INTO assets VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                asset.asset_id,
                asset.name,
                asset.asset_type.value,
                asset.path,
                asset.description,
                asset.category,
                json.dumps(asset.tags),
                json.dumps(asset.metadata),
                asset.created_at,
                asset.updated_at,
                asset.file_size,
                asset.checksum,
                asset.version,
                asset.author,
                asset.license
            ))

        conn.commit()
        conn.close()

    def _load_sqlite(self):
        """Load from SQLite database."""
        conn = sqlite3.connect(self.storage_path)
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM assets')
        rows = cursor.fetchall()

        self.assets.clear()

        for row in rows:
            asset = Asset(
                asset_id=row[0],
                name=row[1],
                asset_type=AssetType(row[2]),
                path=row[3],
                description=row[4] or "",
                category=row[5] or "general",
                tags=json.loads(row[6]) if row[6] else [],
                metadata=json.loads(row[7]) if row[7] else {},
                created_at=row[8],
                updated_at=row[9],
                file_size=row[10],
                checksum=row[11],
                version=row[12] or "1.0.0",
                author=row[13] or "unknown",
                license=row[14] or "unknown"
            )
            self.assets[asset.asset_id] = asset

        conn.close()


# Example registry structure and usage
def create_example_registry() -> AssetRegistry:
    """Create example registry with sample assets."""

    # Create registry with JSON backend
    registry = AssetRegistry(
        storage_path="data/example_registry.json",
        backend=StorageBackend.JSON
    )

    # Add sample 3D models
    registry.add_asset(
        name="Modern Chair",
        path="assets/models/chair_modern.blend",
        asset_type=AssetType.MODEL,
        description="Minimalist modern chair design",
        category="furniture",
        tags=["furniture", "chair", "modern", "indoor"],
        metadata={
            "polycount": 5420,
            "dimensions": {"width": 0.6, "height": 0.9, "depth": 0.6},
            "has_uv": True,
            "has_materials": True
        },
        author="Voxel Team",
        license="CC-BY-4.0"
    )

    registry.add_asset(
        name="Wooden Table",
        path="assets/models/table_wood.fbx",
        asset_type=AssetType.MODEL,
        description="Rustic wooden dining table",
        category="furniture",
        tags=["furniture", "table", "wood", "rustic"],
        metadata={
            "polycount": 8200,
            "dimensions": {"width": 1.8, "height": 0.75, "depth": 0.9}
        }
    )

    # Add textures
    registry.add_asset(
        name="Brick Wall Diffuse",
        path="assets/textures/brick_diffuse.png",
        asset_type=AssetType.TEXTURE,
        description="Red brick wall diffuse texture (4K)",
        category="textures",
        tags=["texture", "brick", "wall", "pbr"],
        metadata={
            "resolution": [4096, 4096],
            "format": "PNG",
            "pbr_maps": ["diffuse", "normal", "roughness", "ao"]
        }
    )

    # Add HDRI
    registry.add_asset(
        name="Studio Softbox",
        path="assets/hdri/studio_softbox.exr",
        asset_type=AssetType.HDRI,
        description="Studio lighting HDRI with soft boxes",
        category="lighting",
        tags=["hdri", "studio", "indoor", "soft"],
        metadata={
            "resolution": [8192, 4096],
            "dynamic_range": "32-bit",
            "lighting_style": "studio"
        }
    )

    # Add material preset
    registry.add_asset(
        name="Gold Material",
        path="assets/materials/gold_pbr.json",
        asset_type=AssetType.MATERIAL,
        description="Realistic gold PBR material",
        category="materials",
        tags=["material", "metal", "gold", "pbr"],
        metadata={
            "shader_type": "principled_bsdf",
            "metallic": 1.0,
            "roughness": 0.2,
            "base_color": [1.0, 0.766, 0.336]
        }
    )

    # Add lighting setup
    registry.add_asset(
        name="Three Point Lighting",
        path="assets/lighting/three_point.py",
        asset_type=AssetType.LIGHTING,
        description="Classic three-point lighting setup script",
        category="lighting",
        tags=["lighting", "setup", "studio", "script"],
        metadata={
            "lights": ["key", "fill", "rim"],
            "preset": "studio"
        }
    )

    return registry


# Example usage and testing
if __name__ == "__main__":
    from utils.logger import setup_logging

    # Setup logging
    setup_logging(level="DEBUG", console=True)

    print("\n" + "="*80)
    print("ASSET REGISTRY - TEST SUITE")
    print("="*80 + "\n")

    # Test 1: Create registry and add assets
    print("\n" + "="*80)
    print("Test 1: Create Example Registry")
    print("="*80 + "\n")

    registry = create_example_registry()
    print(f"Created registry with {len(registry.assets)} assets")

    # Test 2: List assets
    print("\n" + "="*80)
    print("Test 2: List Assets")
    print("="*80 + "\n")

    all_assets = registry.list_assets()
    for asset in all_assets:
        print(f"  - {asset.name} ({asset.asset_type.value}) [{asset.category}]")

    # Test 3: Filter by type
    print("\n" + "="*80)
    print("Test 3: Filter Assets by Type")
    print("="*80 + "\n")

    models = registry.list_assets(asset_type=AssetType.MODEL)
    print(f"Models: {len(models)}")
    for model in models:
        print(f"  - {model.name}")

    # Test 4: Search assets
    print("\n" + "="*80)
    print("Test 4: Search Assets")
    print("="*80 + "\n")

    search_results = registry.search_assets("wood")
    print(f"Search 'wood': {len(search_results)} results")
    for result in search_results:
        print(f"  - {result.name} ({result.description})")

    # Test 5: Get asset by name
    print("\n" + "="*80)
    print("Test 5: Get Asset by Name")
    print("="*80 + "\n")

    chair = registry.get_asset("Modern Chair")
    if chair:
        print(f"Found: {chair.name}")
        print(f"  Path: {chair.path}")
        print(f"  Tags: {', '.join(chair.tags)}")
        print(f"  Metadata: {chair.metadata}")

    # Test 6: Get statistics
    print("\n" + "="*80)
    print("Test 6: Registry Statistics")
    print("="*80 + "\n")

    stats = registry.get_statistics()
    print(f"Total Assets: {stats['total_assets']}")
    print(f"Categories: {stats['categories']}")
    print(f"Tags: {stats['tags']}")
    print("\nAssets by Type:")
    for asset_type, count in stats['by_type'].items():
        if count > 0:
            print(f"  {asset_type}: {count}")

    # Test 7: Categories and tags
    print("\n" + "="*80)
    print("Test 7: Categories and Tags")
    print("="*80 + "\n")

    categories = registry.get_categories()
    print(f"Categories: {', '.join(categories)}")

    tags = registry.get_tags()
    print(f"Tags: {', '.join(tags)}")

    # Test 8: Export assets
    print("\n" + "="*80)
    print("Test 8: Export Assets")
    print("="*80 + "\n")

    export_path = Path("data/exported_assets.json")
    success = registry.export_assets(export_path)
    print(f"Export successful: {success}")

    # Test 9: SQLite backend
    print("\n" + "="*80)
    print("Test 9: SQLite Backend")
    print("="*80 + "\n")

    sqlite_registry = AssetRegistry(
        storage_path="data/test_registry.db",
        backend=StorageBackend.SQLITE
    )

    # Add test asset
    sqlite_registry.add_asset(
        name="Test Cube",
        path="assets/cube.blend",
        asset_type=AssetType.MODEL,
        description="Simple test cube",
        tags=["test", "primitive"]
    )

    print(f"SQLite registry: {len(sqlite_registry.assets)} assets")

    # Test 10: Update asset
    print("\n" + "="*80)
    print("Test 10: Update Asset")
    print("="*80 + "\n")

    updated = registry.update_asset(
        "Modern Chair",
        description="Updated: Minimalist modern chair design with new colors",
        tags=["furniture", "chair", "modern", "indoor", "updated"]
    )

    if updated:
        print(f"Updated: {updated.name}")
        print(f"  New description: {updated.description}")
        print(f"  Updated at: {updated.updated_at}")

    print("\n" + "="*80)
    print("TEST SUITE COMPLETE")
    print("="*80 + "\n")
