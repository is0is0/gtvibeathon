"""
API Schemas
-----------
Pydantic models for API request/response validation.
Designed for seamless Framer frontend integration.
"""

from pydantic import BaseModel, Field, EmailStr, HttpUrl
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime
from enum import Enum


# ============================================================================
# ENUMS
# ============================================================================

class AgentType(str, Enum):
    """Available agent types for selection."""
    PROMPT_INTERPRETER = "prompt_interpreter"
    TEXTURE_SYNTH = "texture_synth"
    LIGHTING_AI = "lighting_ai"
    SPATIAL_VALIDATOR = "spatial_validator"
    RENDER_DIRECTOR = "render_director"
    ASSET_REGISTRY = "asset_registry"


class GenerationMode(str, Enum):
    """Generation mode selection."""
    AUTOMATIC = "automatic"      # AI decides everything
    CUSTOMIZABLE = "customizable"  # User controls settings


class StylePreset(str, Enum):
    """Visual style presets."""
    REALISTIC = "realistic"
    STYLIZED = "stylized"
    MINIMALIST = "minimalist"
    MODERN = "modern"
    VINTAGE = "vintage"
    FUTURISTIC = "futuristic"


class QualityPreset(str, Enum):
    """Render quality presets."""
    DRAFT = "draft"
    PREVIEW = "preview"
    FINAL = "final"
    ULTRA = "ultra"


class ExportFormat(str, Enum):
    """Export format options."""
    BLEND = "blend"
    GLTF = "gltf"
    GLB = "glb"
    FBX = "fbx"
    OBJ = "obj"


