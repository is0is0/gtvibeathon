#!/usr/bin/env python3
"""
ML Training Pipeline Verification Script
Verifies that all training components are properly installed and ready to run.
"""

import sys
from pathlib import Path

def check_component(name, module_path, class_name=None):
    """Check if a component can be imported."""
    try:
        parts = module_path.split('.')
        module = __import__(module_path, fromlist=[parts[-1]])

        if class_name:
            if not hasattr(module, class_name):
                print(f"❌ {name}: Missing class {class_name}")
                return False

        print(f"✅ {name}: OK")
        return True
    except Exception as e:
        print(f"❌ {name}: {str(e)}")
        return False

def check_file_exists(name, file_path):
    """Check if a file exists."""
    path = Path(file_path)
    if path.exists():
        size_kb = path.stat().st_size / 1024
        print(f"✅ {name}: OK ({size_kb:.1f} KB)")
        return True
    else:
        print(f"❌ {name}: Not found")
        return False

def main():
    print("=" * 60)
    print("ML TRAINING PIPELINE VERIFICATION")
    print("=" * 60)

    results = []

    print("\n📦 COMPONENT IMPORTS:")
    print("-" * 60)

    components = [
        ("Blender Scraper", "src.voxel.training.data_collection.blender_scraper", "BlenderFileScraper"),
        ("Blend Parser", "src.voxel.training.data_collection.blend_parser", "BlendFileParser"),
        ("Dataset Builder", "src.voxel.training.dataset_builder.blender_dataset", "BlenderDatasetBuilder"),
        ("Claude Formatter", "src.voxel.training.fine_tuning.claude_formatter", "ClaudeFormatter"),
        ("OpenAI Formatter", "src.voxel.training.fine_tuning.openai_formatter", "OpenAIFormatter"),
        ("Training Orchestrator", "src.voxel.training.fine_tuning.training_orchestrator", "TrainingOrchestrator"),
        ("Quality Metrics", "src.voxel.training.evaluation.quality_metrics", "QualityMetrics"),
        ("Model Deployer", "src.voxel.training.deployment.model_deployer", "ModelDeployer"),
    ]

    for name, module_path, class_name in components:
        results.append(check_component(name, module_path, class_name))

    print("\n📄 DOCUMENTATION FILES:")
    print("-" * 60)

    docs = [
        ("Training Handoff Guide", "TRAINING_HANDOFF.md"),
        ("ML Training Complete", "ML_TRAINING_COMPLETE.md"),
    ]

    for name, file_path in docs:
        results.append(check_file_exists(name, file_path))

    print("\n📂 DIRECTORY STRUCTURE:")
    print("-" * 60)

    directories = [
        "training_data/checkpoints",
        "training_data/scraped",
        "training_data/parsed",
        "training_data/datasets",
        "training_data/fine_tuning/openai",
        "training_data/fine_tuning/claude",
        "training_data/training_jobs",
        "training_data/evaluation",
    ]

    for dir_path in directories:
        path = Path(dir_path)
        if path.exists():
            print(f"✅ {dir_path}: Exists")
            results.append(True)
        else:
            path.mkdir(parents=True, exist_ok=True)
            print(f"✨ {dir_path}: Created")
            results.append(True)

    print("\n🔑 ENVIRONMENT VARIABLES:")
    print("-" * 60)

    import os

    env_vars = [
        ("GITHUB_TOKEN", "Required for scraping .blend files from GitHub"),
        ("ANTHROPIC_API_KEY", "Optional - for Claude fine-tuning"),
        ("OPENAI_API_KEY", "Optional - for GPT fine-tuning"),
    ]

    for var, description in env_vars:
        value = os.getenv(var)
        if value:
            masked = value[:8] + "..." if len(value) > 8 else "***"
            print(f"✅ {var}: Set ({masked})")
        else:
            print(f"⚠️  {var}: Not set - {description}")

    print("\n" + "=" * 60)

    passed = sum(results)
    total = len(results)

    if passed == total:
        print(f"✅ ALL CHECKS PASSED ({passed}/{total})")
        print("\n🚀 ML TRAINING PIPELINE IS READY!")
        print("\nNext steps:")
        print("1. Set GITHUB_TOKEN in .env file")
        print("2. Run: python -m src.voxel.training.data_collection.blender_scraper")
        print("3. Monitor checkpoints in training_data/checkpoints/")
        print("\nSee TRAINING_HANDOFF.md for complete instructions.")
        return 0
    else:
        print(f"❌ SOME CHECKS FAILED ({passed}/{total} passed)")
        print("\nPlease fix the issues above before proceeding.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
