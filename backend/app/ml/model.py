"""
ML model wrapper for inference.
"""
from pathlib import Path
from typing import Dict, List, Tuple
import logging
import random

from app.ml.features import FeatureExtractor
from app.core.config import settings

from urllib.parse import urlparse
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Try to import whois
try:
    import whois
    WHOIS_AVAILABLE = True
except ImportError:
    WHOIS_AVAILABLE = False
    logger.warning("python-whois not found. Domain age check disabled.")

# Try to import Levenshtein
try:
    import Levenshtein
    LEVENSHTEIN_AVAILABLE = True
except ImportError:
    LEVENSHTEIN_AVAILABLE = False
    logger.warning("python-levenshtein not found. Brand impersonation check disabled.")

# Try to import dnspython
try:
    import dns.resolver
    DNS_AVAILABLE = True
except ImportError:
    DNS_AVAILABLE = False
    logger.warning("dnspython not found. DNS check disabled.")

# Try to import requests and bs4
try:
    import requests
    from bs4 import BeautifulSoup
    CONTENT_ANALYSIS_AVAILABLE = True
except ImportError:
    CONTENT_ANALYSIS_AVAILABLE = False
    logger.warning("requests or beautifulsoup4 not found. Content analysis disabled.")

# Trusted domains that should never be flagged
WHITELIST = {
    # Search Engines
    "google.com", "www.google.com", "google.co.uk", "google.ca", "google.com.au", "google.de", "google.fr", "google.it", "google.es", "google.co.in", "google.co.jp", "google.com.br",
    "bing.com", "www.bing.com",
    "duckduckgo.com", "www.duckduckgo.com",
    "yahoo.com", "www.yahoo.com", "yahoo.co.jp",
    
    # Tech Giants
    "github.com", "www.github.com", "github.io",
    "microsoft.com", "www.microsoft.com", "live.com", "office.com", "azure.com",
    "apple.com", "www.apple.com", "icloud.com",
    "facebook.com", "www.facebook.com", "fb.com", "messenger.com",
    "twitter.com", "x.com", "t.co",
    "linkedin.com", "www.linkedin.com",
    "instagram.com", "www.instagram.com",
    "youtube.com", "www.youtube.com", "youtu.be",
    "whatsapp.com", "www.whatsapp.com",
    "netflix.com", "www.netflix.com",
    "dropbox.com", "www.dropbox.com",
    "adobe.com", "www.adobe.com",
    
    # E-commerce
    "amazon.com", "www.amazon.com", "amazon.co.uk", "amazon.de", "amazon.fr", "amazon.it", "amazon.es", "amazon.ca", "amazon.in", "amazon.co.jp", "amazon.com.br", "amazon.com.mx", "amazon.com.au", "aws.amazon.com", "media-amazon.com", "ssl-images-amazon.com",
    "ebay.com", "www.ebay.com", "ebay.co.uk", "ebay.de",
    "walmart.com", "www.walmart.com",
    "target.com", "www.target.com",
    "bestbuy.com", "www.bestbuy.com",
    "aliexpress.com", "www.aliexpress.com",
    "etsy.com", "www.etsy.com",
    
    # Payment
    "paypal.com", "www.paypal.com",
    "stripe.com", "www.stripe.com",
    "chase.com", "www.chase.com",
    "wellsfargo.com", "www.wellsfargo.com",
    "bankofamerica.com", "www.bankofamerica.com",
    "americanexpress.com", "www.americanexpress.com",
    
    # Info & News
    "wikipedia.org", "www.wikipedia.org",
    "nytimes.com", "www.nytimes.com",
    "cnn.com", "www.cnn.com",
    "bbc.co.uk", "www.bbc.co.uk", "bbc.com",
    "reddit.com", "www.reddit.com",
    "stackoverflow.com", "www.stackoverflow.com",
    "medium.com", "www.medium.com",
    
    # Local
    "localhost", "127.0.0.1"
}

