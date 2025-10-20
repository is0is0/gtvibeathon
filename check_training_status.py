#!/usr/bin/env python3
"""
Check Claude Sonnet 4.5 Training Status
Monitor the progress of your fine-tuning jobs.
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def main():
    """Check training job status."""
    
    print("🎯 Claude Sonnet 4.5 Training Status Check")
    print("=" * 60)
    print(f"Checked at: {datetime.now().isoformat()}")
    
    # Check if training jobs file exists
    jobs_file = Path("./training_data/training_jobs/training_jobs.json")
    
    if not jobs_file.exists():
        print("❌ No training jobs found")
        print("Run: python3 claude_training_pipeline.py")
        return
    
    try:
        with open(jobs_file, 'r') as f:
            jobs = json.load(f)
        
        print(f"\n📊 Training Jobs Summary:")
        print(f"   Total Jobs: {len(jobs)}")
        
        # Count by status
        status_counts = {}
        agent_counts = {}
        
        for job in jobs:
            status = job.get('status', 'unknown')
            agent = job.get('agent_role', 'unknown')
            
            status_counts[status] = status_counts.get(status, 0) + 1
            agent_counts[agent] = agent_counts.get(agent, 0) + 1
        
        print(f"\n📈 Job Status:")
        for status, count in status_counts.items():
            print(f"   {status}: {count}")
        
        print(f"\n🤖 Agent Breakdown:")
        for agent, count in agent_counts.items():
            print(f"   {agent}: {count}")
        
        # Show individual job details
        print(f"\n📋 Individual Job Details:")
        for i, job in enumerate(jobs, 1):
            print(f"   {i}. {job.get('agent_role', 'unknown')} Agent")
            print(f"      Job ID: {job.get('job_id', 'unknown')}")
            print(f"      Status: {job.get('status', 'unknown')}")
            print(f"      Provider: {job.get('provider', 'unknown')}")
            print(f"      Model: {job.get('model_base', 'unknown')}")
            print(f"      Created: {job.get('created_at', 'unknown')}")
            if job.get('error'):
                print(f"      Error: {job.get('error')}")
            print()
        
        # Training progress estimation
        print(f"🎯 Training Progress:")
        if 'pending' in status_counts:
            print(f"   ⏳ {status_counts['pending']} jobs pending start")
        if 'training' in status_counts:
            print(f"   🔄 {status_counts['training']} jobs currently training")
        if 'completed' in status_counts:
            print(f"   ✅ {status_counts['completed']} jobs completed")
        if 'failed' in status_counts:
            print(f"   ❌ {status_counts['failed']} jobs failed")
        
        # Next steps
        print(f"\n🎯 Next Steps:")
        if status_counts.get('pending', 0) > 0:
            print("   1. Wait for jobs to start training (usually within minutes)")
            print("   2. Check status again in 30 minutes")
        elif status_counts.get('training', 0) > 0:
            print("   1. Jobs are actively training")
            print("   2. Check status again in 1-2 hours")
        elif status_counts.get('completed', 0) > 0:
            print("   1. Some jobs have completed!")
            print("   2. Test the fine-tuned models")
            print("   3. Deploy to production")
        else:
            print("   1. Monitor job progress")
            print("   2. Check for any errors")
        
        print(f"\n🔧 Commands:")
        print(f"   Check status: python3 check_training_status.py")
        print(f"   Full status: python3 claude_status.py")
        
    except Exception as e:
        print(f"❌ Error reading training jobs: {e}")

if __name__ == "__main__":
    main()
