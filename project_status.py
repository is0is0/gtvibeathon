#!/usr/bin/env python3
"""
Voxel AI Project Status Summary
Comprehensive overview of the entire Voxel AI training and deployment pipeline.
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

def main():
    """Generate comprehensive project status."""
    
    print("🎯 Voxel AI Project Status Summary")
    print("=" * 60)
    print(f"Generated at: {datetime.now().isoformat()}")
    
    # Project Overview
    print("\n📋 Project Overview:")
    print("   🎨 Voxel AI - Advanced 3D Scene Generation System")
    print("   🤖 Multi-Agent AI Architecture")
    print("   🔧 Blender Python Integration")
    print("   🚀 Production-Ready Training Pipeline")
    
    # Training Data Status
    print("\n📊 Training Data Status:")
    
    dataset_files = [
        "./training_data/datasets/train.jsonl",
        "./training_data/datasets/val.jsonl", 
        "./training_data/datasets/test.jsonl"
    ]
    
    total_size = 0
    for file_path in dataset_files:
        if Path(file_path).exists():
            size = Path(file_path).stat().st_size
            total_size += size
            print(f"   ✅ {Path(file_path).name}: {size:,} bytes")
        else:
            print(f"   ❌ {Path(file_path).name}: Missing")
    
    print(f"   📊 Total Dataset Size: {total_size:,} bytes ({total_size/1024/1024:.1f} MB)")
    
    # Formatted Data Status
    print("\n🔄 Formatted Data Status:")
    
    formatted_files = [
        "./training_data/fine_tuning/openai/train_openai.jsonl",
        "./training_data/fine_tuning/openai/val_openai.jsonl",
        "./training_data/fine_tuning/openai/test_openai.jsonl"
    ]
    
    formatted_size = 0
    for file_path in formatted_files:
        if Path(file_path).exists():
            size = Path(file_path).stat().st_size
            formatted_size += size
            print(f"   ✅ {Path(file_path).name}: {size:,} bytes")
        else:
            print(f"   ❌ {Path(file_path).name}: Missing")
    
    print(f"   📊 Total Formatted Size: {formatted_size:,} bytes ({formatted_size/1024/1024:.1f} MB)")
    
    # Dataset Analysis
    print("\n🔍 Dataset Analysis:")
    
    try:
        train_file = Path("./training_data/datasets/train.jsonl")
        if train_file.exists():
            with open(train_file, 'r') as f:
                lines = f.readlines()
            
            categories = {}
            difficulties = {}
            total_examples = len(lines)
            
            for line in lines:
                try:
                    example = json.loads(line)
                    category = example.get('category', 'unknown')
                    difficulty = example.get('difficulty', 'unknown')
                    
                    categories[category] = categories.get(category, 0) + 1
                    difficulties[difficulty] = difficulties.get(difficulty, 0) + 1
                except:
                    continue
            
            print(f"   📊 Total Examples: {total_examples:,}")
            print(f"   🏷️ Categories:")
            for category, count in sorted(categories.items()):
                percentage = (count / total_examples) * 100
                print(f"      - {category}: {count:,} ({percentage:.1f}%)")
            
            print(f"   🎚️ Difficulty Levels:")
            for difficulty, count in sorted(difficulties.items()):
                percentage = (count / total_examples) * 100
                print(f"      - {difficulty}: {count:,} ({percentage:.1f}%)")
                
    except Exception as e:
        print(f"   ❌ Analysis failed: {e}")
    
    # Training Jobs Status
    print("\n🚀 Training Jobs Status:")
    
    try:
        jobs_file = Path("./training_data/training_jobs/training_jobs.json")
        if jobs_file.exists():
            with open(jobs_file, 'r') as f:
                jobs = json.load(f)
            
            print(f"   📋 Total Jobs: {len(jobs)}")
            
            status_counts = {}
            agent_counts = {}
            
            for job in jobs:
                status = job.get('status', 'unknown')
                agent = job.get('agent_role', 'unknown')
                
                status_counts[status] = status_counts.get(status, 0) + 1
                agent_counts[agent] = agent_counts.get(agent, 0) + 1
            
            print(f"   📊 By Status:")
            for status, count in status_counts.items():
                print(f"      - {status}: {count}")
            
            print(f"   🤖 By Agent:")
            for agent, count in agent_counts.items():
                print(f"      - {agent}: {count}")
        else:
            print("   ⚠️ No training jobs found")
            
    except Exception as e:
        print(f"   ❌ Jobs check failed: {e}")
    
    # API Configuration
    print("\n🔑 API Configuration:")
    
    api_keys = {
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
        "ANTHROPIC_API_KEY": os.getenv("ANTHROPIC_API_KEY")
    }
    
    configured_apis = 0
    for key, value in api_keys.items():
        if value:
            configured_apis += 1
            print(f"   ✅ {key}: Configured")
        else:
            print(f"   ❌ {key}: Not set")
    
    print(f"   📊 Configured APIs: {configured_apis}/2")
    
    # System Readiness
    print("\n🎯 System Readiness:")
    
    readiness_checks = [
        ("Dataset Files", all(Path(f).exists() for f in dataset_files)),
        ("Formatted Files", all(Path(f).exists() for f in formatted_files)),
        ("API Keys", configured_apis > 0),
        ("Training Pipeline", Path("./training_pipeline.py").exists()),
        ("Evaluation System", Path("./simple_evaluation.py").exists())
    ]
    
    passed_checks = 0
    for check_name, status in readiness_checks:
        if status:
            passed_checks += 1
            print(f"   ✅ {check_name}")
        else:
            print(f"   ❌ {check_name}")
    
    readiness_percentage = (passed_checks / len(readiness_checks)) * 100
    print(f"   📊 Overall Readiness: {readiness_percentage:.1f}% ({passed_checks}/{len(readiness_checks)})")
    
    # Next Steps
    print("\n🎯 Next Steps:")
    
    if not all(Path(f).exists() for f in dataset_files):
        print("   1. Generate training dataset: python3 -m src.voxel.training.dataset_builder.synthetic_generator")
    
    if not all(Path(f).exists() for f in formatted_files):
        print("   2. Format training data: python3 -m src.voxel.training.fine_tuning.openai_formatter")
    
    if configured_apis == 0:
        print("   3. Set API keys: export OPENAI_API_KEY='your-key'")
        print("   4. Submit training jobs: python3 submit_training_job.py")
    else:
        print("   3. Submit training jobs: python3 submit_training_job.py")
        print("   4. Monitor training progress")
        print("   5. Deploy models when ready")
    
    # Performance Metrics
    print("\n📈 Performance Metrics:")
    
    if total_size > 0:
        print(f"   📊 Dataset Size: {total_size/1024/1024:.1f} MB")
        print(f"   🎯 Examples: {total_examples if 'total_examples' in locals() else 'Unknown'}")
        print(f"   💰 Estimated Training Cost: ${(formatted_size/1024/1024) * 0.5:.2f} (GPT-3.5)")
    
    # Architecture Overview
    print("\n🏗️ Architecture Overview:")
    print("   🤖 Multi-Agent System:")
    print("      - Geometry Agent: 3D model generation")
    print("      - Material Agent: Texture and shader creation")
    print("      - Lighting Agent: Scene illumination")
    print("      - Animation Agent: Motion and keyframes")
    print("      - Scene Agent: Composition and rendering")
    
    print("   🔧 Training Pipeline:")
    print("      - Synthetic Data Generation")
    print("      - OpenAI/Anthropic Fine-tuning")
    print("      - Model Evaluation")
    print("      - Production Deployment")
    
    # Final Status
    print(f"\n🎉 Project Status Complete!")
    print(f"Generated at: {datetime.now().isoformat()}")
    
    if readiness_percentage >= 80:
        print("🚀 System is ready for production training!")
    elif readiness_percentage >= 60:
        print("⚠️ System is mostly ready, minor configuration needed")
    else:
        print("❌ System needs significant setup before training")

if __name__ == "__main__":
    main()
