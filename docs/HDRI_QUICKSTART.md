# HDRI System Quick Start

Get started with intelligent HDRI lighting in 5 minutes.

---

## 1. Download HDRIs (One-Time Setup)

```bash
# Download 10 test HDRIs at 1k resolution
python scripts/download_polyhaven_hdris.py \
  --resolution 1k \
  --limit 10 \
  --register \
  --registry-path data/voxel_assets.db

# For production, download all 2k HDRIs (takes ~1 hour)
python scripts/download_polyhaven_hdris.py \
  --resolution 2k \
  --register \
  --registry-path data/voxel_assets.db
```

**Output:**
```
📦 Found 500 HDRIs to download at 1k resolution
💾 Saving to: C:\Users\...\data\polyhaven_hdri_dataset
⏱️  Delay between requests: 1.5s

[1/10] 📥 abandoned_warehouse
  Downloading ████████████████████ 100% 1.2 MB
✅ abandoned_warehouse - Downloaded (1.2 MB)

...

📊 DOWNLOAD SUMMARY
✅ Completed:  10
⏭️  Skipped:    0
❌ Failed:     0
⏱️  Total time: 45.2s
📚 Assets registered in: data/voxel_assets.db
```

---

## 2. Use in Your Code

### Simple Usage (Automatic)

```python
from subsystems.lighting_ai_enhanced import LightingAIEnhanced

# Initialize (one-time)
lighting = LightingAIEnhanced({
    'registry_path': 'data/voxel_assets.db',
    'enable_hdri_blending': True,
    'max_hdri_layers': 2,
})

# Apply to scene (HDRIs selected automatically!)
scene_data = {
    'objects': [...],
    'interpreted_prompt': {
        'prompt': 'A cozy cafe at sunset',
        'mood': {'cozy': 0.8, 'warm': 0.7},
        'time_of_day': 'sunset',
        'environment': 'indoor',
    }
}

result = lighting.apply(scene_data, style='realistic')

# The system automatically:
# - Searches for HDRIs matching "cozy", "sunset", "indoor"
# - Selects best 2 HDRIs
# - Blends them with optimal parameters
# - Generates complete Blender script
```

### Manual Selection

```python
from subsystems.hdri_manager import HDRIManager

manager = HDRIManager("data/voxel_assets.db")

# Search for specific HDRIs
hdris = manager.search_hdris(
    tags=['sunset', 'warm'],
    limit=2
)

# Create blend
layers = manager.create_blend_configuration(
    hdris,
    blend_mode='layered'
)

# Generate Blender script
script = manager.generate_blend_script(layers)

# Use in Blender
# (copy script to Blender's scripting panel and run)
```

---

## 3. See the Results

```python
# Check what HDRIs were selected
if 'hdri_blend' in result['lighting']:
    blend = result['lighting']['hdri_blend']
    print(f"Used {blend['num_layers']} HDRIs:")
    for name in blend['hdris']:
        print(f"  - {name}")

# Output:
# Used 2 HDRIs:
#   - studio_small_08
#   - abandoned_workshop
```

---

## 4. Integrate with Voxel Pipeline

### CLI Usage

```bash
# Run with enhanced lighting
voxel create "A cozy cafe at sunset" \
  --config config/enhanced_lighting.yaml
```

### Python API

```python
from orchestrator.scene_orchestrator import SceneOrchestrator

# Initialize with enhanced lighting
orchestrator = SceneOrchestrator({
    'lighting_config': {
        'registry_path': 'data/voxel_assets.db',
        'enable_hdri_blending': True,
    }
})

# Generate scene
result = orchestrator.generate_complete_scene(
    prompt="A cozy cafe at sunset",
    style="realistic"
)

# Lighting includes HDRI blend automatically
```

### Framer Frontend

```javascript
// Request generation with HDRI support
const response = await fetch('/api/generate', {
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
      {agent_type: 'lighting'},  // Automatically uses HDRI system
      {agent_type: 'render'},
    ],
    mode: 'automatic',
  })
});

// HDRIs are selected automatically based on prompt analysis
```

