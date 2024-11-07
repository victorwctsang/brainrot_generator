from datetime import timedelta
from dotenv import load_dotenv
from gtts import gTTS
from openai import OpenAI
from PyPDF2 import PdfReader
import extra_streamlit_components as stx
import ffmpeg
import os
import srt
import streamlit as st
import time
import whisper

load_dotenv(override=True)

################################################################################
# Functions
################################################################################

# System prompt for brainrot explainer
SYSTEM_PROMPT = os.getenv('SYSTEM_PROMPT', '')
DEFAULT_WIDTH = int(os.getenv('DEFAULT_WIDTH', 80))


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
        speed (float): The factor by which to speed up the audio (default is 1.75x).

    Raises:
        ValueError: If the speed value is not within the valid range for the 'atempo' filter (0.5 to 2.0).
    """
    # Check if the speed value is valid for the 'atempo' filter
    if not 0.5 <= speed <= 2.0:
        raise ValueError("Invalid speed value. 'atempo' filter supports a speed range of 0.5 to 2.0")

    # Adjust the atempo filter to the desired speed
    (
        ffmpeg
        .input(input_file)
        .filter('atempo', speed)
        .output(output_file)
        .run(overwrite_output=True)
    )

def generateTextToSpeech(text, language='en', filename='audio.mp3'):
    """Generates a text-to-speech audio file.

    This function uses gTTS to convert the given text into speech in the specified language.
    It then speeds up the generated audio by a factor of 1.5 and saves it to the specified filename.

    Args:
        text: The text to convert to speech.
        language: The language code (e.g., 'en' for English, 'es' for Spanish). Defaults to 'en'.
        filename: The name of the output audio file. Defaults to 'audio.mp3'.

    Returns:
        The filepath of the generated audio file.
    """
    tmp_filepath = f"output_folder/tmp-{filename}"
    filepath = f"output_folder/{filename}"
    tts_obj = gTTS(text=text, lang=language, slow=False)
    tts_obj.save(tmp_filepath)
    speed_up_audio(input_file=tmp_filepath, output_file=filepath, speed=1.5)
    os.remove(tmp_filepath)  # Clean up temporary file
    return filepath


def combineVideoAndAudio(video_file='input_folder/subway_surfers.mp4', audio_file='output_folder/audio.mp3', output_filepath='output_folder/finished_video.mp4'):
    """
    Combines video and audio files into a single output file without re-encoding the video.

    Args:
        video_file (str): Path to the video file.
        audio_file (str): Path to the audio file.
        output_filepath (str): Path to the output video file.

    Returns:
        str: Path to the combined output video.
    """

    input_video = ffmpeg.input(video_file)
    input_audio = ffmpeg.input(audio_file)
    (
        ffmpeg
        .output(input_video['v'], input_audio['a'], output_filepath, format='mp4', vcodec='copy', acodec='copy', shortest=None)
        .run(overwrite_output=True)
    )
    return output_filepath


def load_and_transcribe(input_audio_filepath):
    """Loads an audio file and transcribes it using the Whisper model.

    Args:
        input_audio_filepath: Path to the input audio file.

    Returns:
        A dictionary containing the transcription results from Whisper.
    """
    model = whisper.load_model("small")
    whisper_result = model.transcribe(
        input_audio_filepath, task="transcribe", fp16=False)
    return whisper_result


def calculate_target_word_counts(whisper_result, original_text):
    """Calculates the target word count for each segment in the transcription.

    The target word count is determined based on the duration of each segment
    relative to the total duration of the audio and the total number of words
    in the original text.

    Args:
        whisper_result: A dictionary containing the transcription results from Whisper.
        original_text: The original text corresponding to the audio.

    Returns:
        A list of target word counts for each segment.
    """
    original_text_words = original_text.split()
    total_words = len(original_text_words)

    # Total duration of all segments
    total_duration = sum(segment["end"] - segment["start"]
                         for segment in whisper_result["segments"])

    # Calculate target word count for each segment
    target_word_counts = [
        round((segment["end"] - segment["start"]) /
              total_duration * total_words)
        for segment in whisper_result["segments"]
    ]

    return target_word_counts


def split_text_into_chunks(original_text, target_word_counts):
    """Splits the original text into chunks based on the target word counts.

    Args:
        original_text: The original text to be split.
        target_word_counts: A list of target word counts for each chunk.

    Returns:
        A list of text chunks.
    """
    original_text_words = original_text.split()
    original_text_chunks = []
    word_index = 0

    for word_count in target_word_counts:
        chunk = " ".join(
            original_text_words[word_index:word_index + word_count])
        original_text_chunks.append(chunk)
        word_index += word_count

    return original_text_chunks


def create_subtitles(whisper_result, original_text_chunks):
    """Creates subtitle entries from the Whisper transcription and text chunks.

    Args:
        whisper_result: A dictionary containing the transcription results from Whisper.
        original_text_chunks: A list of text chunks.

    Returns:
        A list of subtitle objects.
    """
    subs = []
    for i, chunk in enumerate(original_text_chunks):
        # Ensure we don't go out of bounds
        if i < len(whisper_result["segments"]):
            segment = whisper_result["segments"][i]
            start = timedelta(seconds=segment["start"])
            end = timedelta(seconds=segment["end"])
            subs.append(srt.Subtitle(index=i + 1, start=start,
                        end=end, content=chunk.strip()))

    return subs


def save_srt_file(subtitles, output_srt_filepath):
    """Generates SRT content from subtitles and saves it to a file.

    Args:
        subtitles: A list of subtitle objects.
        output_srt_filepath: Path to the output SRT file.
    """
    srt_content = srt.compose(subtitles)
    with open(output_srt_filepath, "w") as f:
        f.write(srt_content)
    print(f"SRT file created at {output_srt_filepath}")


def generate_srt(input_audio_filepath, original_text, output_srt_filepath):
    """Generates an SRT file from an audio file and its corresponding text.

    This function orchestrates the entire process of loading the audio,
    transcribing it, splitting the text into chunks, creating subtitles,
    and saving the SRT file.

    Args:
        input_audio_filepath: Path to the input audio file.
        original_text: The original text corresponding to the audio.
        output_srt_filepath: Path to the output SRT file.

    Returns:
        The path to the output SRT file.
    """
    whisper_result = load_and_transcribe(input_audio_filepath)
    target_word_counts = calculate_target_word_counts(
        whisper_result, original_text)
    original_text_chunks = split_text_into_chunks(
        original_text, target_word_counts)
    subtitles = create_subtitles(whisper_result, original_text_chunks)
    save_srt_file(subtitles, output_srt_filepath)
    return output_srt_filepath


def process_step(status, message, function, *args, **kwargs):
    """Processes a single step of a pipeline, providing status updates.

    This function executes a given function with the provided arguments and
    displays status updates in a Streamlit application. It also measures
    and displays the execution time of the function.

    Args:
        status: The Streamlit status object.
        message: The message to display in the status update.
        function: The function to execute.
        *args: Positional arguments to pass to the function.
        **kwargs: Keyword arguments to pass to the function.

    Returns:
        The result of the  
    function call.
    """
    status_message = message
    st.info(icon='💬', body=status_message)
    status.update(label=status_message, state="running", expanded=True)
    start_time = time.time()
    result = function(*args, **kwargs)
    end_time = time.time()
    elapsed_time = end_time - start_time
    if result:
        st.success(icon='🔥', body=f'{
                   message} (Time taken: {elapsed_time:.2f} secs)')
    return result


################################################################################
# Interface
################################################################################

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

                brainrot = process_step(
                    status,
                    "Asking the rizzler to turn your words into W brainrot...",
                    createChatCompletion,
                    user_input,
                )

                brainrot_tts_filepath = process_step(
                    status,
                    "Me when I go to the audio generation competition and my opponent is you...",
                    generateTextToSpeech,
                    brainrot,
                )

                brainrot_video_filepath = process_step(
                    status,
                    "I went to video generation island and everyone knew you...",
                    combineVideoAndAudio,
                    audio_file=brainrot_tts_filepath,
                )

                brainrot_srt_filepath = process_step(
                    status,
                    "Generating captions...",
                    generate_srt,
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
