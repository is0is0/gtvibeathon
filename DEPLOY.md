# Voxel Backend Deployment Guide

## Quick Deploy (3 Minutes)

### Option 1: Railway.app (Recommended for Hackathon)

1. **Push to GitHub:**
```bash
cd /Users/justin/Desktop/gthh/gtvibeathon
git add .
git commit -m "Ready for deployment"
git push origin main
```

2. **Deploy on Railway:**
- Go to https://railway.app
- Click "Start a New Project"
- Select "Deploy from GitHub repo"
- Choose your repository
- Railway auto-detects Procfile and deploys
- Get your URL: `https://your-app.up.railway.app`

3. **Add Environment Variables:**
In Railway dashboard:
- Go to Variables tab
- Add: `ANTHROPIC_API_KEY` or `OPENAI_API_KEY`
- Add: `BLENDER_PATH=/usr/bin/blender` (Railway has Blender)
- Save and redeploy

4. **Your API is live!**
- API URL: `https://your-app.up.railway.app/api`
- Test: `https://your-app.up.railway.app/api/health`

### Option 2: Ngrok (Local + Public URL)

1. **Install ngrok:**
```bash
brew install ngrok
# or download from https://ngrok.com
```

2. **Start backend locally:**
```bash
cd /Users/justin/Desktop/gthh/gtvibeathon
python3 start_api.py
```

3. **Expose with ngrok:**
```bash
ngrok http 5000
```

4. **Copy the URL:**
```
Forwarding: https://abc123.ngrok-free.app -> http://localhost:5000
```

5. **Use in Framer:**
Update API_URL to: `https://abc123.ngrok-free.app`

### Option 3: Render.com (Free Tier)

1. **Push to GitHub** (same as Railway)

2. **Deploy on Render:**
- Go to https://render.com
- New → Web Service
- Connect GitHub repo
- Build Command: `pip install -r requirements.txt`
- Start Command: `python start_api.py`
- Add environment variables
- Deploy

3. **Your URL:**
`https://your-app.onrender.com/api`

## Environment Variables Needed

```
ANTHROPIC_API_KEY=sk-ant-...
AI_PROVIDER=anthropic
AI_MODEL=claude-3-5-sonnet-20241022
BLENDER_PATH=/usr/bin/blender
```

## Testing Your Deployment

```bash
# Health check
curl https://your-deployed-url.com/api/health

# Get agents
curl https://your-deployed-url.com/api/agents

# Test generation
curl -X POST https://your-deployed-url.com/api/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "a glowing cube", "agents": ["concept", "builder", "render"]}'
```

## Troubleshooting

### "Module not found" errors
- Check `requirements.txt` is complete
- Redeploy

### CORS errors
- Already configured with `CORS(app)`
- If still issues, check browser console

### Blender not found
- Add `BLENDER_PATH` environment variable
- Railway/Render: `/usr/bin/blender`
- Local: Your Blender installation path

### Timeouts
- Increase timeout in platform settings
- Railway: Settings → Timeout → 300s
- Render: Free tier has 15min limit
