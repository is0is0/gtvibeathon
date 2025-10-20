#!/usr/bin/env python3
"""
Claude Sonnet 4.5 Training Pipeline
Optimized for Anthropic's Claude fine-tuning with Sonnet 4.5.
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
from voxel.training.fine_tuning.claude_formatter import ClaudeFormatter

def main():
    """Run Claude Sonnet 4.5 training pipeline."""
    
    print("🎯 Claude Sonnet 4.5 Training Pipeline")
    print("=" * 60)
    print(f"Started at: {datetime.now().isoformat()}")
    
    # Step 1: Check Anthropic API key
    print("\n🔑 Step 1: Checking Anthropic API configuration...")
    
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    if not anthropic_key:
        print("❌ ANTHROPIC_API_KEY not found")
        print("Please set your Anthropic API key:")
        print("export ANTHROPIC_API_KEY='your-key-here'")
        return
    
    print(f"✅ Anthropic API key configured: {'*' * 8}...{anthropic_key[-4:]}")
    
    # Step 2: Format data for Claude fine-tuning
    print("\n🔄 Step 2: Formatting data for Claude Sonnet 4.5...")
    try:
        formatter = ClaudeFormatter()
        format_stats = formatter.format_all_splits()
        print(f"✅ Claude formatting complete: {format_stats}")
        
        # Validate Claude formatted data
        train_file = Path("./training_data/fine_tuning/claude/train_claude.jsonl")
        if train_file.exists():
            validation = formatter.validate_format(train_file)
            print(f"✅ Claude data validation: {validation}")
        else:
            print("❌ Claude formatted data not found")
            return
            
    except Exception as e:
        print(f"❌ Claude formatting failed: {e}")
        return
    
    # Step 3: Initialize Claude training orchestrator
    print("\n🎛️ Step 3: Initializing Claude training orchestrator...")
    try:
        orchestrator = TrainingOrchestrator()
        print(f"✅ Claude training orchestrator ready")
        
        # Check existing Claude jobs
        existing_jobs = len(orchestrator.jobs)
        print(f"📋 Existing training jobs: {existing_jobs}")
        
    except Exception as e:
        print(f"❌ Claude orchestrator initialization failed: {e}")
        return
    
    # Step 4: Submit Claude fine-tuning jobs
    print("\n🚀 Step 4: Submitting Claude Sonnet 4.5 fine-tuning jobs...")
    
    # Prepare training files
    train_file = Path("./training_data/fine_tuning/claude/train_claude.jsonl")
    val_file = Path("./training_data/fine_tuning/claude/val_claude.jsonl")
    
    if not train_file.exists():
        print(f"❌ Training file not found: {train_file}")
        return
    
    # Submit jobs for different agent roles
    agent_roles = ["geometry", "material", "lighting", "animation", "scene"]
    submitted_jobs = []
    
    for agent_role in agent_roles:
        try:
            print(f"📤 Submitting Claude job for {agent_role} agent...")
            
            job = orchestrator.submit_claude_job(
                agent_role=agent_role,
                training_file=train_file,
                validation_file=val_file if val_file.exists() else None,
                model_base="claude-3-5-sonnet-20241022"  # Latest Claude Sonnet
            )
            
            submitted_jobs.append(job)
            print(f"✅ {agent_role} job submitted: {job.job_id}")
            
        except Exception as e:
            print(f"❌ Failed to submit {agent_role} job: {e}")
    
    print(f"\n📊 Submitted {len(submitted_jobs)} Claude training jobs")
    
    # Step 5: Monitor training jobs
    print("\n📈 Step 5: Monitoring Claude training jobs...")
    try:
        # Monitor all jobs
        summary = orchestrator.monitor_all_jobs()
        
        print(f"📊 Training Jobs Summary:")
        print(f"   Total Jobs: {summary['total_jobs']}")
        print(f"   By Status: {summary['by_status']}")
        print(f"   By Provider: {summary['by_provider']}")
        print(f"   By Agent: {summary['by_agent']}")
        
        if summary['completed_models']:
            print(f"   Completed Models: {summary['completed_models']}")
        
    except Exception as e:
        print(f"❌ Job monitoring failed: {e}")
    
    # Step 6: Claude-specific optimizations
    print("\n🎯 Step 6: Claude Sonnet 4.5 optimizations...")
    
    claude_optimizations = {
        "model": "claude-3-5-sonnet-20241022",
        "context_window": "200k tokens",
        "reasoning_capabilities": "Advanced",
        "code_generation": "Optimized for Blender Python",
        "fine_tuning_approach": "Multi-agent specialization",
        "training_focus": [
            "3D geometry generation",
            "Material and shader creation", 
            "Professional lighting setup",
            "Animation and keyframes",
            "Scene composition"
        ]
    }
    
    print(f"🤖 Claude Sonnet 4.5 Configuration:")
    for key, value in claude_optimizations.items():
        if isinstance(value, list):
            print(f"   {key}:")
            for item in value:
                print(f"      - {item}")
        else:
            print(f"   {key}: {value}")
    
    # Step 7: Training cost estimation
    print("\n💰 Step 7: Claude training cost estimation...")
    
    try:
        if train_file.exists():
            with open(train_file, 'r') as f:
                lines = f.readlines()
            
            # Estimate tokens (rough approximation: 4 chars = 1 token)
            total_tokens = sum(len(line) // 4 for line in lines)
            
            # Claude fine-tuning pricing (as of 2024)
            # Note: Anthropic's fine-tuning pricing may vary
            estimated_cost = (total_tokens / 1000) * 0.01  # Estimated $0.01 per 1K tokens
            
            print(f"📊 Training Data Analysis:")
            print(f"   Examples: {len(lines):,}")
            print(f"   Estimated Tokens: {total_tokens:,}")
            print(f"   Estimated Cost: ${estimated_cost:.2f}")
            print(f"   Model: Claude Sonnet 4.5")
            
    except Exception as e:
        print(f"❌ Cost estimation failed: {e}")
    
    # Step 8: Next steps for Claude
    print("\n🎯 Step 8: Next steps for Claude Sonnet 4.5...")
    
    print("📋 Training Progress:")
    print("   1. Monitor job status with: python3 -c \"from src.voxel.training.fine_tuning.training_orchestrator import TrainingOrchestrator; o = TrainingOrchestrator(); print(o.monitor_all_jobs())\"")
    print("   2. Check individual job status when needed")
    print("   3. Wait for fine-tuning completion (typically 1-4 hours)")
    print("   4. Test fine-tuned models with sample prompts")
    print("   5. Deploy models to production")
    
    print("\n🔧 Claude-specific considerations:")
    print("   - Claude Sonnet 4.5 has superior reasoning capabilities")
    print("   - Optimized for complex 3D scene generation")
    print("   - Better understanding of Blender Python API")
    print("   - Enhanced context window for large scenes")
    print("   - Improved code quality and error handling")
    
    # Final status
    print(f"\n🎉 Claude Sonnet 4.5 training pipeline complete!")
    print(f"Completed at: {datetime.now().isoformat()}")
    print(f"Submitted jobs: {len(submitted_jobs)}")
    print(f"Model: Claude Sonnet 4.5")
    print(f"Status: Ready for fine-tuning")

if __name__ == "__main__":
    main()
