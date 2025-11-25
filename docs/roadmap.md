# Project Roadmap - URL Phishing Detection System

## Executive Summary

This roadmap outlines the step-by-step implementation plan for building a production-ready URL Phishing Detection System. The project is divided into 10 phases over an estimated 8-week timeline (part-time).

---

## Phase 1: Discovery & Architecture ✅ COMPLETE

**Duration**: 1-2 days  
**Status**: ✅ Complete

### Completed Deliverables
- [x] MVP success criteria defined
- [x] Architecture design document
- [x] API specifications
- [x] Database schema design
- [x] Feature engineering strategy (25 features)
- [x] Technology stack selection
- [x] Docker Compose configuration
- [x] Project structure setup

### Key Decisions Made
- **Backend**: FastAPI + PostgreSQL + Celery + Redis
- **Frontend**: Angular 16+ with Material UI
- **ML**: scikit-learn (Random Forest for MVP)
- **Deployment**: Docker containers
- **APIs**: Google Safe Browsing + VirusTotal

---

## Phase 2: Data & Threat-Intel Design

**Duration**: 2-4 days  
**Status**: 🔜 Next

### Tasks
1. **Identify Data Sources**
   - [ ] Research public phishing datasets (PhishTank, OpenPhish)
   - [ ] Identify benign URL sources (Tranco Top 10k)
   - [ ] Document dataset licenses and usage terms
   - [ ] Create data collection plan

2. **Design Enrichment Strategy**
   - [ ] Map out enrichment data points (WHOIS, DNS, GSB, VT)
   - [ ] Define cache TTL for each source
   - [ ] Plan fallback strategies for API failures
   - [ ] Design enrichment result schema

3. **Create Labeling Strategy**
   - [ ] Define labeling criteria (authoritative sources)
   - [ ] Plan for handling ambiguous cases
   - [ ] Create label validation process
   - [ ] Document label sources for auditability

4. **Collect Initial Dataset**
   - [ ] Download 2,500 phishing URLs
   - [ ] Download 2,500 benign URLs
   - [ ] Validate and clean data
   - [ ] Split into train/validation/test sets (70/15/15)

### Deliverables
- Data collection scripts
- Labeled dataset (5k URLs minimum)
- Data documentation (sources, dates, licenses)
- Enrichment pipeline design doc

---

## Phase 3: Backend & Database Skeleton

**Duration**: 3-5 days  
**Status**: ⏳ Pending

### Tasks
1. **Initialize FastAPI Project**
   - [ ] Set up project structure
   - [ ] Configure dependencies (requirements.txt)
   - [ ] Implement health check endpoint
   - [ ] Set up CORS and middleware
   - [ ] Configure logging

2. **Database Setup**
   - [ ] Create SQLAlchemy models
   - [ ] Set up Alembic migrations
   - [ ] Create initial migration
   - [ ] Implement database connection pooling
   - [ ] Add database seeding scripts

3. **Core API Endpoints**
   - [ ] POST /api/v1/url/check
   - [ ] GET /api/v1/url/{id}
   - [ ] GET /api/v1/search
   - [ ] GET /api/v1/stats
   - [ ] Implement Pydantic schemas

4. **Authentication & Rate Limiting**
   - [ ] Implement API key authentication
   - [ ] Add rate limiting middleware (Redis-backed)
   - [ ] Create API key management endpoints
   - [ ] Add request logging

5. **Async Job Queue**
   - [ ] Set up Celery with Redis
   - [ ] Create enrichment task
   - [ ] Create prediction task
   - [ ] Implement task result polling
   - [ ] Add task monitoring

### Deliverables
- Functional FastAPI backend
- Database with migrations
- Core API endpoints (without ML)
- Celery task queue
- API documentation (Swagger)

---

## Phase 4: Feature Extraction & ML Prototype

**Duration**: 5-10 days  
**Status**: ⏳ Pending

### Tasks
1. **Implement Lexical Feature Extractors**
   - [ ] URL length, dots, hyphens
   - [ ] Path depth, query params
   - [ ] Digit ratio, entropy
   - [ ] IP address detection
   - [ ] Suspicious keyword count
   - [ ] URL shortener detection

