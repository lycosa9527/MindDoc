#!/usr/bin/env python3
"""
Test script to verify all routes work correctly
"""

import requests
import json
import os
from dotenv import load_dotenv

def test_routes():
    """Test all application routes"""
    
    # Load environment variables
    load_dotenv()
    
    base_url = "http://localhost:5000"
    
    print("Testing MindDoc Routes")
    print("=" * 30)
    
    tests = [
        test_main_page,
        test_upload_route,
        test_status_route,
        test_api_route
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test(base_url):
                passed += 1
        except Exception as e:
            print(f"❌ {test.__name__}: {str(e)}")
    
    print(f"\nRoute Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All routes are working correctly!")
    else:
        print("❌ Some routes failed. Check the application logs.")

def test_main_page(base_url):
    """Test the main page route"""
    print("Testing main page...")
    
    response = requests.get(base_url, timeout=5)
    
    if response.status_code == 200:
        print("✅ Main page loads successfully")
        return True
    else:
        print(f"❌ Main page failed: {response.status_code}")
        return False

def test_upload_route(base_url):
    """Test the upload route"""
    print("Testing upload route...")
    
    # Test with no file
    response = requests.post(f"{base_url}/upload", timeout=5)
    
    if response.status_code == 400:
        print("✅ Upload route correctly rejects missing file")
        return True
    else:
        print(f"❌ Upload route unexpected response: {response.status_code}")
        return False

def test_status_route(base_url):
    """Test the status route"""
    print("Testing status route...")
    
    # Test with invalid job ID
    response = requests.get(f"{base_url}/status/invalid-job-id", timeout=5)
    
    if response.status_code == 200:
        data = response.json()
        if data.get('status') == 'unknown':
            print("✅ Status route handles invalid job IDs correctly")
            return True
        else:
            print("❌ Status route unexpected response format")
            return False
    else:
        print(f"❌ Status route failed: {response.status_code}")
        return False

def test_api_route(base_url):
    """Test the API route"""
    print("Testing API route...")
    
    # Test with invalid data
    response = requests.post(
        f"{base_url}/api/update-paragraph",
        json={},
        headers={'Content-Type': 'application/json'},
        timeout=5
    )
    
    if response.status_code == 400:
        print("✅ API route correctly validates input")
        return True
    else:
        print(f"❌ API route unexpected response: {response.status_code}")
        return False

def main():
    """Main test function"""
    print("Make sure the application is running on http://localhost:5000")
    print("Run: python run.py")
    print()
    
    try:
        test_routes()
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to application. Make sure it's running on http://localhost:5000")
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")

if __name__ == "__main__":
    main() 