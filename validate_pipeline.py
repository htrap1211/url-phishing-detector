import requests
import pandas as pd
import random
import time
from tabulate import tabulate

API_URL = "http://localhost:8000/api/v1/url/check"
TEST_DATA_PATH = "data/processed/test.csv"

def validate_pipeline():
    print("🚀 Starting Real World Validation Pipeline...")
    
    # 1. Load Test Data
    try:
        df = pd.read_csv(TEST_DATA_PATH)
        print(f"✅ Loaded {len(df)} URLs from test set")
    except Exception as e:
        print(f"❌ Failed to load test data: {e}")
        return

    # 2. Select Sample
    # Get 10 benign and 10 phishing
    benign_sample = df[df['label'] == 0].sample(n=min(10, len(df[df['label'] == 0])), random_state=42)
    phishing_sample = df[df['label'] == 1].sample(n=min(10, len(df[df['label'] == 1])), random_state=42)
    
    sample = pd.concat([benign_sample, phishing_sample])
    print(f"🧪 Testing {len(sample)} URLs ({len(benign_sample)} Benign, {len(phishing_sample)} Phishing)")
    
    results = []
    correct_count = 0
    
    print("\nProcessing...", end="", flush=True)
    
    for _, row in sample.iterrows():
        url = row['url']
        expected_label = "malicious" if row['label'] == 1 else "benign"
        
        try:
            # Call API
            response = requests.post(API_URL, json={"url": url})
            if response.status_code == 200:
                check_id = response.json()["check_id"]
                
                # Get result
                res = requests.get(f"http://localhost:8000/api/v1/url/{check_id}").json()
                
                verdict = res['verdict']
                confidence = res['confidence']
                top_features = [f['name'] for f in res.get('top_features', [])[:2]]
                additional_info = res.get('additional_info', {})
                
                # Normalize verdict for comparison
                # "suspicious" counts as "malicious" for phishing URLs
                normalized_verdict = verdict
                if verdict == "suspicious":
                    normalized_verdict = "malicious"
                
                is_correct = (normalized_verdict == expected_label)
                if is_correct:
                    correct_count += 1
                
                results.append([
                    url[:40] + "..." if len(url) > 40 else url,
                    expected_label,
                    verdict,
                    f"{confidence:.2f}",
                    ", ".join(top_features),
                    "✅" if is_correct else "❌",
                    additional_info.get('domain_age_days', 'N/A'),
                    "HTTPS" if additional_info.get('is_https') else "HTTP"
                ])
                print(".", end="", flush=True)
            else:
                print("E", end="", flush=True)
        except Exception as e:
            print("F", end="", flush=True)
            
    print("\n")
    
    # 3. Print Results
    headers = ["URL", "Expected", "Verdict", "Conf", "Top Features", "Correct", "Age (Days)", "Protocol"]
    print(tabulate(results, headers=headers, tablefmt="grid"))
    
    accuracy = (correct_count / len(sample)) * 100
    print(f"\n🏆 Overall Accuracy: {accuracy:.1f}%")
    
    # 4. Test Heuristics specifically
    print("\n🔍 Testing Special Heuristics:")
    heuristic_tests = [
        ("http://g0ogle.com", "malicious", "impersonates_google"),
        ("https://www.google.com", "benign", "is_whitelisted"),
        ("http://paypal-secure.com", "malicious", "impersonates_paypal"),
        ("http://non-existent-domain-123.com", "malicious", "invalid_dns")
    ]
    
    for url, expected, feature in heuristic_tests:
        try:
            res = requests.post(API_URL, json={"url": url}).json()
            check_id = res["check_id"]
            res = requests.get(f"http://localhost:8000/api/v1/url/{check_id}").json()
            
            verdict = res['verdict']
            top_features = [f['name'] for f in res.get('top_features', [])]
            add_info = res.get('additional_info', {})
            
            success = False
            if feature == "is_whitelisted":
                if add_info.get('is_whitelisted'):
                    success = True
            elif any(feature in f for f in top_features):
                success = True
                
            print(f"  {url:<35} -> {verdict:<10} [{'✅' if success else '❌'}] (Expected: {feature})")
            
        except Exception as e:
            print(f"  {url:<35} -> ERROR: {e}")

if __name__ == "__main__":
    validate_pipeline()
