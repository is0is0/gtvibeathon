#!/usr/bin/env python3
"""
Quick Download Test
Tests the download functionality manually.
"""

import requests
import json

def test_download():
    """Test download functionality."""
    
    print("🧪 Quick Download Test")
    print("=" * 30)
    
    base_url = "http://localhost:5006"
    session_id = "9378e793-8257-4c20-9ed4-65b89531ceb8"
    
    print(f"Testing session: {session_id}")
    
    # Test 1: Check if server is running
    try:
        response = requests.get(f"{base_url}/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running")
        else:
            print(f"❌ Server health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        return False
    
    # Test 2: Get session status
    try:
        response = requests.get(f"{base_url}/api/session/{session_id}")
        if response.status_code == 200:
            session_data = response.json()
            print("✅ Session status retrieved")
            print(f"   Status: {session_data.get('status')}")
            print(f"   Download URLs: {session_data.get('download_urls', 'Not present')}")
            print(f"   Download Available: {session_data.get('download_available', 'Not present')}")
            
            # Check if download URLs are present
            if session_data.get('download_urls'):
                print("\n🎉 SUCCESS: Download URLs are being generated!")
                print("   This means the download functionality is working!")
                print("   The frontend can now use these URLs to enable download buttons.")
                
                # Show the URLs
                urls = session_data.get('download_urls', {})
                print(f"\n📥 Available Download URLs:")
                for file_type, url in urls.items():
                    print(f"   {file_type}: {url}")
                
                return True
            else:
                print("❌ Download URLs not found in session data")
                return False
        else:
            print(f"❌ Session status failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Session status error: {e}")
        return False

if __name__ == "__main__":
    test_download()
