"""Configuration settings for Video Creator AI"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).parent.parent
OUTPUT_DIR = BASE_DIR / "output"
ASSETS_DIR = BASE_DIR / "assets"
TEMPLATES_DIR = BASE_DIR / "templates"

# Ensure directories exist
OUTPUT_DIR.mkdir(exist_ok=True)
ASSETS_DIR.mkdir(exist_ok=True)

# Ollama Configuration (Local LLM)
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")

# Pexels API Configuration (Free stock photos)
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY", "")

# Optional API keys (for upgraded features)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
STABILITY_API_KEY = os.getenv("STABILITY_API_KEY", "")

# Video Settings
VIDEO_CONFIG = {
    "width": 1080,  # 9:16 aspect ratio for reels
    "height": 1920,
    "fps": 30,
    "codec": "libx264",
    "audio_codec": "aac",
    "bitrate": "5000k",
}

# Platform-specific settings
PLATFORMS = {
    "instagram": {"max_duration": 60, "aspect_ratio": "9:16"},
    "tiktok": {"max_duration": 60, "aspect_ratio": "9:16"},
    "youtube_shorts": {"max_duration": 60, "aspect_ratio": "9:16"},
}

# Voice Settings
VOICE_CONFIG = {
    "language": "en",
    "slow": False,
}

# Image Settings
IMAGE_CONFIG = {
    "width": 1080,
    "height": 1920,
    "style": "cinematic",
}

# Story Types
STORY_TYPES = [
    "motivational",
    "history",
    "fantasy",
    "facts",
]

# Text Styling (Dark theme with purple accent)
STYLING = {
    "background_color": "#1a1a2e",
    "accent_color": "#6c63ff",
    "text_color": "#ffffff",
    "font_family": "Arial",
    "font_size_large": 80,
    "font_size_medium": 60,
    "font_size_small": 40,
}