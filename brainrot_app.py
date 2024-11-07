from dotenv import load_dotenv
import extra_streamlit_components as stx
import os
import streamlit as st
import time
from core import createChatCompletion, getTextFromPDF
from media import generateTextToSpeech, combineVideoAndAudio
from captions import generateSubtitles
from utils import processStep

load_dotenv(override=True)

# System prompt for brainrot explainer
SYSTEM_PROMPT = os.getenv('SYSTEM_PROMPT', '')
DEFAULT_WIDTH = int(os.getenv('DEFAULT_WIDTH', 80))

# Streamlit app interface
st.title("Brainrot Generator")
st.write("Enter any text, and get a simple summary that even a gen-z kid could understand.")

# Text input for user
tab = stx.tab_bar(data=[
    stx.TabBarItemData(id="text", title="Type Text",
                       description="Brainrotize your input text."),
    stx.TabBarItemData(id="pdf", title="Upload PDF",
                       description="Brainrotize an entire PDF.")
], default="text")

user_input = None
if tab == "text":
    user_input = st.text_area("Enter text to brainrotize:", "")
elif tab == "pdf":
    uploaded_file = st.file_uploader("Choose a file", type='pdf')
    if uploaded_file is not None:
        pdf_text = getTextFromPDF(uploaded_file)
        user_input = pdf_text
else:
    result = "Select an option first"

if st.button("Brainrotize"):
    if user_input:
        try:
            with st.status('Going to Ohio...') as status:
                initial_start_time = time.time()

                brainrot = processStep(
                    status,
                    "Asking the rizzler to turn your words into W brainrot...",
                    createChatCompletion,
                    user_input,
                    SYSTEM_PROMPT
                )

                brainrot_tts_filepath = processStep(
                    status,
                    "Me when I go to the audio generation competition and my opponent is you...",
                    generateTextToSpeech,
                    brainrot,
                )

                brainrot_video_filepath = processStep(
                    status,
                    "I went to video generation island and everyone knew you...",
                    combineVideoAndAudio,
                    audio_file=brainrot_tts_filepath,
                )

                brainrot_srt_filepath = processStep(
                    status,
                    "Generating captions...",
                    generateSubtitles,
                    brainrot_tts_filepath,
                    brainrot,
                    'output_folder/subtitles.srt',
                )

                # Print total elapsed time
                total_elapsed_time = time.time() - initial_start_time
                status.update(label=f"W brainrot 🗿 ({
                              total_elapsed_time:.2f} secs)", state="complete", expanded=False)

            st.subheader("Brainrot")
            width = DEFAULT_WIDTH
            side = max((100 - width) / 2, 0.01)
            _, container, _ = st.columns([side, width, side])
            container.video(data=brainrot_video_filepath, format='video/mp4',
                            subtitles=brainrot_srt_filepath, autoplay=False)
        except Exception as e:
            st.error(f"An error occurred: {e}")
    else:
        st.warning("Please enter some text to brainrotize.")
