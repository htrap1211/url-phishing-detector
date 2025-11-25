# Feature Engineering Guide

## Overview

The URL Phishing Detection System uses **25 engineered features** across 4 categories to classify URLs. This document details each feature, its rationale, extraction method, and expected distribution.

## Feature Categories

1. **Lexical Features** (10): Extracted from URL string analysis
2. **Host-Based Features** (8): Derived from domain/hosting information
3. **Content-Based Features** (3): Extracted from page content (optional)
4. **Threat-Intel Features** (4): From external threat intelligence APIs

---

## 1. Lexical Features

These features analyze the URL string structure without external API calls.

### 1.1 URL Length
- **Feature Name**: `url_length`
- **Type**: Integer
- **Rationale**: Phishing URLs are often longer due to obfuscation, subdomains, or query parameters
- **Extraction**:
  ```python
  url_length = len(url)
  ```
- **Expected Distribution**:
  - Benign: 20-60 characters (median ~35)
  - Phishing: 40-150 characters (median ~75)
- **Threshold**: >75 characters → suspicious

### 1.2 Number of Dots in Domain
- **Feature Name**: `domain_dots`
- **Type**: Integer
- **Rationale**: Excessive subdomains (e.g., `login.secure.paypal.phishing.com`) indicate typosquatting
- **Extraction**:
  ```python
  from urllib.parse import urlparse
  domain = urlparse(url).netloc
  domain_dots = domain.count('.')
  ```
- **Expected Distribution**:
  - Benign: 1-2 dots (e.g., `example.com`, `www.example.com`)
  - Phishing: 3+ dots
- **Threshold**: >3 dots → suspicious

### 1.3 Number of Hyphens
- **Feature Name**: `hyphen_count`
- **Type**: Integer
- **Rationale**: Hyphens are rare in legitimate domains but common in phishing (e.g., `pay-pal-secure.com`)
- **Extraction**:
  ```python
  hyphen_count = url.count('-')
  ```
- **Expected Distribution**:
  - Benign: 0-1 hyphens
  - Phishing: 2+ hyphens
- **Threshold**: >2 hyphens → suspicious

### 1.4 Path Depth
- **Feature Name**: `path_depth`
- **Type**: Integer
- **Rationale**: Deep paths may hide malicious intent (e.g., `/login/secure/verify/account`)
- **Extraction**:
  ```python
  path = urlparse(url).path
  path_depth = len([p for p in path.split('/') if p])
  ```
- **Expected Distribution**:
  - Benign: 0-2 levels
  - Phishing: 3+ levels
- **Threshold**: >3 levels → suspicious

### 1.5 Query Parameter Count
- **Feature Name**: `query_param_count`
- **Type**: Integer
- **Rationale**: Excessive parameters may indicate session hijacking or tracking
- **Extraction**:
  ```python
  from urllib.parse import parse_qs
  query = urlparse(url).query
  query_param_count = len(parse_qs(query))
  ```
- **Expected Distribution**:
  - Benign: 0-3 parameters
  - Phishing: 4+ parameters (often with encoded data)

### 1.6 Digit-to-Character Ratio
- **Feature Name**: `digit_ratio`
- **Type**: Float (0.0-1.0)
- **Rationale**: High digit ratios suggest IP addresses or random strings
- **Extraction**:
  ```python
  digits = sum(c.isdigit() for c in url)
  digit_ratio = digits / len(url) if len(url) > 0 else 0
  ```
- **Expected Distribution**:
  - Benign: <0.1
  - Phishing: >0.2 (especially if IP-based)

### 1.7 IP Address in Host
- **Feature Name**: `has_ip_address`
- **Type**: Boolean (0/1)
- **Rationale**: Legitimate sites use domain names, not raw IPs
- **Extraction**:
  ```python
  import re
  domain = urlparse(url).netloc
  ip_pattern = r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'
  has_ip_address = 1 if re.search(ip_pattern, domain) else 0
  ```
- **Expected Distribution**:
  - Benign: 0 (rare exceptions: internal tools)
  - Phishing: 1 (common for quick setups)

