# ⚡ START HERE - I DID IT ALL FOR YOU

## 🎉 Everything is ready! Just follow these 4 steps:

---

## STEP 1: Start Backend (30 seconds)

Open Terminal and run these 3 commands:

```bash
cd /Users/justin/Desktop/gthh/gtvibeathon

cp .env.example .env && nano .env
# Type your ANTHROPIC_API_KEY on line 3
# Press: Ctrl+X, then Y, then Enter

./START.sh
```

✅ You should see: "Starting server on http://0.0.0.0:5000"
✅ Keep this terminal window open!

---

## STEP 2: Make It Public (30 seconds)

Open a **NEW terminal** window and run:

```bash
ngrok http 5000
```

✅ Copy the URL that looks like: `https://abc123.ngrok-free.app`
✅ Keep this terminal open too!

---

## STEP 3: Setup Framer (2 minutes)

1. Open Framer → **Assets** → **+** → **Code Component**
2. Name it: `VoxelGenerator`
3. Open this file: `/Users/justin/Desktop/gthh/gtvibeathon/FRAMER_COMPONENT.tsx`
4. **Select All** (Cmd+A) and **Copy** (Cmd+C)
5. **Paste** into Framer
6. Find **line 13** in the code:
   ```typescript
   const API_URL = 'https://your-app.up.railway.app'
   ```
7. Replace with **your ngrok URL**:
   ```typescript
   const API_URL = 'https://abc123.ngrok-free.app'  // YOUR URL HERE
   ```
8. Go to **File** → **Dependencies** → **+** → Type: `socket.io-client` → Version: `4.5.4` → Install
9. **Drag** the VoxelGenerator component onto your canvas
10. **Publish**

---

## STEP 4: Test It! (30 seconds)

1. Click **Preview** in Framer
2. Type: "a glowing cube"
3. Press **Enter**
4. Watch it generate!

---

## 🎉 DONE!

You now have:
- ✅ Working backend with API
- ✅ Beautiful Framer website
- ✅ Real-time updates
- ✅ Download functionality

---

## 📚 More Info:

- **Full Instructions:** `COMPLETE_SETUP.md`
- **Deployment Guide:** `DEPLOY.md`
- **Hackathon Tips:** `README_HACKATHON.md`

---

## 🐛 If Something Breaks:

**Backend won't start:**
```bash
cd /Users/justin/Desktop/gthh/gtvibeathon
pip install -r requirements.txt
./START.sh
```

**Framer not connecting:**
1. Check both terminals are running
2. Make sure ngrok URL is correct in Framer component (line 13)
3. Check browser console (Right-click → Inspect → Console)

**Still stuck:**
- Check `.env` has your API key
- Make sure port 5000 isn't used: `lsof -i :5000`
- Restart everything: `killall python3 ngrok` then start again

---

## 🎬 For Your Demo:

**Cool Prompts to Show:**
- "a cozy cyberpunk cafe with neon lights"
- "floating islands with waterfalls in a purple sky"
- "futuristic spaceship cockpit with holographic displays"

**What to Highlight:**
- Multi-agent AI system
- Real-time progress
- Beautiful UI
- One-click downloads
- Complex 3D scenes

---

## That's it! Go win your hackathon! 🏆
