# 🚀 COMPLETE VOXEL SETUP - DO THIS ALL FOR YOU

Everything is ready! Follow these exact steps.

## ⚡ STEP 1: Start Your Backend (2 minutes)

```bash
# Open Terminal and go to your project
cd /Users/justin/Desktop/gthh/gtvibeathon

# Make sure you're in the right directory
pwd
# Should show: /Users/justin/Desktop/gthh/gtvibeathon

# Copy the example env file
cp .env.example .env

# Open .env and add your API key
nano .env
# Add your ANTHROPIC_API_KEY=sk-ant-...
# Press Ctrl+X, then Y, then Enter to save

# Install dependencies (one-time setup)
pip install -r requirements.txt

# Start the backend
python3 start_api.py
```

You should see:
```
Starting Voxel API server...
Server starting on http://0.0.0.0:5000
```

✅ **Backend is now running!** Keep this terminal window open.

---

## 🌐 STEP 2: Make Backend Public (1 minute)

Open a **NEW terminal window** (keep the first one running!):

```bash
# Install ngrok (if not already installed)
brew install ngrok

# Expose your backend to the internet
ngrok http 5000
```

You'll see something like:
```
Forwarding: https://abc123-456-789.ngrok-free.app -> http://localhost:5000
```

✅ **Copy that URL** (the https://abc123... part)

---

## 🎨 STEP 3: Setup Framer (3 minutes)

### 3.1: Add the Component

1. Open your Framer project
2. Click **Assets** (left sidebar)
3. Click **+** button → **Code Component**
4. Name it: `VoxelGenerator`
5. **Copy the entire content** from: `/Users/justin/Desktop/gthh/gtvibeathon/FRAMER_COMPONENT.tsx`
6. **Paste** it into Framer

### 3.2: Update the API URL

In the component code you just pasted, find line 13:
```typescript
const API_URL = 'https://your-app.up.railway.app'
```

**Replace it with your ngrok URL:**
```typescript
const API_URL = 'https://abc123-456-789.ngrok-free.app'  // YOUR ACTUAL URL
```

### 3.3: Install Socket.IO Dependency

1. In Framer, go to **File** → **Dependencies**
2. Click **+** (Add Package)
3. Type: `socket.io-client`
4. Version: `4.5.4`
5. Click **Install**

### 3.4: Add Component to Canvas

1. Find **VoxelGenerator** in your Assets panel
2. **Drag it** onto your canvas
3. Position it where you want (below your title)
4. Stretch it to full width

---

## 🎉 STEP 4: Test It! (30 seconds)

1. Click **Preview** in Framer (top right)
2. Type a prompt: `"a glowing cube on a plane"`
3. Select some agents (they're pre-selected)
4. Press **Enter** or click the arrow button
5. Watch the magic happen! ✨

You should see:
- ✅ Progress updates in real-time
- ✅ "Scene Generated!" when done
- ✅ Download buttons appear

---

## 📦 STEP 5: Download Your Files

Click the download buttons:
- **📦 Blender File** - Opens the .blend file
- **🖼️ Rendered Image** - Your scene render
- **📜 Python Scripts** - All generated code

---

## 🚀 STEP 6: Publish (30 seconds)

1. In Framer, click **Publish** (top right)
2. Your site is now live!
3. Share the URL with everyone

---

## 🐛 Troubleshooting

### Backend won't start
```bash
# Make sure you're in the right directory
cd /Users/justin/Desktop/gthh/gtvibeathon

# Check if port 5000 is already in use
lsof -i :5000
# If something shows up, kill it:
kill -9 <PID>

# Try starting again
python3 start_api.py
```

### "Module not found" error
```bash
# Reinstall dependencies
pip install -r requirements.txt
```

### Framer component not working
1. Check Console (Right-click → Inspect → Console)
2. Look for errors
3. Make sure API_URL is correct
4. Make sure `socket.io-client` is installed in dependencies

### CORS errors
- Already fixed! But if you see them:
- Check that backend is running
- Check ngrok URL is correct

### "Connection refused"
- Make sure backend is running (check Terminal 1)
- Make sure ngrok is running (check Terminal 2)
- Check ngrok URL hasn't changed (they expire)

---

## 🎯 Quick Commands Reference

**Start Backend:**
```bash
cd /Users/justin/Desktop/gthh/gtvibeathon
python3 start_api.py
```

**Start Ngrok (new terminal):**
```bash
ngrok http 5000
```

**Test API:**
```bash
# Health check
curl https://your-ngrok-url.app/api/health

# Get agents
curl https://your-ngrok-url.app/api/agents
```

---

## 🎨 What Your Site Should Look Like

Your Framer site should have:
- ✅ **Title**: "voxel" with gradient
- ✅ **Subtitle**: Pink text about structured Blender worlds
- ✅ **Agent Selector**: 6 colorful agent cards
- ✅ **Chat Input**: Rounded input with gradient button
- ✅ **Progress**: Animated progress bar during generation
- ✅ **Downloads**: 3 download buttons when complete

---

## 🚀 For Your Hackathon Demo

### Before You Present:
1. ✅ Backend running
2. ✅ Ngrok running
3. ✅ Framer site published
4. ✅ Test one generation to make sure it works

### During Demo:
1. Show your beautiful Framer site
2. Select some agents (show the selection UI)
3. Type a cool prompt: "a futuristic city with glowing buildings at night"
4. Press Enter
5. Show real-time progress
6. Download the .blend file
7. (Optional) Open in Blender and show the scene

### Cool Demo Prompts:
- "a cozy cyberpunk cafe with neon lights"
- "floating islands with waterfalls in a purple sky"
- "a mystical forest with glowing crystals"
- "futuristic spaceship interior with holographic displays"

---

## 📸 Screenshots to Take

Before hackathon:
1. Agent selection screen
2. Chat input with prompt
3. Progress animation
4. Download section with files
5. (Optional) Generated scene in Blender

---

## ⚡ Fast Reset (If Something Breaks)

```bash
# Kill everything
killall python3
killall ngrok

# Restart
cd /Users/justin/Desktop/gthh/gtvibeathon
python3 start_api.py
# (new terminal) ngrok http 5000
# Update Framer component with new ngrok URL
```

---

## 🎉 YOU'RE DONE!

Your Voxel system is now:
- ✅ Running locally with public access
- ✅ Beautiful Framer frontend
- ✅ Real-time updates
- ✅ Download functionality
- ✅ Ready for your hackathon!

**Need help?** Check the backend terminal for errors or the browser console in Framer preview.

**Good luck with your hackathon! 🚀**