2. **Implement Host-Based Extractors**
   - [ ] Domain age (WHOIS)
   - [ ] Registration length
   - [ ] HTTPS/SSL validation
   - [ ] Certificate age
   - [ ] Subdomain count
   - [ ] Hosting country risk
   - [ ] AS number reputation

3. **Implement Content-Based Extractors** (Optional)
   - [ ] HTML form count
   - [ ] Password field detection
   - [ ] Brand typosquatting check

4. **Implement Threat-Intel Extractors**
   - [ ] Google Safe Browsing flag
   - [ ] VirusTotal positives
   - [ ] Phishing list lookup
   - [ ] IP blocklist check

5. **Create Feature Extraction Pipeline**
   - [ ] Orchestrate all extractors
   - [ ] Handle missing/failed enrichments
   - [ ] Log feature values for debugging
   - [ ] Validate feature ranges

6. **Train ML Model**
   - [ ] Prepare training data with features
   - [ ] Train Logistic Regression (baseline)
   - [ ] Train Random Forest (production)
   - [ ] Evaluate models (precision, recall, F1)
   - [ ] Calibrate probabilities
   - [ ] Save model artifacts

7. **Implement Model Wrapper**
   - [ ] Load model from disk
   - [ ] Predict with confidence scores
   - [ ] Extract feature importances
   - [ ] Add explainability (top-5 features)
   - [ ] Version model artifacts

### Deliverables
- 25 feature extractors (tested)
- Feature extraction pipeline
- Trained ML model (F1 >0.85)
- Model evaluation report
- Model versioning system

---

## Phase 5: Third-Party API Integrations

**Duration**: 2-4 days  
**Status**: ⏳ Pending

### Tasks
1. **Google Safe Browsing Integration**
   - [ ] Set up API client
   - [ ] Implement threat lookup
   - [ ] Add caching (30 min TTL)
   - [ ] Handle rate limits
   - [ ] Add retry logic

2. **VirusTotal Integration**
   - [ ] Set up API client
   - [ ] Implement URL report lookup
   - [ ] Add caching (24 hour TTL)
   - [ ] Implement rate limiting (4 req/min)
   - [ ] Add queue for batch requests

3. **WHOIS Integration**
   - [ ] Implement WHOIS lookup
   - [ ] Parse registration dates
   - [ ] Add caching (7 day TTL)
   - [ ] Handle multiple WHOIS servers
   - [ ] Add fallback for failures

4. **DNS Integration**
   - [ ] Implement DNS resolution (A, AAAA, MX)
   - [ ] Add caching (1 hour TTL)
   - [ ] Handle timeouts
   - [ ] Extract IP addresses

5. **IP Geolocation** (Optional)
   - [ ] Integrate GeoIP2 or similar
   - [ ] Add caching (30 day TTL)
   - [ ] Extract country, AS number

6. **Failover & Degraded Mode**
   - [ ] Implement graceful degradation
   - [ ] Mark results as "partial" when enrichments fail
   - [ ] Log API errors
   - [ ] Add monitoring for API health

### Deliverables
- Integrated enrichment services
- Caching layer for all APIs
- Error handling and retries
- API health monitoring

---

## Phase 6: Frontend & Browser Extension

**Duration**: 5-8 days  
**Status**: ⏳ Pending

### Tasks
1. **Initialize Angular Project**
   - [ ] Create Angular app with routing
   - [ ] Set up Angular Material
   - [ ] Configure environment files
   - [ ] Set up HTTP interceptors

2. **URL Check Component**
   - [ ] Create URL input form
   - [ ] Implement submission logic
   - [ ] Add loading spinner
   - [ ] Display quick result
   - [ ] Poll for full result

3. **Dashboard Component**
   - [ ] Create recent checks table
   - [ ] Add pagination
   - [ ] Implement filtering (verdict, date)
   - [ ] Add sorting
   - [ ] Create search functionality

4. **Result Detail Component**
   - [ ] Display verdict badge
   - [ ] Show confidence score
   - [ ] List top-5 feature contributions
   - [ ] Show enrichment timeline
   - [ ] Add expandable raw data section

5. **Statistics Component**
   - [ ] Display aggregate metrics
   - [ ] Create charts (verdict distribution)
   - [ ] Show top domains
   - [ ] Add date range selector

