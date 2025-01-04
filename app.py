import streamlit as st
from dotenv import load_dotenv
import os
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi, _errors

load_dotenv()  # Load all environment variables

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

st.set_page_config(
    page_title="YT",
    page_icon="🖥️",
)

prompt = """You are YouTube video summarizer. You will be taking the transcript text
and summarizing the entire video and providing the important summary in points
within 250 words. Please provide the summary of the text given here:  """

# Get the transcript data from YouTube videos
def extract_transcript_details(youtube_video_url):
    try:
        video_id = youtube_video_url.split("=")[1]
        
        # Attempt to retrieve the transcript
        transcript_text = YouTubeTranscriptApi.get_transcript(video_id)

        transcript = ""
        for i in transcript_text:
            transcript += " " + i["text"]

        return transcript

    except _errors.TranscriptsDisabled as e:
        # Handle the case where subtitles are disabled for the video
        return "Subtitles are disabled for this video. Unable to retrieve transcript."

    except Exception as e:
        # Catch any other exceptions
        return f"An error occurred: {e}"

# Get the summary based on the prompt from Google Gemini Pro
def generate_gemini_content(transcript_text, prompt):
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt + transcript_text)
    return response.text

# Streamlit UI
st.title("YouTube Transcript to Detailed Notes Converter")
youtube_link = st.text_input("Enter YouTube Video Link:")

if youtube_link:
    video_id = youtube_link.split("=")[1]
    st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", use_container_width=True, width=600)

col1, col2, col3 = st.columns(3)

transcript_text = None  # Initialize transcript_text here

with col2:
    if st.button("Get Detailed Notes"):
        transcript_text = extract_transcript_details(youtube_link)

if transcript_text:
    summary = generate_gemini_content(transcript_text, prompt)
    st.markdown("## Detailed Notes:")
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