### 1.8 Character Entropy
- **Feature Name**: `char_entropy`
- **Type**: Float
- **Rationale**: Random strings (e.g., `a3k9xz.com`) have high entropy
- **Extraction**:
  ```python
  from collections import Counter
  import math
  
  def shannon_entropy(s):
      counts = Counter(s)
      probs = [count / len(s) for count in counts.values()]
      return -sum(p * math.log2(p) for p in probs)
  
  char_entropy = shannon_entropy(urlparse(url).netloc)
  ```
- **Expected Distribution**:
  - Benign: 2.5-3.5 (dictionary words)
  - Phishing: >4.0 (random strings)

### 1.9 Suspicious Keyword Count
- **Feature Name**: `suspicious_keywords`
- **Type**: Integer
- **Rationale**: Keywords like "login", "secure", "verify" are common in phishing
- **Extraction**:
  ```python
  keywords = ['login', 'secure', 'account', 'verify', 'update', 
              'confirm', 'banking', 'paypal', 'ebay', 'amazon']
  url_lower = url.lower()
  suspicious_keywords = sum(1 for kw in keywords if kw in url_lower)
  ```
- **Expected Distribution**:
  - Benign: 0-1 keywords
  - Phishing: 2+ keywords

### 1.10 URL Shortener Detection
- **Feature Name**: `is_shortened`
- **Type**: Boolean (0/1)
- **Rationale**: Shortened URLs hide the true destination
- **Extraction**:
  ```python
  shorteners = ['bit.ly', 'goo.gl', 'tinyurl.com', 't.co', 'ow.ly']
  domain = urlparse(url).netloc
  is_shortened = 1 if any(s in domain for s in shorteners) else 0
  ```
- **Expected Distribution**:
  - Benign: 0 (unless legitimate marketing)
  - Phishing: 1 (common for obfuscation)

---

## 2. Host-Based Features

These features require WHOIS, DNS, and SSL certificate data.

### 2.1 Domain Age (Days)
- **Feature Name**: `domain_age_days`
- **Type**: Integer
- **Rationale**: Newly registered domains are often used for phishing
- **Extraction**:
  ```python
  import whois
  from datetime import datetime
  
  w = whois.whois(domain)
  creation_date = w.creation_date
  if isinstance(creation_date, list):
      creation_date = creation_date[0]
  domain_age_days = (datetime.now() - creation_date).days
  ```
- **Expected Distribution**:
  - Benign: >365 days (established sites)
  - Phishing: <30 days (fresh registrations)
- **Threshold**: <30 days → high risk

### 2.2 Domain Registration Length (Years)
- **Feature Name**: `registration_length_years`
- **Type**: Float
- **Rationale**: Legitimate businesses register domains for multiple years
- **Extraction**:
  ```python
  expiration_date = w.expiration_date
  if isinstance(expiration_date, list):
      expiration_date = expiration_date[0]
  registration_length_years = (expiration_date - creation_date).days / 365
  ```
- **Expected Distribution**:
  - Benign: 1-10 years
  - Phishing: <1 year (short-term)

### 2.3 HTTPS Enabled
- **Feature Name**: `has_https`
- **Type**: Boolean (0/1)
- **Rationale**: HTTPS is standard for legitimate sites (but phishing sites can also use it)
- **Extraction**:
  ```python
  has_https = 1 if urlparse(url).scheme == 'https' else 0
  ```
- **Expected Distribution**:
  - Benign: 1 (>90% of sites)
  - Phishing: Mixed (50% use HTTPS now)

### 2.4 Valid SSL Certificate
- **Feature Name**: `valid_ssl`
- **Type**: Boolean (0/1)
- **Rationale**: Self-signed or expired certificates indicate risk
- **Extraction**:
  ```python
  import ssl
  import socket
  
  try:
      context = ssl.create_default_context()
      with socket.create_connection((domain, 443), timeout=5) as sock:
          with context.wrap_socket(sock, server_hostname=domain) as ssock:
              cert = ssock.getpeercert()
              valid_ssl = 1
  except:
      valid_ssl = 0
  ```
