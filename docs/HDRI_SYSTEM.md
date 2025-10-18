# HDRI System Documentation

Complete guide to Voxel's intelligent HDRI selection and blending system.

---

## Overview

The Voxel HDRI system provides intelligent lighting through:

1. **Automatic HDRI Selection**: AI-driven selection based on mood, time, environment
2. **Multi-HDRI Blending**: Mix multiple HDRIs for unique atmospheric effects
3. **AssetRegistry Integration**: Access 500+ HDRIs from Poly Haven
4. **Context-Aware Lighting**: Smart selection based on scene requirements

---

## Architecture

```
┌─────────────────────┐
│   User Prompt       │
│  "Cozy cafe at      │
│   sunset"           │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────────────────────────────┐
│     Prompt Interpretation                   │
│  - Mood: cozy, warm                         │
│  - Time: sunset                             │
│  - Environment: indoor                      │
└──────────┬──────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────┐
│         HDRI Manager                        │
│  ┌─────────────────────────────────────┐   │
│  │ 1. Search Asset Registry            │   │
│  │    - By mood tags                   │   │
│  │    - By time of day                 │   │
│  │    - By environment                 │   │
│  └─────────────────────────────────────┘   │
│  ┌─────────────────────────────────────┐   │
│  │ 2. Score & Rank HDRIs               │   │
│  │    - Relevance scoring              │   │
│  │    - Weighted combination           │   │
│  └─────────────────────────────────────┘   │
│  ┌─────────────────────────────────────┐   │
│  │ 3. Create Blend Configuration       │   │
│  │    - Strength allocation            │   │
│  │    - Rotation distribution          │   │
│  │    - Color adjustments              │   │
│  └─────────────────────────────────────┘   │
└──────────┬──────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────┐
│    Blender Script Generation                │
│  - Multi-layer HDRI node setup              │
│  - Mix RGB nodes for blending               │
│  - Rotation and strength controls           │
└──────────┬──────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────┐
│         Final Render                        │
│  Unique lighting atmosphere from            │
│  blended HDRIs matching scene mood          │
└─────────────────────────────────────────────┘
```

---

## Components

### 1. HDRI Manager (`hdri_manager.py`)

Core HDRI intelligence system.

**Features:**
- Tag-based HDRI search
- Mood-based selection
- Time-of-day matching
- Environment filtering
- Multi-HDRI blending configurations
- Blender script generation

**Example:**
```python
from subsystems.hdri_manager import HDRIManager

# Initialize with AssetRegistry
manager = HDRIManager("data/voxel_assets.db")

# Smart selection based on scene context
scene_context = {
    'interpreted_prompt': {
        'mood': {'cozy': 0.8},
        'time_of_day': 'sunset',
        'environment': 'indoor',
    }
}

hdris = manager.select_smart(scene_context, limit=2)
# Returns 2 most relevant HDRIs

# Create blend configuration
layers = manager.create_blend_configuration(hdris, blend_mode='layered')

# Generate Blender script
script = manager.generate_blend_script(layers, world_strength=1.0)
```

### 2. Enhanced Lighting AI (`lighting_ai_enhanced.py`)

Extends base LightingAI with HDRI intelligence.

**Features:**
- Automatic HDRI selection during lighting setup
- Seamless integration with existing lighting system
- Mood-based HDRI parameter adjustments
- Support for single and multi-HDRI setups

**Example:**
```python
from subsystems.lighting_ai_enhanced import LightingAIEnhanced

# Initialize with configuration
config = {
    'registry_path': 'data/voxel_assets.db',
    'enable_hdri_blending': True,
    'max_hdri_layers': 2,
    'hdri_blend_mode': 'layered',  # 'layered', 'balanced', 'dominant'
}

lighting = LightingAIEnhanced(config)

# Apply lighting (HDRIs selected automatically)
scene_data = lighting.apply(scene_data, style='realistic')

# Check HDRI info
if 'hdri_blend' in scene_data['lighting']:
    blend_info = scene_data['lighting']['hdri_blend']
    print(f"Using {blend_info['num_layers']} HDRIs:")
    print(f"  {', '.join(blend_info['hdris'])}")
```

### 3. Poly Haven Downloader (`scripts/download_polyhaven_hdris.py`)

