import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import extra_streamlit_components as stx
import os
from gtts import gTTS
from PyPDF2 import PdfReader
import ffmpeg

load_dotenv(override=True)

########################################################################################################################
# Functions
########################################################################################################################

# System prompt for brainrot explainer
SYSTEM_PROMPT = os.getenv('SYSTEM_PROMPT')
DEFAULT_WIDTH = int(os.getenv('DEFAULT_WIDTH'))

def createChatCompletion(text_input):
    """
    Generates a completion response from the OpenAI API based on user input.

    Args:
        text_input (str): The user-provided input text to be processed by the language model.

    Returns:
        str: The AI-generated response content based on the provided input.
    """
    client = OpenAI()
    completion = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": text_input
    }])
    return completion.choices[0].message.content

def getTextFromPDF(file):
    """
    Extracts text content from each page of a PDF file.

    Args:
        file (str or file-like object): The PDF file to be read. Can be a file path or a file-like object.

    Returns:
        str: The combined text content of all pages in the PDF.
    """
    reader = PdfReader(file)
    pdf_text = ' '.join([page.extract_text() for page in reader.pages])
    return pdf_text

def splitTextIntoChunks(text, chunk_size=40):
    """
    Splits a long text into chunks of roughly the specified character length, ensuring words are not split.

    Args:
        text (str): The input text to be split into chunks.
        chunk_size (int): The target length of each chunk in characters (default is 40).

    Returns:
        list of str: A list of text chunks, each approximately chunk_size characters long, with words intact.
    """
    words = text.split()
    chunks = []
    current_chunk = []

    for word in words:
        # Check if adding this word would exceed the chunk size
        if len(' '.join(current_chunk + [word])) <= chunk_size:
            current_chunk.append(word)
        else:
            # Add the current chunk to the chunks list and start a new one
            chunks.append(' '.join(current_chunk))
            current_chunk = [word]

    # Append any remaining words as the last chunk
    if current_chunk:
        chunks.append(' '.join(current_chunk))

    return chunks

def speed_up_audio(input_file, output_file, speed=1.75):
    """
    Speeds up an audio file by a specified factor using ffmpeg.

    Args:
        input_file (str): Path to the input audio file.
        output_file (str): Path to save the sped-up output audio file.
        speed (float): The factor by which to speed up the audio (default is 1.5x).
    """
    # Adjust the atempo filter to the desired speed
    # Note: 'atempo' supports a range of 0.5 to 2.0, so for 1.5x we can apply it directly
    (
        ffmpeg
        .input(input_file)
        .filter('atempo', speed)
        .output(output_file)
        .run(overwrite_output=True)
    )

def generateTextToSpeech(text, language='en', filename='audio.mp3'):
    tmp_filepath = f"output_folder/tmp-{filename}"
    filepath = f"output_folder/{filename}"
    tts_obj = gTTS(text=text, lang=language, slow=False)
    tts_obj.save(tmp_filepath)
    speed_up_audio(input_file=tmp_filepath, output_file=filepath, speed=1.5)
    return filepath

def combineVideoAndAudio(video_file='input_folder/subway_surfers.mp4', audio_file='output_folder/audio.mp3', output_filepath='output_folder/finished_video.mp4'):
    input_video = ffmpeg.input(video_file)
    input_audio = ffmpeg.input(audio_file)
    (
        ffmpeg
        .concat(input_video, input_audio, v=1, a=1)
        .output(output_filepath, shortest=None)
        .run(overwrite_output=True)
    )
    return output_filepath

########################################################################################################################
# Interface
########################################################################################################################

# Streamlit app interface
st.title("Brainrot Generator")
st.write("Enter any text, and get a simple summary that even a gen-z kid could understand.")

# Text input for user
tab = stx.tab_bar(data=[
    stx.TabBarItemData(id="text", title="Type Text", description="Brainrotize your input text."),
    stx.TabBarItemData(id="pdf", title="Upload PDF", description="Brainrotize an entire PDF.")
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
                status_message = "Asking the rizzler to turn your words into W brainrot..."
                st.info(icon='💬', body=status_message)
                status.update(label=status_message, state="running", expanded=True)
                brainrot = createChatCompletion(user_input)

                status_message = "Me when I go to the audio generation competition and my opponent is you..."
                st.info(icon='💬', body=status_message)
                status.update(label=status_message, state="running", expanded=True)
                brainrot_tts_filepath = generateTextToSpeech(brainrot)

                status_message = "I went to video generation island and everyone knew you..."
                st.info(icon='💬', body=status_message)
                status.update(label=status_message, state="running", expanded=False)
                brainrot_video_filepath = combineVideoAndAudio(audio_file=brainrot_tts_filepath)

                status.update(label="W brainrot 🗿", state="complete", expanded=False)

            st.subheader("Brainrot")
            width = DEFAULT_WIDTH
            side = max((100 - width) / 2, 0.01)
            _, container, _ = st.columns([side, width, side])
            container.video(data=brainrot_video_filepath, format='video/mp4', autoplay=True)
        except Exception as e:
            st.error(f"An error occurred: {e}")
    else:
        st.warning("Please enter some text to brainrotize.")


