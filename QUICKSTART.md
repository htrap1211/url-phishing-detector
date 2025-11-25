# Quick Start - URL Phishing Detector

## 🚀 Get Started in 3 Steps

### Step 1: Setup (5 minutes)

```bash
cd url-phishing-detector
./setup.sh
```

This will:
- Create virtual environment
- Install dependencies
- Optionally collect training data
- Optionally train ML model

### Step 2: Start Backend (1 minute)

```bash
./run_backend.sh
```

Backend will start at: http://localhost:8000
API docs at: http://localhost:8000/docs

### Step 3: Test API (1 minute)

```bash
python test_api.py
```

## 📡 API Endpoints

### Check URL
```bash
curl -X POST http://localhost:8000/api/v1/url/check \
  -H "Content-Type: application/json" \
  -d '{"url": "https://google.com"}'
```

### Get Result
```bash
curl http://localhost:8000/api/v1/url/{check_id}
```

### Search Checks
```bash
curl -X POST http://localhost:8000/api/v1/url/search \
  -H "Content-Type: application/json" \
  -d '{"verdict": "malicious", "limit": 10}'
```

### Get Stats
```bash
curl http://localhost:8000/api/v1/url/stats
```

## 🎯 What's Working

✅ **Backend API** - FastAPI with 5 endpoints
✅ **ML Model** - Random Forest with 10 lexical features
✅ **Database** - PostgreSQL with 4 tables
✅ **Predictions** - Real-time phishing detection
✅ **Feature Importance** - Top contributing features

## 🔧 Troubleshooting

### Model not found
```bash
cd backend/app/ml
python train.py --model-type random_forest
```

### Database error
Make sure PostgreSQL is running:
```bash
# macOS
brew services start postgresql

# Linux
sudo systemctl start postgresql
```

### Port already in use
Change port in run_backend.sh:
```bash
uvicorn app.main:app --reload --port 8001
```

## 📊 Test with Different URLs

**Benign:**
- https://google.com
- https://github.com
- https://stackoverflow.com

**Suspicious (will likely be flagged):**
- http://paypal-secure-login.com/verify
- http://192.168.1.1/admin/login.php
- http://bit.ly/abc123 (URL shortener)

## 🎨 Next: Build Frontend

The backend is ready! Next step is to build the Angular frontend dashboard.

Want me to continue with Phase 6 (Frontend)?