6. **API Service**
   - [ ] Implement HTTP service
   - [ ] Add error handling
   - [ ] Implement caching
   - [ ] Add retry logic

7. **Browser Extension**
   - [ ] Create Manifest V3 config
   - [ ] Implement popup UI
   - [ ] Add context menu integration
   - [ ] Implement background service worker
   - [ ] Add local storage caching
   - [ ] Package for Chrome
   - [ ] Package for Firefox

### Deliverables
- Angular dashboard (responsive)
- URL check interface
- Result detail view
- Browser extension (Chrome + Firefox)
- User documentation

---

## Phase 7: Testing & Evaluation

**Duration**: 4-7 days  
**Status**: ⏳ Pending

### Tasks
1. **Unit Tests**
   - [ ] Test feature extractors (25 tests)
   - [ ] Test URL normalization
   - [ ] Test API endpoints
   - [ ] Test model wrapper
   - [ ] Achieve >80% code coverage

2. **Integration Tests**
   - [ ] Test full pipeline (mock APIs)
   - [ ] Test database transactions
   - [ ] Test cache behavior
   - [ ] Test Celery tasks

3. **E2E Tests**
   - [ ] Test frontend user flows (Playwright)
   - [ ] Test extension popup
   - [ ] Test API workflows
   - [ ] Test error scenarios

4. **Load Testing**
   - [ ] Simulate 100 concurrent requests
   - [ ] Measure response times
   - [ ] Test cache hit rates
   - [ ] Identify bottlenecks

5. **Adversarial Testing**
   - [ ] Test with obfuscated URLs
   - [ ] Test with very long URLs
   - [ ] Test with IDN/punycode
   - [ ] Test with edge cases

6. **Model Evaluation**
   - [ ] Evaluate on test set
   - [ ] Analyze false positives
   - [ ] Analyze false negatives
   - [ ] Create confusion matrix
   - [ ] Document model limitations

### Deliverables
- Comprehensive test suite
- Test coverage report
- Load testing results
- Model evaluation report
- Bug fixes

---

## Phase 8: Security & Operational Hardening

**Duration**: 3-5 days  
**Status**: ⏳ Pending

### Tasks
1. **Secrets Management**
   - [ ] Move API keys to environment variables
   - [ ] Set up secrets rotation
   - [ ] Document key management process
   - [ ] Add key validation

2. **API Security**
   - [ ] Implement input sanitization
   - [ ] Add SQL injection prevention
   - [ ] Add XSS protection
   - [ ] Implement CSRF tokens
   - [ ] Add request size limits

3. **Database Security**
   - [ ] Enable encryption at rest
   - [ ] Use SSL connections
   - [ ] Create least-privilege users
   - [ ] Set up automated backups

4. **Dependency Security**
   - [ ] Run dependency vulnerability scans
   - [ ] Update vulnerable packages
   - [ ] Set up automated scanning (Dependabot)

5. **Logging & Monitoring**
   - [ ] Implement structured logging
   - [ ] Set up log aggregation
   - [ ] Create alerting rules
   - [ ] Add performance metrics

6. **Operational Playbooks**
   - [ ] Create incident response plan
   - [ ] Document key rotation process
   - [ ] Create backup/restore procedures
   - [ ] Document scaling procedures

### Deliverables
- Security audit report
- Secrets management system
- Monitoring dashboard
- Operational playbooks

---

## Phase 9: CI/CD & Deployment

**Duration**: 3-5 days  
**Status**: ⏳ Pending

### Tasks
1. **Repository Setup**
   - [ ] Initialize Git repository
   - [ ] Create branching strategy
   - [ ] Set up PR templates
   - [ ] Configure branch protection

2. **CI Pipeline**
   - [ ] Set up GitHub Actions
   - [ ] Add linting checks
   - [ ] Add unit tests
   - [ ] Add security scans
   - [ ] Add build checks

3. **CD Pipeline**
   - [ ] Automate Docker image builds
   - [ ] Set up staging deployment
   - [ ] Set up production deployment
   - [ ] Implement blue-green deployment
   - [ ] Add rollback mechanism

