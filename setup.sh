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

# Check for Ollama
echo ""
echo "Checking for Ollama..."
if command -v ollama &> /dev/null; then
    echo "✓ Ollama is installed"
    
    # Check if Ollama is running
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo "✓ Ollama is running"
        
        # Check for llama3 model
        if ollama list | grep -q "llama3"; then
            echo "✓ llama3 model is available"
        else
            echo "Downloading llama3 model (this may take a few minutes)..."
            ollama pull llama3
        fi
    else
        echo "⚠ Ollama is not running"
        echo "  Start it with: ollama serve"
    fi
else
    echo "✗ Ollama not found"
    echo ""
    echo "Installing Ollama..."
    if command -v brew &> /dev/null; then
        brew install ollama
        echo ""
        echo "Start Ollama with: ollama serve"
        echo "Then pull a model: ollama pull llama3"
    else
        echo "Please install Ollama manually:"
        echo "  brew install ollama"
        echo "  OR"
        echo "  Visit: https://ollama.ai"
    fi
fi

# Create .env file if it doesn't exist
echo ""
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "✓ .env file created"
    echo "  Edit .env to add your API keys (optional)"
else
    echo "✓ .env file already exists"
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
echo "1. CLI Mode:"
echo "   python3 run.py --interactive"
echo ""
echo "2. Web UI Mode:"
echo "   streamlit run app.py"
echo ""
echo "3. With arguments:"
echo "   python3 run.py --type motivational --topic 'perseverance' --duration 60"
echo ""
echo "For more info, see README.md"
echo ""