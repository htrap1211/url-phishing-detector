# Getting Started Guide

This guide will walk you through setting up the URL Phishing Detection System from scratch.

## Prerequisites Checklist

Before starting, ensure you have:

- [ ] **Python 3.10+** installed (`python --version`)
- [ ] **Node.js 18+** installed (`node --version`)
- [ ] **PostgreSQL 14+** installed and running
- [ ] **Redis 6+** installed and running
- [ ] **Git** installed
- [ ] **Docker & Docker Compose** (optional, for containerized setup)
- [ ] **Google Safe Browsing API Key** ([Get it here](https://developers.google.com/safe-browsing/v4/get-started))
- [ ] **VirusTotal API Key** ([Get it here](https://www.virustotal.com/gui/join-us))

---

## Quick Start (3 Steps)

### Step 1: Obtain API Keys

#### Google Safe Browsing
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable "Safe Browsing API"
4. Create credentials → API Key
5. Copy the API key

#### VirusTotal
1. Sign up at [VirusTotal](https://www.virustotal.com/gui/join-us)
2. Go to your profile → API Key
3. Copy the API key (free tier: 4 req/min, 500/day)

### Step 2: Collect Training Data

Download labeled URL datasets:

```bash
cd url-phishing-detector/data/raw

# Phishing URLs from PhishTank (example)
wget https://data.phishtank.com/data/online-valid.csv

# Benign URLs from Tranco Top 10k
wget https://tranco-list.eu/top-1m.csv.zip
unzip top-1m.csv.zip
head -10000 top-1m.csv > benign_urls.csv
```

**Expected dataset size**: ~5,000 URLs (2,500 phishing + 2,500 benign)

### Step 3: Run the System

#### Option A: Docker Compose (Recommended)

```bash
cd url-phishing-detector

# Create .env file
cp .env.example .env
# Edit .env and add your API keys

# Start all services
docker-compose up -d

# Check logs
docker-compose logs -f api

# Access the application
# Frontend: http://localhost:4200
# API: http://localhost:8000/docs
```

#### Option B: Manual Setup

See detailed instructions below.

---

## Detailed Setup Instructions

### 1. Clone and Setup Project

```bash
# Clone repository
git clone <your-repo-url> url-phishing-detector
cd url-phishing-detector

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install backend dependencies
cd backend
pip install -r requirements.txt

# Install frontend dependencies
cd ../frontend
npm install
```

### 2. Configure Environment Variables

Create `.env` file in `backend/` directory:

```bash
# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/phishing_detector

# Redis
REDIS_URL=redis://localhost:6379/0

# API Keys
GOOGLE_SAFE_BROWSING_API_KEY=your_gsb_key_here
VIRUSTOTAL_API_KEY=your_vt_key_here

# Application
SECRET_KEY=your_secret_key_here_generate_with_openssl_rand_hex_32
API_KEY_HEADER=X-API-Key
RATE_LIMIT_PER_MINUTE=10

# ML Model
MODEL_PATH=../models/trained/model_v1.0.0.pkl
MODEL_VERSION=v1.0.0

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Logging
LOG_LEVEL=INFO
```

### 3. Setup Database

```bash
# Start PostgreSQL (if not running)
# macOS: brew services start postgresql
# Linux: sudo systemctl start postgresql

# Create database
createdb phishing_detector

# Run migrations
cd backend
alembic upgrade head

# Verify tables
psql phishing_detector -c "\dt"
```

Expected tables:
- `url_checks`
- `enrichments`
- `threat_intel_cache`
- `audit_logs`

### 4. Setup Redis

```bash
# Start Redis (if not running)
# macOS: brew services start redis
# Linux: sudo systemctl start redis

# Verify Redis is running
redis-cli ping
# Expected output: PONG
```

### 5. Prepare Training Data

```bash
cd data

# Run data collection script
python scripts/collect_data.py --phishing-count 2500 --benign-count 2500

# Verify data
ls -lh processed/
# Should see: training_data.csv
```

### 6. Train Initial ML Model

```bash
cd backend

# Train model
python -m app.ml.train \
  --data ../data/processed/training_data.csv \
  --output ../models/trained/model_v1.0.0.pkl \
  --model-type random_forest

# Expected output:
# Training completed!
# Accuracy: 0.92
# Precision: 0.91
# Recall: 0.88
# F1 Score: 0.89
# Model saved to: ../models/trained/model_v1.0.0.pkl
```

### 7. Start Backend Services

#### Terminal 1: FastAPI Server
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Terminal 2: Celery Worker
```bash
cd backend
celery -A app.tasks.celery_app worker --loglevel=info
```

#### Terminal 3: Celery Beat (for periodic tasks)
```bash
cd backend
celery -A app.tasks.celery_app beat --loglevel=info
```

### 8. Start Frontend

```bash
cd frontend
ng serve --open
```

Frontend will open at `http://localhost:4200`

### 9. Verify Installation

#### Test API
```bash
# Health check
curl http://localhost:8000/health

# Submit test URL
curl -X POST http://localhost:8000/api/v1/url/check \
  -H "Content-Type: application/json" \
  -d '{"url": "https://google.com"}'

# Expected response:
# {
#   "check_id": "550e8400-e29b-41d4-a716-446655440000",
#   "status": "processing",
#   "estimated_time_seconds": 5
# }

# Get result
curl http://localhost:8000/api/v1/url/<check_id>
```

#### Test Frontend
1. Open `http://localhost:4200`
2. Enter URL: `https://google.com`
3. Click "Check URL"
4. Verify result shows "Benign" with confidence score

---

## Development Workflow

### Running Tests

```bash
# Backend unit tests
cd backend
pytest tests/ -v

# Frontend tests
cd frontend
ng test

# E2E tests
cd frontend
ng e2e
```

### Code Quality

```bash
# Python linting
cd backend
flake8 app/
black app/ --check
mypy app/

# TypeScript linting
cd frontend
ng lint
```

### Database Migrations

```bash
# Create new migration
cd backend
alembic revision --autogenerate -m "Add new column"

# Apply migration
alembic upgrade head

# Rollback
alembic downgrade -1
```

---

## Browser Extension Setup

### Chrome

```bash
cd extension

# Build extension
npm run build

# Load in Chrome:
# 1. Go to chrome://extensions/
# 2. Enable "Developer mode"
# 3. Click "Load unpacked"
# 4. Select extension/dist/ folder
```

### Firefox

```bash
cd extension

# Build for Firefox
npm run build:firefox

# Load in Firefox:
# 1. Go to about:debugging#/runtime/this-firefox
# 2. Click "Load Temporary Add-on"
# 3. Select extension/dist/manifest.json
```

---

## Common Issues & Troubleshooting

### Issue: Database connection error

**Error**: `sqlalchemy.exc.OperationalError: could not connect to server`

**Solution**:
```bash
# Check PostgreSQL is running
pg_isready

# Check connection string in .env
# Ensure DATABASE_URL matches your PostgreSQL config
```

### Issue: Redis connection error

**Error**: `redis.exceptions.ConnectionError: Error connecting to Redis`

**Solution**:
```bash
# Check Redis is running
redis-cli ping

# Verify REDIS_URL in .env
```

### Issue: API key quota exceeded

**Error**: `VirusTotal API quota exceeded`

**Solution**:
- Free tier: 4 requests/min, 500/day
- Implement caching to reduce API calls
- Consider upgrading to paid tier
- Use mock mode for development:
  ```bash
  export USE_MOCK_APIS=true
  ```

### Issue: Model not found

**Error**: `FileNotFoundError: model_v1.0.0.pkl not found`

**Solution**:
```bash
# Train model first
cd backend
python -m app.ml.train --data ../data/processed/training_data.csv
```

### Issue: Celery tasks not processing

**Error**: Tasks stuck in "processing" state

**Solution**:
```bash
# Check Celery worker is running
ps aux | grep celery

# Restart worker
celery -A app.tasks.celery_app worker --loglevel=info

# Check Redis queue
redis-cli
> LLEN celery
```

---

## Performance Optimization

### Database Indexing

```sql
-- Add indexes for common queries
CREATE INDEX idx_url_checks_timestamp ON url_checks(timestamp DESC);
CREATE INDEX idx_url_checks_verdict ON url_checks(verdict);
CREATE INDEX idx_url_checks_normalized_url ON url_checks(normalized_url);
CREATE INDEX idx_enrichments_url_check_id ON enrichments(url_check_id);
CREATE INDEX idx_threat_intel_cache_lookup_key ON threat_intel_cache(lookup_key);
```

### Redis Configuration

Edit `redis.conf`:
```conf
maxmemory 1gb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
```

### PostgreSQL Tuning

Edit `postgresql.conf`:
```conf
shared_buffers = 256MB
effective_cache_size = 1GB
work_mem = 16MB
maintenance_work_mem = 64MB
```

---

## Monitoring Setup

### Prometheus Metrics

```bash
# Install prometheus-fastapi-instrumentator
pip install prometheus-fastapi-instrumentator

# Metrics available at:
# http://localhost:8000/metrics
```

### Logging

Logs are written to:
- **Backend**: `backend/logs/app.log`
- **Celery**: `backend/logs/celery.log`
- **Frontend**: Browser console

View logs:
```bash
# Tail backend logs
tail -f backend/logs/app.log

# Tail Celery logs
tail -f backend/logs/celery.log
```

---

## Next Steps

1. **Collect more training data**: Aim for 50k+ URLs for production
2. **Tune model hyperparameters**: Use grid search
3. **Implement A/B testing**: Test new models in production
4. **Add more enrichment sources**: WHOIS privacy, DNS history
5. **Build admin dashboard**: Monitor system health
6. **Deploy to production**: See [deployment.md](deployment.md)

---

## Resources

- **API Documentation**: http://localhost:8000/docs (Swagger UI)
- **Architecture**: [docs/architecture.md](architecture.md)
- **Feature Engineering**: [docs/features.md](features.md)
- **Deployment Guide**: [docs/deployment.md](deployment.md)

---

## Support

For issues or questions:
1. Check [Common Issues](#common-issues--troubleshooting)
2. Review logs for error messages
3. Open an issue on GitHub
4. Contact: [your-email@example.com]
