"""
Main Entry Point
---------------
Command-line interface for Voxel Weaver.
"""

import argparse
from pathlib import Path
from utils.logger import setup_logging, get_logger
from orchestrator.scene_orchestrator import SceneOrchestrator

logger = get_logger(__name__)


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(description="Voxel Weaver - AI 3D Scene Builder")
    parser.add_argument("prompt", help="Scene description")
    parser.add_argument("--style", default="realistic", help="Visual style")
    parser.add_argument("--output", type=Path, default=Path("output"), help="Output directory")
    
    args = parser.parse_args()
    
    setup_logging(level="INFO")
    
    logger.info("Starting Voxel Weaver")
    logger.info(f"Prompt: {args.prompt}")
    
    orchestrator = SceneOrchestrator()
    result = orchestrator.generate_complete_scene(prompt=args.prompt, style=args.style)
    
    if result.get("success"):
        logger.info(f"Scene generated: {result.get('output_path')}")
    else:
        logger.error(f"Generation failed: {result.get('error')}")


if __name__ == "__main__":
    main()
