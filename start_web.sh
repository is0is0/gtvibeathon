#!/bin/bash

# Voxel Web Interface Startup Script

echo "🎨 Starting Voxel Web Interface..."
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "⚠️  Virtual environment not found. Creating..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Check if dependencies are installed
if ! python -c "import flask" 2>/dev/null; then
    echo "📦 Installing dependencies..."
    pip install -e .
    echo "✅ Dependencies installed"
fi

# Check for .env file
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found!"
    echo "   Please create a .env file (copy from .env.example) and configure it."
    echo ""
    echo "   Required settings:"
    echo "   - AI_PROVIDER and AI_MODEL"
    echo "   - ANTHROPIC_API_KEY or OPENAI_API_KEY"
    echo "   - BLENDER_PATH"
    echo ""
    exit 1
fi

# Create necessary directories
mkdir -p uploads
mkdir -p output
mkdir -p logs

echo ""
echo "✨ Starting web server..."
echo "   Access the interface at: http://localhost:5000"
echo "   Press Ctrl+C to stop"
echo ""

# Start the web server
voxel-web
