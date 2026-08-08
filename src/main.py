"""Main CLI orchestrator for Video Creator AI"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, Optional

from .config import STORY_TYPES, OUTPUT_DIR
from .story_generator import StoryGenerator
from .voice_generator import VoiceGenerator
from .image_generator import ImageGenerator
from .video_assembler import VideoAssembler


class VideoCreator:
    """Main orchestrator for creating storytelling videos"""
    
    def __init__(self, use_ai_images: bool = False):
        """
        Initialize Video Creator
        
        Args:
            use_ai_images: Use Stable Diffusion for images (requires setup)
        """
        self.story_gen = StoryGenerator()
        self.voice_gen = VoiceGenerator()
        self.image_gen = ImageGenerator(use_ai=use_ai_images)
        self.video_assembler = VideoAssembler()
    
    def create_video(self, story_type: str, topic: str, duration: int = 60,
                     output_name: str = None) -> Optional[str]:
        """
        Create a complete video
        
        Args:
            story_type: Type of story (motivational, history, fantasy, facts)
            topic: Main topic or theme
            duration: Target duration in seconds
            output_name: Custom output filename (optional)
        
        Returns:
            Path to generated video
        """
        print("\n" + "="*60)
        print("VIDEO CREATOR AI")
        print("="*60)
        
        # Validate inputs
        if story_type not in STORY_TYPES:
            print(f"Error: Invalid story type '{story_type}'")
            print(f"Available types: {', '.join(STORY_TYPES)}")
            return None
        
        if not topic.strip():
            print("Error: Topic cannot be empty")
            return None
        
        # Generate output name if not provided
        if not output_name:
            safe_topic = "".join(c for c in topic if c.isalnum() or c in ' -').strip()
            safe_topic = safe_topic.replace(' ', '_')[:30]
            output_name = f"{story_type}_{safe_topic}"
        
        print(f"\nStory Type: {story_type.title()}")
        print(f"Topic: {topic}")
        print(f"Target Duration: {duration} seconds")
        print(f"Output: {output_name}.mp4")
        
        # Step 1: Generate Story
        print("\n[Step 1/5] Generating story...")
        story_data = self.story_gen.generate_story(story_type, topic, duration)
        
        if not story_data:
            print("Error: Failed to generate story")
            return None
        
        print(f"  Title: {story_data.get('title', 'Untitled')}")
        print(f"  Scenes: {len(story_data.get('scenes', []))}")
        
        # Step 2: Generate Voiceovers
        print("\n[Step 2/5] Generating voiceovers...")
        scenes = story_data.get("scenes", [])
        scenes = self.voice_gen.generate_all_scenes(scenes)
        
        # Step 3: Fetch/Generate Images
        print("\n[Step 3/5] Fetching images...")
        scenes = self.image_gen.get_images_for_scenes(scenes)
        
        # Step 4: Assemble Video
        print("\n[Step 4/5] Assembling video...")
        video_path = self.video_assembler.assemble_video(scenes, output_name)
        
        if not video_path:
            print("Error: Failed to assemble video")
            return None
        
        # Step 5: Save story data
        print("\n[Step 5/5] Saving story data...")
        story_output = OUTPUT_DIR / f"{output_name}_story.json"
        story_data["scenes"] = scenes  # Update with processed scenes
        
        with open(story_output, 'w', encoding='utf-8') as f:
            json.dump(story_data, f, indent=2, ensure_ascii=False)
        print(f"  Story data saved to: {story_output}")
        
        # Cleanup temporary files
        self.voice_gen.cleanup()
        
        # Final summary
        print("\n" + "="*60)
        print("VIDEO CREATED SUCCESSFULLY!")
        print("="*60)
        
        video_info = self.video_assembler.get_video_info(video_path)
        print(f"\nOutput: {video_path}")
        print(f"Duration: {video_info.get('duration', 0):.1f} seconds")
        print(f"File Size: {video_info.get('file_size', 0):.1f} MB")
        print(f"Resolution: {video_info.get('size', (0, 0))}")
        
        print("\nStory Summary:")
        print(f"  Title: {story_data.get('title', 'Untitled')}")
        print(f"  Hashtags: {' '.join(story_data.get('hashtags', []))}")
        
        return video_path
    
    def interactive_mode(self):
        """Run in interactive CLI mode"""
        print("\n" + "="*60)
        print("VIDEO CREATOR AI - Interactive Mode")
        print("="*60)
        
        # Select story type
        print("\nAvailable Story Types:")
        for i, st in enumerate(STORY_TYPES, 1):
            print(f"  {i}. {st.title()}")
        
        while True:
            choice = input("\nSelect story type (1-4): ").strip()
            if choice.isdigit() and 1 <= int(choice) <= len(STORY_TYPES):
                story_type = STORY_TYPES[int(choice) - 1]
                break
            print("Invalid choice. Please try again.")
        
        # Get topic
        topic = input("\nEnter topic: ").strip()
        while not topic:
            print("Topic cannot be empty.")
            topic = input("Enter topic: ").strip()
        
        # Get duration
        duration_input = input("\nTarget duration in seconds (default: 60): ").strip()
        duration = int(duration_input) if duration_input.isdigit() else 60
        duration = max(15, min(180, duration))  # Clamp between 15-180 seconds
        
        # Create video
        output_path = self.create_video(story_type, topic, duration)
        
        if output_path:
            print(f"\nYour video is ready at: {output_path}")
        else:
            print("\nFailed to create video. Please try again.")
        
        return output_path


def main():
    """Main entry point for CLI"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Video Creator AI - Create storytelling social media content"
    )
    
    parser.add_argument(
        "--type", "-t",
        choices=STORY_TYPES,
        help="Type of story"
    )
    parser.add_argument(
        "--topic", "-T",
        help="Topic or theme for the story"
    )
    parser.add_argument(
        "--duration", "-d",
        type=int,
        default=60,
        help="Target duration in seconds (default: 60)"
    )
    parser.add_argument(
        "--output", "-o",
        help="Output filename (without extension)"
    )
    parser.add_argument(
        "--ai-images",
        action="store_true",
        help="Use Stable Diffusion for AI images (requires setup)"
    )
    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Run in interactive mode"
    )
    
    args = parser.parse_args()
    
    # Initialize creator
    creator = VideoCreator(use_ai_images=args.ai_images)
    
    # Run based on mode
    if args.interactive or (not args.type and not args.topic):
        creator.interactive_mode()
    else:
        if not args.type or not args.topic:
            parser.error("Both --type and --topic are required for non-interactive mode")
        
        creator.create_video(
            story_type=args.type,
            topic=args.topic,
            duration=args.duration,
            output_name=args.output
        )


if __name__ == "__main__":
    main()