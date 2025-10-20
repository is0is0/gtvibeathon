#!/usr/bin/env python3
"""
Simplified Model Evaluation
Evaluates the training pipeline and provides comprehensive status.
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

def main():
    """Run simplified model evaluation."""
    
    print("🎯 Voxel AI Model Evaluation")
    print("=" * 50)
    print(f"Started at: {datetime.now().isoformat()}")
    
    # Step 1: Check training data
    print("\n📊 Step 1: Checking training data...")
    
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
    
    dataset_status = {}
    for file_path in dataset_files:
        if Path(file_path).exists():
            size = Path(file_path).stat().st_size
            dataset_status[file_path] = {"status": "✅", "size": size}
        else:
            dataset_status[file_path] = {"status": "❌", "size": 0}
    
    formatted_status = {}
    for file_path in formatted_files:
        if Path(file_path).exists():
            size = Path(file_path).stat().st_size
            formatted_status[file_path] = {"status": "✅", "size": size}
        else:
            formatted_status[file_path] = {"status": "❌", "size": 0}
    
    print("📁 Dataset files:")
    for file_path, status in dataset_status.items():
        print(f"   {status['status']} {file_path} ({status['size']:,} bytes)")
    
    print("📁 Formatted files:")
    for file_path, status in formatted_status.items():
        print(f"   {status['status']} {file_path} ({status['size']:,} bytes)")
    
    # Step 2: Analyze dataset quality
    print("\n🔍 Step 2: Analyzing dataset quality...")
    
    try:
        # Analyze training data
        train_file = Path("./training_data/datasets/train.jsonl")
        if train_file.exists():
            with open(train_file, 'r') as f:
                lines = f.readlines()
            
            # Count examples by category
            categories = {}
            total_examples = len(lines)
            
            for line in lines:
                try:
                    example = json.loads(line)
                    category = example.get('category', 'unknown')
                    categories[category] = categories.get(category, 0) + 1
                except:
                    continue
            
            print(f"📊 Dataset analysis:")
            print(f"   Total examples: {total_examples:,}")
            print(f"   Categories: {len(categories)}")
            for category, count in categories.items():
                percentage = (count / total_examples) * 100
                print(f"     - {category}: {count:,} ({percentage:.1f}%)")
        else:
            print("❌ Training dataset not found")
            
    except Exception as e:
        print(f"❌ Dataset analysis failed: {e}")
    
    # Step 3: Check training jobs
    print("\n📋 Step 3: Checking training jobs...")
    
    try:
        jobs_file = Path("./training_data/training_jobs/training_jobs.json")
        if jobs_file.exists():
            with open(jobs_file, 'r') as f:
                jobs = json.load(f)
            
            print(f"📊 Training jobs: {len(jobs)}")
            for job in jobs:
                print(f"   - {job.get('agent_role', 'unknown')}: {job.get('status', 'unknown')}")
        else:
            print("⚠️ No training jobs found")
            
    except Exception as e:
        print(f"❌ Training jobs check failed: {e}")
    
    # Step 4: Check API configuration
    print("\n🔑 Step 4: Checking API configuration...")
    
    api_keys = {
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
        "ANTHROPIC_API_KEY": os.getenv("ANTHROPIC_API_KEY")
    }
    
    for key, value in api_keys.items():
        if value:
            print(f"   ✅ {key}: {'*' * 8}...{value[-4:]}")
        else:
            print(f"   ❌ {key}: Not set")
    
    # Step 5: System readiness assessment
    print("\n🎯 Step 5: System readiness assessment...")
    
    readiness_score = 0
    total_checks = 0
    
    # Check dataset files
    dataset_ready = all(status["status"] == "✅" for status in dataset_status.values())
    if dataset_ready:
        readiness_score += 1
        print("   ✅ Dataset files ready")
    else:
        print("   ❌ Dataset files missing")
    total_checks += 1
    
    # Check formatted files
    formatted_ready = all(status["status"] == "✅" for status in formatted_status.values())
    if formatted_ready:
        readiness_score += 1
        print("   ✅ Formatted files ready")
    else:
        print("   ❌ Formatted files missing")
    total_checks += 1
    
    # Check API keys
    api_ready = any(api_keys.values())
    if api_ready:
        readiness_score += 1
        print("   ✅ API keys configured")
    else:
        print("   ❌ No API keys configured")
    total_checks += 1
    
    # Calculate readiness percentage
    readiness_percentage = (readiness_score / total_checks) * 100
    print(f"\n📊 System readiness: {readiness_percentage:.1f}% ({readiness_score}/{total_checks})")
    
    # Step 6: Recommendations
    print("\n💡 Step 6: Recommendations...")
    
    if not dataset_ready:
        print("   1. Run dataset generation: python3 -m src.voxel.training.dataset_builder.synthetic_generator")
    
    if not formatted_ready:
        print("   2. Run data formatting: python3 -m src.voxel.training.fine_tuning.openai_formatter")
    
    if not api_ready:
        print("   3. Set API keys: export OPENAI_API_KEY='your-key'")
        print("   4. Submit training jobs: python3 submit_training_job.py")
    
    if readiness_percentage == 100:
        print("   🎉 System is ready for production training!")
        print("   Next: Submit training jobs and monitor progress")
    
    # Step 7: Summary
    print(f"\n🎉 Evaluation complete!")
    print(f"Completed at: {datetime.now().isoformat()}")
    
    return {
        "readiness_percentage": readiness_percentage,
        "dataset_ready": dataset_ready,
        "formatted_ready": formatted_ready,
        "api_ready": api_ready,
        "total_examples": total_examples if 'total_examples' in locals() else 0
    }

if __name__ == "__main__":
    main()