class ProjectStatus(str, Enum):
    """Project generation status."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ContextType(str, Enum):
    """Types of context that can be uploaded."""
    MODEL_3D = "model_3d"
    IMAGE = "image"
    VIDEO = "video"
    TEXT = "text"
    CODE = "code"


# ============================================================================
# CONTEXT MODELS
# ============================================================================

class ContextFile(BaseModel):
    """Context file uploaded by user."""
    id: str = Field(..., description="Unique file ID")
    type: ContextType
    filename: str
    url: str = Field(..., description="URL to access the file")
    size: int = Field(..., description="File size in bytes")
    uploaded_at: datetime
    agent_target: Optional[AgentType] = Field(
        None,
        description="Specific agent this context is for, or null for all agents"
    )
    metadata: Dict[str, Any] = Field(default_factory=dict)


# ============================================================================
# AGENT CONFIGURATION
# ============================================================================

class AgentSelection(BaseModel):
    """Agent selection and configuration."""
    agent_type: AgentType
    enabled: bool = True
    custom_config: Optional[Dict[str, Any]] = Field(
        None,
        description="Custom configuration overrides for this agent"
    )


# ============================================================================
# GENERATION SETTINGS
# ============================================================================

class AutomaticSettings(BaseModel):
    """Settings for automatic generation mode."""
    style: Optional[StylePreset] = Field(StylePreset.REALISTIC, description="Visual style preset")
    quality: Optional[QualityPreset] = Field(QualityPreset.PREVIEW, description="Render quality")


class CustomizableSettings(BaseModel):
    """Detailed settings for customizable generation mode."""
    # Style
    style: StylePreset = Field(StylePreset.REALISTIC, description="Visual style")

    # Geometry
    geometry_detail: Literal["low", "medium", "high", "ultra"] = "medium"
    max_objects: int = Field(20, ge=1, le=100, description="Maximum objects in scene")

    # Materials
    material_complexity: Literal["simple", "standard", "advanced"] = "standard"
    use_pbr: bool = Field(True, description="Use physically-based rendering materials")

    # Lighting
    lighting_mode: Literal["realistic", "studio", "stylized", "cinematic"] = "realistic"
    use_hdri: bool = Field(True, description="Use HDRI environment lighting")
    num_lights: int = Field(3, ge=1, le=10, description="Number of lights")

    # Validation
    enable_validation: bool = Field(True, description="Enable spatial validation")
    auto_fix_issues: bool = Field(True, description="Automatically fix validation issues")

    # Rendering
    quality: QualityPreset = QualityPreset.PREVIEW
    resolution: tuple[int, int] = Field((1920, 1080), description="Render resolution (width, height)")
    samples: Optional[int] = Field(None, description="Render samples (null for auto)")
    export_format: ExportFormat = Field(ExportFormat.BLEND, description="Export format")
    render_preview: bool = Field(False, description="Generate preview render image")

    # Camera
    camera_angle: Literal["perspective", "front", "top", "wide", "closeup"] = "perspective"
    enable_dof: bool = Field(False, description="Enable depth of field")


# ============================================================================
# GENERATION REQUEST
# ============================================================================

class GenerationRequest(BaseModel):
    """Request to generate a 3D scene."""
    # Basic prompt
    prompt: str = Field(..., min_length=5, max_length=1000, description="Natural language scene description")

    # Agent selection (optional - defaults to all agents)
    agents: Optional[List[AgentSelection]] = Field(
        None,
        description="Specific agents to use. If null, uses all agents with default config"
    )

    # Context files (optional)
    context_files: List[str] = Field(
        default_factory=list,
        description="List of context file IDs previously uploaded"
    )

    # Generation mode
    mode: GenerationMode = Field(GenerationMode.AUTOMATIC, description="Generation mode")

    # Settings based on mode
    automatic_settings: Optional[AutomaticSettings] = Field(
        None,
        description="Settings for automatic mode (used if mode=automatic)"
    )
    customizable_settings: Optional[CustomizableSettings] = Field(
        None,
        description="Detailed settings for customizable mode (used if mode=customizable)"
    )

    # Project metadata
    project_name: Optional[str] = Field(None, max_length=100, description="Optional project name")
    tags: List[str] = Field(default_factory=list, max_items=10, description="Project tags")


# ============================================================================
# GENERATION RESPONSE
# ============================================================================

class GenerationStageUpdate(BaseModel):
    """Real-time update for generation stage."""
    stage: str = Field(..., description="Current stage name")
    stage_number: int = Field(..., ge=1, description="Stage number")
    total_stages: int = Field(..., ge=1, description="Total number of stages")
    status: Literal["pending", "processing", "completed", "failed"]
    progress: float = Field(..., ge=0.0, le=100.0, description="Progress percentage")
    message: Optional[str] = Field(None, description="Status message")
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None


class GeneratedAsset(BaseModel):
    """Generated asset information."""
    asset_id: str
    name: str
    type: Literal["scene", "model", "texture", "render", "script"]
    format: str = Field(..., description="File format (blend, png, py, etc)")
    size: int = Field(..., description="File size in bytes")
    url: str = Field(..., description="Download URL")
    thumbnail_url: Optional[str] = Field(None, description="Thumbnail preview URL")
    metadata: Dict[str, Any] = Field(default_factory=dict)


class GenerationResponse(BaseModel):
    """Response from generation request."""
    project_id: str = Field(..., description="Unique project ID")
    status: ProjectStatus
    message: str

    # Current stage info (if processing)
    current_stage: Optional[GenerationStageUpdate] = None

    # WebSocket URL for real-time updates
    websocket_url: Optional[str] = Field(
        None,
        description="WebSocket URL to connect for real-time progress updates"
    )

    # Assets (if completed)
    assets: List[GeneratedAsset] = Field(default_factory=list)

    # Timing
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    total_duration_seconds: Optional[float] = None


# ============================================================================
# PROJECT MODELS
# ============================================================================

class ProjectSummary(BaseModel):
    """Summary of a project for list view."""
    project_id: str
    name: str
    prompt: str = Field(..., max_length=200, description="Truncated prompt")
    thumbnail_url: Optional[str] = None
    status: ProjectStatus
    created_at: datetime
    completed_at: Optional[datetime] = None
    tags: List[str] = Field(default_factory=list)
    asset_count: int = Field(..., ge=0, description="Number of generated assets")


class ProjectDetails(BaseModel):
    """Complete project details."""
    project_id: str
    name: str
    prompt: str
    mode: GenerationMode

    # Settings used
    settings: Dict[str, Any] = Field(default_factory=dict, description="Generation settings used")

    # Agents used
    agents_used: List[AgentType] = Field(default_factory=list)

    # Context files
    context_files: List[ContextFile] = Field(default_factory=list)

    # Generation stages
    stages: List[GenerationStageUpdate] = Field(default_factory=list)

    # Assets
    assets: List[GeneratedAsset] = Field(default_factory=list)

    # Status
    status: ProjectStatus
    error_message: Optional[str] = None

    # Metadata
    tags: List[str] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    total_duration_seconds: Optional[float] = None

    # Statistics
    statistics: Dict[str, Any] = Field(
        default_factory=dict,
        description="Scene statistics (object count, vertex count, etc)"
    )


# ============================================================================
# USER MODELS
# ============================================================================

class UserSignUp(BaseModel):
    """User registration request."""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    full_name: str = Field(..., min_length=2, max_length=100)
    agree_to_terms: bool = Field(..., description="Must agree to terms of service")


class UserSignIn(BaseModel):
    """User login request."""
    email: EmailStr
    password: str


class UserProfile(BaseModel):
    """User profile information."""
    user_id: str
    email: EmailStr
    full_name: str
    avatar_url: Optional[HttpUrl] = None
    created_at: datetime

    # Usage statistics
    total_projects: int = Field(..., ge=0)
    total_renders: int = Field(..., ge=0)
    storage_used_mb: float = Field(..., ge=0.0, description="Storage used in MB")

    # Subscription info (for future)
    subscription_tier: Literal["free", "pro", "enterprise"] = "free"
    credits_remaining: Optional[int] = None


class AuthToken(BaseModel):
    """Authentication token response."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int = Field(..., description="Token expiry in seconds")
    user: UserProfile


