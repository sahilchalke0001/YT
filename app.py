import streamlit as st
from dotenv import load_dotenv
import os
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi

# Load environment variables from .env file
load_dotenv()

# Configure Google Gemini API key
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    st.error("⚠️ GOOGLE_API_KEY not found! Please add it to your .env file.")
    st.stop()

# Configure Gemini API
genai.configure(api_key=api_key)

# Page config
st.set_page_config(
    page_title="YouTube to Notes",
    page_icon="📚",
)

# UI Heading
st.title("🎥 YouTube Transcript to Detailed Notes Converter")

# Initial Prompt
prompt = """
You are a YouTube video summarizer. You will receive transcript text and summarize the entire video.
Provide an accurate summary in bullet points within 250 words. Please summarize the text below:
"""

### ✅ Get Transcript from YouTube
def extract_transcript_details(youtube_video_url):
    try:
        if "=" not in youtube_video_url:
            st.error("Invalid YouTube URL. Please check the link.")
            return None
        
        # Extract video ID
        video_id = youtube_video_url.split("=")[1]

        # Get transcript
        transcript_data = YouTubeTranscriptApi.get_transcript(video_id)
        transcript = " ".join([item["text"] for item in transcript_data])
        return transcript

    except Exception as e:
        st.error(f"Error fetching transcript: {e}")
        return None


### ✅ Generate Gemini Content
def generate_gemini_content(transcript_text, prompt):
    try:
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(prompt + transcript_text)

        # Check if response is valid
        if response and response.text:
            return response.text
        else:
            return "⚠️ No response generated. Please check the input or model configuration."
    except Exception as e:
        return f"Error: {e}"


# ✅ Get YouTube Link Input
youtube_link = st.text_input("🎥 Enter YouTube Video Link:")

if youtube_link:
    try:
        video_id = youtube_link.split("=")[1]
        st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", use_container_width=True)
    except Exception:
        st.warning("Unable to load video preview. Please check the URL.")

# ✅ Button to Get Notes
if st.button("Get Detailed Notes"):
    transcript_text = extract_transcript_details(youtube_link)

    if transcript_text:
        summary = generate_gemini_content(transcript_text, prompt)
        
        if "Error" not in summary:
            st.markdown("## 📚 Detailed Notes:")
            st.write(summary)
        else:
            st.error(summary)
    else:
        st.error("❗ No transcript found. Please try another video.")

# Optional - Page Background Styling
page_bg_img = '''
    <style>
        h1 {
            text-align: center;
        }
    </style>
'''
st.markdown(page_bg_img, unsafe_allow_html=True)
