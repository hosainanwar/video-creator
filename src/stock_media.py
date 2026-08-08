"""Stock media fetcher using Pexels API (Free tier: 200 requests/hour)"""

import os
import requests
from pathlib import Path
from typing import Dict, List, Optional
from .config import PEXELS_API_KEY, OUTPUT_DIR


class StockMediaFetcher:
    """Fetch stock photos and videos from Pexels"""
    
    BASE_URL = "https://api.pexels.com/v1"
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or PEXELS_API_KEY
        self.images_dir = OUTPUT_DIR / "images"
        self.images_dir.mkdir(exist_ok=True)
        
        if not self.api_key:
            print("Warning: No Pexels API key. Using placeholder images.")
    
    def search_photos(self, query: str, count: int = 5, orientation: str = "portrait") -> List[Dict]:
        """
        Search for photos on Pexels
        
        Args:
            query: Search query
            count: Number of results
            orientation: portrait, landscape, or square
        
        Returns:
            List of photo data
        """
        if not self.api_key:
            return self._get_placeholder_images(count)
        
        url = f"{self.BASE_URL}/search"
        headers = {"Authorization": self.api_key}
        params = {
            "query": query,
            "per_page": count,
            "orientation": orientation,
        }
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            photos = []
            for photo in data.get("photos", []):
                photos.append({
                    "id": photo["id"],
                    "url": photo["src"]["large2x"],  # High quality
                    "thumbnail": photo["src"]["medium"],
                    "photographer": photo["photographer"],
                    "alt": photo.get("alt", query),
                })
            
            return photos
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching from Pexels: {e}")
            return self._get_placeholder_images(count)
    
    def search_videos(self, query: str, count: int = 3) -> List[Dict]:
        """Search for videos on Pexels"""
        if not self.api_key:
            return self._get_placeholder_videos(count)
        
        url = f"{self.BASE_URL}/videos/search"
        headers = {"Authorization": self.api_key}
        params = {
            "query": query,
            "per_page": count,
            "size": "medium",
        }
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            videos = []
            for video in data.get("videos", []):
                # Get the best quality video file
                video_files = video.get("video_files", [])
                if video_files:
                    # Prefer HD quality
                    best_file = next(
                        (f for f in video_files if f.get("quality") == "hd"),
                        video_files[0]
                    )
                    videos.append({
                        "id": video["id"],
                        "url": best_file["link"],
                        "thumbnail": video.get("image"),
                        "duration": video.get("duration", 0),
                        "width": best_file.get("width", 0),
                        "height": best_file.get("height", 0),
                    })
            
            return videos
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching videos from Pexels: {e}")
            return self._get_placeholder_videos(count)
    
    def download_image(self, url: str, filename: str) -> str:
        """
        Download an image from URL
        
        Args:
            url: Image URL
            filename: Local filename
        
        Returns:
            Path to downloaded image
        """
        output_path = self.images_dir / filename
        
        try:
            response = requests.get(url, timeout=30, stream=True)
            response.raise_for_status()
            
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            print(f"  Downloaded: {filename}")
            return str(output_path)
            
        except Exception as e:
            print(f"  Error downloading {filename}: {e}")
            return None
    
    def fetch_images_for_scenes(self, scenes: List[Dict]) -> List[Dict]:
        """
        Fetch images for all scenes based on their image_prompt
        
        Args:
            scenes: List of scene dictionaries
        
        Returns:
            List of scenes with image_path added
        """
        print("\nFetching images for scenes...")
        
        for i, scene in enumerate(scenes):
            image_prompt = scene.get("image_prompt", "beautiful landscape")
            
            # Search for matching photo
            photos = self.search_photos(image_prompt, count=1)
            
            if photos:
                photo = photos[0]
                filename = f"scene_{i+1:02d}.jpg"
                image_path = self.download_image(photo["url"], filename)
                scene["image_path"] = image_path
                scene["image_source"] = "pexels"
                scene["image_photographer"] = photo.get("photographer", "Unknown")
            else:
                # Use placeholder
                scene["image_path"] = self._create_placeholder(i + 1, image_prompt)
                scene["image_source"] = "placeholder"
        
        return scenes
    
    def _get_placeholder_images(self, count: int) -> List[Dict]:
        """Return placeholder image data when API is unavailable"""
        # Use solid color placeholders (will be created by image_generator)
        return [{"id": i, "url": None, "placeholder": True} for i in range(count)]
    
    def _get_placeholder_videos(self, count: int) -> List[Dict]:
        """Return placeholder video data when API is unavailable"""
        return [{"id": i, "url": None, "placeholder": True} for i in range(count)]
    
    def _create_placeholder(self, scene_number: int, prompt: str) -> str:
        """Create a simple placeholder image"""
        from PIL import Image, ImageDraw, ImageFont
        
        # Create a gradient background
        width, height = 1080, 1920
        img = Image.new('RGB', (width, height), color='#1a1a2e')
        draw = ImageDraw.Draw(img)
        
        # Add gradient effect
        for y in range(height):
            r = int(26 + (y / height) * 30)
            g = int(26 + (y / height) * 20)
            b = int(46 + (y / height) * 50)
            draw.line([(0, y), (width, y)], fill=(r, g, b))
        
        # Add text
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 40)
        except:
            font = ImageFont.load_default()
        
        text = f"Scene {scene_number}"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (width - text_width) // 2
        y = (height - text_height) // 2
        
        draw.text((x, y), text, fill='#6c63ff', font=font)
        
        # Add prompt as subtitle
        try:
            small_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 24)
        except:
            small_font = ImageFont.load_default()
        
        # Wrap prompt text
        words = prompt.split()[:10]
        prompt_text = " ".join(words)
        bbox = draw.textbbox((0, 0), prompt_text, font=small_font)
        prompt_width = bbox[2] - bbox[0]
        x = (width - prompt_width) // 2
        draw.text((x, y + text_height + 20), prompt_text, fill='#ffffff', font=small_font)
        
        # Save
        output_path = self.images_dir / f"scene_{scene_number:02d}.jpg"
        img.save(str(output_path), quality=90)
        
        return str(output_path)


def main():
    """Test the stock media fetcher"""
    fetcher = StockMediaFetcher()
    
    test_scenes = [
        {"scene_number": 1, "image_prompt": "person walking on mountain sunrise"},
        {"scene_number": 2, "image_prompt": "city skyline at night"},
        {"scene_number": 3, "image_prompt": "ocean waves sunset"},
    ]
    
    scenes = fetcher.fetch_images_for_scenes(test_scenes)
    
    for scene in scenes:
        print(f"Scene {scene['scene_number']}: {scene.get('image_path', 'No image')}")


if __name__ == "__main__":
    main()