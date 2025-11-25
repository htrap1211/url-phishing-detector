#!/bin/bash
# Quick start script for backend

echo "🚀 Starting URL Phishing Detector Backend"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Run ./setup.sh first"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if model exists
if [ ! -f "models/trained/model_v1.0.0.pkl" ]; then
    echo "⚠️  ML model not found. Training model first..."
    cd backend/app/ml
    python train.py --model-type random_forest --model-version v1.0.0
    cd ../../..
fi

# Start FastAPI
echo ""
echo "Starting FastAPI server on http://localhost:8000"
echo "API docs: http://localhost:8000/docs"
echo ""

cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