Downloads HDRIs and registers them with AssetRegistry.

**Example:**
```bash
# Download all 2k HDRIs and register
python scripts/download_polyhaven_hdris.py \
  --resolution 2k \
  --register \
  --registry-path data/voxel_assets.db

# Test with 5 HDRIs at 1k
python scripts/download_polyhaven_hdris.py \
  --resolution 1k \
  --limit 5 \
  --register
```

---

## HDRI Selection Algorithms

### Mood-Based Selection

Maps scene moods to HDRI tags:

```python
MOOD_TAG_MAP = {
    'cozy': ['indoor', 'warm', 'soft', 'studio'],
    'dramatic': ['sunset', 'dark', 'dramatic', 'clouds'],
    'energetic': ['sunny', 'bright', 'daylight', 'clear'],
    'peaceful': ['nature', 'forest', 'peaceful', 'soft'],
    'mysterious': ['night', 'dark', 'foggy', 'atmospheric'],
    'futuristic': ['urban', 'city', 'night', 'neon'],
    'natural': ['outdoor', 'daylight', 'nature', 'clear'],
    'romantic': ['sunset', 'warm', 'soft', 'pink'],
}
```

**Scoring:**
- Tag match: +1.0 per matching tag
- Name match: +0.5 bonus
- Top-scored HDRIs selected

### Time-of-Day Selection

Maps times to lighting characteristics:

```python
TIME_OF_DAY_TAGS = {
    'sunrise': ['sunrise', 'dawn', 'morning', 'warm'],
    'noon': ['noon', 'daylight', 'sunny', 'bright'],
    'sunset': ['sunset', 'dusk', 'evening', 'warm'],
    'night': ['night', 'dark', 'moon', 'stars'],
}
```

**Scoring:**
- Tag match: +1.5 per match
- Name match: +2.0 (higher weight)

### Smart Selection

Combines multiple criteria with weighted scoring:

1. **Mood matching** (weight: 2.0)
2. **Time-of-day matching** (weight: 1.5)
3. **Environment matching** (weight: 1.0)

```
Final Score = (mood_score × 2.0) + (time_score × 1.5) + (env_score × 1.0)
```

Top-scored HDRIs are selected and blended.

---

## Blending Modes

### Layered Mode (Default)

Decreasing strength for each layer:

```
Layer 1: 100% strength
Layer 2: 50% strength
Layer 3: 33% strength
Layer N: 1/N strength
```

Each layer rotated evenly around 360°.

**Best for:** Subtle environmental variation with dominant base HDRI.

### Balanced Mode

Equal strength for all layers:

```
Each layer: 1/N strength
Random rotations
```

**Best for:** Equal contribution from all HDRIs.

### Dominant Mode

First HDRI is primary, others are subtle accents:

```
Layer 1: 70% strength
Layers 2-N: 30% / (N-1) strength each
```

**Best for:** Strong base lighting with subtle environmental hints.

---

## Blender Node Setup

### Single HDRI

```
TextureCoordinate → Mapping → Environment Texture → Background → World Output
                       ↓
                   Rotation
```

### Multi-HDRI Blend (2 layers)

```
                        ┌─ Env Texture 1 ─┐
TextureCoordinate ──┬─→ Mapping 1        │
                    │                     ├─→ Mix RGB ─→ Background ─→ World Output
TextureCoordinate ──┴─→ Mapping 2        │
                        └─ Env Texture 2 ─┘
                               ↓
                          Rotation 1, 2
```

### Multi-HDRI Blend (3+ layers)

```
Env 1 ──┐
        ├─ Mix 1 ──┐
Env 2 ──┘          ├─ Mix 2 ──┐
                   │           ├─ Mix 3 ── ... ─→ Background
Env 3 ─────────────┘           │
                               │
Env 4 ─────────────────────────┘
```

---

## Usage Examples

### Example 1: Automatic HDRI Selection

