import ffmpeg
import os
from gtts import gTTS

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
