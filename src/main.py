"""
Main Entry Point
---------------
Command-line interface for Voxel Weaver AI 3D Scene Generator.

Full pipeline demonstration with timing metrics, progress tracking,
and comprehensive error handling.
"""

import argparse
import sys
import time
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import json

from utils.logger import setup_logging, get_logger
from orchestrator.async_scene_orchestrator import AsyncSceneOrchestrator

logger = get_logger(__name__)


# Color codes for terminal output
class Colors:
    """ANSI color codes for terminal output."""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class PipelineTimer:
    """Timer for tracking pipeline stage execution times."""

    def __init__(self):
        """Initialize timer."""
        self.start_time = None
        self.stage_times = {}
        self.current_stage = None
        self.stage_start = None

    def start(self):
        """Start overall timer."""
        self.start_time = time.time()

    def start_stage(self, stage_name: str):
        """Start timing a pipeline stage."""
        self.current_stage = stage_name
        self.stage_start = time.time()

    def end_stage(self):
        """End timing current stage."""
        if self.current_stage and self.stage_start:
            elapsed = time.time() - self.stage_start
            self.stage_times[self.current_stage] = elapsed
            self.current_stage = None
            self.stage_start = None

    def get_total_time(self) -> float:
        """Get total elapsed time."""
        if self.start_time:
            return time.time() - self.start_time
        return 0.0

    def get_summary(self) -> Dict[str, Any]:
        """Get timing summary."""
        total = self.get_total_time()
        return {
            'total_seconds': total,
            'total_formatted': self._format_time(total),
            'stages': {
                name: {
                    'seconds': elapsed,
                    'formatted': self._format_time(elapsed),
                    'percentage': (elapsed / total * 100) if total > 0 else 0
                }
                for name, elapsed in self.stage_times.items()
            }
        }

    @staticmethod
    def _format_time(seconds: float) -> str:
        """Format time as human-readable string."""
        if seconds < 1:
            return f"{seconds*1000:.0f}ms"
        elif seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            secs = int(seconds % 60)
            return f"{minutes}m {secs}s"
        else:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            return f"{hours}h {minutes}m"


def print_banner():
    """Print application banner."""
    banner = f"""
{Colors.CYAN}{Colors.BOLD}
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║                          VOXEL WEAVER                                        ║
║                   AI-Powered 3D Scene Generator                              ║
║                                                                              ║
║              Transform Natural Language into 3D Scenes                       ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
{Colors.ENDC}
"""
    print(banner)


def print_section(title: str, color: str = Colors.BLUE):
    """Print section header."""
    print(f"\n{color}{Colors.BOLD}{'='*80}")
    print(f"{title}")
    print(f"{'='*80}{Colors.ENDC}\n")


def print_stage(stage_num: int, total_stages: int, stage_name: str):
    """Print pipeline stage header."""
    print(f"\n{Colors.CYAN}{Colors.BOLD}[Stage {stage_num}/{total_stages}] {stage_name}{Colors.ENDC}")
    print(f"{Colors.CYAN}{'─'*80}{Colors.ENDC}")


def print_step(step_name: str, status: str = "running"):
    """Print step within a stage."""
    if status == "running":
        print(f"{Colors.YELLOW}  ⟳ {step_name}...{Colors.ENDC}")
    elif status == "success":
        print(f"{Colors.GREEN}  ✓ {step_name}{Colors.ENDC}")
    elif status == "error":
        print(f"{Colors.RED}  ✗ {step_name}{Colors.ENDC}")
    elif status == "info":
        print(f"{Colors.BLUE}  ℹ {step_name}{Colors.ENDC}")


def print_metric(label: str, value: Any):
    """Print a metric."""
    print(f"{Colors.CYAN}  {label}:{Colors.ENDC} {value}")


def print_timing_summary(timer: PipelineTimer):
    """Print timing summary."""
    summary = timer.get_summary()

    print_section("⏱  PIPELINE TIMING SUMMARY", Colors.CYAN)

    print(f"{Colors.BOLD}Total Time:{Colors.ENDC} {summary['total_formatted']}\n")

    if summary['stages']:
        print(f"{Colors.BOLD}Stage Breakdown:{Colors.ENDC}\n")

        for stage_name, stage_data in summary['stages'].items():
            percentage = stage_data['percentage']
            bar_length = int(percentage / 2)
            bar = '█' * bar_length + '░' * (50 - bar_length)

            print(f"  {stage_name}:")
            print(f"    {Colors.CYAN}{bar}{Colors.ENDC} {percentage:.1f}%")
            print(f"    Time: {stage_data['formatted']} ({stage_data['seconds']:.2f}s)\n")