```python
from subsystems.lighting_ai_enhanced import LightingAIEnhanced

# Initialize
lighting = LightingAIEnhanced({
    'registry_path': 'data/voxel_assets.db',
    'enable_hdri_blending': True,
    'max_hdri_layers': 2,
})

# Scene with mood
scene_data = {
    'objects': [...],
    'interpreted_prompt': {
        'mood': {'cozy': 0.8, 'warm': 0.7},
        'time_of_day': 'evening',
        'environment': 'indoor',
    }
}

# Apply lighting (HDRIs selected automatically)
result = lighting.apply(scene_data, style='realistic')

# Result includes:
# - Automatically selected HDRIs matching "cozy", "evening", "indoor"
# - Blended HDRI configuration
# - Complete Blender script
```

### Example 2: Manual HDRI Selection

```python
from subsystems.hdri_manager import HDRIManager

manager = HDRIManager("data/voxel_assets.db")

# Search for specific HDRIs
sunset_hdris = manager.search_hdris(
    tags=['sunset', 'warm', 'outdoor'],
    limit=3
)

# Create blend with custom parameters
layers = manager.create_blend_configuration(
    sunset_hdris,
    blend_mode='dominant'
)

# Adjust parameters
layers[0].strength = 0.8
layers[0].rotation = math.radians(45)
layers[1].color_tint = (1.0, 0.9, 0.8)  # Warmer tint

# Generate script
script = manager.generate_blend_script(layers, world_strength=1.2)
```

### Example 3: Time-of-Day Animation

```python
# Create lighting for different times
times = ['sunrise', 'noon', 'sunset', 'night']

for time in times:
    scene_data['interpreted_prompt']['time_of_day'] = time
    result = lighting.apply(scene_data, style='realistic')

    # Each time gets different HDRIs:
    # sunrise: warm, soft morning light
    # noon: bright, clear daylight
    # sunset: golden hour, dramatic clouds
    # night: dark, moonlit, stars
```

### Example 4: Mood Variations

```python
moods = [
    {'cozy': 1.0},
    {'dramatic': 1.0},
    {'peaceful': 1.0},
    {'energetic': 1.0},
]

for mood in moods:
    scene_data['interpreted_prompt']['mood'] = mood
    result = lighting.apply(scene_data, style='realistic')

    # Each mood gets different HDRI selection:
    # cozy: indoor, warm, soft lighting
    # dramatic: sunset, clouds, high contrast
    # peaceful: nature, soft, calm atmosphere
    # energetic: bright, sunny, clear sky
```

---

## Configuration Options

### LightingAIEnhanced Config

```python
config = {
    # AssetRegistry path
    'registry_path': 'data/voxel_assets.db',

    # Enable multi-HDRI blending
    'enable_hdri_blending': True,  # False for single HDRI only

    # Maximum HDRIs to blend
    'max_hdri_layers': 2,  # 1-4 recommended

    # Blending mode
    'hdri_blend_mode': 'layered',  # 'layered', 'balanced', 'dominant'

    # Base LightingAI options
    'default_mode': 'realistic',
    'shadow_quality': 'high',
}
```

### HDRIManager Config

```python
# Initialize with registry
manager = HDRIManager(registry_path="data/voxel_assets.db")

# Or without registry (manual HDRI paths)
manager = HDRIManager(registry_path=None)
```

---

## API Integration

### REST API Endpoints

The Framer API automatically uses HDRI system when generating:

```javascript
// Request with mood and time
fetch('/api/generate', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`,
  },
  body: JSON.stringify({
    prompt: "A cozy cafe at sunset",
    agents: [
      {agent_type: 'concept'},
      {agent_type: 'builder'},
      {agent_type: 'texture'},
      {agent_type: 'lighting'},  // Uses HDRI system
      {agent_type: 'render'},
    ],
    mode: 'customizable',
    customizable_settings: {
      lighting_mode: 'realistic',  // Enables HDRI
      // HDRI system automatically selects based on prompt
    }
  })
})
```

### WebSocket Updates

Real-time HDRI selection updates:

```javascript
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);

  if (data.type === 'stage_update' && data.stage === 'lighting') {
    console.log('HDRI selected:', data.message);
    // e.g., "Selected 2 HDRIs: studio_small_08, abandoned_workshop"
  }
}
```

---

## Performance Considerations

### HDRI File Sizes

Resolution recommendations:

| Resolution | File Size | Use Case |
|------------|-----------|----------|
| 1k         | 1-2 MB    | Quick previews, testing |
| 2k         | 4-8 MB    | Production (default) |
| 4k         | 16-32 MB  | High quality renders |
| 8k         | 64-128 MB | Ultra quality (slow) |

### Blending Performance

- **1 HDRI**: No performance impact
- **2 HDRIs**: ~5% slower render time
- **3 HDRIs**: ~10% slower render time
- **4+ HDRIs**: Not recommended (diminishing returns)

**Recommendation:** Use 1-2 HDRIs for best quality/performance balance.

### Memory Usage

Blender loads entire HDRI into memory:

```
Memory = Resolution² × 4 channels × 4 bytes (float)

