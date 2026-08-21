#!/bin/bash

# Quick Start Script for Multimodal Mental Health Analysis
# This script helps you set up and run the application quickly

set -e  # Exit on error

echo "🧠 Multimodal Mental Health Analysis - Quick Start"
echo "=================================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi
print_success "Python 3 found: $(python3 --version)"

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    print_error "Node.js is not installed. Please install Node.js 16 or higher."
    exit 1
fi
print_success "Node.js found: $(node --version)"

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    print_error "npm is not installed. Please install npm."
    exit 1
fi
print_success "npm found: $(npm --version)"

echo ""
print_info "Setting up backend..."
echo ""

# Setup backend
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    print_info "Creating virtual environment..."
    python3 -m venv venv
    print_success "Virtual environment created"
else
    print_success "Virtual environment already exists"
fi

# Activate virtual environment
print_info "Activating virtual environment..."
source venv/bin/activate

# Install backend dependencies
print_info "Installing backend dependencies..."
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt > /dev/null 2>&1
print_success "Backend dependencies installed"

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    print_info "Creating .env file..."
    cat > .env << EOF
DATABASE_URL=sqlite:///./mental_health.db
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=True
CORS_ORIGINS=http://localhost:3000
SECRET_KEY=$(openssl rand -hex 32)
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
EOF
    print_success ".env file created"
else
    print_success ".env file already exists"
fi

# Initialize database
print_info "Initializing database..."
python -c "from database import init_db; init_db()" 2>/dev/null || print_info "Database already initialized"
print_success "Database ready"

cd ..

echo ""
print_info "Setting up frontend..."
echo ""

# Setup frontend
cd frontend

# Install frontend dependencies
if [ ! -d "node_modules" ]; then
    print_info "Installing frontend dependencies (this may take a few minutes)..."
    npm install > /dev/null 2>&1
    print_success "Frontend dependencies installed"
else
    print_success "Frontend dependencies already installed"
fi

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    print_info "Creating frontend .env file..."
    cat > .env << EOF
REACT_APP_API_URL=http://localhost:8000
REACT_APP_ENV=development
EOF
    print_success "Frontend .env file created"
else
    print_success "Frontend .env file already exists"
fi

cd ..

echo ""
echo "=================================================="
print_success "Setup complete!"
echo "=================================================="
echo ""
print_info "To start the application:"
echo ""
echo "1. Start the backend (in one terminal):"
echo "   cd backend"
echo "   source venv/bin/activate"
echo "   python main.py"
echo ""
echo "2. Start the frontend (in another terminal):"
echo "   cd frontend"
echo "   npm start"
echo ""
echo "3. Open your browser to: http://localhost:3000"
echo ""
print_info "For DAIC-WOZ dataset setup, see: DAIC_WOZ_DATASET_GUIDE.md"
print_info "For complete setup guide, see: MULTIMODAL_SETUP_GUIDE.md"
echo ""
print_success "Happy analyzing! 🎭"

# Made with Bob