def print_result_summary(result: Dict[str, Any]):
    """Print generation result summary."""
    print_section("📊 GENERATION RESULTS", Colors.GREEN)

    if result.get('success'):
        print(f"{Colors.GREEN}{Colors.BOLD}✓ Generation Successful!{Colors.ENDC}\n")

        metadata = result.get('metadata', {})

        print(f"{Colors.BOLD}Output Files:{Colors.ENDC}")
        print(f"  Scene File: {Colors.CYAN}{result.get('output_path', 'N/A')}{Colors.ENDC}")
        if result.get('render_path'):
            print(f"  Rendered Image: {Colors.CYAN}{result['render_path']}{Colors.ENDC}")
        print(f"  Session Directory: {Colors.CYAN}{result.get('session_dir', 'N/A')}{Colors.ENDC}")

        print(f"\n{Colors.BOLD}Scene Statistics:{Colors.ENDC}")
        print(f"  Prompt: {Colors.YELLOW}{metadata.get('prompt', 'N/A')}{Colors.ENDC}")
        print(f"  Style: {metadata.get('style', 'N/A')}")
        print(f"  Objects: {metadata.get('num_objects', 0)}")
        print(f"  Lights: {metadata.get('num_lights', 0)}")

        pipeline_state = metadata.get('pipeline_state', {})
        print(f"\n{Colors.BOLD}Pipeline Stages:{Colors.ENDC}")
        for stage, completed in pipeline_state.items():
            status = f"{Colors.GREEN}✓{Colors.ENDC}" if completed else f"{Colors.RED}✗{Colors.ENDC}"
            print(f"  {status} {stage.replace('_', ' ').title()}")

    else:
        print(f"{Colors.RED}{Colors.BOLD}✗ Generation Failed{Colors.ENDC}\n")
        print(f"{Colors.RED}Error: {result.get('error', 'Unknown error')}{Colors.ENDC}")


def save_run_report(
    result: Dict[str, Any],
    timer: PipelineTimer,
    args: argparse.Namespace,
    output_path: Path
):
    """Save detailed run report to JSON."""
    report = {
        'timestamp': datetime.now().isoformat(),
        'arguments': {
            'prompt': args.prompt,
            'style': args.style,
            'quality': args.quality,
            'validate': args.validate,
            'render': args.render,
            'output_format': args.format
        },
        'timing': timer.get_summary(),
        'result': result,
        'success': result.get('success', False)
    }

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)

    logger.info(f"Run report saved: {output_path}")


