# Session State Fix - Preventing Stuck Sessions

## Problem
Sessions were getting stuck because:
1. **In-memory only** - State stored only in RAM, lost on restart
2. **No file sync** - Backend didn't check actual files on disk
3. **SocketIO only** - If client disconnected, missed completion events
4. **No recovery** - Couldn't rebuild state after crash/restart

## Solution Implemented

### 1. Persistent Session Storage
Every state change now writes to `output/{session_id}/session_state.json`:

```json
{
  "id": "e4ea3146-4274-4f0b-bf89-55c579db741c",
  "status": "completed",
  "prompt": "generate an Under Armour 3d logo",
  "created_at": "2025-10-19T16:27:45.284568",
  "completed_at": "2025-10-19T17:16:23.000000",
  "result": {
    "success": true,
    "output_path": "/path/to/render.png",
    "session_dir": "/path/to/session"
  }
}
```

### 2. Automatic State Recovery
On backend startup, the system:
- Scans `output/` directory for all sessions
- Loads saved `session_state.json` files
- Syncs state with actual files on disk
- Detects completed sessions even without state file

**File-based detection logic:**
```
Has render.png + scene.blend = COMPLETED ✅
Has concept.md but no render = IN_PROGRESS or FAILED ⏳
Concept > 30 minutes old = FAILED ❌
```

### 3. New REST Endpoints

#### List All Sessions
```bash
GET /api/sessions
GET /api/sessions?status=completed
GET /api/sessions?limit=20
```

Response:
```json
{
  "sessions": [
    {
      "id": "session-uuid",
      "status": "completed",
      "prompt": "...",
      "created_at": "...",
      "result": {...}
    }
  ],
  "total": 15
}
```

#### Get Specific Session
```bash
GET /api/session/{session_id}
```

### 4. Frontend Integration Guide

#### Option A: Polling (Recommended)
Poll the sessions endpoint every 3-5 seconds while generation is active:

```javascript
// Poll for session updates
const pollSession = async (sessionId) => {
  const response = await fetch(`/api/session/${sessionId}`);
  const data = await response.json();

  if (data.status === 'completed') {
    // Show download buttons
    showDownloadButtons(sessionId);
    stopPolling();
  } else if (data.status === 'failed') {
    // Show error
    showError(data.result?.error);
    stopPolling();
  }

  return data;
};

// Start polling
const intervalId = setInterval(() => pollSession(sessionId), 3000);
```

#### Option B: SocketIO + Polling Fallback
Use SocketIO for real-time, but poll as backup:

```javascript
// Listen for SocketIO events
socket.on('complete', (data) => {
  handleCompletion(data);
  stopPolling();
});

// But also poll in case SocketIO fails
const intervalId = setInterval(() => pollSession(sessionId), 5000);
```

#### Option C: List Recent Sessions
On page load, check for any completed sessions:

```javascript
// On page load or reconnect
const loadRecentSessions = async () => {
  const response = await fetch('/api/sessions?status=completed&limit=10');
  const { sessions } = await response.json();

  // Show completed sessions in UI
  sessions.forEach(session => {
    if (session.result?.success) {
      addToDownloadsList(session);
    }
  });
};
```

## Benefits

### ✅ Survives Backend Restarts
Sessions persist to disk and are recovered on startup

### ✅ Self-Healing
System detects completion from files, even if state was corrupted

### ✅ No Lost Sessions
Completed work is never lost - always recoverable from disk

### ✅ Better UX
Frontend can poll and discover completed sessions after reconnection

### ✅ Debugging
`session_state.json` files make it easy to debug stuck sessions

## Testing the Fix

### 1. Test State Persistence
```bash
# Start backend
python3 start_api.py

# Submit a generation
curl -X POST http://localhost:5002/api/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "test scene", "agents": []}'

# Check state file exists
ls output/{session-id}/session_state.json
```

### 2. Test Recovery
```bash
# Kill backend
pkill -f start_api

# Verify files exist
ls output/e4ea3146-4274-4f0b-bf89-55c579db741c/

# Restart backend
python3 start_api.py

# Check session was recovered
curl http://localhost:5002/api/sessions
```

### 3. Test Frontend Polling
```bash
# Get session status
curl http://localhost:5002/api/session/e4ea3146-4274-4f0b-bf89-55c579db741c

# Should show:
# "status": "completed"
# "result": { "success": true, ... }
```

## Migration Notes

**Existing sessions** will be detected and recovered automatically on next backend start. The system will:
1. Find all session directories in `output/`
2. Look for render files and blend files
3. Create state files for any missing ones
4. Mark them as "recovered_from_disk": true

**No data loss** - All your existing generated scenes are preserved and will appear in the sessions list.

## Summary

**Before:** Session state only in RAM → Lost on restart → Frontend stuck
**After:** State persisted to disk → Recovered on startup → Frontend can poll → Never stuck ✅
