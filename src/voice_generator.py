"""Voice generator using gTTS (Google Text-to-Speech) - Free"""

import os
from pathlib import Path
from typing import Dict, List, Optional
from gtts import gTTS
from pydub import AudioSegment
from .config import VOICE_CONFIG, OUTPUT_DIR


class VoiceGenerator:
    """Generate voiceovers using gTTS (free)"""
    
    def __init__(self, language: str = None):
        self.language = language or VOICE_CONFIG.get("language", "en")
        self.slow = VOICE_CONFIG.get("slow", False)
        self.temp_dir = OUTPUT_DIR / "temp_audio"
        self.temp_dir.mkdir(exist_ok=True)
    
    def generate_scene_voice(self, text: str, scene_number: int) -> str:
        """
        Generate voice for a single scene
        
        Args:
            text: Narration text
            scene_number: Scene number for file naming
        
        Returns:
            Path to the generated audio file
        """
        output_path = self.temp_dir / f"scene_{scene_number:02d}.mp3"
        
        try:
            tts = gTTS(text=text, lang=self.language, slow=self.slow)
            tts.save(str(output_path))
            print(f"  Generated audio for scene {scene_number}")
            return str(output_path)
        except Exception as e:
            print(f"  Error generating audio for scene {scene_number}: {e}")
            return None
    
    def generate_all_scenes(self, scenes: List[Dict]) -> List[Dict]:
        """
        Generate voice for all scenes
        
        Args:
            scenes: List of scene dictionaries with narration
        
        Returns:
            List of scenes with audio_path added
        """
        print("\nGenerating voiceovers...")
        
        for scene in scenes:
            scene_num = scene.get("scene_number", 1)
            narration = scene.get("narration", "")
            
            if narration:
                audio_path = self.generate_scene_voice(narration, scene_num)
                scene["audio_path"] = audio_path
            else:
                print(f"  Warning: No narration for scene {scene_num}")
                scene["audio_path"] = None
        
        return scenes
    
    def get_audio_duration(self, audio_path: str) -> float:
        """Get duration of audio file in seconds"""
        try:
            audio = AudioSegment.from_mp3(audio_path)
            return len(audio) / 1000.0
        except Exception as e:
            print(f"Error getting audio duration: {e}")
            return 8.0  # Default duration
    
    def combine_scenes(self, scenes: List[Dict], output_filename: str = "voiceover") -> str:
        """
        Combine all scene audio files into one
        
        Args:
            scenes: List of scenes with audio_path
            output_filename: Name of output file (without extension)
        
        Returns:
            Path to combined audio file
        """
        print("\nCombining audio files...")
        
        combined = AudioSegment.empty()
        
        for scene in scenes:
            audio_path = scene.get("audio_path")
            if audio_path and os.path.exists(audio_path):
                audio = AudioSegment.from_mp3(audio_path)
                combined += audio
                
                # Add a small pause between scenes
                pause = AudioSegment.silent(duration=500)  # 0.5 seconds
                combined += pause
        
        output_path = OUTPUT_DIR / f"{output_filename}.mp3"
        combined.export(str(output_path), format="mp3")
        
        print(f"Combined voiceover saved to: {output_path}")
        return str(output_path)
    
    def cleanup(self):
        """Clean up temporary audio files"""
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
            print("Cleaned up temporary audio files")


def main():
    """Test the voice generator"""
    generator = VoiceGenerator()
    
    test_scenes = [
        {"scene_number": 1, "narration": "Welcome to this amazing story about perseverance."},
        {"scene_number": 2, "narration": "Every great achievement starts with a single step."},
        {"scene_number": 3, "narration": "Never give up on your dreams."},
    ]
    
    # Generate voice for each scene
    scenes = generator.generate_all_scenes(test_scenes)
    
    # Combine into single file
    output = generator.combine_scenes(scenes, "test_voiceover")
    
    print(f"\nTest voiceover created: {output}")
    
    # Get durations
    for scene in scenes:
        if scene.get("audio_path"):
            duration = generator.get_audio_duration(scene["audio_path"])
            print(f"Scene {scene['scene_number']}: {duration:.1f} seconds")


if __name__ == "__main__":
    main()