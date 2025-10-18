# Framer Frontend Integration Guide

Complete guide for integrating the Voxel API with a Framer frontend.

## Table of Contents

- [Overview](#overview)
- [API Endpoints](#api-endpoints)
- [Authentication Flow](#authentication-flow)
- [Generation Workflow](#generation-workflow)
- [WebSocket Real-Time Updates](#websocket-real-time-updates)
- [File Upload](#file-upload)
- [Project Management](#project-management)
- [Example Code](#example-code)
- [Framer Setup](#framer-setup)

---

## Overview

The Voxel API provides a complete backend for AI-powered 3D scene generation. This guide shows how to integrate it with a Framer frontend.

### Base URL

```
http://localhost:8000/api
```

For production, replace with your deployed API URL.

### CORS Configuration

The API is pre-configured to accept requests from:
- `https://*.framer.app`
- `https://*.framer.website`
- `http://localhost:*` (development)

---

## API Endpoints

### Authentication

#### Sign Up
```http
POST /api/auth/signup
Content-Type: application/json

{
  "email": "user@example.com",
  "username": "username",
  "password": "SecurePassword123!",
  "subscription_tier": "free"
}
```

**Response:**
```json
{
  "user_id": "usr_abc123",
  "email": "user@example.com",
  "username": "username",
  "subscription_tier": "free",
  "created_at": "2025-01-15T10:30:00Z",
  "token": {
    "access_token": "eyJhbGc...",
    "refresh_token": "eyJhbGc...",
    "token_type": "bearer",
    "expires_in": 3600
  }
}
```

#### Sign In
```http
POST /api/auth/signin
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

**Response:** Same as sign up

#### Get Current User
```http
GET /api/auth/me
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "user_id": "usr_abc123",
  "email": "user@example.com",
  "username": "username",
  "subscription_tier": "free",
  "created_at": "2025-01-15T10:30:00Z",
  "total_generations": 42,
  "total_downloads": 38
}
```

---

### Agents

#### List Available Agents
```http
GET /api/agents
```

**Response:**
```json
{
  "agents": [
    {
      "agent_type": "concept",
      "name": "Concept Agent",
      "description": "Interprets prompts and generates detailed scene concepts",
      "capabilities": [
        "Natural language understanding",
        "Scene composition planning",
        "Style interpretation"
      ],
      "accepted_context": ["text", "image"]
    },
    {
      "agent_type": "builder",
      "name": "Builder Agent",
      "description": "Creates 3D geometry from concepts",
      "capabilities": [
        "Mesh modeling",
        "Modifier application",
        "Complex geometry"
      ],
      "accepted_context": ["model_3d", "image"]
    },
    // ... other agents
  ]
}
```

---

### File Upload

#### Upload Context File
```http
POST /api/upload
Authorization: Bearer <access_token>
Content-Type: multipart/form-data

file: <binary data>
agent_type: "builder"
context_type: "model_3d"
project_id: "proj_123" (optional)
```

**Response:**
```json
{
  "file_id": "file_xyz789",
  "filename": "reference_model.obj",
  "file_size": 1024000,
  "context_type": "model_3d",
  "agent_type": "builder",
  "url": "/api/files/file_xyz789",
  "uploaded_at": "2025-01-15T10:35:00Z"
}
```

**Supported File Types:**
- **3D Models:** `.obj`, `.fbx`, `.gltf`, `.glb`, `.blend`
- **Images:** `.png`, `.jpg`, `.jpeg`, `.webp`
- **Videos:** `.mp4`, `.mov`, `.avi`
- **Text:** `.txt`, `.md`
- **Code:** `.py`, `.js`, `.json`

---

### Generation

#### Start Generation
```http
POST /api/generate
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "prompt": "A cozy cyberpunk cafe at sunset with neon lights",
  "agents": [
    {"agent_type": "concept"},
    {"agent_type": "builder"},
    {"agent_type": "texture"},
    {"agent_type": "lighting"},
    {"agent_type": "render"}
  ],
  "context_files": ["file_xyz789"],
  "mode": "automatic",
  "automatic_settings": {
    "style": "realistic",
    "quality": "high"
  }
}
```

**Response:**
```json
{
  "project_id": "proj_abc123",
  "status": "pending",
  "websocket_url": "ws://localhost:8000/api/ws/generation/proj_abc123",
  "estimated_time": 45.0,
  "message": "Generation started. Connect to WebSocket for real-time updates."
}
```

#### Customizable Mode Example
```json
{
  "prompt": "A mystical forest with glowing crystals",
  "agents": [
    {"agent_type": "concept"},
    {"agent_type": "builder"},
    {"agent_type": "texture"},
    {"agent_type": "render"}
  ],
  "mode": "customizable",
  "customizable_settings": {
    "geometry_detail": "high",
    "texture_resolution": 2048,
    "lighting_mode": "cinematic",
    "camera_angle": "perspective",
    "render_samples": 256,
    "render_engine": "cycles",
    "enable_validation": true,
    "export_formats": ["png", "gltf", "blend"]
  }
}
```

---

### Projects

#### List Projects
```http
GET /api/projects?skip=0&limit=20&status=completed
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "projects": [
    {
      "project_id": "proj_abc123",
      "prompt": "A cozy cyberpunk cafe...",
      "status": "completed",
      "preview_url": "/api/projects/proj_abc123/assets/preview.png",
      "created_at": "2025-01-15T10:40:00Z",
      "completed_at": "2025-01-15T10:41:30Z"
    }
  ],
  "total": 42,
  "skip": 0,
  "limit": 20
}
```

#### Get Project Details
```http
GET /api/projects/{project_id}
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "project_id": "proj_abc123",
  "prompt": "A cozy cyberpunk cafe at sunset...",
  "agents": ["concept", "builder", "texture", "lighting", "render"],
  "settings": {
    "mode": "automatic",
    "style": "realistic",
    "quality": "high"
  },
  "status": "completed",
  "progress": 1.0,
  "current_stage": "render",
  "assets": [
    {
      "asset_type": "render",
      "filename": "final_render.png",
      "url": "/api/projects/proj_abc123/assets/final_render.png",
      "file_size": 2048000,
      "preview_url": "/api/projects/proj_abc123/assets/final_render.png",
      "created_at": "2025-01-15T10:41:30Z"
    },
    {
      "asset_type": "model",
      "filename": "scene.gltf",
      "url": "/api/projects/proj_abc123/assets/scene.gltf",
      "file_size": 5120000,
      "created_at": "2025-01-15T10:41:30Z"
    },
    {
      "asset_type": "blend_file",
      "filename": "scene.blend",
      "url": "/api/projects/proj_abc123/assets/scene.blend",
      "file_size": 10240000,
      "created_at": "2025-01-15T10:41:30Z"
    }
  ],
  "stages": [
    {
      "stage": "concept",
      "status": "completed",
      "progress": 1.0,
      "message": "Concept generated successfully"
    },
    {
      "stage": "builder",
      "status": "completed",
      "progress": 1.0,
      "message": "Geometry created: 15 objects"
    }
    // ... other stages
  ],
  "created_at": "2025-01-15T10:40:00Z",
  "updated_at": "2025-01-15T10:41:30Z",
  "completed_at": "2025-01-15T10:41:30Z",
  "estimated_time": 45.0,
  "error_message": null
}
```

#### Delete Project
```http
DELETE /api/projects/{project_id}
Authorization: Bearer <access_token>
```

---

### Downloads

#### Create Download Link
```http
POST /api/download
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "project_id": "proj_abc123",
  "filename": "final_render.png"
}
```

**Response:**
```json
{
  "download_url": "http://localhost:8000/api/download/secure_token_abc123xyz",
  "expires_at": "2025-01-15T11:40:00Z",
  "filename": "final_render.png"
}
```

#### Direct Asset Download
```http
GET /api/projects/{project_id}/assets/{filename}
Authorization: Bearer <access_token>
```

Returns the file directly for download.

---

### Statistics

#### Get User Statistics
```http
GET /api/statistics
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "total_projects": 42,
  "completed_projects": 38,
  "processing_projects": 1,
  "failed_projects": 3,
  "total_generations": 42,
  "total_downloads": 156,
  "subscription_tier": "free"
}
```

---

## WebSocket Real-Time Updates

Connect to receive real-time generation progress updates.

### Connection

```javascript
const ws = new WebSocket('ws://localhost:8000/api/ws/generation/proj_abc123');

ws.onopen = () => {
  console.log('Connected to generation updates');
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  handleUpdate(data);
};

ws.onerror = (error) => {
  console.error('WebSocket error:', error);
};

ws.onclose = () => {
  console.log('Disconnected from updates');
};
```

### Message Types

#### Connection Confirmation
```json
{
  "type": "connected",
  "project_id": "proj_abc123",
  "timestamp": "2025-01-15T10:40:00Z",
  "message": "Connected to generation updates"
}
```

#### Stage Update
```json
{
  "type": "stage_update",
  "project_id": "proj_abc123",
  "stage": "builder",
  "status": "processing",
  "progress": 0.5,
  "message": "Creating 3D geometry...",
  "timestamp": "2025-01-15T10:40:15Z"
}
```

#### Progress Update
```json
{
  "type": "progress",
  "project_id": "proj_abc123",
  "progress": 0.6,
  "current_stage": "texture",
  "message": "Applying materials and textures...",
  "timestamp": "2025-01-15T10:40:30Z"
}
```

#### Asset Generated
```json
{
  "type": "asset_generated",
  "project_id": "proj_abc123",
  "asset": {
    "asset_type": "render",
    "filename": "preview.png",
    "url": "/api/projects/proj_abc123/assets/preview.png",
    "preview_url": "/api/projects/proj_abc123/assets/preview.png"
  },
  "timestamp": "2025-01-15T10:41:00Z"
}
```

#### Generation Complete
```json
{
  "type": "complete",
  "project_id": "proj_abc123",
  "status": "completed",
  "assets": [
    {
      "asset_type": "render",
      "filename": "final_render.png",
      "url": "/api/projects/proj_abc123/assets/final_render.png"
    },
    {
      "asset_type": "model",
      "filename": "scene.gltf",
      "url": "/api/projects/proj_abc123/assets/scene.gltf"
    }
  ],
  "total_time": 45.2,
  "timestamp": "2025-01-15T10:41:30Z",
  "message": "Generation completed successfully!"
}
```

#### Error
```json
{
  "type": "error",
  "project_id": "proj_abc123",
  "status": "failed",
  "error": "Blender script execution failed",
  "stage": "builder",
  "timestamp": "2025-01-15T10:40:45Z"
}
```

#### Heartbeat
```json
{
  "type": "heartbeat",
  "timestamp": "2025-01-15T10:41:00Z"
}
```

---

## Example Code

### React/TypeScript Example

```typescript
import { useState, useEffect } from 'react';

interface GenerationState {
  status: 'idle' | 'connecting' | 'generating' | 'completed' | 'error';
  progress: number;
  currentStage: string;
  message: string;
  assets: any[];
  error?: string;
}

export function useGeneration(projectId: string, accessToken: string) {
  const [state, setState] = useState<GenerationState>({
    status: 'idle',
    progress: 0,
    currentStage: '',
    message: '',
    assets: [],
  });

  useEffect(() => {
    if (!projectId) return;

    setState(prev => ({ ...prev, status: 'connecting' }));

    const ws = new WebSocket(
      `ws://localhost:8000/api/ws/generation/${projectId}`
    );

    ws.onopen = () => {
      setState(prev => ({ ...prev, status: 'generating' }));
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);

      switch (data.type) {
        case 'stage_update':
          setState(prev => ({
            ...prev,
            currentStage: data.stage,
            message: data.message || `${data.stage}: ${data.status}`,
          }));
          break;

        case 'progress':
          setState(prev => ({
            ...prev,
            progress: data.progress,
            currentStage: data.current_stage || prev.currentStage,
            message: data.message || prev.message,
          }));
          break;

        case 'asset_generated':
          setState(prev => ({
            ...prev,
            assets: [...prev.assets, data.asset],
          }));
          break;

        case 'complete':
          setState(prev => ({
            ...prev,
            status: 'completed',
            progress: 1,
            assets: data.assets,
            message: data.message,
          }));
          break;

        case 'error':
          setState(prev => ({
            ...prev,
            status: 'error',
            error: data.error,
            message: data.error,
          }));
          break;
      }
    };

    ws.onerror = (error) => {
      setState(prev => ({
        ...prev,
        status: 'error',
        error: 'WebSocket connection failed',
      }));
    };

    ws.onclose = () => {
      if (state.status === 'generating') {
        setState(prev => ({
          ...prev,
          status: 'error',
          error: 'Connection lost',
        }));
      }
    };

    return () => {
      ws.close();
    };
  }, [projectId]);

  return state;
}
```

### Starting a Generation

```typescript
async function startGeneration(
  prompt: string,
  accessToken: string
): Promise<string> {
  const response = await fetch('http://localhost:8000/api/generate', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${accessToken}`,
    },
    body: JSON.stringify({
      prompt,
      agents: [
        { agent_type: 'concept' },
        { agent_type: 'builder' },
        { agent_type: 'texture' },
        { agent_type: 'lighting' },
        { agent_type: 'render' },
      ],
      mode: 'automatic',
      automatic_settings: {
        style: 'realistic',
        quality: 'high',
      },
    }),
  });

  const data = await response.json();
  return data.project_id;
}
```

### File Upload with Progress

```typescript
async function uploadContextFile(
  file: File,
  agentType: string,
  contextType: string,
  accessToken: string,
  onProgress?: (progress: number) => void
): Promise<string> {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('agent_type', agentType);
  formData.append('context_type', contextType);

  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();

    xhr.upload.onprogress = (e) => {
      if (e.lengthComputable && onProgress) {
        onProgress((e.loaded / e.total) * 100);
      }
    };

    xhr.onload = () => {
      if (xhr.status === 200) {
        const data = JSON.parse(xhr.responseText);
        resolve(data.file_id);
      } else {
        reject(new Error('Upload failed'));
      }
    };

    xhr.onerror = () => reject(new Error('Upload failed'));

    xhr.open('POST', 'http://localhost:8000/api/upload');
    xhr.setRequestHeader('Authorization', `Bearer ${accessToken}`);
    xhr.send(formData);
  });
}
```

---

## Framer Setup

### 1. Create Code Components

In Framer, create these reusable code components:

#### AuthProvider Component
```typescript
import { createContext, useContext, useState } from 'react';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);

  const signIn = async (email, password) => {
    const response = await fetch('http://localhost:8000/api/auth/signin', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });
    const data = await response.json();
    setUser(data);
    setToken(data.token.access_token);
    return data;
  };

  const signOut = () => {
    setUser(null);
    setToken(null);
  };

  return (
    <AuthContext.Provider value={{ user, token, signIn, signOut }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
```

#### GenerationForm Component
```typescript
import { useState } from 'react';
import { useAuth } from './AuthProvider';

export function GenerationForm({ onGenerate }) {
  const { token } = useAuth();
  const [prompt, setPrompt] = useState('');
  const [selectedAgents, setSelectedAgents] = useState([
    'concept', 'builder', 'texture', 'lighting', 'render'
  ]);

  const handleSubmit = async (e) => {
    e.preventDefault();

    const response = await fetch('http://localhost:8000/api/generate', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify({
        prompt,
        agents: selectedAgents.map(type => ({ agent_type: type })),
        mode: 'automatic',
        automatic_settings: {
          style: 'realistic',
          quality: 'high',
        },
      }),
    });

    const data = await response.json();
    onGenerate(data.project_id);
  };

  return (
    <form onSubmit={handleSubmit}>
      <textarea
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
        placeholder="Describe your 3D scene..."
      />
      {/* Agent selection checkboxes */}
      <button type="submit">Generate</button>
    </form>
  );
}
```

#### ProgressDisplay Component
```typescript
import { useGeneration } from './useGeneration';

export function ProgressDisplay({ projectId, token }) {
  const state = useGeneration(projectId, token);

  return (
    <div>
      <h3>Status: {state.status}</h3>
      <progress value={state.progress} max={1} />
      <p>{state.message}</p>

      {state.status === 'completed' && (
        <div>
          <h4>Generated Assets:</h4>
          {state.assets.map(asset => (
            <a key={asset.filename} href={asset.url} download>
              {asset.filename}
            </a>
          ))}
          <button onClick={() => openBlender(projectId)}>
            Open in Blender
          </button>
        </div>
      )}
    </div>
  );
}
```

### 2. Page Structure

Create these pages in Framer:

1. **Landing Page** (`/`)
   - Hero section with example renders
   - Features overview
   - CTA to sign up

2. **Sign In/Sign Up** (`/auth`)
   - Auth forms
   - Social login (optional)

3. **Dashboard** (`/dashboard`)
   - Project grid/list
   - Statistics
   - Quick generate button

4. **Generate** (`/generate`)
   - Prompt input
   - Agent selection
   - Context file uploads
   - Settings (automatic/customizable)

5. **Project Details** (`/project/[id]`)
   - Project information
   - Asset downloads
   - Preview images
   - "Open in Blender" button

6. **History** (`/history`)
   - All past projects
   - Filters (status, date)
   - Pagination

### 3. Environment Variables

Add to your Framer project settings:

```
VOXEL_API_URL=http://localhost:8000/api
VOXEL_WS_URL=ws://localhost:8000/api/ws
```

For production:
```
VOXEL_API_URL=https://api.yourdomain.com/api
VOXEL_WS_URL=wss://api.yourdomain.com/api/ws
```

---

## Complete Flow Example

### User Journey

1. **User lands on site** → Shows hero with example projects
2. **User signs up** → POST `/api/auth/signup` → Receives token
3. **User navigates to generate** → Shows prompt box and agent selection
4. **User uploads reference files** → POST `/api/upload` for each file
5. **User submits prompt** → POST `/api/generate` → Receives `project_id`
6. **Frontend connects to WebSocket** → `ws://api/ws/generation/{project_id}`
7. **User sees real-time progress** → Updates from WebSocket messages
8. **Generation completes** → Shows "Open in Blender" and download buttons
9. **User downloads assets** → GET `/api/projects/{project_id}/assets/{filename}`
10. **User views project history** → GET `/api/projects`

---

## Error Handling

### Common Errors

```typescript
// Unauthorized
{ "detail": "Invalid or expired token" }
// Status: 401

// Validation error
{
  "detail": [
    {
      "loc": ["body", "prompt"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
// Status: 422

// Server error
{ "detail": "Internal server error" }
// Status: 500
```

### Retry Logic

```typescript
async function fetchWithRetry(url, options, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      const response = await fetch(url, options);
      if (response.ok) return response;

      if (response.status >= 500) {
        // Server error, retry
        await new Promise(resolve => setTimeout(resolve, 1000 * (i + 1)));
        continue;
      }

      // Client error, don't retry
      throw new Error(`HTTP ${response.status}`);
    } catch (error) {
      if (i === maxRetries - 1) throw error;
    }
  }
}
```

---

## Testing

### Test Credentials

For development/testing:
```json
{
  "email": "test@voxel.ai",
  "password": "TestPassword123!",
  "username": "testuser"
}
```

### Example Prompts

Test the API with these prompts:
- "A cozy bedroom with warm lighting and wooden furniture"
- "A futuristic cyberpunk cafe with neon signs"
- "A mystical forest with glowing mushrooms and fog"
- "A modern office space with large windows"

---

## Support

For issues or questions:
- GitHub: https://github.com/yourusername/voxel
- Email: support@voxel.ai
- Discord: discord.gg/voxel

---

## License

MIT License - See LICENSE file for details
