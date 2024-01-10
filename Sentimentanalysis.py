from openai import OpenAI
from dotenv import load_dotenv
import streamlit as st
from pathlib import Path
import moviepy.editor
import os

load_dotenv()
client = OpenAI()

st.title("Sentiment Analysis")
st.divider()
st.sidebar.title("Upload Video")

uploaded_file = st.sidebar.file_uploader("Choose a video file...", type=["mp4", "mpeg"])

if uploaded_file is not None:
    try:
        video_path = Path(uploaded_file.name)
        with open(video_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        video = moviepy.editor.VideoFileClip(str(video_path))
        audio = video.audio
        audio_path = "temp_audio.ogg"
        audio.write_audiofile(audio_path, codec='libvorbis')  # Specify codec for OGG format
        st.subheader("Soundtrack")
        st.audio(audio_path, format='audio/ogg')  # Play the audio

        with open(audio_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
            st.subheader("Transcript")
            text = transcript.text
            st.write(text)
        # Deleting temporary audio file
        os.remove(audio_path)

        response = client.moderations.create(input=text)
        output = response.results[0]
        st.subheader("Analysis Result")
        st.write(output.categories)
        st.subheader("Category Score")
        st.write(output.category_scores)
            
    except moviepy.editor.ImageioError as e:
        st.warning("Error: Video file not supported or incorrect format.")
    except Exception as e:
        st.warning(f"Error processing the video: {e}")
