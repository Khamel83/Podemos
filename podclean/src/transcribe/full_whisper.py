from faster_whisper import WhisperModel
import os

# Global model instance to avoid reloading for each transcription
_full_model = None

def get_full_whisper_model(model_size: str = "medium", device: str = "auto", compute_type: str = "auto"):
    global _full_model
    if _full_model is None:
        print(f"Loading full Whisper model: {model_size} on {device} with {compute_type} compute type...")
        _full_model = WhisperModel(model_size, device=device, compute_type=compute_type)
        print("Full Whisper model loaded.")
    return _full_model

def full_transcribe(audio_path: str, model_size: str = "medium", vad: bool = True, beam_size: int = 2, word_timestamps: bool = True):
    """
    Performs full transcription of an audio file using faster-whisper.

    Args:
        audio_path: Path to the audio file.
        model_size: Size of the Whisper model to use (e.g., "medium", "large").
        vad: Whether to use Voice Activity Detection.
        beam_size: Beam size for transcription.
        word_timestamps: Whether to return word-level timestamps.

    Returns:
        A list of dictionaries, each representing a segment with 'start', 'end', and 'text'.
        If word_timestamps is True, each segment will also contain 'words'.
    """
    if not os.path.exists(audio_path):
        print(f"Error: Audio file not found at {audio_path}")
        return []

    model = get_full_whisper_model(model_size, device="auto", compute_type="auto") # Use auto for device and compute_type

    segments, info = model.transcribe(
        audio_path,
        vad_filter=vad,
        beam_size=beam_size,
        word_timestamps=word_timestamps
    )

    transcription_results = []
    for segment in segments:
        segment_data = {
            "start": segment.start,
            "end": segment.end,
            "text": segment.text
        }
        if word_timestamps:
            segment_data["words"] = [{
                "word": word.word,
                "start": word.start,
                "end": word.end,
                "probability": word.probability
            } for word in segment.words]
        transcription_results.append(segment_data)

    print(f"Full Transcription complete for {audio_path}. Language: {info.language}, Duration: {info.duration_after_vad}s")
    return transcription_results

if __name__ == "__main__":
    # Example usage (requires a dummy audio file)
    # Create a dummy audio file for testing:
    # ffmpeg -f lavfi -i "sine=frequency=1000:duration=10" test_audio_full.mp3
    test_audio_path = "test_audio_full.mp3" # Create this file for testing
    if os.path.exists(test_audio_path):
        print(f"Transcribing {test_audio_path} with full model...")
        results = full_transcribe(test_audio_path, model_size="tiny", vad=True, beam_size=2, word_timestamps=True)
        for segment in results:
            print(f"[{segment['start']:.2f}s -> {segment['end']:.2f}s] {segment['text']}")
            if 'words' in segment:
                for word in segment['words']:
                    print(f"  - {word['word']} ({word['start']:.2f}s-{word['end']:.2f}s)")
    else:
        print(f"Please create a dummy audio file named '{test_audio_path}' in the current directory for testing.")
        print("You can create one using: ffmpeg -f lavfi -i \"sine=frequency=1000:duration=10\" test_audio_full.mp3")
