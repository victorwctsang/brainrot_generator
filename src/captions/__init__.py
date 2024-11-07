from datetime import timedelta
import srt
import whisper


def loadAndTranscribe(input_audio_filepath):
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


def calculateTargetWordCounts(whisper_result, original_text):
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


def splitTextIntoChunks(original_text, target_word_counts):
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


def createSubtitles(whisper_result, original_text_chunks):
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


def saveSrtFile(subtitles, output_srt_filepath):
    """Generates SRT content from subtitles and saves it to a file.

    Args:
        subtitles: A list of subtitle objects.
        output_srt_filepath: Path to the output SRT file.
    """
    srt_content = srt.compose(subtitles)
    with open(output_srt_filepath, "w") as f:
        f.write(srt_content)
    print(f"SRT file created at {output_srt_filepath}")


def generateSubtitles(input_audio_filepath, original_text, output_srt_filepath):
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
    whisper_result = loadAndTranscribe(input_audio_filepath)
    target_word_counts = calculateTargetWordCounts(
        whisper_result, original_text)
    original_text_chunks = splitTextIntoChunks(
        original_text, target_word_counts)
    subtitles = createSubtitles(whisper_result, original_text_chunks)
    saveSrtFile(subtitles, output_srt_filepath)
    return output_srt_filepath
