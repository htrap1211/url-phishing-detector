# URL Phishing Detection System

AI-powered URL phishing detection with machine learning and real-time analysis.

## 🚀 Quick Start

```bash
# 1. Setup (first time only)
./setup.sh

# 2. Run application
./run_all.sh
```

**Frontend**: http://localhost:4200  
**Backend API**: http://localhost:8000  
**API Docs**: http://localhost:8000/docs

## 🎯 Project Overview

This system ingests URLs, enriches them with threat intelligence from multiple sources, extracts 25+ features, and uses machine learning to classify URLs as benign, suspicious, or malicious. It provides a FastAPI backend, Angular frontend dashboard, and browser extension for real-time protection.

## 🏗️ Architecture

```
┌─────────────────┐
│ Browser Extension│
│  (Chrome/FF)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐      ┌──────────────┐
│  Angular        │◄────►│  FastAPI     │
│  Frontend       │      │  Backend     │
└─────────────────┘      └──────┬───────┘
                                │
                    ┌───────────┼───────────┐
                    ▼           ▼           ▼
              ┌──────────┐ ┌────────┐ ┌─────────┐
              │PostgreSQL│ │ Redis  │ │ Celery  │
              │          │ │ Cache  │ │ Workers │
              └──────────┘ └────────┘ └─────────┘
                                            │
                    ┌───────────────────────┼─────────────┐
                    ▼                       ▼             ▼
              ┌──────────┐          ┌──────────┐   ┌──────────┐
              │  WHOIS   │          │  Google  │   │VirusTotal│
              │   DNS    │          │Safe Browse│   │   API    │
              └──────────┘          └──────────┘   └──────────┘
```

## 🚀 Features

### Core Capabilities
- ✅ Real-time URL phishing detection
- ✅ Multi-source threat intelligence enrichment
- ✅ 25+ engineered features (lexical, host-based, content-based, threat-intel)
- ✅ Explainable ML predictions with feature contributions
- ✅ RESTful API with async processing
- ✅ Web dashboard for analysis and search
- ✅ Browser extension for one-click checks

### ML & Intelligence
- **Models**: Logistic Regression (baseline), Random Forest (production)
- **Enrichment Sources**: WHOIS, DNS, Google Safe Browsing, VirusTotal, IP geolocation
- **Feature Categories**: Lexical (10), Host-based (8), Content-based (3), Threat-intel (4)
- **Explainability**: Top-5 feature contributions for each prediction

### Security & Privacy
- API key authentication
- Rate limiting (10 req/min per IP)
- 30-day data retention policy
- Optional request anonymization
- GDPR-compliant data deletion endpoint

## 📋 Prerequisites

- **Python**: 3.10+
- **Node.js**: 18+
- **PostgreSQL**: 14+
- **Redis**: 6+
- **API Keys**:
  - Google Safe Browsing API (free tier)
  - VirusTotal API (free tier: 4 req/min, 500/day)

## 🛠️ Technology Stack

### Backend
- **Framework**: FastAPI
- **Database**: PostgreSQL + SQLAlchemy
- **Task Queue**: Celery + Redis
- **ML**: scikit-learn, pandas, numpy
- **Enrichment**: python-whois, dnspython, requests

### Frontend
- **Framework**: Angular 16+
- **UI**: Angular Material
- **State**: RxJS
- **Charts**: Chart.js

### Extension
- **Target**: Chrome & Firefox (Manifest V3)
- **Language**: TypeScript

### DevOps
- **Containerization**: Docker + Docker Compose
- **CI/CD**: GitHub Actions
- **Testing**: pytest, Playwright

## 📁 Project Structure

```
url-phishing-detector/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── endpoints/
│   │   │       └── url_check.py
│   │   ├── ml/
│   │   │   ├── model.py
│   │   │   └── train.py
│   │   ├── services/
│   │   │   ├── enrichment.py
│   │   │   └── feature_extraction.py
│   │   ├── tasks/
│   │   │   └── celery_app.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   └── main.py
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── url-check/
│   │   │   ├── dashboard/
│   │   │   ├── result-detail/
│   │   │   └── services/
│   │   └── environments/
│   ├── package.json
│   └── Dockerfile
├── extension/
│   ├── manifest.json
│   ├── popup.html
│   ├── background.js
│   └── content.js
├── data/
│   ├── raw/
│   └── processed/
├── models/
│   └── trained/
├── docs/
│   ├── architecture.md
│   ├── api-spec.md
│   └── deployment.md
└── docker-compose.yml
```

