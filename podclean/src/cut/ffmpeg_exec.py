import subprocess
import os

def cut_with_ffmpeg(input_mp3: str, keeps: list, output_path: str, codec: str = "mp3", bitrate: str = "v4", normalize_loudness: bool = False) -> bool:
    """
    Cuts and concatenates audio segments using ffmpeg.

    Args:
        input_mp3: Path to the input MP3 file.
        keeps: List of [start, end] segments to keep.
        output_path: Path for the output cleaned MP3 file.
        codec: Audio codec for output (e.g., "mp3", "aac").
        bitrate: Audio bitrate for output (e.g., "v4" for VBR MP3, "96k").
        normalize_loudness: Whether to apply EBU R 128 loudness normalization.

    Returns:
        True if successful, False otherwise.
    """
    if not keeps:
        print("No segments to keep. Skipping ffmpeg execution.")
        return False

    filter_complex = []
    for i, k in enumerate(keeps):
        filter_complex.append(f"[0:a]atrim=start={k[0]}:end={k[1]},asetpts=PTS-STARTPTS[s{i}]")
    
    concat_refs = ''.join([f"[s{i}]" for i in range(len(keeps))])
    
    if normalize_loudness:
        filter_complex.append(f"{concat_refs}concat=n={len(keeps)}:v=0:a=1[concat_out];[concat_out]loudnorm=I=-23:LRA=7:TP=-2[outa]")
    else:
        filter_complex.append(f"{concat_refs}concat=n={len(keeps)}:v=0:a=1[outa]")

    command = [
        "ffmpeg",
        "-i", input_mp3,
        "-filter_complex", ";".join(filter_complex),
        "-map", "[outa]",
        "-c:a", codec,
    ]

    if codec == "mp3" and bitrate.startswith("v"):
        command.extend([f"-q:a", bitrate[1:]]) # For VBR MP3, e.g., -q:a 4
    else:
        command.extend([f"-b:a", bitrate])

    command.append(output_path)
    command.append("-y") # Overwrite output files without asking

    print(f"Executing FFmpeg command: {' '.join(command)}")
    try:
        # Using subprocess.run with capture_output=True and check=True
        # will raise CalledProcessError if the command returns a non-zero exit code
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        print("FFmpeg Stdout:", result.stdout)
        print("FFmpeg Stderr:", result.stderr)
        print(f"Successfully created cleaned audio at {output_path}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg command failed with error: {e}")
        print("FFmpeg Stdout:", e.stdout)
        print("FFmpeg Stderr:", e.stderr)
        return False
    except FileNotFoundError:
        print("Error: ffmpeg not found. Please ensure ffmpeg is installed and in your PATH.")
        return False

if __name__ == "__main__":
    # Example usage (requires a dummy input.mp3 and ffmpeg installed)
    # Create a dummy mp3 for testing:
    # ffmpeg -f lavfi -i "sine=frequency=1000:duration=30" input.mp3
    
    # Ensure data/cleaned directory exists
    cleaned_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'data', 'cleaned')
    if not os.path.exists(cleaned_dir):
        os.makedirs(cleaned_dir)

    input_file = "input.mp3" # Create this file for testing
    output_file = os.path.join(cleaned_dir, "output_cleaned.mp3")
    duration = 30.0
    keeps_example = [
        [0.0, 5.0],
        [10.0, 15.0],
        [20.0, 30.0]
    ]

    if os.path.exists(input_file):
        print(f"Attempting to cut {input_file}...")
        success = cut_with_ffmpeg(input_file, keeps_example, output_file)
        if success:
            print("FFmpeg cutting test successful.")
        else:
            print("FFmpeg cutting test failed.")
    else:
        print(f"Please create a dummy audio file named '{input_file}' in the current directory for testing.")
        print("You can create one using: ffmpeg -f lavfi -i \"sine=frequency=1000:duration=30\" input.mp3")
