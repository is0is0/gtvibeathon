#!/usr/bin/env python3
"""
Claude Sonnet 4.5 Training Status
Comprehensive status for Claude fine-tuning preparation.
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

def main():
    """Generate Claude Sonnet 4.5 training status."""
    
    print("🎯 Claude Sonnet 4.5 Training Status")
    print("=" * 60)
    print(f"Generated at: {datetime.now().isoformat()}")
    
    # Claude-specific overview
    print("\n🤖 Claude Sonnet 4.5 Overview:")
    print("   🧠 Advanced reasoning capabilities")
    print("   🔧 Optimized for complex 3D scene generation")
    print("   🎨 Superior understanding of Blender Python API")
    print("   📊 Enhanced context window (200k tokens)")
    print("   🚀 Multi-agent specialization support")
    
    # Training data status for Claude
    print("\n📊 Claude Training Data Status:")
    
    claude_files = [
        "./training_data/fine_tuning/claude/train_claude.jsonl",
        "./training_data/fine_tuning/claude/val_claude.jsonl",
        "./training_data/fine_tuning/claude/test_claude.jsonl"
    ]
    
    claude_size = 0
    for file_path in claude_files:
        if Path(file_path).exists():
            size = Path(file_path).stat().st_size
            claude_size += size
            print(f"   ✅ {Path(file_path).name}: {size:,} bytes")
        else:
            print(f"   ❌ {Path(file_path).name}: Missing")
    
    print(f"   📊 Total Claude Data Size: {claude_size:,} bytes ({claude_size/1024/1024:.1f} MB)")
    
    # Claude-specific analysis
    print("\n🔍 Claude Dataset Analysis:")
    
    try:
        train_file = Path("./training_data/fine_tuning/claude/train_claude.jsonl")
        if train_file.exists():
            with open(train_file, 'r') as f:
                lines = f.readlines()
            
            # Analyze Claude format
            claude_examples = []
            for line in lines:
                try:
                    example = json.loads(line)
                    claude_examples.append(example)
                except:
                    continue
            
            # Count by agent role
            agent_roles = {}
            total_examples = len(claude_examples)
            
            for example in claude_examples:
                # Extract agent role from system prompt
                system = example.get('system', '')
                if 'geometry' in system.lower():
                    role = 'geometry'
                elif 'material' in system.lower():
                    role = 'material'
                elif 'lighting' in system.lower():
                    role = 'lighting'
                elif 'animation' in system.lower():
                    role = 'animation'
                elif 'scene' in system.lower():
                    role = 'scene'
                else:
                    role = 'unknown'
                
                agent_roles[role] = agent_roles.get(role, 0) + 1
            
            print(f"   📊 Total Claude Examples: {total_examples:,}")
            print(f"   🤖 Agent Specialization:")
            for role, count in sorted(agent_roles.items()):
                percentage = (count / total_examples) * 100
                print(f"      - {role}: {count:,} ({percentage:.1f}%)")
            
            # Analyze message structure
            message_counts = []
            for example in claude_examples[:100]:  # Sample first 100
                messages = example.get('messages', [])
                message_counts.append(len(messages))
            
            avg_messages = sum(message_counts) / len(message_counts) if message_counts else 0
            print(f"   💬 Average Messages per Example: {avg_messages:.1f}")
            
        else:
            print("   ❌ Claude training data not found")
            
    except Exception as e:
        print(f"   ❌ Claude analysis failed: {e}")
    
    # Claude API configuration
    print("\n🔑 Claude API Configuration:")
    
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    if anthropic_key:
        print(f"   ✅ ANTHROPIC_API_KEY: {'*' * 8}...{anthropic_key[-4:]}")
        api_configured = True
    else:
        print(f"   ❌ ANTHROPIC_API_KEY: Not set")
        api_configured = False
    
    # Claude training readiness
    print("\n🎯 Claude Training Readiness:")
    
    readiness_checks = [
        ("Claude Training Data", all(Path(f).exists() for f in claude_files)),
        ("Anthropic API Key", api_configured),
        ("Training Pipeline", Path("./claude_training_pipeline.py").exists()),
        ("Claude Formatter", Path("./src/voxel/training/fine_tuning/claude_formatter.py").exists()),
        ("Training Orchestrator", Path("./src/voxel/training/fine_tuning/training_orchestrator.py").exists())
    ]
    
    passed_checks = 0
    for check_name, status in readiness_checks:
        if status:
            passed_checks += 1
            print(f"   ✅ {check_name}")
        else:
            print(f"   ❌ {check_name}")
    
    readiness_percentage = (passed_checks / len(readiness_checks)) * 100
    print(f"   📊 Claude Readiness: {readiness_percentage:.1f}% ({passed_checks}/{len(readiness_checks)})")
    
    # Claude-specific optimizations
    print("\n🚀 Claude Sonnet 4.5 Optimizations:")
    
    claude_benefits = {
        "Reasoning": "Superior logical reasoning for complex 3D scenes",
        "Context": "200k token context window for large Blender scripts",
        "Code Quality": "Enhanced Python code generation and error handling",
        "Multi-Agent": "Specialized agents for different 3D tasks",
        "Blender API": "Deep understanding of bpy, bmesh, and modifiers",
        "Performance": "Faster inference and better memory efficiency"
    }
    
    for benefit, description in claude_benefits.items():
        print(f"   🎯 {benefit}: {description}")
    
    # Training cost estimation for Claude
    print("\n💰 Claude Training Cost Estimation:")
    
    try:
        if claude_size > 0:
            # Estimate tokens (rough approximation: 4 chars = 1 token)
            estimated_tokens = claude_size // 4
            
            # Claude fine-tuning pricing (estimated)
            # Note: Anthropic's actual pricing may vary
            estimated_cost = (estimated_tokens / 1000) * 0.01  # $0.01 per 1K tokens
            
            print(f"   📊 Training Data: {claude_size:,} bytes")
            print(f"   🎯 Estimated Tokens: {estimated_tokens:,}")
            print(f"   💰 Estimated Cost: ${estimated_cost:.2f}")
            print(f"   🤖 Model: Claude Sonnet 4.5")
            print(f"   ⏱️ Estimated Training Time: 1-4 hours")
            
    except Exception as e:
        print(f"   ❌ Cost estimation failed: {e}")
    
    # Next steps for Claude
    print("\n🎯 Next Steps for Claude Sonnet 4.5:")
    
    if not api_configured:
        print("   1. Set Anthropic API key: export ANTHROPIC_API_KEY='your-key'")
        print("   2. Run Claude training: python3 claude_training_pipeline.py")
    else:
        print("   1. Run Claude training: python3 claude_training_pipeline.py")
        print("   2. Monitor training progress")
        print("   3. Test fine-tuned models")
        print("   4. Deploy to production")
    
    print("\n🔧 Claude-specific commands:")
    print("   📊 Check status: python3 claude_status.py")
    print("   🚀 Start training: python3 claude_training_pipeline.py")
    print("   📈 Monitor jobs: python3 -c \"from src.voxel.training.fine_tuning.training_orchestrator import TrainingOrchestrator; o = TrainingOrchestrator(); print(o.monitor_all_jobs())\"")
    
    # Final status
    print(f"\n🎉 Claude Sonnet 4.5 Status Complete!")
    print(f"Generated at: {datetime.now().isoformat()}")
    
    if readiness_percentage >= 80:
        print("🚀 Claude Sonnet 4.5 is ready for training!")
    elif readiness_percentage >= 60:
        print("⚠️ Claude setup mostly complete, minor configuration needed")
    else:
        print("❌ Claude setup needs completion before training")

if __name__ == "__main__":
    main()