## 🎓 Feature Engineering

### Lexical Features (10)
1. URL length
2. Number of dots in domain
3. Number of hyphens
4. Path depth
5. Query parameter count
6. Digit-to-character ratio
7. IP address in host
8. Character entropy
9. Suspicious keyword count
10. URL shortener detection

### Host-Based Features (8)
11. Domain age
12. Registration length
13. HTTPS enabled
14. Valid SSL certificate
15. Certificate age
16. Subdomain count
17. Hosting country risk
18. AS number reputation

### Content-Based Features (3)
19. HTML form count
20. Password field presence
21. Brand typosquatting

### Threat-Intel Features (4)
22. Google Safe Browsing flag
23. VirusTotal detections
24. Known phishing list
25. IP blocklist

## 📊 API Endpoints

### POST /api/v1/url/check
Submit URL for analysis
```json
{
  "url": "https://example.com/login",
  "metadata": {"source": "extension"}
}
```

### GET /api/v1/url/{check_id}
Retrieve check result with full enrichment data

### GET /api/v1/search
Search and filter checks
- Query params: `domain`, `verdict`, `start_date`, `end_date`, `limit`, `offset`

### GET /api/v1/stats
Aggregate statistics and metrics

## 🧪 Testing Strategy

### Unit Tests
- Feature extractors (25 functions)
- URL normalization
- Input validation
- Model wrapper

### Integration Tests
- Full pipeline with mocked APIs
- Database transactions
- Cache behavior

### E2E Tests
- Frontend user flows
- Extension popup
- API workflows

### Performance Targets
- **Cached results**: <300ms (p95)
- **Full enrichment**: <5s (p95)
- **Cache hit rate**: >70%

## 📈 Success Metrics

- **Precision**: >90% (minimize false positives)
- **Recall**: >85% (catch phishing URLs)
- **F1 Score**: >0.87
- **Uptime**: >99.5%

## 🔒 Security Considerations

- Input sanitization for SQL injection prevention
- XSS protection in frontend
- Rate limiting per IP
- API key rotation
- Secrets management (never commit keys)
- HTTPS everywhere
- Database encryption at rest



## 📚 Data Sources

### Training Data
- **Phishing URLs**: PhishTank, OpenPhish
- **Benign URLs**: Tranco Top 10k, Alexa Top 1M
- **Target size**: 50k URLs (balanced)

### Threat Intelligence
- Google Safe Browsing API
- VirusTotal API
- WHOIS databases
- Public IP blocklists

## 🚢 Deployment

### Development
```bash
docker-compose up -d
```

### Production
- Containerized deployment (Docker)
- Infrastructure as Code (Terraform)
- CI/CD via GitHub Actions
- Monitoring with Prometheus + Grafana

## 📖 Documentation

- [Architecture Overview](docs/architecture.md)
- [API Specification](docs/api-spec.md)
- [Deployment Guide](docs/deployment.md)
- [Feature Engineering](docs/features.md)

## 🤝 Contributing

This is a portfolio/educational project. Contributions welcome for:
- Additional threat intelligence sources
- Feature engineering ideas
- ML model improvements
- UI/UX enhancements

## ⚖️ Legal & Ethics

- **Purpose**: Educational/portfolio demonstration
- **Data Privacy**: No user browsing history stored
- **API Compliance**: Adheres to Google Safe Browsing and VirusTotal terms
- **Disclaimer**: Not for production security use without further hardening

## 📧 Contact

Built by Parth Rathi as a portfolio project demonstrating full-stack ML engineering.

## 🙏 Acknowledgments

- PhishTank for phishing URL datasets
- Google Safe Browsing for threat intelligence
- VirusTotal for multi-engine scanning
- Open-source ML community

---

**Status**: 🚧 In Development | **Version**: 0.1.0 | **License**: MIT