1k HDRI:  1024² × 4 × 4 = 16 MB
2k HDRI:  2048² × 4 × 4 = 64 MB
4k HDRI:  4096² × 4 × 4 = 256 MB
```

Multiple HDRIs multiply memory usage.

---

## Troubleshooting

### No HDRIs Available

**Problem:** `No HDRIs available in registry`

**Solution:**
```bash
# Download HDRIs from Poly Haven
python scripts/download_polyhaven_hdris.py \
  --resolution 2k \
  --register \
  --registry-path data/voxel_assets.db
```

### HDRIs Not Matching Scene

**Problem:** Selected HDRIs don't match mood/time

**Solution:**
- Check HDRI tags: `manager.available_hdris[0].tags`
- Ensure HDRIs are properly tagged during download
- Use manual selection: `manager.search_hdris(tags=['sunset'])`

### Blend Script Errors

**Problem:** Blender script fails to execute

**Solution:**
- Check HDRI file paths are absolute
- Verify HDRI files exist and are readable
- Test individual HDRI loading in Blender

### Performance Issues

**Problem:** Rendering is very slow with HDRIs

**Solution:**
- Reduce resolution: Use 1k or 2k HDRIs
- Use single HDRI instead of blending
- Lower render samples
- Use EEVEE instead of CYCLES

---

## Advanced Usage

### Custom HDRI Scoring

Override scoring functions for custom selection logic:

```python
class CustomHDRIManager(HDRIManager):
    def _calculate_mood_score(self, asset, tags):
        # Custom scoring logic
        score = super()._calculate_mood_score(asset, tags)

        # Boost HDRIs with "studio" tag
        if 'studio' in asset.tags:
            score += 2.0

        return score
```

### Dynamic HDRI Adjustment

Adjust HDRI parameters based on scene analysis:

```python
def adjust_hdri_for_scene(layers, scene_analysis):
    max_dimension = scene_analysis['max_dimension']

    for layer in layers:
        # Increase strength for large scenes
        if max_dimension > 50:
            layer.strength *= 1.5

        # Rotate based on scene center
        center_angle = math.atan2(
            scene_analysis['center'][1],
            scene_analysis['center'][0]
        )
        layer.rotation = center_angle

    return layers
```

### HDRI Caching

Optimize repeated renders with caching:

```python
class CachedHDRIManager(HDRIManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.selection_cache = {}

    def select_smart(self, scene_context, limit=3):
        # Create cache key from context
        key = self._make_cache_key(scene_context)

        if key in self.selection_cache:
            return self.selection_cache[key]

        # Select and cache
        result = super().select_smart(scene_context, limit)
        self.selection_cache[key] = result

        return result
```

---

## Future Enhancements

### Planned Features

1. **AI-Generated HDRIs**
   - Generate custom HDRIs with Stable Diffusion
   - Panorama generation from text prompts

2. **Real-Time HDRI Preview**
   - Interactive HDRI selection in UI
   - Live preview of blended results

3. **Temporal HDRI Blending**
   - Animate between different HDRIs
   - Smooth time-of-day transitions

4. **Style Transfer HDRIs**
   - Apply artistic styles to HDRIs
   - Match HDRI to scene aesthetic

5. **HDRI Completion**
   - Inpaint missing HDRI regions
   - Extend HDRI resolution with AI

---

## Credits

- **HDRIs**: [Poly Haven](https://polyhaven.com) (CC0)
- **Blender**: [Blender Foundation](https://www.blender.org)
- **Voxel System**: GT Vibeathon 2025

---

## Support

For questions or issues:
- GitHub: https://github.com/yourusername/voxel
- Discord: discord.gg/voxel
- Docs: https://voxel.readthedocs.io

---

## License

MIT License - See LICENSE file for details
