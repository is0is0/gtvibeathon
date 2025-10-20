#!/usr/bin/env python3
"""
Submit fine-tuning job for Voxel AI agents.
This script will submit a training job for the geometry/builder agent.
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from voxel.training.fine_tuning.training_orchestrator import TrainingOrchestrator
from voxel.training.fine_tuning.openai_formatter import OpenAIFormatter

def main():
    """Submit fine-tuning job for geometry agent."""
    
    print("🚀 Starting Voxel AI Fine-Tuning Job Submission")
    print("=" * 50)
    
    # Initialize orchestrator
    orchestrator = TrainingOrchestrator()
    
    # Check if we have API keys
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY not found in environment")
        print("Please set your OpenAI API key:")
        print("export OPENAI_API_KEY='your-key-here'")
        return
    
    # Check if formatted data exists
    train_file = Path("./training_data/fine_tuning/openai/train_openai.jsonl")
    val_file = Path("./training_data/fine_tuning/openai/val_openai.jsonl")
    
    if not train_file.exists():
        print("❌ Training data not found. Please run the formatter first:")
        print("python3 -m src.voxel.training.fine_tuning.openai_formatter")
        return
    
    print(f"✅ Found training data: {train_file}")
    print(f"✅ Found validation data: {val_file}")
    
    # Submit fine-tuning job for geometry agent
    print("\n🎯 Submitting fine-tuning job for geometry agent...")
    
    try:
        job = orchestrator.submit_openai_job(
            agent_role="geometry",
            training_file=train_file,
            validation_file=val_file,
            model_base="gpt-3.5-turbo",  # Use GPT-3.5 for cost efficiency
            n_epochs=3
        )
        
        print(f"✅ Job submitted successfully!")
        print(f"   Job ID: {job.job_id}")
        print(f"   Status: {job.status}")
        print(f"   Provider: {job.provider}")
        print(f"   Agent: {job.agent_role}")
        print(f"   Base Model: {job.model_base}")
        
        # Monitor job status
        print(f"\n📊 Monitoring job status...")
        summary = orchestrator.monitor_all_jobs()
        
        print(f"Job Summary:")
        print(f"  Total Jobs: {summary['total_jobs']}")
        print(f"  By Status: {summary['by_status']}")
        print(f"  By Provider: {summary['by_provider']}")
        print(f"  By Agent: {summary['by_agent']}")
        
        if summary['completed_models']:
            print(f"  Completed Models: {summary['completed_models']}")
        
        print(f"\n🎉 Fine-tuning job submitted and monitored!")
        print(f"Check job status with: python3 -c \"from src.voxel.training.fine_tuning.training_orchestrator import TrainingOrchestrator; o = TrainingOrchestrator(); print(o.check_job_status('{job.job_id}'))\"")
        
    except Exception as e:
        print(f"❌ Error submitting job: {e}")
        return

if __name__ == "__main__":
    main()
