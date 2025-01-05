import streamlit as st
from dotenv import load_dotenv
import os
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs

load_dotenv()  # Load environment variables

# Configure Google Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

st.set_page_config(page_title="YT", page_icon="🖥️")

prompt = """You are a YouTube video summarizer. Summarize the video transcript into key points within 250 words: """

# Extract video ID
def extract_video_id(youtube_video_url):
    try:
        parsed_url = urlparse(youtube_video_url)
        query_params = parse_qs(parsed_url.query)
        if "v" in query_params:
            return query_params["v"][0]
        else:
            # If the URL contains no query parameters, extract from path
            path_parts = parsed_url.path.split("/")
            if len(path_parts) > 1:
                return path_parts[-1]
        return None
    except Exception as e:
        st.error(f"Invalid YouTube URL: {e}")
        return None

# Get transcript
def extract_transcript_details(youtube_video_url):
    try:
        video_id = extract_video_id(youtube_video_url)
        if not video_id:
            raise ValueError("Invalid YouTube URL")

        transcript_text = YouTubeTranscriptApi.get_transcript(video_id)
        transcript = " ".join([i["text"] for i in transcript_text])
        return transcript

    except Exception as e:
        st.error("Unable to retrieve transcript: " + str(e))
        return None

# Generate Gemini content
def generate_gemini_content(transcript_text, prompt):
    try:
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(prompt + transcript_text)
        return response.text
    except Exception as e:
        st.error(f"Error generating summary: {e}")
        return None

# App UI
st.title("YouTube Transcript to Detailed Notes Converter")
youtube_link = st.text_input("Enter YouTube Video Link:")

if youtube_link:
    video_id = extract_video_id(youtube_link)
    if video_id:
        # Display video thumbnail
        st.image(f"https://img.youtube.com/vi/{video_id}/0.jpg", use_container_width=True)

if st.button("Get Detailed Notes"):
    transcript_text = extract_transcript_details(youtube_link)

    if transcript_text:
        summary = generate_gemini_content(transcript_text, prompt)
        if summary:
            st.markdown("## Detailed Notes:")
            st.write(summary)
    else:
        st.warning("Transcript could not be retrieved. Please check the video.")

# Page background styling (optional)
page_bg_img = '''
    <style>
        h1 {
            text-align: center;
        }
    </style>
'''
st.markdown(page_bg_img, unsafe_allow_html=True)
