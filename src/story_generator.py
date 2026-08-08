"""Story generator using Ollama (local LLM)"""

import json
import requests
from typing import Dict, List, Optional
from .config import OLLAMA_BASE_URL, OLLAMA_MODEL


class StoryGenerator:
    """Generate stories using Ollama (local LLM)"""
    
    def __init__(self, model: str = None):
        self.base_url = OLLAMA_BASE_URL
        self.model = model or OLLAMA_MODEL
    
    def _call_ollama(self, prompt: str, system_prompt: str = None) -> str:
        """Call Ollama API"""
        url = f"{self.base_url}/api/generate"
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
        }
        
        if system_prompt:
            payload["system"] = system_prompt
        
        try:
            response = requests.post(url, json=payload, timeout=120)
            response.raise_for_status()
            return response.json()["response"]
        except requests.exceptions.RequestException as e:
            print(f"Error calling Ollama: {e}")
            return None
    
    def generate_story(self, story_type: str, topic: str, duration: int = 60) -> Dict:
        """
        Generate a complete story with scenes and image prompts
        
        Args:
            story_type: Type of story (motivational, history, fantasy, facts)
            topic: Main topic or theme
            duration: Target duration in seconds
        
        Returns:
            Dictionary with story data
        """
        
        system_prompt = """You are a professional storyteller creating content for social media.
Output ONLY valid JSON, no additional text or markdown.
Focus on creating engaging, short-form content that captures attention quickly."""
        
        num_scenes = max(3, min(10, duration // 10))  # 1 scene per 10 seconds
        
        prompt = f"""Create a {story_type} story about "{topic}" for a {duration}-second social media video.

Output JSON format:
{{
    "title": "Catchy title (max 10 words)",
    "hook": "Opening hook to grab attention (1 sentence)",
    "scenes": [
        {{
            "scene_number": 1,
            "narration": "What the voiceover says (2-3 sentences)",
            "text_overlay": "Short text shown on screen (max 8 words)",
            "image_prompt": "Detailed prompt for generating an image",
            "duration": 8
        }}
    ],
    "moral": "Takeaway or call-to-action (1 sentence)",
    "hashtags": ["relevant", "hashtags", "for", "social", "media"]
}}

Create exactly {num_scenes} scenes. Each scene narration should be 2-3 sentences.
The image_prompt should be detailed enough for AI image generation.
Make the content emotional, engaging, and shareable.

Output ONLY the JSON, no other text."""
        
        response = self._call_ollama(prompt, system_prompt)
        
        if not response:
            return self._get_fallback_story(story_type, topic)
        
        # Parse JSON from response
        try:
            # Try to extract JSON from response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start != -1 and json_end != -1:
                json_str = response[json_start:json_end]
                story_data = json.loads(json_str)
                
                # Ensure required fields exist
                story_data = self._validate_story(story_data, topic)
                return story_data
            else:
                print("No JSON found in response, using fallback")
                return self._get_fallback_story(story_type, topic)
                
        except json.JSONDecodeError as e:
            print(f"JSON parse error: {e}, using fallback")
            return self._get_fallback_story(story_type, topic)
    
    def _validate_story(self, story_data: Dict, topic: str) -> Dict:
        """Validate and ensure story has all required fields"""
        
        defaults = {
            "title": f"Amazing {topic} Story",
            "hook": f"Let me tell you something incredible about {topic}",
            "scenes": [],
            "moral": "Never stop learning!",
            "hashtags": ["storytelling", "motivation", "facts"]
        }
        
        for key, value in defaults.items():
            if key not in story_data or not story_data[key]:
                story_data[key] = value
        
        # Ensure scenes have all required fields
        for i, scene in enumerate(story_data["scenes"]):
            scene_defaults = {
                "scene_number": i + 1,
                "narration": f"Scene {i + 1} about {topic}",
                "text_overlay": f"Scene {i + 1}",
                "image_prompt": f"A beautiful scene about {topic}",
                "duration": 8
            }
            for key, value in scene_defaults.items():
                if key not in scene:
                    scene[key] = value
        
        return story_data
    
    def _get_fallback_story(self, story_type: str, topic: str) -> Dict:
        """Fallback story when API fails"""
        
        fallback_stories = {
            "motivational": {
                "title": f"The Power of {topic.title()}",
                "hook": f"Did you know {topic} can change your life?",
                "scenes": [
                    {
                        "scene_number": 1,
                        "narration": f"Every great journey begins with a single step. {topic} teaches us that success isn't overnight.",
                        "text_overlay": "Every Journey Starts",
                        "image_prompt": f"A person walking on a sunrise path, inspirational, cinematic",
                        "duration": 10
                    },
                    {
                        "scene_number": 2,
                        "narration": f"Those who master {topic} discover something powerful within themselves.",
                        "text_overlay": "Discover Your Power",
                        "image_prompt": f"A person standing on a mountain peak, triumphant, epic landscape",
                        "duration": 10
                    },
                    {
                        "scene_number": 3,
                        "narration": f"Your story with {topic} starts today. Take that first step.",
                        "text_overlay": "Start Today",
                        "image_prompt": f"A new beginning, sunrise over city, hopeful mood",
                        "duration": 10
                    }
                ],
                "moral": "The best time to start was yesterday. The second best time is now.",
                "hashtags": ["motivation", "inspiration", topic.lower().replace(" ", "")]
            },
            "history": {
                "title": f"The Story of {topic.title()}",
                "hook": f"History was made when {topic} changed everything.",
                "scenes": [
                    {
                        "scene_number": 1,
                        "narration": f"In the annals of history, {topic} stands as a pivotal moment that shaped our world.",
                        "text_overlay": "A Pivotal Moment",
                        "image_prompt": f"Historical scene, ancient times, dramatic lighting, cinematic",
                        "duration": 10
                    },
                    {
                        "scene_number": 2,
                        "narration": f"The people involved in {topic} never imagined they were making history.",
                        "text_overlay": "Making History",
                        "image_prompt": f"Historical figures in dramatic pose, epic scene",
                        "duration": 10
                    },
                    {
                        "scene_number": 3,
                        "narration": f"Today, we remember {topic} as a turning point in human civilization.",
                        "text_overlay": "A Turning Point",
                        "image_prompt": f"Modern memorial or monument, respectful mood",
                        "duration": 10
                    }
                ],
                "moral": "History teaches us that ordinary people can achieve extraordinary things.",
                "hashtags": ["history", "education", "facts", topic.lower().replace(" ", "")]
            },
            "fantasy": {
                "title": f"The Legend of {topic.title()}",
                "hook": f"In a world beyond imagination, {topic} held the key.",
                "scenes": [
                    {
                        "scene_number": 1,
                        "narration": f"Long ago, in a realm where magic flowed like rivers, there existed {topic}.",
                        "text_overlay": "A Magical Realm",
                        "image_prompt": f"Fantasy landscape, magical forest, ethereal lighting, mystical",
                        "duration": 10
                    },
                    {
                        "scene_number": 2,
                        "narration": f"The heroes of this tale discovered that {topic} held powers beyond comprehension.",
                        "text_overlay": "Untold Powers",
                        "image_prompt": f"Fantasy heroes discovering magical artifact, dramatic scene",
                        "duration": 10
                    },
                    {
                        "scene_number": 3,
                        "narration": f"And so, the legend of {topic} was born, a story told for generations.",
                        "text_overlay": "A Legend is Born",
                        "image_prompt": f"Legendary epic scene, golden light, majestic",
                        "duration": 10
                    }
                ],
                "moral": "Magic exists in those who dare to believe.",
                "hashtags": ["fantasy", "storytelling", "fiction", topic.lower().replace(" ", "")]
            },
            "facts": {
                "title": f"Mind-Blowing Facts About {topic.title()}",
                "hook": f"You won't believe what {topic} can do!",
                "scenes": [
                    {
                        "scene_number": 1,
                        "narration": f"Here's something incredible about {topic} that most people don't know.",
                        "text_overlay": "Did You Know?",
                        "image_prompt": f"Surprising discovery, mind-blown expression, colorful",
                        "duration": 10
                    },
                    {
                        "scene_number": 2,
                        "narration": f"Scientists and experts have found that {topic} defies everything we thought we knew.",
                        "text_overlay": "Defying Expectations",
                        "image_prompt": f"Scientific discovery, research, breakthrough moment",
                        "duration": 10
                    },
                    {
                        "scene_number": 3,
                        "narration": f"Share this with someone who needs to know this amazing fact about {topic}!",
                        "text_overlay": "Share the Knowledge",
                        "image_prompt": f"Sharing knowledge, connection, social media vibe",
                        "duration": 10
                    }
                ],
                "moral": "Knowledge is power. Share it generously.",
                "hashtags": ["facts", "didyouknow", "amazing", topic.lower().replace(" ", "")]
            }
        }
        
        return fallback_stories.get(story_type, fallback_stories["motivational"])
    
    def generate_image_prompts(self, story_data: Dict) -> List[str]:
        """Extract image prompts from story data"""
        return [scene.get("image_prompt", "A beautiful scene") 
                for scene in story_data.get("scenes", [])]


def main():
    """Test the story generator"""
    generator = StoryGenerator()
    
    # Test with motivational story
    story = generator.generate_story(
        story_type="motivational",
        topic="perseverance",
        duration=30
    )
    
    print("Generated Story:")
    print(json.dumps(story, indent=2))


if __name__ == "__main__":
    main()