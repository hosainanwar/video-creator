"""Streamlit UI for Video Creator AI"""

import streamlit as st
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.config import STORY_TYPES, OUTPUT_DIR, LLM_PROVIDER
from src.story_generator import StoryGenerator
from src.voice_generator import VoiceGenerator
from src.image_generator import ImageGenerator
from src.video_assembler import VideoAssembler


# Page config
st.set_page_config(
    page_title="Video Creator AI",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #6c63ff;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stButton > button {
        background-color: #6c63ff;
        color: white;
        width: 100%;
        padding: 0.75rem;
        font-size: 1.1rem;
        border-radius: 8px;
    }
    .stButton > button:hover {
        background-color: #5a52d5;
    }
    .info-box {
        background-color: #1a1a2e;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #6c63ff;
    }
</style>
""", unsafe_allow_html=True)


def main():
    """Main Streamlit app"""
    
    # Header
    st.markdown('<p class="main-header">🎬 Video Creator AI</p>', unsafe_allow_html=True)
    st.markdown("Create storytelling social media content with AI")
    
    # Sidebar
    with st.sidebar:
        st.header("Settings")
        
        # LLM Provider selection
        llm_provider = st.selectbox(
            "LLM Provider",
            options=["ollama", "openai"],
            index=0 if LLM_PROVIDER == "ollama" else 1,
            format_func=lambda x: "Ollama (Local)" if x == "ollama" else "OpenAI (API)"
        )
        
        # Story type selection
        story_type = st.selectbox(
            "Story Type",
            options=STORY_TYPES,
            format_func=lambda x: x.title()
        )
        
        # Topic input
        topic = st.text_input(
            "Topic",
            placeholder="e.g., perseverance, ancient Egypt, space exploration"
        )
        
        # Duration slider
        duration = st.slider(
            "Video Duration (seconds)",
            min_value=15,
            max_value=180,
            value=60,
            step=15
        )
        
        # Advanced options
        with st.expander("Advanced Options"):
            use_ai_images = st.checkbox(
                "Use AI Images (Stable Diffusion)",
                value=False,
                help="Requires additional setup"
            )
            
            output_name = st.text_input(
                "Output Filename",
                placeholder="Leave empty for auto-naming"
            )
        
        # API Keys
        with st.expander("API Keys"):
            if llm_provider == "openai":
                openai_key = st.text_input(
                    "OpenAI API Key",
                    type="password",
                    help="Enter your OpenAI API key"
                )
                if openai_key:
                    os.environ["OPENAI_API_KEY"] = openai_key
            
            pexels_key = st.text_input(
                "Pexels API Key",
                type="password",
                help="Get free key at pexels.com/api"
            )
            
            if pexels_key:
                os.environ["PEXELS_API_KEY"] = pexels_key
                st.success("Pexels API key set!")
    
    # Main content
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Story Preview")
        
        if topic:
            st.info(f"**Type:** {story_type.title()}\n\n**Topic:** {topic}\n\n**Duration:** {duration} seconds")
        else:
            st.warning("Enter a topic to begin")
    
    with col2:
        st.subheader("Generate Video")
        
        if st.button("🎬 Create Video", type="primary"):
            if not topic:
                st.error("Please enter a topic!")
                return
            
            with st.spinner("Creating your video..."):
                # Initialize components
                story_gen = StoryGenerator(provider=llm_provider)
                voice_gen = VoiceGenerator()
                image_gen = ImageGenerator(use_ai=use_ai_images)
                video_assembler = VideoAssembler()
                
                # Generate story
                st.write("📝 Generating story...")
                story_data = story_gen.generate_story(story_type, topic, duration)
                
                if story_data:
                    st.success(f"Story: {story_data.get('title', 'Untitled')}")
                    
                    # Generate voiceovers
                    st.write("🎙️ Generating voiceovers...")
                    scenes = story_data.get("scenes", [])
                    scenes = voice_gen.generate_all_scenes(scenes)
                    
                    # Fetch images
                    st.write("🖼️ Fetching images...")
                    scenes = image_gen.get_images_for_scenes(scenes)
                    
                    # Assemble video
                    st.write("🎬 Assembling video...")
                    
                    # Generate output name
                    if not output_name:
                        safe_topic = "".join(c for c in topic if c.isalnum() or c in ' -').strip()
                        safe_topic = safe_topic.replace(' ', '_')[:30]
                        final_output_name = f"{story_type}_{safe_topic}"
                    else:
                        final_output_name = output_name
                    
                    video_path = video_assembler.assemble_video(scenes, final_output_name)
                    
                    if video_path:
                        st.success("✅ Video created!")
                        
                        # Show video info
                        video_info = video_assembler.get_video_info(video_path)
                        
                        st.write(f"**Duration:** {video_info.get('duration', 0):.1f} seconds")
                        st.write(f"**File Size:** {video_info.get('file_size', 0):.1f} MB")
                        
                        # Display video
                        st.video(video_path)
                        
                        # Download button
                        with open(video_path, 'rb') as f:
                            st.download_button(
                                label="📥 Download Video",
                                data=f.read(),
                                file_name=f"{final_output_name}.mp4",
                                mime="video/mp4"
                            )
                        
                        # Show story data
                        with st.expander("View Story Data"):
                            st.json(story_data)
                    else:
                        st.error("Failed to create video")
                else:
                    st.error("Failed to generate story")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    ### Quick Start Guide
    
    1. **Install dependencies:** `pip install -r requirements.txt`
    2. **Run Ollama:** `ollama run llama3` (for story generation)
    3. **Optional:** Get a free Pexels API key for stock photos
    
    **Story Types:**
    - **Motivational** - Inspiring stories about overcoming challenges
    - **History** - Historical events and famous figures
    - **Fantasy** - Magical and fictional stories
    - **Facts** - Mind-blowing facts and information
    """)


if __name__ == "__main__":
    main()