# Target brands often impersonated (with legitimate domains)
TARGET_BRANDS = {
    "google": ["google.com", "gmail.com", "google.co.uk", "google.de", "google.fr", "google.it", "google.es", "google.ca", "google.com.au", "google.co.in", "google.co.jp", "google.com.br"],
    "microsoft": ["microsoft.com", "office.com", "live.com", "azure.com", "outlook.com", "hotmail.com", "windows.com"],
    "apple": ["apple.com", "icloud.com", "itunes.com"],
    "amazon": ["amazon.com", "amazon.co.uk", "amazon.de", "amazon.fr", "amazon.it", "amazon.es", "amazon.ca", "amazon.in", "amazon.co.jp", "amazon.com.br", "amazon.com.mx", "amazon.com.au", "aws.amazon.com"],
    "paypal": ["paypal.com", "paypal.me"],
    "netflix": ["netflix.com"],
    "facebook": ["facebook.com", "fb.com", "messenger.com"],
    "instagram": ["instagram.com"],
    "linkedin": ["linkedin.com"],
    "twitter": ["twitter.com", "x.com", "t.co"],
    "dropbox": ["dropbox.com"],
    "adobe": ["adobe.com"],
    "chase": ["chase.com"],
    "wellsfargo": ["wellsfargo.com"],
    "bankofamerica": ["bankofamerica.com"],
    "ebay": ["ebay.com", "ebay.co.uk", "ebay.de"]
}

# Try to import ML libs, handle failure gracefully
try:
    import joblib
    import numpy as np
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    logger.warning("ML libraries (joblib, numpy) not found. Using mock model.")


