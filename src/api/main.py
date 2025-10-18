"""
API Main
--------
FastAPI backend for Framer frontend integration.

Provides RESTful endpoints and WebSocket support for real-time updates.
"""

from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, WebSocket, WebSocketDisconnect, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Optional
import asyncio
from pathlib import Path
import uuid
from datetime import datetime, timedelta
import json

from api.schemas import *
from api.database import DatabaseManager
from api.auth import AuthManager
from api.storage import StorageManager
from api.websocket_manager import WebSocketManager
from orchestrator.async_scene_orchestrator import AsyncSceneOrchestrator
from utils.logger import get_logger, setup_logging

# Initialize logging
setup_logging(level="INFO", console=True)
logger = get_logger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Voxel Weaver API",
    description="AI-Powered 3D Scene Generator API for Framer Frontend Integration",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS middleware for Framer frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://*.framer.app",
        "https://*.framer.website",
        "http://localhost:*",  # For local development
        "*"  # For development - restrict in production!
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize managers
db = DatabaseManager()
auth = AuthManager()
storage = StorageManager()
ws_manager = WebSocketManager()
security = HTTPBearer()

# ============================================================================
# DEPENDENCIES
# ============================================================================

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> UserProfile:
    """Get current authenticated user."""
    token = credentials.credentials
    user = await auth.verify_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    return user


# ============================================================================
# HEALTH CHECK
# ============================================================================

@app.get("/api/health", response_model=HealthCheck, tags=["System"])
async def health_check():
    """Check API health status."""
    return HealthCheck(
        status="healthy",
        version="2.0.0",
        services={
            "database": "up",
            "storage": "up",
            "orchestrator": "up"
        }
    )


# ============================================================================
# AUTHENTICATION
# ============================================================================

@app.post("/api/auth/signup", response_model=AuthToken, tags=["Authentication"])
async def sign_up(user_data: UserSignUp):
    """Register a new user account."""
    try:
        # Check if user exists
        existing_user = await db.get_user_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Create user
        user = await db.create_user(
            email=user_data.email,
            password=user_data.password,
            full_name=user_data.full_name
        )

        # Generate token
        token = auth.create_token(user.user_id)

        return AuthToken(
            access_token=token,
            expires_in=3600 * 24 * 30,  # 30 days
            user=user
        )

    except Exception as e:
        logger.error(f"Signup failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create account"
        )