def demonstrate_pipeline(args: argparse.Namespace) -> Dict[str, Any]:
    """
    Demonstrate full Voxel Weaver pipeline.

    Flow:
    1. Prompt Interpretation (NLP analysis)
    2. Geometry Generation (Voxel models)
    3. Texture Application (Advanced materials)
    4. Lighting Setup (Intelligent lighting)
    5. Spatial Validation (Physics checks)
    6. Render Configuration (Optimization)
    7. Final Rendering (Export & render)
    8. Asset Registration (Library updates)

    Args:
        args: Command-line arguments

    Returns:
        Generation result dictionary
    """
    # Initialize timer
    timer = PipelineTimer()
    timer.start()

    # Print configuration
    print_section("⚙  CONFIGURATION", Colors.BLUE)
    print_metric("Prompt", f'"{args.prompt}"')
    print_metric("Style", args.style)
    print_metric("Quality", args.quality)
    print_metric("Validation", "Enabled" if args.validate else "Disabled")
    print_metric("Rendering", "Enabled" if args.render else "Disabled")
    print_metric("Output Format", args.format)
    print_metric("Output Directory", args.output)

    try:
        # Stage 1: Initialize Orchestrator
        timer.start_stage("initialization")
        print_stage(1, 8, "SYSTEM INITIALIZATION")
        print_step("Initializing Scene Orchestrator", "running")

        config = {
            'output_dir': str(args.output),
            'quality': args.quality,
            'subsystems': {
                'render_director': {
                    'default_quality': args.quality
                }
            }
        }

        orchestrator = AsyncSceneOrchestrator(config=config)
        print_step("Scene Orchestrator initialized", "success")
        timer.end_stage()

        # Stage 2: Interpret Prompt
        timer.start_stage("prompt_interpretation")
        print_stage(2, 8, "PROMPT INTERPRETATION")
        print_step("Analyzing natural language prompt", "running")

        interpreted_prompt = orchestrator.handle_prompt(args.prompt, args.style)

        print_step("Prompt interpretation complete", "success")
        print_metric("Objects Detected", len(interpreted_prompt.get('objects', [])))
        print_metric("Relationships Found", len(interpreted_prompt.get('relationships', [])))
        print_metric("Mood", interpreted_prompt.get('mood', 'N/A'))
        timer.end_stage()

        # Stage 3: Generate Geometry
        timer.start_stage("geometry_generation")
        print_stage(3, 8, "GEOMETRY GENERATION")
        print_step("Generating 3D voxel models", "running")

        scene_data = orchestrator.build_scene(interpreted_prompt, args.style)

        print_step("Geometry generation complete", "success")
        print_metric("Objects Generated", len(scene_data.get('objects', [])))
        print_metric("Vertices", sum(len(obj.get('vertices', [])) for obj in scene_data.get('objects', [])))
        timer.end_stage()

        # Stage 4: Apply Textures
        timer.start_stage("texture_application")
        print_stage(4, 8, "TEXTURE APPLICATION")
        print_step("Applying advanced materials and textures", "running")

        scene_data = orchestrator._apply_textures(scene_data, args.style)

        print_step("Texture application complete", "success")
        print_metric("Materials Applied", len(scene_data.get('materials', [])))
        timer.end_stage()

        # Stage 5: Setup Lighting
        timer.start_stage("lighting_setup")
        print_stage(5, 8, "LIGHTING SETUP")
        print_step("Configuring intelligent lighting", "running")

        scene_data = orchestrator._setup_lighting(scene_data, args.style)

        num_lights = len(scene_data.get('lighting', {}).get('lights', []))
        print_step("Lighting setup complete", "success")
        print_metric("Lights Placed", num_lights)
        print_metric("Lighting Style", scene_data.get('lighting', {}).get('mode', 'N/A'))
        timer.end_stage()

        # Stage 6: Validate Scene (if enabled)
        if args.validate:
            timer.start_stage("spatial_validation")
            print_stage(6, 8, "SPATIAL VALIDATION")
            print_step("Validating physics and spatial relationships", "running")

            scene_data = orchestrator._validate_scene(scene_data)

            print_step("Spatial validation complete", "success")
            timer.end_stage()
        else:
            print_stage(6, 8, "SPATIAL VALIDATION")
            print_step("Validation skipped (disabled)", "info")

        # Stage 7: Configure Rendering
        timer.start_stage("render_configuration")
        print_stage(7, 8, "RENDER CONFIGURATION")
        print_step("Optimizing render settings", "running")

        scene_data = orchestrator._configure_rendering(scene_data, args.format)

        print_step("Render configuration complete", "success")
        print_metric("Render Quality", scene_data.get('render_settings', {}).get('quality', 'N/A'))
        print_metric("Render Engine", scene_data.get('render_settings', {}).get('engine', 'N/A'))
        timer.end_stage()

        # Stage 8: Final Rendering
        timer.start_stage("final_rendering")
        print_stage(8, 8, "FINAL RENDERING & EXPORT")
        print_step("Exporting scene and rendering", "running")

        result = orchestrator.render_scene(scene_data, args.format)

        if result.get('success'):
            print_step("Rendering complete", "success")
            print_metric("Scene File", result.get('output_path', 'N/A'))
            if result.get('render_path') and args.render:
                print_metric("Rendered Image", result['render_path'])
        else:
            print_step("Rendering failed", "error")

        timer.end_stage()

        # Asset Registration
        if result.get('success'):
            print_step("Registering assets in library", "running")
            orchestrator._register_assets(scene_data, result)
            print_step("Asset registration complete", "success")

        return result

    except Exception as e:
        logger.error(f"Pipeline failed: {e}", exc_info=True)
        print(f"\n{Colors.RED}{Colors.BOLD}✗ Pipeline Error:{Colors.ENDC} {str(e)}\n")

        return {
            'success': False,
            'error': str(e),
            'output_path': None
        }

    finally:
        # Print timing summary
        print_timing_summary(timer)


# Example prompts for demonstration
EXAMPLE_PROMPTS = {
    'bedroom': "A cozy bedroom with a lamp on the nightstand and a desk by the window",
    'cafe': "A modern coffee shop with wooden tables, hanging lights, and a bar counter",
    'office': "A minimalist office with a desk, ergonomic chair, and potted plants",
    'living_room': "A living room with a comfortable sofa, coffee table, and bookshelf",
    'kitchen': "A bright kitchen with marble countertops, modern appliances, and pendant lights",
    'library': "An old library with wooden bookshelves, reading chairs, and a fireplace",
    'garden': "A peaceful garden with a fountain, flower beds, and a wooden bench",
    'studio': "An art studio with an easel, paint supplies, and natural lighting"
}


