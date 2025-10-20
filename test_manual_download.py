#!/usr/bin/env python3
"""
Manual Download Test
Tests download functionality with a specific session that has files.
"""

import requests
import json
from pathlib import Path

def test_manual_download():
    """Test download functionality with a specific session."""
    
    print("🔗 Manual Download Test")
    print("=" * 30)
    
    base_url = "http://localhost:5005"
    session_id = "9378e793-8257-4c20-9ed4-65b89531ceb8"  # Session with files
    
    print(f"Testing session: {session_id}")
    
    # Test 1: Check session status
    print(f"\n📊 Test 1: Session Status")
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
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Session status error: {e}")
        return False
    
    # Test 2: Test blend download
    print(f"\n🎨 Test 2: Blend File Download")
    try:
        response = requests.get(f"{base_url}/api/download/{session_id}/blend", timeout=10)
        print(f"   Status Code: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('Content-Type')}")
        print(f"   Content-Length: {len(response.content)} bytes")
        
        if response.status_code == 200:
            print("✅ Blend file download successful")
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
    
    # Test 3: Test scripts download
    print(f"\n📄 Test 3: Scripts Download")
    try:
        response = requests.get(f"{base_url}/api/download/{session_id}/scripts", timeout=10)
        print(f"   Status Code: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('Content-Type')}")
        print(f"   Content-Length: {len(response.content)} bytes")
        
        if response.status_code == 200:
            print("✅ Scripts download successful")
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
    
    # Test 4: Test render download
    print(f"\n🖼️ Test 4: Render Download")
    try:
        response = requests.get(f"{base_url}/api/download/{session_id}/render", timeout=10)
        print(f"   Status Code: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('Content-Type')}")
        print(f"   Content-Length: {len(response.content)} bytes")
        
        if response.status_code == 200:
            print("✅ Render download successful")
            # Save the file
            with open("test_download_render.png", "wb") as f:
                f.write(response.content)
            print("   File saved as: test_download_render.png")
        else:
            print(f"❌ Render download failed")
            try:
                error_data = response.json()
                print(f"   Error: {error_data.get('error', 'Unknown error')}")
            except:
                print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Render download error: {e}")
    
    print(f"\n🎯 Manual download test complete!")

if __name__ == "__main__":
    test_manual_download()