@app.post("/api/auth/signin", response_model=AuthToken, tags=["Authentication"])
async def sign_in(credentials: UserSignIn):
    """Sign in to user account."""
    user = await db.verify_user_credentials(credentials.email, credentials.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    token = auth.create_token(user.user_id)

    return AuthToken(
        access_token=token,
        expires_in=3600 * 24 * 30,  # 30 days
        user=user
    )


@app.get("/api/auth/me", response_model=UserProfile, tags=["Authentication"])
async def get_current_user_profile(user: UserProfile = Depends(get_current_user)):
    """Get current user profile."""
    return user


# ============================================================================
# AGENTS
# ============================================================================

@app.get("/api/agents", response_model=AgentListResponse, tags=["Agents"])
async def list_agents():
    """List all available agents with their capabilities."""
    agents = [
        AgentInfo(
            agent_type=AgentType.PROMPT_INTERPRETER,
            name="Prompt Interpreter",
            description="Analyzes natural language and extracts scene structure",
            capabilities=[
                "Natural language understanding",
                "Object extraction",
                "Relationship detection",
                "Style classification",
                "Mood analysis"
            ],
            configurable_options={}
        ),
        AgentInfo(
            agent_type=AgentType.TEXTURE_SYNTH,
            name="Texture Synthesizer",
            description="Creates advanced materials and textures",
            capabilities=[
                "PBR materials",
                "Procedural textures",
                "50+ shader nodes",
                "UV optimization"
            ],
            configurable_options={
                "material_complexity": ["simple", "standard", "advanced"],
                "use_pbr": bool
            }
        ),
        AgentInfo(
            agent_type=AgentType.LIGHTING_AI,
            name="Lighting AI",
            description="Intelligent scene lighting and atmosphere",
            capabilities=[
                "HDRI environments",
                "Three-point lighting",
                "Cinematic setups",
                "Auto-placement"
            ],
            configurable_options={
                "lighting_mode": ["realistic", "studio", "stylized", "cinematic"],
                "use_hdri": bool,
                "num_lights": {"min": 1, "max": 10}
            }
        ),
        AgentInfo(
            agent_type=AgentType.SPATIAL_VALIDATOR,
            name="Spatial Validator",
            description="Physics-based validation and collision detection",
            capabilities=[
                "Collision detection",
                "Gravity validation",
                "Auto-fixing",
                "Relationship validation"
            ],
            configurable_options={
                "enable_validation": bool,
                "auto_fix_issues": bool
            }
        ),
        AgentInfo(
            agent_type=AgentType.RENDER_DIRECTOR,
            name="Render Director",
            description="Camera setup and render configuration",
            capabilities=[
                "8 camera presets",
                "Quality optimization",
                "Multi-format export",
                "Depth of field"
            ],
            configurable_options={
                "camera_angle": ["perspective", "front", "top", "wide", "closeup"],
                "quality": ["draft", "preview", "final", "ultra"],
                "enable_dof": bool
            }
        ),
        AgentInfo(
            agent_type=AgentType.ASSET_REGISTRY,
            name="Asset Registry",
            description="Asset library management",
            capabilities=[
                "Asset cataloging",
                "Search and filter",
                "Version control",
                "Metadata management"
            ],
            configurable_options={}
        )
    ]

    return AgentListResponse(
        agents=agents,
        total=len(agents)
    )


# ============================================================================
# FILE UPLOAD
# ============================================================================

@app.post("/api/upload", response_model=FileUploadResponse, tags=["Files"])
async def upload_context_file(
    file: UploadFile = File(...),
    context_type: ContextType = ContextType.IMAGE,
    agent_target: Optional[AgentType] = None,
    user: UserProfile = Depends(get_current_user)
):
    """Upload context file (3D model, image, video, text, code)."""
    try:
        # Generate file ID
        file_id = str(uuid.uuid4())

        # Save file
        file_path = await storage.save_file(
            file_id=file_id,
            file=file,
            user_id=user.user_id,
            context_type=context_type
        )

        # Get file info
        file_size = file_path.stat().st_size

        # Store metadata in database
        await db.save_context_file(
            file_id=file_id,
            user_id=user.user_id,
            filename=file.filename,
            context_type=context_type,
            file_path=str(file_path),
            size=file_size,
            agent_target=agent_target
        )

        # Generate URL
        file_url = f"/api/files/{file_id}"

        return FileUploadResponse(
            file_id=file_id,
            filename=file.filename,
            type=context_type,
            size=file_size,
            url=file_url,
            uploaded_at=datetime.now()
        )

    except Exception as e:
        logger.error(f"File upload failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload file"
        )


@app.get("/api/files/{file_id}", tags=["Files"])
async def download_file(
    file_id: str,
    user: UserProfile = Depends(get_current_user)
):
    """Download a context file."""
    file_info = await db.get_context_file(file_id, user.user_id)

    if not file_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )

    file_path = Path(file_info["file_path"])

    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found on storage"
        )

    return FileResponse(
        path=file_path,
        filename=file_info["filename"],
        media_type="application/octet-stream"
    )


# ============================================================================
# SCENE GENERATION
# ============================================================================

