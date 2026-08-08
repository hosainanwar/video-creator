"""Image generator - supports Pexels (free) and optional Stable Diffusion"""

import os
from pathlib import Path
from typing import Dict, List, Optional
from PIL import Image, ImageDraw, ImageFont
from .config import IMAGE_CONFIG, OUTPUT_DIR, STABILITY_API_KEY
from .stock_media import StockMediaFetcher


class ImageGenerator:
    """Generate images for video scenes"""
    
    def __init__(self, use_ai: bool = False):
        """
        Initialize image generator
        
        Args:
            use_ai: If True, try to use Stable Diffusion (requires GPU/RAM)
                    If False, use Pexels stock photos (free, recommended)
        """
        self.use_ai = use_ai
        self.width = IMAGE_CONFIG.get("width", 1080)
        self.height = IMAGE_CONFIG.get("height", 1920)
        self.images_dir = OUTPUT_DIR / "images"
        self.images_dir.mkdir(exist_ok=True)
        
        # Initialize stock media fetcher
        self.stock_fetcher = StockMediaFetcher()
        
        # Try to load Stable Diffusion if requested
        self.sd_pipeline = None
        if use_ai:
            self._init_stable_diffusion()
    
    def _init_stable_diffusion(self):
        """Initialize Stable Diffusion pipeline (optional)"""
        try:
            from diffusers import StableDiffusionPipeline
            import torch
            
            print("Loading Stable Diffusion (this may take a moment)...")
            
            # Use a smaller model for M4 Air
            model_id = "stabilityai/stable-diffusion-2-1"
            
            self.sd_pipeline = StableDiffusionPipeline.from_pretrained(
                model_id,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            )
            self.sd_pipeline = self.sd_pipeline.to("mps")  # Apple Silicon
            
            print("Stable Diffusion loaded successfully!")
            
        except ImportError:
            print("Warning: diffusers/torch not installed. Using stock photos.")
            self.use_ai = False
        except Exception as e:
            print(f"Warning: Could not load Stable Diffusion: {e}")
            print("Using stock photos instead.")
            self.use_ai = False
    
    def generate_ai_image(self, prompt: str, scene_number: int) -> str:
        """Generate image using Stable Diffusion"""
        if not self.sd_pipeline:
            return None
        
        try:
            print(f"  Generating AI image for scene {scene_number}...")
            
            # Enhance prompt for better results
            enhanced_prompt = f"{prompt}, cinematic lighting, high quality, detailed, 4k"
            
            image = self.sd_pipeline(enhanced_prompt).images[0]
            
            # Resize to target dimensions
            image = image.resize((self.width, self.height), Image.LANCZOS)
            
            # Save
            output_path = self.images_dir / f"scene_{scene_number:02d}.jpg"
            image.save(str(output_path), quality=90)
            
            print(f"  Generated: scene_{scene_number:02d}.jpg")
            return str(output_path)
            
        except Exception as e:
            print(f"  Error generating AI image: {e}")
            return None
    
    def generate_gradient_placeholder(self, scene_number: int, prompt: str = "") -> str:
        """Generate a gradient placeholder image with text"""
        
        # Create gradient background
        img = Image.new('RGB', (self.width, self.height))
        draw = ImageDraw.Draw(img)
        
        # Create vertical gradient (dark purple theme)
        for y in range(self.height):
            r = int(26 + (y / self.height) * 30)
            g = int(26 + (y / self.height) * 20)
            b = int(46 + (y / self.height) * 50)
            draw.line([(0, y), (self.width, y)], fill=(r, g, b))
        
        # Add accent line
        accent_y = self.height // 3
        draw.line([(100, accent_y), (self.width - 100, accent_y)], fill='#6c63ff', width=3)
        
        # Add scene number
        try:
            title_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 60)
        except:
            title_font = ImageFont.load_default()
        
        scene_text = f"Scene {scene_number}"
        bbox = draw.textbbox((0, 0), scene_text, font=title_font)
        text_width = bbox[2] - bbox[0]
        x = (self.width - text_width) // 2
        draw.text((x, accent_y - 80), scene_text, fill='#6c63ff', font=title_font)
        
        # Add prompt preview
        if prompt:
            try:
                small_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 28)
            except:
                small_font = ImageFont.load_default()
            
            # Wrap text
            words = prompt.split()[:15]
            wrapped = []
            line = ""
            for word in words:
                if len(line) + len(word) < 40:
                    line += word + " "
                else:
                    wrapped.append(line.strip())
                    line = word + " "
            if line:
                wrapped.append(line.strip())
            
            y_offset = accent_y + 30
            for line_text in wrapped:
                bbox = draw.textbbox((0, 0), line_text, font=small_font)
                line_width = bbox[2] - bbox[0]
                x = (self.width - line_width) // 2
                draw.text((x, y_offset), line_text, fill='#ffffff', font=small_font)
                y_offset += 35
        
        # Add decorative elements
        draw.rectangle([(50, 50), (self.width - 50, 55)], fill='#6c63ff')
        draw.rectangle([(50, self.height - 55), (self.width - 50, self.height - 50)], fill='#6c63ff')
        
        # Save
        output_path = self.images_dir / f"scene_{scene_number:02d}.jpg"
        img.save(str(output_path), quality=90)
        
        return str(output_path)
    
    def get_images_for_scenes(self, scenes: List[Dict]) -> List[Dict]:
        """
        Get images for all scenes
        
        Args:
            scenes: List of scene dictionaries
        
        Returns:
            List of scenes with image_path added
        """
        print("\nGenerating images...")
        
        for scene in scenes:
            scene_num = scene.get("scene_number", 1)
            prompt = scene.get("image_prompt", "")
            
            # Try AI generation first if enabled
            if self.use_ai:
                image_path = self.generate_ai_image(prompt, scene_num)
                if image_path:
                    scene["image_path"] = image_path
                    scene["image_source"] = "ai"
                    continue
            
            # Fallback to stock photos
            print(f"  Fetching stock image for scene {scene_num}...")
            photos = self.stock_fetcher.search_photos(prompt, count=1)
            
            if photos and photos[0].get("url"):
                # Download the stock photo
                filename = f"scene_{scene_num:02d}.jpg"
                image_path = self.stock_fetcher.download_image(photos[0]["url"], filename)
                if image_path:
                    scene["image_path"] = image_path
                    scene["image_source"] = "pexels"
                    continue
            
            # Final fallback: gradient placeholder
            print(f"  Creating placeholder for scene {scene_num}")
            image_path = self.generate_gradient_placeholder(scene_num, prompt)
            scene["image_path"] = image_path
            scene["image_source"] = "placeholder"
        
        return scenes
    
    def apply_text_overlay(self, image_path: str, text: str, 
                           font_size: int = 60, position: str = "center") -> str:
        """
        Add text overlay to an image
        
        Args:
            image_path: Path to input image
            text: Text to add
            font_size: Font size
            position: top, center, or bottom
        
        Returns:
            Path to modified image
        """
        img = Image.open(image_path)
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", font_size)
        except:
            font = ImageFont.load_default()
        
        # Calculate position
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (img.width - text_width) // 2
        
        if position == "top":
            y = 100
        elif position == "bottom":
            y = img.height - text_height - 100
        else:  # center
            y = (img.height - text_height) // 2
        
        # Draw text shadow
        draw.text((x + 3, y + 3), text, fill='#000000', font=font)
        # Draw main text
        draw.text((x, y), text, fill='#ffffff', font=font)
        
        # Save
        output_path = image_path.replace('.jpg', '_text.jpg')
        img.save(str(output_path), quality=90)
        
        return output_path


def main():
    """Test the image generator"""
    generator = ImageGenerator(use_ai=False)
    
    test_scenes = [
        {"scene_number": 1, "image_prompt": "person walking on mountain sunrise"},
        {"scene_number": 2, "image_prompt": "city skyline at night"},
        {"scene_number": 3, "image_prompt": "ocean waves sunset"},
    ]
    
    scenes = generator.get_images_for_scenes(test_scenes)
    
    for scene in scenes:
        print(f"Scene {scene['scene_number']}: {scene.get('image_path', 'No image')}")


if __name__ == "__main__":
    main()