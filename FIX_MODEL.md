# How to Fix the Model Error

## The Issue
The model name `claude-3-5-sonnet-20241022` is not recognized by your API key.

## Solution: Update the Model Name

### Option 1: Use Environment Variable (Easiest)
```bash
export AI_MODEL="claude-3-5-sonnet-20241022"
voxel create "a simple cube"
```

### Option 2: Edit the Config File
Open `/Users/justin/Desktop/gthh/gtvibeathon/src/agency3d/core/config.py` and change line 27 to use a valid model name.

Valid Claude model names you can try:
- `claude-3-5-sonnet-20241022` (latest as of Oct 2024)
- `claude-3-opus-20240229`
- `claude-3-sonnet-20240229`
- `claude-3-haiku-20240307`

### Option 3: Create a .env File
Create a file called `.env` in the project root:
```bash
cd /Users/justin/Desktop/gthh/gtvibeathon
cat > .env << 'EOF'
ANTHROPIC_API_KEY=YOUR_ANTHROPIC_API_KEY_HERE
AI_MODEL=claude-3-5-sonnet-20241022
BLENDER_PATH=/Applications/Blender.app/Contents/MacOS/Blender
EOF
```

### Check Your API Access
Visit https://console.anthropic.com/ to check which models your API key has access to.

## Test After Fixing
```bash
voxel config-check
voxel create "a simple cube"
```