---

## 5. Common Scenarios

### Scenario 1: Different Times of Day

```python
times = ['sunrise', 'noon', 'sunset', 'night']

for time in times:
    scene_data['interpreted_prompt']['time_of_day'] = time
    result = lighting.apply(scene_data, style='realistic')

# Each time gets matching HDRIs:
# - sunrise: warm morning light
# - noon: bright clear sky
# - sunset: golden hour
# - night: dark moonlit
```

### Scenario 2: Mood Variations

```python
moods = {
    'cozy': "warm indoor lighting",
    'dramatic': "high contrast dramatic clouds",
    'peaceful': "soft nature lighting",
    'energetic': "bright sunny day",
}

for mood_name, description in moods.items():
    scene_data['interpreted_prompt']['mood'] = {mood_name: 1.0}
    result = lighting.apply(scene_data, style='realistic')
    print(f"{mood_name}: {result['lighting']['hdri_blend']['hdris']}")
```

### Scenario 3: Environment Types

```python
environments = ['indoor', 'outdoor', 'urban', 'nature', 'studio']

for env in environments:
    scene_data['interpreted_prompt']['environment'] = env
    result = lighting.apply(scene_data, style='realistic')

# Each environment gets appropriate HDRIs
```

---

## 6. Verify Installation

```python
from subsystems.hdri_manager import HDRIManager

manager = HDRIManager("data/voxel_assets.db")

# Check available HDRIs
print(f"Total HDRIs: {len(manager.available_hdris)}")

# List first 5
for hdri in manager.available_hdris[:5]:
    print(f"  - {hdri.name}: {hdri.tags[:3]}")

# Search capabilities
sunset_hdris = manager.search_hdris(tags=['sunset'], limit=5)
print(f"\nFound {len(sunset_hdris)} sunset HDRIs")
```

**Expected Output:**
```
Total HDRIs: 487
  - abandoned_warehouse: ['indoor', 'dark', 'urban']
  - forest_slope: ['outdoor', 'nature', 'daylight']
  - studio_small_08: ['studio', 'indoor', 'neutral']
  - sunset_fairway: ['outdoor', 'sunset', 'warm']
  - urban_alley: ['urban', 'outdoor', 'alley']

Found 23 sunset HDRIs
```

---

## 7. Troubleshooting

### Problem: "No HDRIs available"

**Solution:** Download HDRIs first
```bash
python scripts/download_polyhaven_hdris.py --resolution 1k --limit 5 --register
```

### Problem: HDRIs not matching scene

**Solution:** Check tagging
```python
# See what tags are available
manager = HDRIManager("data/voxel_assets.db")
all_tags = set()
for hdri in manager.available_hdris:
    all_tags.update(hdri.tags)
print(f"Available tags: {sorted(all_tags)}")
```

### Problem: Blender script fails

**Solution:** Check file paths
```python
# Verify HDRI files exist
for hdri in manager.available_hdris[:5]:
    exists = os.path.exists(hdri.path)
    print(f"{hdri.name}: {exists}")
```

---

## 8. Next Steps

- **Read full documentation**: `docs/HDRI_SYSTEM.md`
- **Download more HDRIs**: Increase `--limit` or remove to get all
- **Experiment with blend modes**: Try `'balanced'` or `'dominant'`
- **Create custom HDRI selections**: Use `search_hdris()` with specific tags
- **Integrate with your pipeline**: Add to your scene generation workflow

---

## Quick Reference

### Download HDRIs
```bash
python scripts/download_polyhaven_hdris.py --resolution 2k --register
```

### Initialize System
```python
from subsystems.lighting_ai_enhanced import LightingAIEnhanced
lighting = LightingAIEnhanced({'registry_path': 'data/voxel_assets.db'})
```

### Apply Lighting
```python
result = lighting.apply(scene_data, style='realistic')
```

### Check Results
```python
print(result['lighting']['hdri_blend']['hdris'])
```

---

**That's it!** You now have intelligent HDRI lighting that automatically selects and blends HDRIs based on your scene's mood, time, and environment. 🎨✨