- **Expected Distribution**:
  - Benign: 1
  - Phishing: 0 (if self-signed)

### 2.5 Certificate Age (Days)
- **Feature Name**: `cert_age_days`
- **Type**: Integer
- **Rationale**: Newly issued certificates may indicate fresh phishing setup
- **Extraction**:
  ```python
  from datetime import datetime
  not_before = datetime.strptime(cert['notBefore'], '%b %d %H:%M:%S %Y %Z')
  cert_age_days = (datetime.now() - not_before).days
  ```
- **Expected Distribution**:
  - Benign: >30 days
  - Phishing: <7 days

### 2.6 Subdomain Count
- **Feature Name**: `subdomain_count`
- **Type**: Integer
- **Rationale**: Excessive subdomains suggest typosquatting
- **Extraction**:
  ```python
  parts = domain.split('.')
  subdomain_count = len(parts) - 2  # Exclude domain + TLD
  ```
- **Expected Distribution**:
  - Benign: 0-1 (e.g., `www`)
  - Phishing: 2+ (e.g., `login.secure.paypal`)

### 2.7 Hosting Country Risk
- **Feature Name**: `high_risk_country`
- **Type**: Boolean (0/1)
- **Rationale**: Some countries have higher phishing rates
- **Extraction**:
  ```python
  import geoip2.database
  
  reader = geoip2.database.Reader('GeoLite2-Country.mmdb')
  response = reader.country(ip_address)
  country_code = response.country.iso_code
  
  high_risk_countries = ['CN', 'RU', 'NG', 'VN', 'IN']  # Example list
  high_risk_country = 1 if country_code in high_risk_countries else 0
  ```
- **Note**: Use with caution to avoid bias

### 2.8 AS Number Reputation
- **Feature Name**: `as_reputation_score`
- **Type**: Float (0.0-1.0)
- **Rationale**: Some ASNs are known for hosting malicious content
- **Extraction**:
  ```python
  # Lookup AS number from IP
  # Cross-reference with known bad ASNs
  # Return reputation score (0=bad, 1=good)
  ```
- **Data Source**: Public ASN reputation lists

---

## 3. Content-Based Features

These features require fetching and parsing the page HTML (optional, slow).

### 3.1 HTML Form Count
- **Feature Name**: `form_count`
- **Type**: Integer
- **Rationale**: Phishing pages often have login forms
- **Extraction**:
  ```python
  import requests
  from bs4 import BeautifulSoup
  
  response = requests.get(url, timeout=5)
  soup = BeautifulSoup(response.content, 'html.parser')
  form_count = len(soup.find_all('form'))
  ```
- **Expected Distribution**:
  - Benign: 0-2 forms
  - Phishing: 1+ forms (credential theft)

### 3.2 Password Field Presence
- **Feature Name**: `has_password_field`
- **Type**: Boolean (0/1)
- **Rationale**: Password inputs on suspicious domains are red flags
- **Extraction**:
  ```python
  password_inputs = soup.find_all('input', {'type': 'password'})
  has_password_field = 1 if len(password_inputs) > 0 else 0
  ```

### 3.3 Brand Typosquatting
- **Feature Name**: `typosquatting_score`
- **Type**: Float (0.0-1.0)
- **Rationale**: Domains similar to popular brands (e.g., `paypa1.com`)
- **Extraction**:
  ```python
  from difflib import SequenceMatcher
  
  popular_brands = ['paypal', 'amazon', 'google', 'facebook', 'apple']
  domain_name = domain.split('.')[0]
  
  max_similarity = max(
      SequenceMatcher(None, domain_name, brand).ratio()
      for brand in popular_brands
  )
  typosquatting_score = max_similarity if max_similarity > 0.8 else 0
  ```
- **Threshold**: >0.85 similarity → likely typosquatting

---

## 4. Threat-Intel Features

These features aggregate data from external threat intelligence APIs.

