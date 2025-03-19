import streamlit as st
from dotenv import load_dotenv
import os
import time
import json
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Set page title and icon
st.set_page_config(
    page_title="YT Transcript Summarizer",
    page_icon="🖥️",
)

# Prompt for Gemini model
prompt = """
You are a YouTube video summarizer. You will take the transcript text
and summarize the entire video, providing the important points within 250 words.
Please provide the summary of the text given here:
"""

# Define transcript caching folder
TRANSCRIPT_CACHE_DIR = "transcripts"

# Ensure cache directory exists
if not os.path.exists(TRANSCRIPT_CACHE_DIR):
    os.makedirs(TRANSCRIPT_CACHE_DIR)


### ✅ Load cached transcript if available
def load_transcript(video_id):
    transcript_path = f"{TRANSCRIPT_CACHE_DIR}/{video_id}.json"
    if os.path.exists(transcript_path):
        with open(transcript_path, "r") as file:
            return json.load(file)
    return None


### ✅ Save transcript to avoid duplicate API requests
def save_transcript(video_id, transcript):
    transcript_path = f"{TRANSCRIPT_CACHE_DIR}/{video_id}.json"
    with open(transcript_path, "w") as file:
        json.dump(transcript, file)


### ✅ Extract transcript with error handling and rate limiting
def extract_transcript_details(youtube_video_url):
    try:
        if "=" not in youtube_video_url:
            st.error("Invalid YouTube URL. Please check the link.")
            return None
        
        # Extract video ID from URL
        video_id = youtube_video_url.split("=")[1]

        # Check if transcript is already cached
        cached_transcript = load_transcript(video_id)
        if cached_transcript:
            return cached_transcript

        # Delay to avoid hitting rate limits
        time.sleep(5)

        # Fetch transcript
        transcript_data = YouTubeTranscriptApi.get_transcript(video_id)
        transcript = " ".join([item["text"] for item in transcript_data])

        # Cache the transcript
        save_transcript(video_id, transcript)

        return transcript

    except Exception as e:
        st.error(f"Error fetching transcript: {e}")
        return None


### ✅ Generate content using Gemini API
def generate_gemini_content(transcript_text, prompt):
    try:
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(prompt + transcript_text)
        return response.text
    except Exception as e:
        st.error(f"Error generating summary: {e}")
        return "Unable to generate a summary."


### 🎯 Streamlit UI
st.title("YouTube Transcript to Detailed Notes Converter")
youtube_link = st.text_input("Enter YouTube Video Link:")

# Show thumbnail when a link is provided
if youtube_link:
    try:
        video_id = youtube_link.split("=")[1]
        st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", use_container_width=True)
    except IndexError:
        st.error("Invalid YouTube URL. Please check the link format.")

# Button to get the transcript and generate a summary
if st.button("Get Detailed Notes"):
    transcript_text = extract_transcript_details(youtube_link)

    if transcript_text:
        summary = generate_gemini_content(transcript_text, prompt)
        st.markdown("## 📚 Detailed Notes:")
        st.write(summary)

# Page background styling (optional)
page_bg_img = '''
    <style>
        h1 {
            text-align: center;
        }
    </style>
    '''
st.markdown(page_bg_img, unsafe_allow_html=True)
