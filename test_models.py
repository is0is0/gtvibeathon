#!/usr/bin/env python3
"""Test different Claude model names to find one that works."""

import os
from anthropic import Anthropic

def test_models():
    """Test different Claude model names."""
    api_key = "YOUR_ANTHROPIC_API_KEY_HERE"
    
    client = Anthropic(api_key=api_key)
    
    # Models to test
    models_to_test = [
        "claude-3-5-sonnet-20241022",
        "claude-3-5-sonnet-20241022", 
        "claude-3-5-sonnet-20241022",
        "claude-3-opus-20240229",
        "claude-3-sonnet-20240229",
        "claude-3-haiku-20240307"
    ]
    
    print("🔍 Testing Claude model names...")
    print()
    
    for model in models_to_test:
        try:
            print(f"Testing {model}...")
            response = client.messages.create(
                model=model,
                max_tokens=10,
                messages=[{"role": "user", "content": "Hello"}]
            )
            print(f"✅ {model} - WORKS!")
            print(f"   Response: {response.content[0].text[:50]}...")
            return model
        except Exception as e:
            print(f"❌ {model} - {str(e)[:100]}...")
    
    print()
    print("❌ No working models found. Check your API key permissions.")
    return None

if __name__ == "__main__":
    working_model = test_models()
    if working_model:
        print(f"\n🎉 Use this model: {working_model}")
        print(f"Add to .env: AI_MODEL={working_model}")
