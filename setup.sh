#!/bin/bash
# Setup script for URL Phishing Detection System
# This script helps you get started quickly

set -e  # Exit on error

echo "=================================================="
echo "URL Phishing Detection System - Setup Script"
echo "=================================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check for Python
echo "Checking Python version..."

# Prefer Python 3.9, 3.10, 3.11, or 3.12 over system default if it's too new
if command -v python3.9 &> /dev/null; then
    PYTHON_CMD="python3.9"
elif command -v python3.10 &> /dev/null; then
    PYTHON_CMD="python3.10"
elif command -v python3.11 &> /dev/null; then
    PYTHON_CMD="python3.11"
elif command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
else
    echo -e "${RED}Error: Python 3 not found${NC}"
    exit 1
fi

echo "Using Python: $($PYTHON_CMD --version)"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    $PYTHON_CMD -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${YELLOW}Virtual environment already exists${NC}"
fi

echo "Activating virtual environment..."
source venv/bin/activate
echo -e "${GREEN}✓ Virtual environment activated${NC}"
echo ""

# Install backend dependencies
echo "Installing backend dependencies..."
cd backend
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt
echo -e "${GREEN}✓ Backend dependencies installed${NC}"
cd ..
echo ""

# Check if data exists
if [ ! -f "data/processed/train.csv" ]; then
    echo -e "${YELLOW}Training data not found. Would you like to collect it now? (y/n)${NC}"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        echo "Collecting training data (this may take 5-10 minutes)..."
        cd data/scripts
        python collect_data.py --phishing-count 2500 --benign-count 2500
        cd ../..
        echo -e "${GREEN}✓ Training data collected${NC}"
    else
        echo -e "${YELLOW}Skipping data collection. You can run it later with:${NC}"
        echo "  cd data/scripts && python collect_data.py"
    fi
else
    echo -e "${GREEN}✓ Training data already exists${NC}"
fi
echo ""

# Check if model exists
if [ ! -f "models/trained/model_v1.0.0.pkl" ]; then
    echo -e "${YELLOW}ML model not found. Would you like to train it now? (y/n)${NC}"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        echo "Training ML model (this may take 5-10 minutes)..."
        cd backend/app/ml
        python train.py --model-type random_forest --model-version v1.0.0
        cd ../../..
        echo -e "${GREEN}✓ ML model trained${NC}"
    else
        echo -e "${YELLOW}Skipping model training. You can run it later with:${NC}"
        echo "  cd backend/app/ml && python train.py"
    fi
else
    echo -e "${GREEN}✓ ML model already exists${NC}"
fi
echo ""

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo -e "${YELLOW}⚠ Please edit .env and add your API keys:${NC}"
    echo "  - GOOGLE_SAFE_BROWSING_API_KEY"
    echo "  - VIRUSTOTAL_API_KEY"
    echo ""
    echo "  You can get these from:"
    echo "  - Google Safe Browsing: https://console.cloud.google.com/"
    echo "  - VirusTotal: https://www.virustotal.com/gui/join-us"
else
    echo -e "${GREEN}✓ .env file exists${NC}"
fi
echo ""

# Summary
echo "=================================================="
echo "Setup Complete! 🎉"
echo "=================================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Activate virtual environment (if not already active):"
echo "   source venv/bin/activate"
echo ""
echo "2. If you haven't collected data yet:"
echo "   cd data/scripts && python collect_data.py"
echo ""
echo "3. If you haven't trained the model yet:"
echo "   cd backend/app/ml && python train.py"
echo ""
echo "4. (Phase 3) Start the backend:"
echo "   cd backend && uvicorn app.main:app --reload"
echo ""
echo "5. (Phase 6) Start the frontend:"
echo "   cd frontend && npm install && ng serve"
echo ""
echo "=================================================="
echo ""
echo "For detailed instructions, see:"
echo "  - docs/quick-start.md"
echo "  - docs/getting-started.md"
echo "  - backend/README.md"
echo ""
echo "=================================================="