class PhishingDetector:
    """Wrapper for ML model inference."""
    
    def __init__(self):
        self.model = None
        self.scaler = None
        self.extractor = FeatureExtractor()
        self.feature_names = self.extractor.get_feature_names()
        self.model_version = settings.MODEL_VERSION
        self._load_model()
    
    def _load_model(self):
        """Load trained model and scaler."""
        if not ML_AVAILABLE:
            logger.info("ML not available, skipping model load")
            return

        try:
            model_path = Path(settings.MODEL_PATH)
            scaler_path = Path(settings.SCALER_PATH)
            
            if not model_path.exists():
                logger.warning(f"Model not found at {model_path}. Using mock predictions.")
                return
            
            self.model = joblib.load(model_path)
            self.scaler = joblib.load(scaler_path)
            
            logger.info(f"✅ Loaded model {self.model_version} from {model_path}")
            
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            # Don't raise, just fallback to mock
    
    def predict(self, url: str, enrichment_data: Dict = None) -> Dict:
        """
        Predict if URL is phishing.
        """
        # Check whitelist first
        try:
            domain = urlparse(url).netloc.lower()
            # Check exact match OR subdomain match (e.g., docs.google.com -> google.com)
            is_whitelisted = domain in WHITELIST
            if not is_whitelisted:
                for trusted in WHITELIST:
                    if domain.endswith("." + trusted):
                        is_whitelisted = True
                        break
            
            if is_whitelisted:
                logger.info(f"URL {url} is in whitelist")
                
                # Fetch enrichment data even for whitelisted sites
                server_location = self._get_server_location(domain)
                age_days = self._get_domain_age_days(url) if WHOIS_AVAILABLE else None
                dns_valid = self._check_dns(url) if DNS_AVAILABLE else None
                
                return {
                    "verdict": "benign",
                    "confidence": 1.0,
                    "model_version": self.model_version,
                    "top_features": [],
                    "all_features": {},
                    "additional_info": {
                        "is_whitelisted": True,
                        "domain": domain,
                        "server_location": server_location,
                        "domain_age_days": age_days,
                        "dns_valid": dns_valid,
                        "is_https": url.startswith("https")
                    }
                }
        except Exception as e:
            logger.warning(f"Failed to parse domain for whitelist check: {e}")

        # Extract features (always works as it's pure Python)
        features = self.extractor.extract_all(url, enrichment_data)
        
        # Calculate additional info (always available)
        try:
            domain = urlparse(url).netloc.lower()
            server_location = self._get_server_location(domain)
            age_days = self._get_domain_age_days(url) if WHOIS_AVAILABLE else None
            dns_valid = self._check_dns(url) if DNS_AVAILABLE else None
            impersonated_brand = self._check_brand_impersonation(url) if LEVENSHTEIN_AVAILABLE else None
            
            additional_info = {
                "domain_age_days": age_days,
                "dns_valid": dns_valid,
                "is_https": url.startswith("https"),
                "impersonated_brand": impersonated_brand,
                "server_location": server_location
            }
        except Exception:
            additional_info = {}

        if self.model and self.scaler and ML_AVAILABLE:
            try:
                # Real prediction
                feature_array = np.array([[features[name] for name in self.feature_names]])
                feature_array_scaled = self.scaler.transform(feature_array)
                
                prediction = self.model.predict(feature_array_scaled)[0]
                probabilities = self.model.predict_proba(feature_array_scaled)[0]
                
                confidence = float(probabilities[prediction])
                verdict_map = {0: "benign", 1: "malicious"}
                verdict = verdict_map.get(prediction, "unknown")
                
                top_features = self._get_top_features(features, prediction)
                
                # Check domain age (Heuristic)
                if additional_info.get("domain_age_days") is not None and additional_info["domain_age_days"] < 30:
                    logger.info(f"Domain is new ({additional_info['domain_age_days']} days). Adjusting verdict.")
                    if verdict == "benign":
                        verdict = "suspicious"
                        confidence = 0.65
                        top_features.insert(0, {"name": "newly_registered_domain", "value": additional_info["domain_age_days"], "contribution": 0.5})
                    elif verdict == "suspicious":
                        verdict = "malicious"
                        confidence = min(confidence + 0.2, 0.99)
                        top_features.insert(0, {"name": "newly_registered_domain", "value": additional_info["domain_age_days"], "contribution": 0.8})
                
                # Check brand impersonation (Heuristic)
                if additional_info.get("impersonated_brand"):
                    logger.info(f"Brand impersonation detected: {additional_info['impersonated_brand']}")
                    verdict = "malicious"
                    confidence = 0.95
                    top_features.insert(0, {"name": f"impersonates_{additional_info['impersonated_brand']}", "value": 1.0, "contribution": 0.9})

                # Check DNS (Heuristic)
                if additional_info.get("dns_valid") is False:
                    logger.info("DNS lookup failed. Domain might be invalid.")
                    verdict = "malicious"
                    confidence = 0.9
                    top_features.insert(0, {"name": "invalid_dns", "value": 1.0, "contribution": 0.8})

                # Check Content (Heuristic) - Only if not already malicious and confidence < 0.9
                if CONTENT_ANALYSIS_AVAILABLE and verdict != "malicious":
                    content_score = self._analyze_content(url)
                    if content_score > 0:
                        logger.info(f"Content analysis suspicious score: {content_score}")
                        if content_score >= 2:
                            verdict = "malicious"
                            confidence = max(confidence, 0.9)
                            top_features.insert(0, {"name": "suspicious_content", "value": content_score, "contribution": 0.7})
                        else:
                            verdict = "suspicious"
                            confidence = max(confidence, 0.7)
                            top_features.insert(0, {"name": "suspicious_content", "value": content_score, "contribution": 0.5})

                return {
                    "verdict": verdict,
                    "confidence": confidence,
                    "model_version": self.model_version,
                    "top_features": top_features,
                    "all_features": features,
                    "additional_info": additional_info
                }
            except Exception as e:
                logger.error(f"Prediction failed: {e}. Falling back to mock.")
        
        # Mock prediction (heuristic based)
        return self._mock_predict(url, features, additional_info)

    def _get_domain_age_days(self, url: str) -> int:
        """Get domain age in days."""
        try:
            domain = urlparse(url).netloc
            w = whois.whois(domain)
            creation_date = w.creation_date
            
            if isinstance(creation_date, list):
                creation_date = creation_date[0]
                
            if isinstance(creation_date, datetime):
                age = (datetime.now() - creation_date).days
                return age
        except Exception as e:
            # logger.debug(f"WHOIS lookup failed: {e}")
            pass
        return None

    def _check_brand_impersonation(self, url: str) -> str:
        """Check if URL impersonates a target brand."""
        try:
            domain = urlparse(url).netloc.lower()
            # Remove www.
            if domain.startswith("www."):
                domain = domain[4:]
            
            # If domain is in whitelist, it's not impersonation
            if domain in WHITELIST:
                return None
            
            # Check against target brands
            for brand, legitimate_domains in TARGET_BRANDS.items():
                # If it's a legitimate domain, skip
                if domain in legitimate_domains:
                    continue
                
                # Check fuzzy match
                # 1. Contains brand name but is not legitimate
                if brand in domain:
                    # e.g. paypal-secure.com
                    return brand
                
                # 2. Levenshtein distance (typosquatting)
                # e.g. g0ogle.com (distance 1 from google.com)
                for leg_domain in legitimate_domains:
                    leg_base = leg_domain.split('.')[0] # e.g. google
                    domain_base = domain.split('.')[0] # e.g. g0ogle
                    
                    dist = Levenshtein.distance(domain_base, leg_base)
                    if dist > 0 and dist <= 2 and len(domain_base) > 4:
                        return brand
                        
        except Exception as e:
            pass
        return None

    def _check_dns(self, url: str) -> bool:
        """Check if domain has valid DNS records."""
        try:
            domain = urlparse(url).netloc
            # Check A record
            try:
                dns.resolver.resolve(domain, 'A')
                return True
            except:
                pass
            # Check MX record
            try:
                dns.resolver.resolve(domain, 'MX')
                return True
            except:
                pass
            return False
        except Exception:
            return True # Assume valid if check fails to avoid false positives on network errors

    def _analyze_content(self, url: str) -> int:
        """
        Analyze page content for suspicious elements.
        Returns a score (0-3).
        """
        score = 0
        try:
            response = requests.get(url, timeout=3, verify=False)
            if response.status_code != 200:
                return 0
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 1. Check for login forms on non-HTTPS (or just presence of login form)
            forms = soup.find_all('form')
            has_password_field = False
            for form in forms:
                if form.find('input', {'type': 'password'}):
                    has_password_field = True
                    break
            
            if has_password_field:
                # Login form present
                if not url.startswith('https'):
                    score += 2 # Critical: Login on HTTP
                else:
                    score += 1 # Suspicious: Login form on unknown site
            
            # 2. Check title vs domain
            title = soup.title.string if soup.title else ""
            domain = urlparse(url).netloc
            
            # If title mentions a target brand but domain doesn't
            if title:
                title_lower = title.lower()
                for brand, legitimate_domains in TARGET_BRANDS.items():
                    if brand in title_lower:
                        is_legit = False
                        for leg_domain in legitimate_domains:
                            if leg_domain in domain:
                                is_legit = True
                                break
                        if not is_legit:
                            score += 1
            
            # 3. Check for external resource loading (e.g. images from other domains)
            # This is complex, skipping for MVP speed
            
        except Exception:
            pass
        return score
    
    def _get_server_location(self, domain: str) -> str:
        """Get server location using IP-API (free tier)."""
        try:
            # Use HTTP as free tier doesn't support HTTPS
            response = requests.get(f"http://ip-api.com/json/{domain}", timeout=1.5)
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    country = data.get('country')
                    country_code = data.get('countryCode')
                    return f"{country} {country_code}"
        except Exception:
            pass
        return "Unknown"
    
    def _mock_predict(self, url: str, features: Dict, additional_info: Dict = None) -> Dict:
        """Simple heuristic-based prediction for when ML is unavailable."""
        score = 0
        
        # Simple heuristics
        if features['suspicious_keywords'] > 0: score += 2
        if features['is_shortened'] > 0: score += 1
        if features['has_ip_address'] > 0: score += 3
        if features['url_length'] > 75: score += 1
        if features['domain_dots'] > 3: score += 1
        
        # Random noise for demo
        # score += random.random() * 0.5
        
        if score >= 2:
            verdict = "malicious"
            confidence = min(0.6 + (score * 0.1), 0.99)
        elif score >= 1:
            verdict = "suspicious"
            confidence = 0.65
        else:
            verdict = "benign"
            confidence = 0.85 + (random.random() * 0.1)
            
        # Get top features based on values
        top_features = [
            {
                "name": name,
                "value": float(value),
                "contribution": float(value) * 0.5  # Fake contribution
            }
            for name, value in features.items()
            if value > 0
        ]
        top_features.sort(key=lambda x: x["contribution"], reverse=True)
        
        return {
            "verdict": verdict,
            "confidence": confidence,
            "model_version": f"{self.model_version}-mock",
            "top_features": top_features[:5],
            "all_features": features,
            "additional_info": additional_info
        }

    def _get_top_features(self, features: Dict, prediction: int, top_n: int = 5) -> List[Dict]:
        """Get top N most important features."""
        if hasattr(self.model, 'feature_importances_'):
            importances = self.model.feature_importances_
            feature_importance_list = [
                {
                    "name": name,
                    "value": float(features[name]),
                    "contribution": float(importances[i])
                }
                for i, name in enumerate(self.feature_names)
            ]
            feature_importance_list.sort(key=lambda x: x["contribution"], reverse=True)
            return feature_importance_list[:top_n]
        return []


# Global instance
_detector = None

def get_detector() -> PhishingDetector:
    """Get or create global detector instance."""
    global _detector
    if _detector is None:
        _detector = PhishingDetector()
    return _detector
