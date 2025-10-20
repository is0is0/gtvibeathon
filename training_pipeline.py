#!/usr/bin/env python3
"""
Voxel AI Training Pipeline - Complete training workflow.
This script orchestrates the entire training process from data generation to model deployment.
"""

import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from voxel.training.fine_tuning.training_orchestrator import TrainingOrchestrator
from voxel.training.fine_tuning.openai_formatter import OpenAIFormatter
from voxel.training.dataset_builder.synthetic_generator import SyntheticDatasetGenerator

def main():
    """Run complete training pipeline."""
    
    print("🎯 Voxel AI Training Pipeline")
    print("=" * 50)
    print(f"Started at: {datetime.now().isoformat()}")
    
    # Step 1: Generate synthetic dataset
    print("\n📊 Step 1: Generating synthetic training dataset...")
    try:
        generator = SyntheticDatasetGenerator()
        examples = generator.generate_dataset(total_examples=10000)
        
        # Save dataset
        dataset_dir = Path("./training_data/datasets")
        dataset_dir.mkdir(parents=True, exist_ok=True)
        
        # Split into train/val/test (80/10/10)
        train_size = int(len(examples) * 0.8)
        val_size = int(len(examples) * 0.1)
        
        train_examples = examples[:train_size]
        val_examples = examples[train_size:train_size + val_size]
        test_examples = examples[train_size + val_size:]
        
        # Save splits
        for split, split_examples in [("train", train_examples), ("val", val_examples), ("test", test_examples)]:
            output_file = dataset_dir / f"{split}.jsonl"
            with open(output_file, 'w') as f:
                for example in split_examples:
                    f.write(json.dumps({
                        "prompt": example.prompt,
                        "completion": example.completion,
                        "category": example.category,
                        "difficulty": example.difficulty,
                        "quality_score": example.quality_score
                    }) + '\n')
        
        stats = {
            "total_examples": len(examples),
            "train": len(train_examples),
            "val": len(val_examples), 
            "test": len(test_examples)
        }
        print(f"✅ Dataset generation complete: {stats}")
    except Exception as e:
        print(f"❌ Dataset generation failed: {e}")
        return
    
    # Step 2: Format data for fine-tuning
    print("\n🔄 Step 2: Formatting data for fine-tuning...")
    try:
        formatter = OpenAIFormatter()
        format_stats = formatter.format_all_splits()
        print(f"✅ Data formatting complete: {format_stats}")
        
        # Validate formatted data
        train_file = Path("./training_data/fine_tuning/openai/train_openai.jsonl")
        validation = formatter.validate_format(train_file)
        print(f"✅ Data validation: {validation}")
        
    except Exception as e:
        print(f"❌ Data formatting failed: {e}")
        return
    
    # Step 3: Initialize training orchestrator
    print("\n🎛️ Step 3: Initializing training orchestrator...")
    try:
        orchestrator = TrainingOrchestrator()
        print(f"✅ Training orchestrator ready")
        
        # Check existing jobs
        existing_jobs = len(orchestrator.jobs)
        print(f"📋 Existing training jobs: {existing_jobs}")
        
    except Exception as e:
        print(f"❌ Training orchestrator initialization failed: {e}")
        return
    
    # Step 4: Prepare training jobs (simulate if no API keys)
    print("\n🚀 Step 4: Preparing training jobs...")
    
    api_keys_available = bool(os.getenv("OPENAI_API_KEY") or os.getenv("ANTHROPIC_API_KEY"))
    
    if api_keys_available:
        print("✅ API keys detected - ready for live training")
        
        # Submit actual training jobs
        try:
            train_file = Path("./training_data/fine_tuning/openai/train_openai.jsonl")
            val_file = Path("./training_data/fine_tuning/openai/val_openai.jsonl")
            
            # Submit geometry agent job
            job = orchestrator.submit_openai_job(
                agent_role="geometry",
                training_file=train_file,
                validation_file=val_file,
                model_base="gpt-3.5-turbo",
                n_epochs=3
            )
            
            print(f"✅ Training job submitted: {job.job_id}")
            
        except Exception as e:
            print(f"❌ Training job submission failed: {e}")
            return
            
    else:
        print("⚠️ No API keys detected - creating mock training jobs")
        
        # Create mock training jobs for demonstration
        mock_jobs = [
            {
                "agent_role": "geometry",
                "model_base": "gpt-3.5-turbo",
                "status": "pending",
                "description": "3D geometry generation agent"
            },
            {
                "agent_role": "material", 
                "model_base": "gpt-3.5-turbo",
                "status": "pending",
                "description": "Material and texture agent"
            },
            {
                "agent_role": "lighting",
                "model_base": "gpt-3.5-turbo", 
                "status": "pending",
                "description": "Lighting and rendering agent"
            }
        ]
        
        # Save mock jobs
        mock_jobs_file = Path("./training_data/training_jobs/mock_jobs.json")
        mock_jobs_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(mock_jobs_file, 'w') as f:
            json.dump(mock_jobs, f, indent=2)
        
        print(f"✅ Mock training jobs created: {len(mock_jobs)} jobs")
        for job in mock_jobs:
            print(f"   - {job['agent_role']}: {job['description']}")
    
    # Step 5: Training pipeline summary
    print("\n📈 Step 5: Training pipeline summary...")
    
    # Check generated files
    dataset_files = [
        "./training_data/datasets/train.jsonl",
        "./training_data/datasets/val.jsonl", 
        "./training_data/datasets/test.jsonl"
    ]
    
    formatted_files = [
        "./training_data/fine_tuning/openai/train_openai.jsonl",
        "./training_data/fine_tuning/openai/val_openai.jsonl",
        "./training_data/fine_tuning/openai/test_openai.jsonl"
    ]
    
    print(f"📁 Dataset files:")
    for file_path in dataset_files:
        if Path(file_path).exists():
            size = Path(file_path).stat().st_size
            print(f"   ✅ {file_path} ({size:,} bytes)")
        else:
            print(f"   ❌ {file_path} (missing)")
    
    print(f"📁 Formatted files:")
    for file_path in formatted_files:
        if Path(file_path).exists():
            size = Path(file_path).stat().st_size
            print(f"   ✅ {file_path} ({size:,} bytes)")
        else:
            print(f"   ❌ {file_path} (missing)")
    
    # Calculate total dataset size
    total_size = sum(Path(f).stat().st_size for f in dataset_files if Path(f).exists())
    print(f"📊 Total dataset size: {total_size:,} bytes ({total_size/1024/1024:.1f} MB)")
    
    # Step 6: Next steps
    print("\n🎯 Next Steps:")
    if api_keys_available:
        print("1. Monitor training jobs with: python3 -c \"from src.voxel.training.fine_tuning.training_orchestrator import TrainingOrchestrator; o = TrainingOrchestrator(); print(o.monitor_all_jobs())\"")
        print("2. Check job status when training completes")
        print("3. Deploy fine-tuned models to production")
    else:
        print("1. Set API keys: export OPENAI_API_KEY='your-key'")
        print("2. Run: python3 submit_training_job.py")
        print("3. Monitor training progress")
        print("4. Deploy models when ready")
    
    print(f"\n🎉 Training pipeline complete!")
    print(f"Completed at: {datetime.now().isoformat()}")

if __name__ == "__main__":
    main()
