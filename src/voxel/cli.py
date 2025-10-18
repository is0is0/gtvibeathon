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

from voxel import Voxel, Config

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

        # Initialize Voxel
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Initializing Voxel...", total=None)
            voxel = Voxel(config)
            progress.update(task, completed=True)

        # Generate scene
        console.print("\n[bold yellow]Starting scene generation...[/bold yellow]\n")

        result = voxel.create_scene(
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
    from voxel import __version__

    console.print(f"Voxel version [cyan]{__version__}[/cyan]")


# Database commands
@app.command()
def list_projects() -> None:
    """List all projects."""
    try:
        voxel = Voxel()
        projects = voxel.get_projects()

        if not projects:
            console.print("[yellow]No projects found[/yellow]")
            return

        table = Table(title="Projects")
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("Status", style="blue")
        table.add_column("Created", style="dim")

        for project in projects:
            table.add_row(
                str(project["id"]),
                project["name"],
                project["status"],
                project["created_at"][:10]  # Just the date part
            )

        console.print(table)
        voxel.close()
        
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def project_history(
    project_id: int = typer.Argument(..., help="Project ID to show history for")
) -> None:
    """Show generation history for a project."""
    try:
        voxel = Voxel()
        history = voxel.get_project_history(project_id)

        if not history:
            console.print(f"[yellow]No generations found for project {project_id}[/yellow]")
            return

        table = Table(title=f"Generation History for Project {project_id}")
        table.add_column("ID", style="cyan")
        table.add_column("Prompt", style="green", max_width=50)
        table.add_column("Status", style="blue")
        table.add_column("Quality", style="yellow")
        table.add_column("Created", style="dim")

        for generation in history:
            quality = f"{generation['quality_score']:.2f}" if generation['quality_score'] else "N/A"
            table.add_row(
                str(generation["id"]),
                generation["prompt"][:47] + "..." if len(generation["prompt"]) > 50 else generation["prompt"],
                generation["status"],
                quality,
                generation["created_at"][:10]
            )

        console.print(table)
        voxel.close()
        
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def stats(
    days: int = typer.Option(30, "--days", "-d", help="Number of days to analyze")
) -> None:
    """Show system analytics and statistics."""
    try:
        voxel = Voxel()
        analytics = voxel.get_system_analytics(days)

        console.print(f"[bold]System Analytics ({days} days)[/bold]")
        console.print(f"Total generations: [cyan]{analytics.get('total_generations', 0)}[/cyan]")
        console.print(f"Successful generations: [green]{analytics.get('successful_generations', 0)}[/green]")
        console.print(f"Success rate: [blue]{analytics.get('success_rate', 0):.1f}%[/blue]")
        console.print(f"Average quality: [yellow]{analytics.get('avg_quality', 0):.2f}[/yellow]")
        console.print(f"Total render time: [magenta]{analytics.get('total_render_time', 0):.1f}s[/magenta]")
        console.print(f"Total tokens used: [cyan]{analytics.get('total_tokens', 0)}[/cyan]")

        # Show most used tags
        most_used_tags = analytics.get('most_used_tags', [])
        if most_used_tags:
            console.print(f"\n[bold]Most Used Tags:[/bold]")
            for tag in most_used_tags[:5]:
                console.print(f"  {tag['name']}: {tag['count']} uses")

        voxel.close()
        
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def search(
    query: str = typer.Argument(..., help="Search query for generations"),
    limit: int = typer.Option(20, "--limit", "-l", help="Maximum number of results")
) -> None:
    """Search generations by prompt text."""
    try:
        voxel = Voxel()
        results = voxel.search_generations(query, limit)

        if not results:
            console.print(f"[yellow]No generations found for query: '{query}'[/yellow]")
            return

        table = Table(title=f"Search Results for '{query}'")
        table.add_column("ID", style="cyan")
        table.add_column("Project ID", style="blue")
        table.add_column("Prompt", style="green", max_width=60)
        table.add_column("Status", style="yellow")
        table.add_column("Quality", style="magenta")
        table.add_column("Created", style="dim")

        for result in results:
            quality = f"{result['quality_score']:.2f}" if result['quality_score'] else "N/A"
            table.add_row(
                str(result["id"]),
                str(result["project_id"]),
                result["prompt"][:57] + "..." if len(result["prompt"]) > 60 else result["prompt"],
                result["status"],
                quality,
                result["created_at"][:10]
            )

        console.print(table)
        voxel.close()
        
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def create_project(
    name: str = typer.Argument(..., help="Project name"),
    description: Optional[str] = typer.Option(None, "--description", "-d", help="Project description")
) -> None:
    """Create a new project."""
    try:
        voxel = Voxel()
        project = voxel.create_project(name, description)

        console.print(f"[green]✓[/green] Created project: {project['name']} (ID: {project['id']})")
        voxel.close()
        
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


def main() -> None:
    """Main entry point."""
    app()


if __name__ == "__main__":
    main()
