# Video Creator AI 🎬

Create storytelling social media content with AI - 100% free and runs locally!

## Features

- **AI Story Generation** - Uses Ollama (local LLM) to create engaging stories
- **Voice Over** - Free text-to-speech with gTTS
- **Stock Images** - Free images from Pexels or AI-generated
- **Video Assembly** - Automatic video creation with MoviePy
- **Multi-Platform** - Output optimized for Instagram, TikTok, YouTube Shorts

## Story Types

| Type | Description |
|------|-------------|
| Motivational | Inspiring stories about overcoming challenges |
| History | Historical events and famous figures |
| Fantasy | Magical and fictional stories |
| Facts | Mind-blowing facts and information |

## Quick Start

### 1. Install Dependencies

```bash
cd video-creator
pip install -r requirements.txt
```

### 2. Install Ollama (Local LLM)

```bash
# macOS
brew install ollama

# Start Ollama
ollama serve

# Download a model (in another terminal)
ollama pull llama3
```

### 3. Run the CLI

```bash
# Interactive mode
python run.py

# Or with arguments
python run.py --type motivational --topic "perseverance" --duration 60
```

### 4. Run the Web UI

```bash
streamlit run app.py
```

## Project Structure

```
video-creator/
├── src/
│   ├── config.py              # Configuration settings
│   ├── story_generator.py     # AI story generation (Ollama)
│   ├── voice_generator.py     # Text-to-speech (gTTS)
│   ├── image_generator.py     # Image generation
│   ├── stock_media.py         # Pexels API integration
│   ├── video_assembler.py     # Video creation (MoviePy)
│   └── main.py                # CLI orchestrator
├── templates/                 # Story templates
├── output/                    # Generated videos
├── assets/                    # Fonts, music, etc.
├── app.py                     # Streamlit web UI
├── run.py                     # CLI runner
└── requirements.txt           # Dependencies
```

## Usage

### CLI Options

```bash
# Basic usage
python run.py --type motivational --topic "never give up"

# With custom duration
python run.py --type history --topic "ancient Egypt" --duration 90

# Custom output name
python run.py --type facts --topic "space" --output "space_facts"

# Interactive mode
python run.py --interactive
```

### Web UI

1. Open browser to `http://localhost:8501`
2. Select story type from dropdown
3. Enter your topic
4. Adjust duration slider
5. Click "Create Video"

## API Keys (Optional)

The tool works without API keys, but you can add them for better results:

### Pexels (Free - Recommended)
1. Go to [pexels.com/api](https://www.pexels.com/api/)
2. Sign up for free
3. Get your API key
4. Set in `.env` file or enter in web UI

```bash
# Create .env file
cp .env.example .env

# Edit .env and add your key
PEXELS_API_KEY=your_key_here
```

## Advanced: AI Images (Stable Diffusion)

For AI-generated images instead of stock photos:

```bash
# Install additional dependencies
pip install torch diffusers accelerate

# Run with AI images
python run.py --type fantasy --topic "dragon" --ai-images
```

**Note:** Requires significant RAM (16GB+ recommended for M4 Air)

## Customization

### Change Voice Language

Edit `src/config.py`:
```python
VOICE_CONFIG = {
    "language": "es",  # Spanish
    "slow": False,
}
```

### Change Video Settings

Edit `src/config.py`:
```python
VIDEO_CONFIG = {
    "width": 1080,      # Width in pixels
    "height": 1920,     # Height in pixels (9:16 aspect ratio)
    "fps": 30,          # Frames per second
}
```

## Troubleshooting

### "Ollama not found"
Make sure Ollama is running:
```bash
ollama serve
```

### "No audio generated"
Check your internet connection (gTTS requires it for free tier)

### "MoviePy error"
Make sure FFmpeg is installed:
```bash
brew install ffmpeg
```

## License

This project is for personal use. Feel free to modify and customize!

## Credits

- **Ollama** - Local LLM inference
- **gTTS** - Free text-to-speech
- **Pexels** - Free stock photos
- **MoviePy** - Video editing
- **Streamlit** - Web UI framework# video-creator