# ============================================================================
# HISTORY/PAGINATION
# ============================================================================

class PaginationParams(BaseModel):
    """Pagination parameters."""
    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(20, ge=1, le=100, description="Items per page")
    sort_by: Literal["created_at", "updated_at", "name"] = "created_at"
    sort_order: Literal["asc", "desc"] = "desc"


class ProjectListResponse(BaseModel):
    """Paginated list of projects."""
    projects: List[ProjectSummary]
    total: int = Field(..., ge=0, description="Total number of projects")
    page: int
    page_size: int
    total_pages: int = Field(..., ge=0)
    has_next: bool
    has_previous: bool


# ============================================================================
# FILE UPLOAD
# ============================================================================

class FileUploadResponse(BaseModel):
    """Response after file upload."""
    file_id: str
    filename: str
    type: ContextType
    size: int
    url: str
    uploaded_at: datetime


# ============================================================================
# WEBSOCKET MESSAGES
# ============================================================================

class WebSocketMessage(BaseModel):
    """WebSocket message format."""
    type: Literal["stage_update", "progress", "completed", "error", "cancelled"]
    project_id: str
    data: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.now)


# ============================================================================
# ERROR RESPONSES
# ============================================================================

class ErrorResponse(BaseModel):
    """Error response format."""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    timestamp: datetime = Field(default_factory=datetime.now)


# ============================================================================
# HEALTH CHECK
# ============================================================================

class HealthCheck(BaseModel):
    """API health check response."""
    status: Literal["healthy", "degraded", "unhealthy"]
    version: str
    timestamp: datetime = Field(default_factory=datetime.now)
    services: Dict[str, Literal["up", "down"]] = Field(
        default_factory=dict,
        description="Status of dependent services"
    )


# ============================================================================
# AGENT INFO
# ============================================================================

class AgentInfo(BaseModel):
    """Information about an agent."""
    agent_type: AgentType
    name: str
    description: str
    capabilities: List[str]
    configurable_options: Dict[str, Any] = Field(
        default_factory=dict,
        description="Available configuration options"
    )
    default_config: Dict[str, Any] = Field(default_factory=dict)


class AgentListResponse(BaseModel):
    """List of available agents."""
    agents: List[AgentInfo]
    total: int


# ============================================================================
# DOWNLOAD
# ============================================================================

class DownloadRequest(BaseModel):
    """Request to download multiple assets."""
    asset_ids: List[str] = Field(..., min_items=1, description="Asset IDs to download")
    format: Literal["zip", "individual"] = "zip"


class DownloadResponse(BaseModel):
    """Download link response."""
    download_url: str
    expires_at: datetime = Field(..., description="URL expiration time")
    size: int = Field(..., description="Total download size in bytes")


# ============================================================================
# STATISTICS
# ============================================================================

class UserStatistics(BaseModel):
    """User account statistics."""
    total_projects: int
    completed_projects: int
    failed_projects: int
    total_assets: int
    total_renders: int
    storage_used_mb: float
    average_generation_time_seconds: float

    # Recent activity
    projects_this_week: int
    projects_this_month: int

    # Popular settings
    most_used_style: Optional[StylePreset] = None
    most_used_quality: Optional[QualityPreset] = None
