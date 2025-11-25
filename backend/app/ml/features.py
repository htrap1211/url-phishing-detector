"""
Feature extraction for URL phishing detection.

This module implements 25 features across 4 categories:
- Lexical features (10): URL structure analysis
- Host-based features (8): Domain and hosting information
- Content-based features (3): Page content analysis (optional)
- Threat-intel features (4): External threat intelligence
"""
from urllib.parse import urlparse, parse_qs
import re
import math
from collections import Counter
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class FeatureExtractor:
    """Extract features from URLs for phishing detection."""
    
    # Suspicious keywords commonly found in phishing URLs
    SUSPICIOUS_KEYWORDS = [
        'login', 'signin', 'account', 'verify', 'update', 'confirm',
        'secure', 'banking', 'paypal', 'ebay', 'amazon', 'apple',
        'microsoft', 'google', 'password', 'credential', 'suspend'
    ]
    
    # Known URL shortener domains
    URL_SHORTENERS = [
        'bit.ly', 'goo.gl', 'tinyurl.com', 't.co', 'ow.ly',
        'buff.ly', 'is.gd', 'cli.gs', 'tiny.cc'
    ]
    
    def __init__(self):
        """Initialize feature extractor."""
        self.feature_names = [
            # Lexical features
            'url_length', 'domain_dots', 'hyphen_count', 'path_depth',
            'query_param_count', 'digit_ratio', 'has_ip_address',
            'char_entropy', 'suspicious_keywords', 'is_shortened',
            # Host-based features (placeholders for now, will be filled by enrichment)
            'domain_age_days', 'registration_length_years', 'has_https',
            'valid_ssl', 'cert_age_days', 'subdomain_count',
            'high_risk_country', 'as_reputation_score',
            # Content-based features (optional)
            'form_count', 'has_password_field', 'typosquatting_score',
            # Threat-intel features (from enrichment)
            'gsb_threat_type', 'vt_positives', 'in_phishing_list', 'ip_blocklisted'
        ]
    
    def extract_all(self, url: str, enrichment_data: Optional[Dict] = None) -> Dict[str, float]:
        """
        Extract all features from a URL.
        
        Args:
            url: URL to analyze
            enrichment_data: Optional enrichment data from external sources
            
        Returns:
            Dictionary of feature names to values
        """
        try:
            parsed = urlparse(url)
            features = {}
            
            # Lexical features (always available)
            features.update(self._extract_lexical(url, parsed))
            
            # Host-based, content-based, and threat-intel features
            # (require enrichment data, default to 0 if not available)
            if enrichment_data:
                features.update(self._extract_enriched(enrichment_data))
            else:
                # Default values for enriched features
                for feature_name in self.feature_names[10:]:  # Skip lexical features
                    features[feature_name] = 0.0
            
            return features
            
        except Exception as e:
            logger.error(f"Failed to extract features from {url}: {e}")
            # Return default features (all zeros)
            return {name: 0.0 for name in self.feature_names}
    
    def _extract_lexical(self, url: str, parsed) -> Dict[str, float]:
        """Extract lexical features from URL string."""
        features = {}
        
        # 1. URL length
        features['url_length'] = float(len(url))
        
        # 2. Number of dots in domain
        features['domain_dots'] = float(parsed.netloc.count('.'))
        
        # 3. Number of hyphens
        features['hyphen_count'] = float(url.count('-'))
        
        # 4. Path depth
        path_parts = [p for p in parsed.path.split('/') if p]
        features['path_depth'] = float(len(path_parts))
        
        # 5. Query parameter count
        features['query_param_count'] = float(len(parse_qs(parsed.query)))
        
        # 6. Digit-to-character ratio
        features['digit_ratio'] = self._digit_ratio(url)
        
        # 7. Has IP address in host
        features['has_ip_address'] = float(self._has_ip_address(parsed.netloc))
        
        # 8. Character entropy
        features['char_entropy'] = self._shannon_entropy(parsed.netloc)
        
        # 9. Suspicious keyword count
        features['suspicious_keywords'] = float(self._count_suspicious_keywords(url))
        
        # 10. Is shortened URL
        features['is_shortened'] = float(self._is_shortened(parsed.netloc))
        
        return features
    
    def _extract_enriched(self, enrichment_data: Dict) -> Dict[str, float]:
        """Extract features from enrichment data."""
        features = {}
        
        # Host-based features
        whois_data = enrichment_data.get('whois', {})
        features['domain_age_days'] = float(whois_data.get('domain_age_days', 0))
        features['registration_length_years'] = float(whois_data.get('registration_length_years', 0))
        
        ssl_data = enrichment_data.get('ssl', {})
        features['has_https'] = float(ssl_data.get('has_https', 0))
        features['valid_ssl'] = float(ssl_data.get('valid_ssl', 0))
        features['cert_age_days'] = float(ssl_data.get('cert_age_days', 0))
        
        dns_data = enrichment_data.get('dns', {})
        features['subdomain_count'] = float(dns_data.get('subdomain_count', 0))
        
        geo_data = enrichment_data.get('geo', {})
        features['high_risk_country'] = float(geo_data.get('high_risk_country', 0))
        features['as_reputation_score'] = float(geo_data.get('as_reputation_score', 0.5))
        
        # Content-based features
        content_data = enrichment_data.get('content', {})
        features['form_count'] = float(content_data.get('form_count', 0))
        features['has_password_field'] = float(content_data.get('has_password_field', 0))
        features['typosquatting_score'] = float(content_data.get('typosquatting_score', 0))
        
        # Threat-intel features
        gsb_data = enrichment_data.get('google_safe_browsing', {})
        features['gsb_threat_type'] = float(gsb_data.get('threat_type_code', 0))
        
        vt_data = enrichment_data.get('virustotal', {})
        features['vt_positives'] = float(vt_data.get('positives', 0))
        
        blocklist_data = enrichment_data.get('blocklists', {})
        features['in_phishing_list'] = float(blocklist_data.get('in_phishing_list', 0))
        features['ip_blocklisted'] = float(blocklist_data.get('ip_blocklisted', 0))
        
        return features
    
    # Helper methods for lexical features
    
    def _digit_ratio(self, url: str) -> float:
        """Calculate ratio of digits to total characters."""
        if len(url) == 0:
            return 0.0
        digits = sum(c.isdigit() for c in url)
        return digits / len(url)
    
    def _has_ip_address(self, domain: str) -> int:
        """Check if domain contains an IP address."""
        # IPv4 pattern
        ipv4_pattern = r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'
        if re.search(ipv4_pattern, domain):
            return 1
        
        # IPv6 pattern (simplified)
        ipv6_pattern = r'[0-9a-fA-F:]{10,}'
        if re.search(ipv6_pattern, domain):
            return 1
        
        return 0
    
    def _shannon_entropy(self, s: str) -> float:
        """
        Calculate Shannon entropy of a string.
        Higher entropy indicates more randomness.
        """
        if len(s) == 0:
            return 0.0
        
        counts = Counter(s)
        probs = [count / len(s) for count in counts.values()]
        entropy = -sum(p * math.log2(p) for p in probs if p > 0)
        
        return entropy
    
    def _count_suspicious_keywords(self, url: str) -> int:
        """Count suspicious keywords in URL."""
        url_lower = url.lower()
        count = sum(1 for keyword in self.SUSPICIOUS_KEYWORDS if keyword in url_lower)
        return count
    
    def _is_shortened(self, domain: str) -> int:
        """Check if URL uses a shortener service."""
        domain_lower = domain.lower()
        return 1 if any(shortener in domain_lower for shortener in self.URL_SHORTENERS) else 0
    
    def get_feature_names(self) -> list:
        """Return list of feature names in order."""
        return self.feature_names.copy()


# Convenience function for quick feature extraction
def extract_features(url: str, enrichment_data: Optional[Dict] = None) -> Dict[str, float]:
    """
    Extract features from a URL.
    
    Args:
        url: URL to analyze
        enrichment_data: Optional enrichment data
        
    Returns:
        Dictionary of features
    """
    extractor = FeatureExtractor()
    return extractor.extract_all(url, enrichment_data)