def list_example_prompts():
    """Print list of example prompts."""
    print_section("📝 EXAMPLE PROMPTS", Colors.CYAN)

    for name, prompt in EXAMPLE_PROMPTS.items():
        print(f"{Colors.BOLD}{name}:{Colors.ENDC}")
        print(f'  "{Colors.YELLOW}{prompt}{Colors.ENDC}"')
        print(f"  Usage: python main.py --example {name}\n")


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Voxel Weaver - AI-Powered 3D Scene Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate from custom prompt
  python main.py "A cozy bedroom with a lamp and desk"

  # Use example prompt
  python main.py --example bedroom

  # Specify style and quality
  python main.py "Modern office" --style minimalist --quality final

  # Export to GLTF format
  python main.py "Garden scene" --format gltf

  # Disable validation for faster generation
  python main.py "Quick test scene" --no-validate

  # List example prompts
  python main.py --list-examples
        """
    )

    # Prompt input
    parser.add_argument(
        'prompt',
        nargs='?',
        help='Scene description in natural language'
    )

    parser.add_argument(
        '--example',
        choices=list(EXAMPLE_PROMPTS.keys()),
        help='Use an example prompt'
    )

    parser.add_argument(
        '--list-examples',
        action='store_true',
        help='List available example prompts and exit'
    )

    # Style options
    parser.add_argument(
        '--style',
        default='realistic',
        choices=['realistic', 'stylized', 'minimalist', 'modern', 'vintage', 'futuristic'],
        help='Visual style for the scene (default: realistic)'
    )

    # Quality settings
    parser.add_argument(
        '--quality',
        default='preview',
        choices=['draft', 'preview', 'final', 'ultra'],
        help='Render quality preset (default: preview)'
    )

    # Output options
    parser.add_argument(
        '--output',
        type=Path,
        default=Path('output'),
        help='Output directory (default: output/)'
    )

    parser.add_argument(
        '--format',
        default='blend',
        choices=['blend', 'gltf', 'glb', 'fbx', 'obj'],
        help='Export format (default: blend)'
    )

    # Pipeline options
    parser.add_argument(
        '--validate',
        dest='validate',
        action='store_true',
        default=True,
        help='Enable spatial validation (default: enabled)'
    )

    parser.add_argument(
        '--no-validate',
        dest='validate',
        action='store_false',
        help='Disable spatial validation for faster generation'
    )

    parser.add_argument(
        '--render',
        action='store_true',
        default=False,
        help='Render preview image (slower but generates PNG)'
    )

    # Logging options
    parser.add_argument(
        '--log-level',
        default='INFO',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        help='Logging level (default: INFO)'
    )

    parser.add_argument(
        '--log-file',
        type=Path,
        help='Write logs to file'
    )

    # Metadata
    parser.add_argument(
        '--save-report',
        action='store_true',
        help='Save detailed run report as JSON'
    )

    return parser.parse_args()


def main():
    """Main execution function."""
    args = parse_arguments()

    # Handle special commands
    if args.list_examples:
        print_banner()
        list_example_prompts()
        return 0

    # Resolve prompt
    if args.example:
        prompt = EXAMPLE_PROMPTS[args.example]
    elif args.prompt:
        prompt = args.prompt
    else:
        print(f"{Colors.RED}Error: No prompt provided. Use --help for usage information.{Colors.ENDC}")
        return 1

    args.prompt = prompt

    # Setup logging
    setup_logging(
        level=args.log_level,
        console=True,
        file=str(args.log_file) if args.log_file else None
    )

    # Print banner
    print_banner()

    logger.info("="*80)
    logger.info("Voxel Weaver Starting")
    logger.info("="*80)
    logger.info(f"Prompt: {args.prompt}")
    logger.info(f"Style: {args.style}")
    logger.info(f"Quality: {args.quality}")

    # Run pipeline
    result = demonstrate_pipeline(args)

    # Print results
    print_result_summary(result)

    # Save report if requested
    if args.save_report and result.get('session_dir'):
        report_path = Path(result['session_dir']) / 'run_report.json'
        timer = PipelineTimer()  # Create timer for report
        save_run_report(result, timer, args, report_path)
        print(f"\n{Colors.CYAN}Report saved: {report_path}{Colors.ENDC}")

    # Return appropriate exit code
    return 0 if result.get('success') else 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}⚠ Generation interrupted by user{Colors.ENDC}\n")
        sys.exit(130)
    except Exception as e:
        print(f"\n{Colors.RED}✗ Fatal error: {e}{Colors.ENDC}\n")
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
