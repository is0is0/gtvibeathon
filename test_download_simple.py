#!/usr/bin/env python3
"""
Simple Download Test
Tests the download functionality with a specific session.
"""

import requests
import json
import time

def test_download():
    """Test download functionality."""
    
    print("🧪 Testing Download Functionality")
    print("=" * 40)
    
    base_url = "http://localhost:5006"
    session_id = "9378e793-8257-4c20-9ed4-65b89531ceb8"  # Session with files
    
    print(f"Testing session: {session_id}")
    print(f"Server URL: {base_url}")
    
    # Wait for server to start
    print("\n⏳ Waiting for server to start...")
    time.sleep(3)
    
    # Test 1: Health check
    print("\n🏥 Test 1: Server Health Check")
    try:
        response = requests.get(f"{base_url}/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running")
        else:
            print(f"❌ Server health check failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to server: {e}")
        print("   Make sure the server is running on port 5006")
        return False
    
    # Test 2: Session status
    print(f"\n📊 Test 2: Session Status")
    try:
        response = requests.get(f"{base_url}/api/session/{session_id}")
        if response.status_code == 200:
            session_data = response.json()
            print("✅ Session status retrieved")
            print(f"   Status: {session_data.get('status')}")
            print(f"   Download URLs: {session_data.get('download_urls', 'Not present')}")
            print(f"   Download Available: {session_data.get('download_available', 'Not present')}")
        else:
            print(f"❌ Session status failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Session status error: {e}")
        return False
    
    # Test 3: Download blend file
    print(f"\n🎨 Test 3: Download Blend File")
    try:
        response = requests.get(f"{base_url}/api/download/{session_id}/blend", timeout=10)
        print(f"   Status Code: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('Content-Type')}")
        print(f"   Content-Length: {len(response.content)} bytes")
        
        if response.status_code == 200:
            print("✅ Blend file download successful!")
            # Save the file
            with open("test_download.blend", "wb") as f:
                f.write(response.content)
            print("   File saved as: test_download.blend")
        else:
            print(f"❌ Blend download failed")
            try:
                error_data = response.json()
                print(f"   Error: {error_data.get('error', 'Unknown error')}")
            except:
                print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Blend download error: {e}")
    
    # Test 4: Download scripts
    print(f"\n📄 Test 4: Download Scripts")
    try:
        response = requests.get(f"{base_url}/api/download/{session_id}/scripts", timeout=10)
        print(f"   Status Code: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('Content-Type')}")
        print(f"   Content-Length: {len(response.content)} bytes")
        
        if response.status_code == 200:
            print("✅ Scripts download successful!")
            # Save the file
            with open("test_download_scripts.py", "wb") as f:
                f.write(response.content)
            print("   File saved as: test_download_scripts.py")
        else:
            print(f"❌ Scripts download failed")
            try:
                error_data = response.json()
                print(f"   Error: {error_data.get('error', 'Unknown error')}")
            except:
                print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Scripts download error: {e}")
    
    print(f"\n🎯 Download test complete!")
    return True

if __name__ == "__main__":
    test_download()
