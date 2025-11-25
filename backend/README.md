# Backend - URL Phishing Detection System

FastAPI backend for URL phishing detection with ML-based classification.

## Quick Start

### 1. Install Dependencies

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Collect Training Data

```bash
# Run data collection script
cd ../data/scripts
python collect_data.py --phishing-count 2500 --benign-count 2500
```

### 3. Train ML Model

```bash
# Train Random Forest model
cd app/ml
python train.py --model-type random_forest --model-version v1.0.0
```

Expected output:
- Test F1 Score: >0.85
- Model saved to: `../../models/trained/model_v1.0.0.pkl`

### 4. Start Backend (Coming in Phase 3)

```bash
# Start FastAPI server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Project Structure

```
backend/
├── app/
│   ├── api/
│   │   └── endpoints/     # API route handlers
│   ├── core/              # Configuration, security
│   ├── ml/                # Machine learning
│   │   ├── features.py    # Feature extraction
│   │   ├── train.py       # Model training
│   │   └── model.py       # Model inference (Phase 3)
│   ├── services/          # Business logic
│   │   ├── enrichment.py  # Threat intelligence (Phase 5)
│   │   └── prediction.py  # ML prediction service
│   ├── tasks/             # Celery tasks
│   ├── models.py          # SQLAlchemy models
│   ├── schemas.py         # Pydantic schemas
│   └── main.py            # FastAPI app
├── tests/                 # Unit & integration tests
├── logs/                  # Application logs
└── requirements.txt       # Python dependencies
```

## Features Implemented

### Phase 2: Data & ML ✅
- [x] Data collection script (PhishTank + Tranco)
- [x] Feature extraction (10 lexical features)
- [x] ML model training (Random Forest)
- [x] Model evaluation & metrics

### Phase 3: Backend API (Next)
- [ ] FastAPI application setup
- [ ] Database models (SQLAlchemy)
- [ ] Core API endpoints
- [ ] Celery task queue
- [ ] Authentication & rate limiting

### Phase 5: Enrichment (Future)
- [ ] Google Safe Browsing integration
- [ ] VirusTotal integration
- [ ] WHOIS lookups
- [ ] DNS resolution
- [ ] Additional 15 features

## Development

### Run Tests
```bash
pytest tests/ -v --cov=app
```

### Code Formatting
```bash
black app/
isort app/
flake8 app/
```

### Type Checking
```bash
mypy app/
```

## Current Status

✅ **Phase 2 Complete**: Data collection and ML model training  
🔜 **Phase 3 Next**: FastAPI backend development

## Model Performance

Current model (lexical features only):
- **Features**: 10 lexical features
- **Target F1**: >0.85
- **Model**: Random Forest (100 trees)

Future improvements (Phase 5):
- Add 15 enrichment features
- Improve to F1 >0.90
- Add model explainability

## API Documentation

Once backend is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
