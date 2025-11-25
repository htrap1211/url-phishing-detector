#!/bin/bash
# Start both backend and frontend

echo "🚀 Starting URL Phishing Detector"
echo "=================================="
echo ""

# Check if setup was run
if [ ! -d "venv" ]; then
    echo "❌ Please run ./setup.sh first"
    exit 1
fi

# Check if model exists
if [ ! -f "models/trained/model_v1.0.0.pkl" ]; then
    echo "❌ ML model not found. Please train the model first:"
    echo "   cd backend/app/ml && python train.py"
    exit 1
fi

echo "Starting backend on http://localhost:8000..."
echo "Starting frontend on http://localhost:4200..."
echo ""
echo "Press Ctrl+C to stop both services"
echo ""

# Start backend in background
source venv/bin/activate
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 3

# Start frontend
cd frontend
npm start &
FRONTEND_PID=$!
cd ..

# Wait for Ctrl+C
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT

wait
