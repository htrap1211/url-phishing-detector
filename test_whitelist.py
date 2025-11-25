import requests
import json

API_URL = "http://localhost:8000/api/v1/url/check"

def test_whitelist():
    urls = [
        "https://www.google.com/search?q=phishing+test",
        "https://github.com/htrap1211/url-phishing-detector",
        "http://paypal-secure-login.com/verify"  # Should still be malicious/suspicious
    ]
    
    for url in urls:
        print(f"Checking {url}...")
        try:
            response = requests.post(API_URL, json={"url": url})
            if response.status_code == 200:
                data = response.json()
                check_id = data["check_id"]
                
                # Get result
                result_response = requests.get(f"http://localhost:8000/api/v1/url/{check_id}")
                result = result_response.json()
                
                print(f"Verdict: {result['verdict']}")
                print(f"Confidence: {result['confidence']}")
                print("-" * 30)
            else:
                print(f"Error: {response.status_code}")
        except Exception as e:
            print(f"Failed: {e}")

if __name__ == "__main__":
    test_whitelist()
