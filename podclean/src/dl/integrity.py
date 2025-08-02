import subprocess
import json
import os

def get_audio_duration(file_path: str) -> float | None:
    """
    Gets the duration of an audio file using ffprobe.

    Args:
        file_path: Path to the audio file.

    Returns:
        Duration in seconds as a float, or None if an error occurs.
    """
    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        return None

    command = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "json",
        file_path
    ]

    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        data = json.loads(result.stdout)
        duration = float(data['format']['duration'])
        return duration
    except (subprocess.CalledProcessError, FileNotFoundError, json.JSONDecodeError, KeyError) as e:
        print(f"Error getting audio duration for {file_path}: {e}")
        return None

if __name__ == "__main__":
    # Example usage (requires a dummy audio file and ffprobe installed)
    # Create a dummy mp3 for testing:
    # ffmpeg -f lavfi -i "sine=frequency=1000:duration=30" test_audio_duration.mp3
    test_file = "test_audio_duration.mp3" # Create this file for testing
    if os.path.exists(test_file):
        duration = get_audio_duration(test_file)
        if duration is not None:
            print(f"Duration of {test_file}: {duration} seconds")
        else:
            print(f"Failed to get duration for {test_file}")
    else:
        print(f"Please create a dummy audio file named '{test_file}' for testing.")
        print("You can create one using: ffmpeg -f lavfi -i \"sine=frequency=1000:duration=30\" test_audio_duration.mp3")