@app.post("/api/generate", response_model=GenerationResponse, tags=["Generation"])
async def generate_scene(
    request: GenerationRequest,
    user: UserProfile = Depends(get_current_user)
):
    """
    Generate 3D scene from prompt.

    This endpoint initiates scene generation and returns immediately.
    Connect to the WebSocket URL to receive real-time progress updates.
    """
    try:
        # Create project
        project_id = str(uuid.uuid4())

        # Get context files
        context_files = []
        for file_id in request.context_files:
            file_info = await db.get_context_file(file_id, user.user_id)
            if file_info:
                context_files.append(ContextFile(**file_info))

        # Save project to database
        await db.create_project(
            project_id=project_id,
            user_id=user.user_id,
            name=request.project_name or f"Scene from '{request.prompt[:30]}...'",
            prompt=request.prompt,
            mode=request.mode,
            settings=request.dict(exclude={"prompt", "project_name", "tags"}),
            tags=request.tags,
            context_files=[cf.dict() for cf in context_files]
        )

        # Start generation in background
        asyncio.create_task(
            run_generation(project_id, request, context_files, user.user_id)
        )

        # Return immediately with WebSocket URL
        return GenerationResponse(
            project_id=project_id,
            status=ProjectStatus.PENDING,
            message="Generation started. Connect to WebSocket for real-time updates.",
            websocket_url=f"/api/ws/generation/{project_id}",
            created_at=datetime.now()
        )

    except Exception as e:
        logger.error(f"Failed to start generation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


async def run_generation(
    project_id: str,
    request: GenerationRequest,
    context_files: List[ContextFile],
    user_id: str
):
    """Background task to run scene generation."""
    try:
        # Update status
        await db.update_project_status(project_id, ProjectStatus.PROCESSING)
        await ws_manager.send_update(project_id, {
            "type": "stage_update",
            "project_id": project_id,
            "data": {
                "stage": "Initializing",
                "status": "processing",
                "message": "Starting scene generation..."
            }
        })

        # Determine settings based on mode
        if request.mode == GenerationMode.AUTOMATIC:
            settings = request.automatic_settings or AutomaticSettings()
            config = {
                "style": settings.style,
                "quality": settings.quality,
                "validate": True,
                "format": "blend"
            }
        else:
            settings = request.customizable_settings or CustomizableSettings()
            config = settings.dict()

        # Create orchestrator
        orchestrator = AsyncSceneOrchestrator(config={
            "output_dir": f"output/projects/{project_id}",
            "quality": config.get("quality", "preview")
        })

        # Run generation with progress callbacks
        result = await orchestrator.generate_complete_scene(
            prompt=request.prompt,
            style=config.get("style", "realistic"),
            validate=config.get("enable_validation", True),
            output_format=config.get("export_format", "blend")
        )

        if result.get("success"):
            # Collect generated assets
            assets = await collect_assets(project_id, result)

            # Update project with assets
            await db.update_project_completion(
                project_id=project_id,
                status=ProjectStatus.COMPLETED,
                assets=assets,
                statistics=result.get("metadata", {})
            )

            # Send completion via WebSocket
            await ws_manager.send_update(project_id, {
                "type": "completed",
                "project_id": project_id,
                "data": {
                    "assets": [asset.dict() for asset in assets],
                    "message": "Generation completed successfully!"
                }
            })

        else:
            # Generation failed
            await db.update_project_status(
                project_id,
                ProjectStatus.FAILED,
                error_message=result.get("error")
            )

            await ws_manager.send_update(project_id, {
                "type": "error",
                "project_id": project_id,
                "data": {
                    "error": result.get("error", "Unknown error")
                }
            })

    except Exception as e:
        logger.error(f"Generation failed for project {project_id}: {e}", exc_info=True)

        await db.update_project_status(
            project_id,
            ProjectStatus.FAILED,
            error_message=str(e)
        )

        await ws_manager.send_update(project_id, {
            "type": "error",
            "project_id": project_id,
            "data": {"error": str(e)}
        })


async def collect_assets(project_id: str, result: Dict[str, Any]) -> List[GeneratedAsset]:
    """Collect generated assets from result."""
    assets = []

    output_path = result.get("output_path")
    if output_path and Path(output_path).exists():
        file_path = Path(output_path)
        assets.append(GeneratedAsset(
            asset_id=str(uuid.uuid4()),
            name=file_path.name,
            type="scene",
            format=file_path.suffix.lstrip("."),
            size=file_path.stat().st_size,
            url=f"/api/projects/{project_id}/assets/{file_path.name}",
            thumbnail_url=None
        ))

    render_path = result.get("render_path")
    if render_path and Path(render_path).exists():
        file_path = Path(render_path)
        assets.append(GeneratedAsset(
            asset_id=str(uuid.uuid4()),
            name=file_path.name,
            type="render",
            format=file_path.suffix.lstrip("."),
            size=file_path.stat().st_size,
            url=f"/api/projects/{project_id}/assets/{file_path.name}",
            thumbnail_url=f"/api/projects/{project_id}/assets/{file_path.name}"
        ))

    return assets


# ============================================================================
# WEBSOCKET
# ============================================================================

@app.websocket("/api/ws/generation/{project_id}")
async def websocket_endpoint(websocket: WebSocket, project_id: str):
    """WebSocket endpoint for real-time generation updates."""
    await ws_manager.connect(websocket, project_id)

    try:
        while True:
            # Keep connection alive and listen for client messages
            data = await websocket.receive_text()

            # Handle client messages (e.g., cancel request)
            message = json.loads(data)
            if message.get("action") == "cancel":
                await db.update_project_status(project_id, ProjectStatus.CANCELLED)
                await ws_manager.send_update(project_id, {
                    "type": "cancelled",
                    "project_id": project_id,
                    "data": {"message": "Generation cancelled by user"}
                })
                break

    except WebSocketDisconnect:
        ws_manager.disconnect(project_id)
        logger.info(f"WebSocket disconnected for project {project_id}")


# ============================================================================
# PROJECTS
# ============================================================================

@app.get("/api/projects", response_model=ProjectListResponse, tags=["Projects"])
async def list_projects(
    page: int = 1,
    page_size: int = 20,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    status: Optional[ProjectStatus] = None,
    user: UserProfile = Depends(get_current_user)
):
    """List user's projects with pagination."""
    projects, total = await db.get_user_projects(
        user_id=user.user_id,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order,
        status_filter=status
    )

    total_pages = (total + page_size - 1) // page_size

    return ProjectListResponse(
        projects=projects,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_previous=page > 1
    )


@app.get("/api/projects/{project_id}", response_model=ProjectDetails, tags=["Projects"])
async def get_project_details(
    project_id: str,
    user: UserProfile = Depends(get_current_user)
):
    """Get detailed information about a project."""
    project = await db.get_project(project_id, user.user_id)

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    return project


@app.delete("/api/projects/{project_id}", tags=["Projects"])
async def delete_project(
    project_id: str,
    user: UserProfile = Depends(get_current_user)
):
    """Delete a project and all its assets."""
    success = await db.delete_project(project_id, user.user_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    # Also delete files
    await storage.delete_project_files(project_id)

    return {"message": "Project deleted successfully"}


# ============================================================================
# DOWNLOADS
# ============================================================================

@app.post("/api/download", response_model=DownloadResponse, tags=["Downloads"])
async def create_download(
    request: DownloadRequest,
    project_id: str,
    user: UserProfile = Depends(get_current_user)
):
    """Create download link for project assets."""
    # Verify project ownership
    project = await db.get_project(project_id, user.user_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    # Generate download link
    download_url = await storage.create_download_link(
        project_id=project_id,
        asset_ids=request.asset_ids,
        format=request.format
    )

    return DownloadResponse(
        download_url=download_url,
        expires_at=datetime.now() + timedelta(hours=24),
        size=0  # Calculate actual size
    )


@app.get("/api/projects/{project_id}/assets/{filename}", tags=["Downloads"])
async def download_asset(
    project_id: str,
    filename: str,
    user: UserProfile = Depends(get_current_user)
):
    """Download a specific asset file."""
    # Verify ownership
    project = await db.get_project(project_id, user.user_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    file_path = Path(f"output/projects/{project_id}") / filename

    if not file_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found")

    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/octet-stream"
    )


# ============================================================================
# STATISTICS
# ============================================================================

@app.get("/api/statistics", response_model=UserStatistics, tags=["Statistics"])
async def get_user_statistics(user: UserProfile = Depends(get_current_user)):
    """Get user account statistics."""
    stats = await db.get_user_statistics(user.user_id)
    return stats


# ============================================================================
# RUN APP
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
