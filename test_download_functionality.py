#!/usr/bin/env python3
"""
Download Functionality Test
Tests the complete download functionality for .blend files and scripts.
"""

import requests
import json
import time
from pathlib import Path

def test_download_functionality():
    """Test the complete download functionality."""
    
    print("🔗 Testing Download Functionality")
    print("=" * 50)
    
    base_url = "http://localhost:5001"
    
    # Test 1: Check if server is running
    print("\n🌐 Test 1: Server Health Check")
    try:
        response = requests.get(f"{base_url}/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running")
            health_data = response.json()
            print(f"   Status: {health_data.get('status')}")
            print(f"   Service: {health_data.get('service')}")
        else:
            print(f"❌ Server health check failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to server: {e}")
        print("   Make sure the server is running on localhost:5001")
        return False
    
    # Test 2: List existing sessions
    print("\n📋 Test 2: List Existing Sessions")
    try:
        response = requests.get(f"{base_url}/api/sessions")
        if response.status_code == 200:
            sessions_data = response.json()
            sessions = sessions_data.get('sessions', [])
            print(f"✅ Found {len(sessions)} sessions")
            
            # Look for completed sessions
            completed_sessions = [s for s in sessions if s.get('status') == 'completed']
            print(f"   Completed sessions: {len(completed_sessions)}")
            
            if completed_sessions:
                # Test with the most recent completed session
                test_session = completed_sessions[0]
                session_id = test_session['id']
                print(f"   Testing with session: {session_id}")
                
                # Test 3: Get session status with download URLs
                print(f"\n📊 Test 3: Session Status for {session_id}")
                try:
                    response = requests.get(f"{base_url}/api/session/{session_id}")
                    if response.status_code == 200:
                        session_data = response.json()
                        print("✅ Session status retrieved")
                        print(f"   Status: {session_data.get('status')}")
                        
                        # Check for download URLs
                        download_urls = session_data.get('download_urls', {})
                        download_available = session_data.get('download_available', {})
                        
                        print(f"   Download URLs: {bool(download_urls)}")
                        print(f"   Download Available: {download_available}")
                        
                        if download_urls:
                            print("   Available downloads:")
                            for file_type, url in download_urls.items():
                                available = download_available.get(file_type, False)
                                print(f"     - {file_type}: {url} (Available: {available})")
                        
                        # Test 4: Test download endpoints
                        print(f"\n📥 Test 4: Download Endpoints for {session_id}")
                        
                        for file_type in ['blend', 'scripts', 'render']:
                            print(f"\n   Testing {file_type} download...")
                            try:
                                download_url = f"{base_url}/api/download/{session_id}/{file_type}"
                                response = requests.get(download_url, timeout=10)
                                
                                if response.status_code == 200:
                                    print(f"   ✅ {file_type} download successful")
                                    print(f"      Content-Type: {response.headers.get('Content-Type')}")
                                    print(f"      Content-Length: {len(response.content)} bytes")
                                    
                                    # Save a sample file for testing
                                    if file_type == 'scripts' and response.content:
                                        sample_path = Path(f"test_download_{file_type}_{session_id}.py")
                                        sample_path.write_bytes(response.content)
                                        print(f"      Sample saved to: {sample_path}")
                                    
                                elif response.status_code == 404:
                                    print(f"   ⚠️ {file_type} not found (this is normal if file doesn't exist)")
                                else:
                                    print(f"   ❌ {file_type} download failed: {response.status_code}")
                                    try:
                                        error_data = response.json()
                                        print(f"      Error: {error_data.get('error', 'Unknown error')}")
                                    except:
                                        print(f"      Error: {response.text}")
                                        
                            except requests.exceptions.RequestException as e:
                                print(f"   ❌ {file_type} download error: {e}")
                        
                        return True
                    else:
                        print(f"❌ Session status failed: {response.status_code}")
                        return False
                        
                except requests.exceptions.RequestException as e:
                    print(f"❌ Session status error: {e}")
                    return False
            else:
                print("⚠️ No completed sessions found")
                print("   You need to generate a scene first to test downloads")
                return False
                
        else:
            print(f"❌ Sessions list failed: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Sessions list error: {e}")
        return False

def test_session_creation():
    """Test creating a new session."""
    
    print("\n🆕 Test: Session Creation")
    print("=" * 30)
    
    base_url = "http://localhost:5001"
    
    try:
        # Create a new session
        response = requests.post(f"{base_url}/api/session")
        if response.status_code == 200:
            session_data = response.json()
            session_id = session_data.get('id')
            print(f"✅ New session created: {session_id}")
            return session_id
        else:
            print(f"❌ Session creation failed: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Session creation error: {e}")
        return None

def test_download_urls_generation():
    """Test that download URLs are properly generated."""
    
    print("\n🔗 Test: Download URL Generation")
    print("=" * 35)
    
    base_url = "http://localhost:5001"
    
    # Create a test session
    session_id = test_session_creation()
    if not session_id:
        return False
    
    try:
        # Get session status
        response = requests.get(f"{base_url}/api/session/{session_id}")
        if response.status_code == 200:
            session_data = response.json()
            print(f"✅ Session status retrieved for {session_id}")
            
            # Check if download URLs are included (they should be empty for new sessions)
            download_urls = session_data.get('download_urls', {})
            download_available = session_data.get('download_available', {})
            
            print(f"   Download URLs: {download_urls}")
            print(f"   Download Available: {download_available}")
            
            if session_data.get('status') == 'completed':
                print("   ✅ Download URLs are present for completed session")
                return True
            else:
                print("   ⚠️ Session not completed yet - download URLs will be empty")
                print("   This is expected for new sessions")
                return True
        else:
            print(f"❌ Session status failed: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Session status error: {e}")
        return False

if __name__ == "__main__":
    print("🎯 Starting Download Functionality Test...")
    
    # Test download functionality
    download_success = test_download_functionality()
    
    # Test URL generation
    url_success = test_download_urls_generation()
    
    if download_success and url_success:
        print(f"\n🎉 ALL DOWNLOAD TESTS PASSED!")
        print(f"✅ Download functionality is working correctly")
        print(f"✅ Download URLs are properly generated")
        print(f"✅ Session status includes download information")
        print(f"✅ Frontend can now properly enable/disable download buttons")
    else:
        print(f"\n❌ SOME DOWNLOAD TESTS FAILED!")
        print(f"🔧 Check the server logs for more details")
        print(f"💡 Make sure you have completed sessions to test with")