4. **Infrastructure as Code**
   - [ ] Create Terraform/CloudFormation scripts
   - [ ] Define VPC and networking
   - [ ] Set up load balancer
   - [ ] Configure auto-scaling

5. **Deployment**
   - [ ] Deploy to staging
   - [ ] Run smoke tests
   - [ ] Deploy to production
   - [ ] Monitor for issues

### Deliverables
- CI/CD pipeline
- Infrastructure as code
- Staging environment
- Production deployment
- Deployment documentation

---

## Phase 10: Documentation & Portfolio

**Duration**: 2-3 days  
**Status**: ⏳ Pending

### Tasks
1. **Technical Documentation**
   - [x] README.md
   - [x] Architecture documentation
   - [x] API documentation
   - [x] Feature engineering guide
   - [x] Getting started guide
   - [ ] Deployment guide
   - [ ] Troubleshooting guide

2. **Demo Preparation**
   - [ ] Create demo script
   - [ ] Prepare test URLs (phishing + benign)
   - [ ] Record demo video (5-10 min)
   - [ ] Create screenshots

3. **Portfolio Assets**
   - [ ] Write project summary
   - [ ] Create architecture diagram (visual)
   - [ ] Highlight key features
   - [ ] Document challenges & solutions
   - [ ] Add to portfolio website

4. **Interview Preparation**
   - [ ] Prepare talking points
   - [ ] Document design decisions
   - [ ] Prepare for technical questions
   - [ ] Create presentation slides

### Deliverables
- Complete documentation
- Demo video
- Portfolio page
- Interview materials

---

## Timeline Overview

```
Week 1-2: Backend & Database
├─ Phase 3: Backend skeleton
└─ Phase 2: Data collection

Week 3: ML & Features
└─ Phase 4: Feature extraction & ML

Week 4: Integrations
└─ Phase 5: Third-party APIs

Week 5: Frontend
└─ Phase 6: Angular dashboard

Week 6: Extension & Testing
├─ Phase 6: Browser extension
└─ Phase 7: Testing (start)

Week 7: Testing & Security
├─ Phase 7: Testing (complete)
└─ Phase 8: Security hardening

Week 8: Deployment & Docs
├─ Phase 9: CI/CD & deployment
└─ Phase 10: Documentation & demo
```

---

## Success Metrics

### Technical Metrics
- **Model Performance**: F1 score >0.85
- **API Performance**: p95 latency <5s
- **Cache Hit Rate**: >70%
- **Test Coverage**: >80%
- **Uptime**: >99% (after deployment)

### Portfolio Metrics
- **GitHub Stars**: Target 50+ (if public)
- **Demo Views**: Track video views
- **Interview Mentions**: Use in job interviews
- **Blog Post**: Write technical blog post

---

## Risk Mitigation

### Technical Risks
1. **API Quota Limits**
   - Mitigation: Aggressive caching, mock mode for development
   
2. **Model Performance**
   - Mitigation: Start with baseline, iterate with more data
   
3. **Scalability**
   - Mitigation: Design for horizontal scaling from day 1

### Timeline Risks
1. **Scope Creep**
   - Mitigation: Stick to MVP, defer advanced features
   
2. **API Integration Issues**
   - Mitigation: Implement mock mode, graceful degradation

---

## Next Steps (Immediate)

1. **Obtain API Keys** (30 minutes)
   - Google Safe Browsing
   - VirusTotal

2. **Collect Training Data** (2-3 hours)
   - Download phishing URLs
   - Download benign URLs
   - Clean and validate

3. **Set Up Development Environment** (1-2 hours)
   - Install PostgreSQL, Redis
   - Create virtual environment
   - Install dependencies

4. **Start Phase 3** (Backend Development)
   - Initialize FastAPI project
   - Set up database models
   - Create first API endpoint

---

## Resources & References

- **Datasets**: PhishTank, OpenPhish, Tranco
- **APIs**: Google Safe Browsing, VirusTotal
- **Frameworks**: FastAPI, Angular, scikit-learn
- **Deployment**: Docker, GitHub Actions
- **Monitoring**: Prometheus, Grafana (future)

---

**Last Updated**: 2025-11-25  
**Project Status**: Phase 1 Complete ✅  
**Next Milestone**: Complete Phase 2 (Data Collection)
