# Quick Start: First 3 Tasks

This guide walks you through the **first 3 concrete tasks** to get started with the URL Phishing Detection System.

---

## Task 1: Obtain API Keys (30 minutes)

### Google Safe Browsing API

1. **Create Google Cloud Project**
   ```
   1. Go to: https://console.cloud.google.com/
   2. Click "Select a project" → "New Project"
   3. Name: "phishing-detector"
   4. Click "Create"
   ```

2. **Enable Safe Browsing API**
   ```
   1. In the search bar, type "Safe Browsing API"
   2. Click "Safe Browsing API"
   3. Click "Enable"
   ```

3. **Create API Key**
   ```
   1. Go to "Credentials" (left sidebar)
   2. Click "Create Credentials" → "API Key"
   3. Copy the API key
   4. Click "Restrict Key" (recommended)
   5. Under "API restrictions", select "Safe Browsing API"
   6. Click "Save"
   ```

4. **Save API Key**
   ```bash
   cd url-phishing-detector
   echo "GOOGLE_SAFE_BROWSING_API_KEY=your_key_here" >> .env
   ```

**Free Tier Limits**: 10,000 requests/day

---

### VirusTotal API

1. **Sign Up**
   ```
   1. Go to: https://www.virustotal.com/gui/join-us
   2. Fill in email and password
   3. Verify email
   ```

2. **Get API Key**
   ```
   1. Log in to VirusTotal
   2. Click your profile icon (top right)
   3. Click "API Key"
   4. Copy the API key
   ```

3. **Save API Key**
   ```bash
   echo "VIRUSTOTAL_API_KEY=your_key_here" >> .env
   ```

**Free Tier Limits**: 4 requests/minute, 500 requests/day

---

### Verify API Keys

```bash
# Test Google Safe Browsing
curl "https://safebrowsing.googleapis.com/v4/threatMatches:find?key=YOUR_GSB_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "client": {"clientId": "test", "clientVersion": "1.0"},
    "threatInfo": {
      "threatTypes": ["MALWARE"],
      "platformTypes": ["ANY_PLATFORM"],
      "threatEntryTypes": ["URL"],
      "threatEntries": [{"url": "http://malware.testing.google.test/testing/malware/"}]
    }
  }'

# Expected: {"matches": [...]}

# Test VirusTotal
curl "https://www.virustotal.com/api/v3/domains/google.com" \
  -H "x-apikey: YOUR_VT_KEY"

# Expected: {"data": {...}}
```

✅ **Task 1 Complete** when both API keys are saved in `.env`

---

## Task 2: Collect Training Data (2-3 hours)

### Setup Data Directory

```bash
cd url-phishing-detector
mkdir -p data/{raw,processed}
mkdir -p data/scripts
```

### Create Data Collection Script

Create `data/scripts/collect_data.py`:

```python
#!/usr/bin/env python3
"""
Collect and prepare training data for URL phishing detection.
"""
import pandas as pd
import requests
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).parent.parent
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"

def download_phishing_urls(count=2500):
    """Download phishing URLs from PhishTank."""
    logger.info(f"Downloading {count} phishing URLs from PhishTank...")
    
    # PhishTank requires registration for API access
    # Alternative: Download verified phishing URLs CSV
    url = "http://data.phishtank.com/data/online-valid.csv"
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # Save raw data
        raw_file = RAW_DIR / "phishtank_raw.csv"
        raw_file.write_text(response.text)
        
        # Parse and sample
        df = pd.read_csv(raw_file)
        df = df.head(count)
        df['label'] = 1  # 1 = phishing
        df['source'] = 'phishtank'
        
        # Keep only URL and label
        df = df[['url', 'label', 'source']]
        
        logger.info(f"Downloaded {len(df)} phishing URLs")
        return df
        
    except Exception as e:
        logger.error(f"Failed to download phishing URLs: {e}")
        return pd.DataFrame()

def download_benign_urls(count=2500):
    """Download benign URLs from Tranco Top 1M."""
    logger.info(f"Downloading {count} benign URLs from Tranco...")
    
    try:
        # Download Tranco list
        url = "https://tranco-list.eu/top-1m.csv.zip"
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # Save and extract
        zip_file = RAW_DIR / "tranco.csv.zip"
        zip_file.write_bytes(response.content)
        
        # Read CSV from zip
        df = pd.read_csv(zip_file, names=['rank', 'domain'])
        df = df.head(count)
        
        # Convert domains to URLs
        df['url'] = 'https://' + df['domain']
        df['label'] = 0  # 0 = benign
        df['source'] = 'tranco'
        
        # Keep only URL and label
        df = df[['url', 'label', 'source']]
        
        logger.info(f"Downloaded {len(df)} benign URLs")
        return df
        
    except Exception as e:
        logger.error(f"Failed to download benign URLs: {e}")
        return pd.DataFrame()

def combine_and_split(phishing_df, benign_df):
    """Combine datasets and split into train/val/test."""
    logger.info("Combining and splitting datasets...")
    
    # Combine
    df = pd.concat([phishing_df, benign_df], ignore_index=True)
    
    # Shuffle
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    
    # Split: 70% train, 15% val, 15% test
    n = len(df)
    train_end = int(0.7 * n)
    val_end = int(0.85 * n)
    
    train_df = df[:train_end]
    val_df = df[train_end:val_end]
    test_df = df[val_end:]
    
    # Save
    train_df.to_csv(PROCESSED_DIR / "train.csv", index=False)
    val_df.to_csv(PROCESSED_DIR / "val.csv", index=False)
    test_df.to_csv(PROCESSED_DIR / "test.csv", index=False)
    
    logger.info(f"Train: {len(train_df)}, Val: {len(val_df)}, Test: {len(test_df)}")
    logger.info(f"Saved to {PROCESSED_DIR}")
    
    return train_df, val_df, test_df

def main():
    """Main data collection pipeline."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    
    # Download data
    phishing_df = download_phishing_urls(count=2500)
    benign_df = download_benign_urls(count=2500)
    
    if phishing_df.empty or benign_df.empty:
        logger.error("Failed to download data. Exiting.")
        return
    
    # Combine and split
    combine_and_split(phishing_df, benign_df)
    
    logger.info("✅ Data collection complete!")

if __name__ == "__main__":
    main()
```

### Run Data Collection

```bash
cd url-phishing-detector/data/scripts

# Install dependencies
pip install pandas requests

# Run collection script
python collect_data.py
```

**Expected Output**:
```
INFO:__main__:Downloading 2500 phishing URLs from PhishTank...
INFO:__main__:Downloaded 2500 phishing URLs
INFO:__main__:Downloading 2500 benign URLs from Tranco...
INFO:__main__:Downloaded 2500 benign URLs
INFO:__main__:Combining and splitting datasets...
INFO:__main__:Train: 3500, Val: 750, Test: 750
INFO:__main__:Saved to .../data/processed
INFO:__main__:✅ Data collection complete!
```

### Verify Data

```bash
cd data/processed
ls -lh

# Should see:
# train.csv (3500 rows)
# val.csv (750 rows)
# test.csv (750 rows)

# Inspect data
head train.csv
```

**Expected format**:
```csv
url,label,source
https://example.com,0,tranco
http://phishing-site.com/login,1,phishtank
...
```

✅ **Task 2 Complete** when you have `train.csv`, `val.csv`, `test.csv` in `data/processed/`

---

## Task 3: Train Initial ML Model (3-4 hours)

### Create Feature Extraction Module

Create `backend/app/ml/features.py`:

```python
"""
Feature extraction for URL phishing detection.
"""
from urllib.parse import urlparse, parse_qs
import re
import math
from collections import Counter

class FeatureExtractor:
    """Extract features from URLs."""
    
    SUSPICIOUS_KEYWORDS = [
        'login', 'secure', 'account', 'verify', 'update',
        'confirm', 'banking', 'paypal', 'ebay', 'amazon'
    ]
    
    URL_SHORTENERS = [
        'bit.ly', 'goo.gl', 'tinyurl.com', 't.co', 'ow.ly'
    ]
    
    def extract_all(self, url: str) -> dict:
        """Extract all features from a URL."""
        parsed = urlparse(url)
        
        features = {}
        
        # Lexical features
        features['url_length'] = len(url)
        features['domain_dots'] = parsed.netloc.count('.')
        features['hyphen_count'] = url.count('-')
        features['path_depth'] = len([p for p in parsed.path.split('/') if p])
        features['query_param_count'] = len(parse_qs(parsed.query))
        features['digit_ratio'] = self._digit_ratio(url)
        features['has_ip_address'] = self._has_ip_address(parsed.netloc)
        features['char_entropy'] = self._shannon_entropy(parsed.netloc)
        features['suspicious_keywords'] = self._count_suspicious_keywords(url)
        features['is_shortened'] = self._is_shortened(parsed.netloc)
        
        return features
    
    def _digit_ratio(self, url: str) -> float:
        """Calculate ratio of digits to total characters."""
        if len(url) == 0:
            return 0.0
        digits = sum(c.isdigit() for c in url)
        return digits / len(url)
    
    def _has_ip_address(self, domain: str) -> int:
        """Check if domain contains an IP address."""
        ip_pattern = r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'
        return 1 if re.search(ip_pattern, domain) else 0
    
    def _shannon_entropy(self, s: str) -> float:
        """Calculate Shannon entropy of a string."""
        if len(s) == 0:
            return 0.0
        counts = Counter(s)
        probs = [count / len(s) for count in counts.values()]
        return -sum(p * math.log2(p) for p in probs if p > 0)
    
    def _count_suspicious_keywords(self, url: str) -> int:
        """Count suspicious keywords in URL."""
        url_lower = url.lower()
        return sum(1 for kw in self.SUSPICIOUS_KEYWORDS if kw in url_lower)
    
    def _is_shortened(self, domain: str) -> int:
        """Check if URL uses a shortener service."""
        return 1 if any(s in domain for s in self.URL_SHORTENERS) else 0
```

### Create Training Script

Create `backend/app/ml/train.py`:

```python
"""
Train ML model for URL phishing detection.
"""
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.preprocessing import StandardScaler
import joblib
from pathlib import Path
import logging

from features import FeatureExtractor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_data(train_path, val_path, test_path):
    """Load train/val/test datasets."""
    train_df = pd.read_csv(train_path)
    val_df = pd.read_csv(val_path)
    test_df = pd.read_csv(test_path)
    
    logger.info(f"Loaded {len(train_df)} train, {len(val_df)} val, {len(test_df)} test samples")
    return train_df, val_df, test_df

def extract_features(df, extractor):
    """Extract features from URLs in dataframe."""
    logger.info("Extracting features...")
    features_list = []
    
    for url in df['url']:
        try:
            features = extractor.extract_all(url)
            features_list.append(features)
        except Exception as e:
            logger.warning(f"Failed to extract features from {url}: {e}")
            features_list.append({})
    
    features_df = pd.DataFrame(features_list)
    features_df = features_df.fillna(0)  # Fill missing values
    
    logger.info(f"Extracted {len(features_df.columns)} features")
    return features_df

def train_model(X_train, y_train, model_type='random_forest'):
    """Train ML model."""
    logger.info(f"Training {model_type} model...")
    
    if model_type == 'logistic_regression':
        model = LogisticRegression(max_iter=1000, random_state=42)
    elif model_type == 'random_forest':
        model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
    else:
        raise ValueError(f"Unknown model type: {model_type}")
    
    model.fit(X_train, y_train)
    logger.info("Training complete!")
    
    return model

def evaluate_model(model, X, y, dataset_name='Test'):
    """Evaluate model performance."""
    logger.info(f"Evaluating on {dataset_name} set...")
    
    y_pred = model.predict(X)
    
    print(f"\n{dataset_name} Set Results:")
    print(classification_report(y, y_pred, target_names=['Benign', 'Phishing']))
    print("\nConfusion Matrix:")
    print(confusion_matrix(y, y_pred))

def main():
    # Paths
    data_dir = Path(__file__).parent.parent.parent.parent / "data"
    train_path = data_dir / "processed" / "train.csv"
    val_path = data_dir / "processed" / "val.csv"
    test_path = data_dir / "processed" / "test.csv"
    
    model_dir = Path(__file__).parent.parent.parent.parent / "models" / "trained"
    model_dir.mkdir(parents=True, exist_ok=True)
    
    # Load data
    train_df, val_df, test_df = load_data(train_path, val_path, test_path)
    
    # Extract features
    extractor = FeatureExtractor()
    X_train = extract_features(train_df, extractor)
    X_val = extract_features(val_df, extractor)
    X_test = extract_features(test_df, extractor)
    
    y_train = train_df['label']
    y_val = val_df['label']
    y_test = test_df['label']
    
    # Normalize features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_val_scaled = scaler.transform(X_val)
    X_test_scaled = scaler.transform(X_test)
    
    # Train model
    model = train_model(X_train_scaled, y_train, model_type='random_forest')
    
    # Evaluate
    evaluate_model(model, X_val_scaled, y_val, 'Validation')
    evaluate_model(model, X_test_scaled, y_test, 'Test')
    
    # Save model
    model_path = model_dir / "model_v1.0.0.pkl"
    scaler_path = model_dir / "scaler_v1.0.0.pkl"
    
    joblib.dump(model, model_path)
    joblib.dump(scaler, scaler_path)
    
    logger.info(f"✅ Model saved to {model_path}")
    logger.info(f"✅ Scaler saved to {scaler_path}")

if __name__ == "__main__":
    main()
```

