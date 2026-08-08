"""Video assembler using MoviePy"""

import os
from pathlib import Path
from typing import Dict, List, Optional
from moviepy.editor import (
    ImageClip, AudioFileClip, TextClip, CompositeVideoClip,
    CompositeAudioClip, concatenate_videoclips
)
from moviepy.video.fx.fadein import fadein
from moviepy.video.fx.fadeout import fadeout
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from .config import VIDEO_CONFIG, STYLING, OUTPUT_DIR


class VideoAssembler:
    """Assemble video from images, audio, and text"""
    
    def __init__(self):
        self.width = VIDEO_CONFIG.get("width", 1080)
        self.height = VIDEO_CONFIG.get("height", 1920)
        self.fps = VIDEO_CONFIG.get("fps", 30)
        self.output_dir = OUTPUT_DIR
        self.output_dir.mkdir(exist_ok=True)
    
    def _create_text_image(self, text: str, width: int, height: int,
                           font_size: int = 60, position: str = "bottom") -> np.ndarray:
        """
        Create an image with text overlay
        
        Returns:
            numpy array for MoviePy
        """
        # Create transparent image
        img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", font_size)
        except:
            font = ImageFont.load_default()
        
        # Wrap text
        words = text.split()
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + " " + word if current_line else word
            bbox = draw.textbbox((0, 0), test_line, font=font)
            if bbox[2] - bbox[0] < width - 100:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)
        
        # Calculate total height
        line_height = font_size + 10
        total_height = len(lines) * line_height
        
        # Position
        if position == "bottom":
            y_start = height - total_height - 150
        elif position == "top":
            y_start = 150
        else:  # center
            y_start = (height - total_height) // 2
        
        # Draw text background
        padding = 30
        bg_top = y_start - padding
        bg_bottom = y_start + total_height + padding
        draw.rectangle(
            [(50, bg_top), (width - 50, bg_bottom)],
            fill=(0, 0, 0, 180)  # Semi-transparent black
        )
        
        # Draw text
        y = y_start
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            x = (width - text_width) // 2
            
            # Draw shadow
            draw.text((x + 3, y + 3), line, fill=(0, 0, 0, 200), font=font)
            # Draw main text
            draw.text((x, y), line, fill=(255, 255, 255, 255), font=font)
            
            y += line_height
        
        return np.array(img)
    
    def _create_scene_clip(self, scene: Dict) -> Optional[CompositeVideoClip]:
        """Create a video clip for a single scene"""
        
        image_path = scene.get("image_path")
        audio_path = scene.get("audio_path")
        text_overlay = scene.get("text_overlay", "")
        duration = scene.get("duration", 8)
        
        if not image_path or not os.path.exists(image_path):
            print(f"  Warning: No image for scene {scene.get('scene_number')}")
            return None
        
        # Create image clip
        try:
            # Load and resize image
            img = Image.open(image_path)
            img = img.resize((self.width, self.height), Image.LANCZOS)
            img_array = np.array(img)
            
            # Create clip from image
            image_clip = ImageClip(img_array, duration=duration)
            
            # Add Ken Burns effect (slow zoom)
            def zoom_effect(get_frame, t):
                frame = get_frame(t)
                # Simple zoom: scale from 100% to 110%
                scale = 1.0 + (t / duration) * 0.1
                h, w = frame.shape[:2]
                new_h, new_w = int(h * scale), int(w * scale)
                
                # Resize
                pil_img = Image.fromarray(frame)
                pil_img = pil_img.resize((new_w, new_h), Image.LANCZOS)
                
                # Crop to original size
                left = (new_w - w) // 2
                top = (new_h - h) // 2
                pil_img = pil_img.crop((left, top, left + w, top + h))
                
                return np.array(pil_img)
            
            image_clip = image_clip.fl(zoom_effect, apply_to=['mask'])
            
            clips = [image_clip]
            
            # Add text overlay
            if text_overlay:
                text_img = self._create_text_image(
                    text_overlay, self.width, self.height,
                    font_size=STYLING.get("font_size_medium", 60),
                    position="bottom"
                )
                
                # Only show text for first 70% of duration
                text_duration = duration * 0.7
                text_clip = (
                    ImageClip(text_img, duration=text_duration)
                    .set_position(('center', 'center'))
                )
                
                # Fade in/out
                text_clip = text_clip.fx(fadein, 0.5).fx(fadeout, 0.5)
                clips.append(text_clip)
            
            # Combine layers
            final_clip = CompositeVideoClip(clips, size=(self.width, self.height))
            
            # Add audio if available
            if audio_path and os.path.exists(audio_path):
                try:
                    audio_clip = AudioFileClip(audio_path)
                    # Adjust video duration to match audio
                    if audio_clip.duration > 0:
                        final_clip = final_clip.set_duration(audio_clip.duration)
                    final_clip = final_clip.set_audio(audio_clip)
                except Exception as e:
                    print(f"  Warning: Could not load audio: {e}")
            
            # Add fade effects
            final_clip = final_clip.fx(fadein, 0.5).fx(fadeout, 0.5)
            
            return final_clip
            
        except Exception as e:
            print(f"  Error creating scene clip: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def assemble_video(self, scenes: List[Dict], output_filename: str = "story_video",
                       add_music: bool = False) -> str:
        """
        Assemble all scenes into a complete video
        
        Args:
            scenes: List of scene dictionaries
            output_filename: Output filename (without extension)
            add_music: Whether to add background music
        
        Returns:
            Path to final video
        """
        print("\nAssembling video...")
        
        scene_clips = []
        
        for i, scene in enumerate(scenes):
            print(f"  Processing scene {i + 1}/{len(scenes)}...")
            clip = self._create_scene_clip(scene)
            if clip:
                scene_clips.append(clip)
        
        if not scene_clips:
            print("Error: No valid scenes to compile!")
            return None
        
        # Concatenate all scenes
        print("  Concatenating scenes...")
        final_video = concatenate_videoclips(scene_clips, method="compose")
        
        # Export
        output_path = self.output_dir / f"{output_filename}.mp4"
        
        print(f"  Exporting to: {output_path}")
        print("  This may take a while...")
        
        final_video.write_videofile(
            str(output_path),
            fps=self.fps,
            codec=VIDEO_CONFIG.get("codec", "libx264"),
            audio_codec=VIDEO_CONFIG.get("audio_codec", "aac"),
            bitrate=VIDEO_CONFIG.get("bitrate", "5000k"),
            preset="medium",
            threads=4,
            logger=None  # Suppress MoviePy output
        )
        
        # Close clips to free memory
        for clip in scene_clips:
            clip.close()
        final_video.close()
        
        print(f"\nVideo saved to: {output_path}")
        return str(output_path)
    
    def get_video_info(self, video_path: str) -> Dict:
        """Get video metadata"""
        from moviepy.editor import VideoFileClip
        
        try:
            clip = VideoFileClip(video_path)
            info = {
                "duration": clip.duration,
                "fps": clip.fps,
                "size": (clip.w, clip.h),
                "file_size": os.path.getsize(video_path) / (1024 * 1024),  # MB
            }
            clip.close()
            return info
        except Exception as e:
            print(f"Error getting video info: {e}")
            return {}


def main():
    """Test the video assembler"""
    from .voice_generator import VoiceGenerator
    from .image_generator import ImageGenerator
    
    # Create test scenes
    test_scenes = [
        {
            "scene_number": 1,
            "narration": "Welcome to this test video.",
            "text_overlay": "Welcome",
            "duration": 5,
        },
        {
            "scene_number": 2,
            "narration": "This is a demonstration of our video creator.",
            "text_overlay": "Demo Time",
            "duration": 5,
        },
    ]
    
    # Generate audio
    voice_gen = VoiceGenerator()
    test_scenes = voice_gen.generate_all_scenes(test_scenes)
    
    # Generate images
    image_gen = ImageGenerator(use_ai=False)
    test_scenes = image_gen.get_images_for_scenes(test_scenes)
    
    # Assemble video
    assembler = VideoAssembler()
    output = assembler.assemble_video(test_scenes, "test_output")
    
    if output:
        info = assembler.get_video_info(output)
        print(f"\nVideo info: {info}")


if __name__ == "__main__":
    main()