# Video Creator AI 🎬

Create storytelling social media content with AI using the OpenAI API.

## Features

- **AI Story Generation** - Uses OpenAI to create engaging stories
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

### 2. Configure API Keys

```bash
cp .env.example .env
```

Edit `.env` and set:

```bash
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4o-mini
```

Optional: add a free [Pexels API key](https://www.pexels.com/api/) for better stock photos.

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
│   ├── story_generator.py     # AI story generation (OpenAI)
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

## API Keys

### OpenAI (Required)
1. Go to [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
2. Create an API key
3. Set `OPENAI_API_KEY` in `.env`

### Pexels (Optional - Recommended)
1. Go to [pexels.com/api](https://www.pexels.com/api/)
2. Sign up for free
3. Set `PEXELS_API_KEY` in `.env`

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

### "OPENAI_API_KEY not set"
Add your key to `.env`, or enter it in the Web UI sidebar under API Keys.

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

- **OpenAI** - Story generation
- **gTTS** - Free text-to-speech
- **Pexels** - Free stock photos
- **MoviePy** - Video editing
- **Streamlit** - Web UI framework
