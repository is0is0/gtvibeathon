"""Configuration management for Voxel."""

from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    """Main configuration for Voxel."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # API Configuration
    anthropic_api_key: str = Field(default="", description="Anthropic API key")
    openai_api_key: str = Field(default="", description="OpenAI API key")
    ai_provider: Literal["anthropic", "openai"] = Field(
        default="anthropic", description="AI provider to use"
    )
    ai_model: str = Field(
        default="claude-3-5-sonnet-20241022", description="AI model to use"
    )

    # Blender Configuration
    blender_path: Path = Field(
        default=Path("/Applications/Blender.app/Contents/MacOS/Blender"),
        description="Path to Blender executable",
    )

    # Output Configuration
    output_dir: Path = Field(default=Path("./output"), description="Output directory")
    render_samples: int = Field(default=128, description="Number of render samples", ge=1)
    render_engine: Literal["CYCLES", "EEVEE"] = Field(
        default="CYCLES", description="Render engine"
    )

    # Agent Configuration
    max_iterations: int = Field(
        default=3, description="Maximum refinement iterations", ge=1, le=10
    )
    enable_reviewer: bool = Field(default=True, description="Enable reviewer agent")
    enable_animation: bool = Field(default=True, description="Enable animation generation")
    auto_refine: bool = Field(default=True, description="Auto-refine based on reviews")
    agent_temperature: float = Field(
        default=0.7, description="Temperature for AI agents", ge=0.0, le=2.0
    )
    agent_max_tokens: int = Field(
        default=4000, description="Max tokens for agent responses", ge=100
    )

    # Animation Configuration
    animation_frames: int = Field(
        default=180, description="Default animation length in frames", ge=24, le=1000
    )
    animation_fps: int = Field(
        default=24, description="Animation framerate", ge=12, le=60
    )

    # Database Configuration
    database_url: str = Field(
        default="sqlite:///database/voxel.db", description="Database connection URL"
    )
    database_echo: bool = Field(
        default=False, description="Enable SQLAlchemy query logging"
    )

    # Logging
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = Field(
        default="INFO", description="Logging level"
    )
    log_file: Path = Field(
        default=Path("./logs/voxel.log"), description="Log file path"
    )

    def validate_paths(self) -> None:
        """Validate that required paths exist."""
        if not self.blender_path.exists():
            raise ValueError(f"Blender executable not found at {self.blender_path}")

        # Create output and log directories if they don't exist
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

    def validate_api_keys(self) -> None:
        """Validate that required API keys are set."""
        if self.ai_provider == "anthropic" and not self.anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY must be set when using anthropic provider")
        if self.ai_provider == "openai" and not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY must be set when using openai provider")
