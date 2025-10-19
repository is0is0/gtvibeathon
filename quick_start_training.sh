#!/bin/bash
# Quick Start Script for ML Training Pipeline
# Run this script to begin the full training process

set -e  # Exit on error

echo "=========================================="
echo "ML TRAINING PIPELINE - QUICK START"
echo "=========================================="
echo ""

# Step 1: Verify system
echo "Step 1/5: Verifying system..."
python3 verify_ml_training.py
if [ $? -ne 0 ]; then
    echo "❌ Verification failed. Please fix issues above."
    exit 1
fi
echo ""

# Step 2: Check for GitHub token
echo "Step 2/5: Checking environment..."
if [ -z "$GITHUB_TOKEN" ]; then
    echo "⚠️  GITHUB_TOKEN not set!"
    echo ""
    echo "Please set your GitHub token:"
    echo "  export GITHUB_TOKEN=ghp_your_token_here"
    echo ""
    echo "Or add to .env file:"
    echo "  GITHUB_TOKEN=ghp_your_token_here"
    echo ""
    echo "Get a token at: https://github.com/settings/tokens"
    echo "Required scope: public_repo"
    exit 1
fi
echo "✅ GITHUB_TOKEN is set"
echo ""

# Step 3: Scrape .blend files
echo "Step 3/5: Scraping .blend files from GitHub..."
echo "This may take 2-4 hours depending on rate limits."
echo "The scraper will save checkpoints every 10 queries."
echo ""
read -p "Start scraping? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    python3 -m src.voxel.training.data_collection.blender_scraper
    echo "✅ Scraping complete!"
else
    echo "Scraping skipped. You can run it later with:"
    echo "  python3 -m src.voxel.training.data_collection.blender_scraper"
    exit 0
fi
echo ""

# Step 4: Parse .blend files
echo "Step 4/5: Parsing .blend files..."
echo "This will extract objects, materials, and modifiers."
echo ""
read -p "Start parsing? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    python3 -m src.voxel.training.data_collection.blend_parser
    echo "✅ Parsing complete!"
else
    echo "Parsing skipped. You can run it later with:"
    echo "  python3 -m src.voxel.training.data_collection.blend_parser"
    exit 0
fi
echo ""

# Step 5: Build datasets
echo "Step 5/5: Building training datasets..."
echo "This will generate prompt-completion pairs."
echo ""
read -p "Build datasets? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    python3 -m src.voxel.training.dataset_builder.blender_dataset
    echo "✅ Dataset building complete!"
else
    echo "Dataset building skipped. You can run it later with:"
    echo "  python3 -m src.voxel.training.dataset_builder.blender_dataset"
    exit 0
fi
echo ""

# Success!
echo "=========================================="
echo "✅ DATA PREPARATION COMPLETE!"
echo "=========================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Format for training:"
echo "   python3 -m src.voxel.training.fine_tuning.openai_formatter"
echo "   python3 -m src.voxel.training.fine_tuning.claude_formatter"
echo ""
echo "2. Estimate costs:"
echo "   Check the output from the formatters for cost estimates"
echo ""
echo "3. Submit training jobs:"
echo "   See training_orchestrator.py main() for examples"
echo ""
echo "4. Monitor training:"
echo "   orchestrator.monitor_all_jobs()"
echo ""
echo "5. Evaluate and deploy:"
echo "   See quality_metrics.py and model_deployer.py"
echo ""
echo "See TRAINING_HANDOFF.md for detailed instructions."
echo ""