### Install Dependencies

```bash
cd backend
pip install pandas numpy scikit-learn joblib
```

### Run Training

```bash
cd backend/app/ml
python train.py
```

**Expected Output**:
```
INFO:__main__:Loaded 3500 train, 750 val, 750 test samples
INFO:__main__:Extracting features...
INFO:__main__:Extracted 10 features
INFO:__main__:Training random_forest model...
INFO:__main__:Training complete!
INFO:__main__:Evaluating on Validation set...

Validation Set Results:
              precision    recall  f1-score   support

      Benign       0.92      0.89      0.90       375
    Phishing       0.90      0.92      0.91       375

    accuracy                           0.91       750
   macro avg       0.91      0.91      0.91       750
weighted avg       0.91      0.91      0.91       750

Confusion Matrix:
[[334  41]
 [ 29 346]]

Test Set Results:
...

INFO:__main__:✅ Model saved to .../models/trained/model_v1.0.0.pkl
INFO:__main__:✅ Scaler saved to .../models/trained/scaler_v1.0.0.pkl
```

### Verify Model

```bash
cd models/trained
ls -lh

# Should see:
# model_v1.0.0.pkl
# scaler_v1.0.0.pkl
```

✅ **Task 3 Complete** when model achieves F1 score >0.85 on test set

---

## Summary

After completing these 3 tasks, you will have:

1. ✅ **API Keys** for Google Safe Browsing and VirusTotal
2. ✅ **Training Data** (5,000 labeled URLs split into train/val/test)
3. ✅ **Trained ML Model** (Random Forest with F1 >0.85)

**Next Steps**: Proceed to Phase 3 (Backend Development) to build the FastAPI backend and integrate the model.

---

## Troubleshooting

### Issue: PhishTank download fails
**Solution**: Use alternative source or manually download from PhishTank website

### Issue: Model F1 score <0.85
**Solution**: 
- Collect more data (10k+ URLs)
- Add more features (host-based, threat-intel)
- Tune hyperparameters

### Issue: Feature extraction errors
**Solution**: Add try-except blocks and log failed URLs for debugging

---

**Estimated Time**: 5-7 hours total  
**Difficulty**: Beginner-Intermediate  
**Prerequisites**: Python 3.10+, pip, internet connection
