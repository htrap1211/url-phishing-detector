#!/usr/bin/env python3
"""
Test script for URL Phishing Detection API.
"""
import requests
import json
import time

API_BASE = "http://localhost:8000"


def test_health():
    """Test health endpoint."""
    print("Testing /health endpoint...")
    response = requests.get(f"{API_BASE}/health")
    print(f"  Status: {response.status_code}")
    print(f"  Response: {json.dumps(response.json(), indent=2)}")
    print()


def test_url_check(url):
    """Test URL check endpoint."""
    print(f"Testing URL: {url}")
    
    # Submit URL
    response = requests.post(
        f"{API_BASE}/api/v1/url/check",
        json={"url": url}
    )
    
    print(f"  Submit Status: {response.status_code}")
    result = response.json()
    print(f"  Check ID: {result['check_id']}")
    print(f"  Status: {result['status']}")
    print()
    
    # Get result
    check_id = result['check_id']
    response = requests.get(f"{API_BASE}/api/v1/url/{check_id}")
    
    print(f"  Result Status: {response.status_code}")
    result = response.json()
    print(f"  Verdict: {result['verdict']}")
    print(f"  Confidence: {result['confidence']:.2%}")
    print(f"  Top Features:")
    for feature in result['top_features'][:3]:
        print(f"    - {feature['name']}: {feature['value']:.2f} (importance: {feature['contribution']:.3f})")
    print()


def test_stats():
    """Test stats endpoint."""
    print("Testing /stats endpoint...")
    response = requests.get(f"{API_BASE}/api/v1/url/stats")
    print(f"  Status: {response.status_code}")
    result = response.json()
    print(f"  Total Checks: {result['total_checks']}")
    print(f"  Verdict Distribution: {result['verdict_distribution']}")
    print()


def main():
    print("="*60)
    print("URL Phishing Detection API - Test Script")
    print("="*60)
    print()
    
    # Test health
    try:
        test_health()
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        print("Make sure the backend is running: ./run_backend.sh")
        return
    
    # Test benign URLs
    print("Testing Benign URLs:")
    print("-" * 60)
    test_url_check("https://google.com")
    test_url_check("https://github.com")
    
    # Test suspicious URLs
    print("Testing Suspicious URLs:")
    print("-" * 60)
    test_url_check("http://paypal-secure-login-verify-account.com/update")
    test_url_check("http://192.168.1.1/login.php?redirect=secure")
    
    # Test stats
    test_stats()
    
    print("="*60)
    print("✅ All tests complete!")
    print("="*60)


if __name__ == "__main__":
    main()
