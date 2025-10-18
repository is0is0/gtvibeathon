"""
Async Main Entry Point
----------------------
Command-line interface for Voxel Weaver with async agent system.

Demonstrates the message-passing architecture where each subsystem
is an independent agent communicating via asyncio queues.
"""

import argparse
import sys
import asyncio
import time
from pathlib import Path
from typing import Dict, Any
from datetime import datetime
import json

from utils.logger import setup_logging, get_logger
from orchestrator.async_scene_orchestrator import AsyncSceneOrchestrator

logger = get_logger(__name__)


# Reuse color and timer classes from main.py
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
        self.start_time = None
        self.stage_times = {}

    def start(self):
        self.start_time = time.time()

    def get_total_time(self) -> float:
        if self.start_time:
            return time.time() - self.start_time
        return 0.0

    @staticmethod
    def format_time(seconds: float) -> str:
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
║                     VOXEL WEAVER ASYNC                                       ║
║             AI-Powered 3D Scene Generator (Async Edition)                    ║
║                                                                              ║
║          Message-Passing Architecture with Concurrent Agents                 ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
{Colors.ENDC}
"""
    print(banner)


# Example prompts
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


async def demonstrate_async_pipeline(args: argparse.Namespace) -> Dict[str, Any]:
    """
    Demonstrate async pipeline with concurrent agent processing.

    Args:
        args: Command-line arguments

    Returns:
        Generation result dictionary
    """
    timer = PipelineTimer()
    timer.start()

    # Print configuration
    print(f"\n{Colors.BLUE}{Colors.BOLD}{'='*80}")
    print("⚙  CONFIGURATION")
    print(f"{'='*80}{Colors.ENDC}\n")
    print(f"{Colors.CYAN}  Prompt:{Colors.ENDC} \"{args.prompt}\"")
    print(f"{Colors.CYAN}  Style:{Colors.ENDC} {args.style}")
    print(f"{Colors.CYAN}  Quality:{Colors.ENDC} {args.quality}")
    print(f"{Colors.CYAN}  Validation:{Colors.ENDC} {'Enabled' if args.validate else 'Disabled'}")
    print(f"{Colors.CYAN}  Output Format:{Colors.ENDC} {args.format}")
    print(f"{Colors.CYAN}  Output Directory:{Colors.ENDC} {args.output}")
    print(f"{Colors.CYAN}  Architecture:{Colors.ENDC} Async Message-Passing Agents")

    try:
        # Create orchestrator
        config = {
            'output_dir': str(args.output),
            'quality': args.quality,
            'subsystems': {}
        }

        print(f"\n{Colors.YELLOW}Initializing async agent system...{Colors.ENDC}")
        orchestrator = AsyncSceneOrchestrator(config=config)

        # Generate scene
        result = await orchestrator.generate_complete_scene(
            prompt=args.prompt,
            style=args.style,
            validate=args.validate,
            output_format=args.format
        )

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
        # Print timing
        total_time = timer.get_total_time()
        print(f"\n{Colors.CYAN}{Colors.BOLD}{'='*80}")
        print(f"⏱  TOTAL PIPELINE TIME: {PipelineTimer.format_time(total_time)}")
        print(f"{'='*80}{Colors.ENDC}\n")


def print_result_summary(result: Dict[str, Any]):
    """Print generation result summary."""
    print(f"\n{Colors.GREEN if result.get('success') else Colors.RED}{Colors.BOLD}{'='*80}")
    print("📊 GENERATION RESULTS")
    print(f"{'='*80}{Colors.ENDC}\n")

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

        print(f"\n{Colors.CYAN}{'─'*80}{Colors.ENDC}")
        print(f"{Colors.BOLD}Architecture Benefits:{Colors.ENDC}")
        print(f"  {Colors.GREEN}✓{Colors.ENDC} Concurrent processing (Texture + Lighting in parallel)")
        print(f"  {Colors.GREEN}✓{Colors.ENDC} Non-blocking asset registration")
        print(f"  {Colors.GREEN}✓{Colors.ENDC} Message-based agent communication")
        print(f"  {Colors.GREEN}✓{Colors.ENDC} Scalable and fault-tolerant")

    else:
        print(f"{Colors.RED}{Colors.BOLD}✗ Generation Failed{Colors.ENDC}\n")
        print(f"{Colors.RED}Error: {result.get('error', 'Unknown error')}{Colors.ENDC}")


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Voxel Weaver Async - AI-Powered 3D Scene Generator (Message-Passing Architecture)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate from custom prompt
  python main_async.py "A cozy bedroom with a lamp and desk"

  # Use example prompt
  python main_async.py --example bedroom

  # Specify style and quality
  python main_async.py "Modern office" --style minimalist --quality final

  # Fast generation (no validation)
  python main_async.py "Quick test" --no-validate --quality draft

Architecture Features:
  - Async message-passing between agents
  - Concurrent processing where possible (texture + lighting)
  - Non-blocking asset registration
  - Scalable to multiple agent instances
        """
    )

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
        '--style',
        default='realistic',
        choices=['realistic', 'stylized', 'minimalist', 'modern', 'vintage', 'futuristic'],
        help='Visual style (default: realistic)'
    )

    parser.add_argument(
        '--quality',
        default='preview',
        choices=['draft', 'preview', 'final', 'ultra'],
        help='Render quality (default: preview)'
    )

    parser.add_argument(
        '--output',
        type=Path,
        default=Path('output/async'),
        help='Output directory (default: output/async/)'
    )

    parser.add_argument(
        '--format',
        default='blend',
        choices=['blend', 'gltf', 'glb', 'fbx', 'obj'],
        help='Export format (default: blend)'
    )

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
        help='Disable spatial validation'
    )

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

    return parser.parse_args()


async def main_async():
    """Async main execution function."""
    args = parse_arguments()

    # Resolve prompt
    if args.example:
        prompt = EXAMPLE_PROMPTS[args.example]
    elif args.prompt:
        prompt = args.prompt
    else:
        print(f"{Colors.RED}Error: No prompt provided. Use --help for usage.{Colors.ENDC}")
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
    logger.info("Voxel Weaver Async Starting")
    logger.info("="*80)
    logger.info(f"Prompt: {args.prompt}")
    logger.info(f"Style: {args.style}")

    # Run async pipeline
    result = await demonstrate_async_pipeline(args)

    # Print results
    print_result_summary(result)

    # Return exit code
    return 0 if result.get('success') else 1


def main():
    """Synchronous entry point that runs async main."""
    try:
        exit_code = asyncio.run(main_async())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}⚠ Generation interrupted by user{Colors.ENDC}\n")
        sys.exit(130)
    except Exception as e:
        print(f"\n{Colors.RED}✗ Fatal error: {e}{Colors.ENDC}\n")
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
