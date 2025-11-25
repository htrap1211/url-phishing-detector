import requests
import json

API_URL = "http://localhost:8000/api/v1/url/check"

def test_advanced_features():
    tests = [
        {
            "name": "Brand Impersonation (Typosquatting)",
            "url": "http://g0ogle.com/login",
            "expected_verdict": "malicious",
            "expected_feature": "impersonates_google"
        },
        {
            "name": "Brand Impersonation (Keyword)",
            "url": "http://paypal-secure-update.com",
            "expected_verdict": "malicious",
            "expected_feature": "impersonates_paypal"
        },
        {
            "name": "Invalid DNS",
            "url": "http://this-domain-definitely-does-not-exist-12345.com",
            "expected_verdict": "malicious",
            "expected_feature": "invalid_dns"
        },
        {
            "name": "Legitimate Site (Should pass)",
            "url": "https://www.google.com",
            "expected_verdict": "benign",
            "expected_feature": None
        }
    ]
    
    print("🧪 Testing Advanced Features...")
    print("=" * 50)
    
    for test in tests:
        print(f"Testing: {test['name']}")
        print(f"URL: {test['url']}")
        try:
            response = requests.post(API_URL, json={"url": test['url']})
            if response.status_code == 200:
                data = response.json()
                check_id = data["check_id"]
                
                # Get result
                result_response = requests.get(f"http://localhost:8000/api/v1/url/{check_id}")
                result = result_response.json()
                
                print(f"Verdict: {result['verdict']}")
                print(f"Confidence: {result['confidence']}")
                
                # Check features
                top_features = [f['name'] for f in result['top_features']]
                print(f"Top Features: {top_features}")
                
                if test['expected_feature']:
                    if any(test['expected_feature'] in f for f in top_features):
                        print("✅ Feature detected")
                    else:
                        print(f"❌ Feature NOT detected (Expected {test['expected_feature']})")
                
                if result['verdict'] == test['expected_verdict']:
                    print("✅ Verdict matches")
                else:
                    print(f"❌ Verdict mismatch (Expected {test['expected_verdict']})")
                    
            else:
                print(f"Error: {response.status_code}")
        except Exception as e:
            print(f"Failed: {e}")
        print("-" * 50)

if __name__ == "__main__":
    test_advanced_features()
