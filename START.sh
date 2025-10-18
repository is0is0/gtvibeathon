#!/bin/bash
#
# Voxel Backend Startup Script
# This script starts the Voxel API server
#

echo "🚀 Starting Voxel Backend..."
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found!"
    echo "Creating from .env.example..."
    cp .env.example .env
    echo "✅ Created .env - Please add your API key and restart"
    echo ""
    echo "To edit: nano .env"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install/upgrade dependencies
echo "📚 Installing dependencies..."
pip install -q -r requirements.txt

echo ""
echo "✅ Setup complete!"
echo ""
echo "🌐 Starting server on http://0.0.0.0:5000"
echo "📡 API available at http://0.0.0.0:5000/api"
echo "💚 Health check: http://0.0.0.0:5000/api/health"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Start the server
python3 start_api.py