### 4.1 Google Safe Browsing Flag
- **Feature Name**: `gsb_threat_type`
- **Type**: Categorical (0=safe, 1=malware, 2=social_engineering, 3=unwanted_software)
- **Rationale**: Authoritative threat database
- **Extraction**:
  ```python
  # Call GSB API
  # Map threat types to numeric codes
  ```
- **Expected Distribution**:
  - Benign: 0
  - Phishing: 2 (social engineering)

### 4.2 VirusTotal Positive Detections
- **Feature Name**: `vt_positives`
- **Type**: Integer (0-90)
- **Rationale**: Number of AV engines flagging the URL
- **Extraction**:
  ```python
  # Call VirusTotal API
  # Extract positives count
  ```
- **Expected Distribution**:
  - Benign: 0-1 (false positives)
  - Phishing: 5+ detections
- **Threshold**: >3 detections → malicious

### 4.3 Known Phishing List
- **Feature Name**: `in_phishing_list`
- **Type**: Boolean (0/1)
- **Rationale**: Direct match with known phishing databases
- **Extraction**:
  ```python
  # Check against PhishTank, OpenPhish databases
  ```

### 4.4 IP in Blocklist
- **Feature Name**: `ip_blocklisted`
- **Type**: Boolean (0/1)
- **Rationale**: IP reputation from public blocklists
- **Extraction**:
  ```python
  # Check IP against Spamhaus, SORBS, etc.
  ```

---

## Feature Importance (Expected)

Based on prior research, expected feature importance ranking:

1. **vt_positives** (0.18) - Strong signal
2. **gsb_threat_type** (0.15) - Authoritative
3. **domain_age_days** (0.12) - Very predictive
4. **suspicious_keywords** (0.10) - Common pattern
5. **has_ip_address** (0.08) - Clear indicator
6. **url_length** (0.07)
7. **char_entropy** (0.06)
8. **domain_dots** (0.05)
9. **typosquatting_score** (0.04)
10. **has_password_field** (0.03)
11. Others (0.12 combined)

---

## Feature Extraction Pipeline

```python
class FeatureExtractor:
    def extract_all(self, url: str, enrichment_data: dict) -> dict:
        features = {}
        
        # Lexical (fast)
        features.update(self.extract_lexical(url))
        
        # Host-based (requires enrichment)
        features.update(self.extract_host_based(url, enrichment_data))
        
        # Content-based (optional, slow)
        if enrichment_data.get('fetch_content'):
            features.update(self.extract_content_based(url))
        
        # Threat-intel (from enrichment)
        features.update(self.extract_threat_intel(enrichment_data))
        
        return features
```

---

## Feature Validation

### Unit Tests
- Test each extractor with known inputs
- Verify edge cases (empty URLs, malformed URLs)
- Check for exceptions and fallback values

### Distribution Analysis
- Plot histograms for benign vs. phishing
- Verify separation between classes
- Identify features with low variance (remove)

### Correlation Analysis
- Remove highly correlated features (>0.9)
- Example: `url_length` and `path_depth` may be correlated

---

## Feature Versioning

Track feature versions in model metadata:

```json
{
  "model_version": "v1.2.0",
  "feature_version": "v1.0",
  "features": [
    "url_length", "domain_dots", "hyphen_count", ...
  ],
  "feature_count": 25
}
```

When adding new features, increment `feature_version` and retrain.

---

## Future Feature Ideas

1. **JavaScript Obfuscation Score**: Detect heavily obfuscated scripts
2. **Redirect Chain Length**: Number of redirects before final page
3. **Favicon Similarity**: Compare favicon to known brands
4. **Page Load Time**: Slow pages may indicate compromised hosting
5. **Social Media Presence**: Legitimate sites have social profiles
6. **Domain Similarity to Alexa Top 1M**: Levenshtein distance
7. **TLD Risk Score**: `.tk`, `.ml`, `.ga` are high-risk TLDs
8. **WHOIS Privacy**: Hidden registrant info is suspicious
9. **Email in WHOIS**: Free email providers (Gmail) vs. corporate
10. **Historical DNS Changes**: Frequent IP changes indicate instability
