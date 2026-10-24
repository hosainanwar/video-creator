#!/bin/bash

# Video Creator AI - Setup Script
# This script will install all dependencies

echo "=================================="
echo "  Video Creator AI - Setup"
echo "=================================="

# Check Python version
echo ""
echo "Checking Python version..."
python3 --version

# Install pip dependencies
echo ""
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Check for FFmpeg
echo ""
echo "Checking for FFmpeg..."
if command -v ffmpeg &> /dev/null; then
    echo "✓ FFmpeg is installed"
    ffmpeg -version | head -n 1
else
    echo "✗ FFmpeg not found"
    echo ""
    echo "Installing FFmpeg via Homebrew..."
    if command -v brew &> /dev/null; then
        brew install ffmpeg
    else
        echo "Homebrew not found. Please install FFmpeg manually:"
        echo "  brew install ffmpeg"
        echo "  OR"
        echo "  Download from: https://ffmpeg.org/download.html"
    fi
fi

# Create .env file if it doesn't exist
echo ""
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "✓ .env file created"
    echo "  Edit .env and add your OPENAI_API_KEY"
else
    echo "✓ .env file already exists"
fi

# Check for OpenAI API key
echo ""
echo "Checking OpenAI API key..."
if grep -q "OPENAI_API_KEY=.\+" .env 2>/dev/null && ! grep -q "OPENAI_API_KEY=your_openai_api_key_here" .env 2>/dev/null; then
    echo "✓ OPENAI_API_KEY looks set in .env"
else
    echo "⚠ OPENAI_API_KEY not set yet"
    echo "  Edit .env and add your key from https://platform.openai.com/api-keys"
fi

# Create output directory
echo ""
mkdir -p output
echo "✓ Output directory ready"

echo ""
echo "=================================="
echo "  Setup Complete!"
echo "=================================="
echo ""
echo "Quick Start:"
echo ""
echo "1. Set OPENAI_API_KEY in .env"
echo ""
echo "2. CLI Mode:"
echo "   python3 run.py --interactive"
echo ""
echo "3. Web UI Mode:"
echo "   streamlit run app.py"
echo ""
echo "4. With arguments:"
echo "   python3 run.py --type motivational --topic 'perseverance' --duration 60"
echo ""
echo "For more info, see README.md"
echo ""
