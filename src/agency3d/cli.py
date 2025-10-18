"""Command-line interface for Voxel."""

import logging
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.logging import RichHandler
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from agency3d import Agency3D, Config

app = typer.Typer(
    name="voxel",
    help="AI-powered autonomous 3D scene generation system for Blender",
    add_completion=False,
)

console = Console()


def setup_logging(log_level: str) -> None:
    """Set up logging with rich handler."""
    logging.basicConfig(
        level=log_level,
        format="%(message)s",
        handlers=[RichHandler(console=console, rich_tracebacks=True)],
    )


@app.command()
def create(
    prompt: str = typer.Argument(..., help="Natural language description of the scene"),
    session_name: Optional[str] = typer.Option(
        None, "--session", "-s", help="Custom session name"
    ),
    samples: Optional[int] = typer.Option(
        None, "--samples", help="Number of render samples"
    ),
    engine: Optional[str] = typer.Option(
        None, "--engine", help="Render engine (CYCLES or EEVEE)"
    ),
    review: bool = typer.Option(
        True, "--review/--no-review", help="Enable reviewer agent"
    ),
    max_iterations: Optional[int] = typer.Option(
        None, "--max-iterations", "-i", help="Maximum refinement iterations", min=1, max=10
    ),
    # New enhancement options
    enable_rigging: bool = typer.Option(
        False, "--enable-rigging", help="Enable rigging agent for character/object rigs"
    ),
    enable_compositing: bool = typer.Option(
        False, "--enable-compositing", help="Enable compositing agent for post-processing effects"
    ),
    enable_sequence: bool = typer.Option(
        False, "--enable-sequence", help="Enable sequence agent for video editing"
    ),
    enable_rag: bool = typer.Option(
        False, "--enable-rag", help="Enable RAG system for pattern-based enhancement"
    ),
    log_level: str = typer.Option(
        "INFO", "--log-level", "-l", help="Logging level"
    ),
) -> None:
    """
    Create a 3D scene from a text prompt.

    Example:
        voxel create "a cozy cyberpunk cafe at sunset"
    """
    setup_logging(log_level)

    console.print(
        Panel.fit(
            "[bold cyan]Voxel[/bold cyan] - AI-Powered 3D Scene Generation",
            border_style="cyan",
        )
    )

    try:
        # Load configuration
        config = Config()

        # Override config with CLI arguments
        if samples is not None:
            config.render_samples = samples
        if engine is not None:
            config.render_engine = engine
        if max_iterations is not None:
            config.max_iterations = max_iterations

        config.enable_reviewer = review

        # Validate configuration
        try:
            config.validate_api_keys()
            config.validate_paths()
        except ValueError as e:
            console.print(f"[bold red]Configuration error:[/bold red] {e}")
            console.print("\n[yellow]Make sure to:[/yellow]")
            console.print("1. Copy .env.example to .env")
            console.print("2. Add your API key")
            console.print("3. Set correct Blender path")
            raise typer.Exit(1)

        # Display settings
        settings_table = Table(title="Generation Settings", show_header=False)
        settings_table.add_column("Setting", style="cyan")
        settings_table.add_column("Value", style="green")

        settings_table.add_row("Prompt", prompt)
        settings_table.add_row("AI Provider", config.ai_provider)
        settings_table.add_row("AI Model", config.ai_model)
        settings_table.add_row("Render Engine", config.render_engine)
        settings_table.add_row("Render Samples", str(config.render_samples))
        settings_table.add_row("Review Enabled", "Yes" if review else "No")
        settings_table.add_row("Max Iterations", str(config.max_iterations))

        console.print(settings_table)
        console.print()

        # Initialize Agency3D
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Initializing Agency3D...", total=None)
            agency = Agency3D(config)
            progress.update(task, completed=True)

        # Generate scene
        console.print("\n[bold yellow]Starting scene generation...[/bold yellow]\n")

        result = agency.create_scene(
            prompt=prompt,
            session_name=session_name,
        )

        # Display results
        if result.success:
            console.print(
                Panel.fit(
                    f"[bold green]Success![/bold green]\n\n"
                    f"Render saved to: [cyan]{result.output_path}[/cyan]\n"
                    f"Iterations: {result.iterations}\n"
                    f"Render time: {result.render_time:.2f}s",
                    border_style="green",
                    title="Scene Generated",
                )
            )

            # Show scripts generated
            if result.scripts:
                scripts_table = Table(title="Generated Scripts")
                scripts_table.add_column("Script", style="cyan")
                scripts_table.add_column("Path", style="dim")

                for script in result.scripts:
                    scripts_table.add_row(script.name, str(script))

                console.print(scripts_table)

        else:
            console.print(
                Panel.fit(
                    f"[bold red]Failed[/bold red]\n\n"
                    f"Error: {result.error or 'Unknown error'}",
                    border_style="red",
                    title="Generation Failed",
                )
            )
            raise typer.Exit(1)

    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user[/yellow]")
        raise typer.Exit(130)
    except Exception as e:
        console.print(f"\n[bold red]Error:[/bold red] {e}")
        if log_level == "DEBUG":
            console.print_exception()
        raise typer.Exit(1)


@app.command()
def config_check() -> None:
    """Check configuration and validate settings."""
    setup_logging("INFO")

    console.print("[bold cyan]Checking configuration...[/bold cyan]\n")

    try:
        config = Config()

        # Check .env file
        env_file = Path(".env")
        if not env_file.exists():
            console.print("[yellow]Warning:[/yellow] .env file not found")
            console.print("Copy .env.example to .env and configure it")
        else:
            console.print("[green]✓[/green] .env file found")

        # Check API keys
        if config.ai_provider == "anthropic":
            if config.anthropic_api_key:
                console.print("[green]✓[/green] Anthropic API key configured")
            else:
                console.print("[red]✗[/red] Anthropic API key missing")
        elif config.ai_provider == "openai":
            if config.openai_api_key:
                console.print("[green]✓[/green] OpenAI API key configured")
            else:
                console.print("[red]✗[/red] OpenAI API key missing")

        # Check Blender
        if config.blender_path.exists():
            console.print(f"[green]✓[/green] Blender found at {config.blender_path}")
        else:
            console.print(f"[red]✗[/red] Blender not found at {config.blender_path}")
            console.print("Update BLENDER_PATH in .env")

        # Check output directory
        if config.output_dir.exists():
            console.print(f"[green]✓[/green] Output directory: {config.output_dir}")
        else:
            console.print(f"[yellow]Warning:[/yellow] Output directory will be created")

        console.print("\n[bold]Current Settings:[/bold]")
        settings = {
            "AI Provider": config.ai_provider,
            "AI Model": config.ai_model,
            "Render Engine": config.render_engine,
            "Render Samples": config.render_samples,
            "Max Iterations": config.max_iterations,
            "Review Enabled": config.enable_reviewer,
        }

        for key, value in settings.items():
            console.print(f"  {key}: [cyan]{value}[/cyan]")

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def version() -> None:
    """Show version information."""
    from agency3d import __version__

    console.print(f"Voxel version [cyan]{__version__}[/cyan]")


def main() -> None:
    """Main entry point."""
    app()


if __name__ == "__main__":
    main()
