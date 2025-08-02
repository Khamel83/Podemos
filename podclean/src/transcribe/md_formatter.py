import json

def format_transcript_to_md(transcript_json: str) -> str:
    """
    Formats a JSON transcript (from faster-whisper output) into a human-readable Markdown string.
    Each segment will be a paragraph, with speaker labels (if available) and timestamps.
    """
    if not transcript_json:
        return ""

    try:
        segments = json.loads(transcript_json)
    except json.JSONDecodeError:
        return "Error: Invalid JSON transcript."

    md_content = []
    for segment in segments:
        start_time = segment.get('start', 0)
        end_time = segment.get('end', 0)
        text = segment.get('text', '').strip()
        
        # Format timestamp (e.g., [00:01:23 - 00:01:28])
        start_h, start_m, start_s = int(start_time // 3600), int((start_time % 3600) // 60), int(start_time % 60)
        end_h, end_m, end_s = int(end_time // 3600), int((end_time % 3600) // 60), int(end_time % 60)
        timestamp = f"[{start_h:02d}:{start_m:02d}:{start_s:02d} - {end_h:02d}:{end_m:02d}:{end_s:02d}]"

        # Add speaker label if available (assuming a 'speaker' key might be added later)
        speaker = segment.get('speaker', '')
        if speaker:
            md_content.append(f"**{speaker}**: {timestamp} {text}\n")
        else:
            md_content.append(f"{timestamp} {text}\n")

    return "\n".join(md_content)

if __name__ == "__main__":
    # Example usage
    example_transcript_json = '''
    [
        {"start": 0.0, "end": 5.5, "text": " Hello, and welcome to the podcast.", "words": []},
        {"start": 6.0, "end": 10.2, "text": " This is a test segment.", "words": []},
        {"start": 11.0, "end": 15.0, "text": " Thank you for listening.", "words": []}
    ]
    '''
    md_output = format_transcript_to_md(example_transcript_json)
    print(md_output)

    example_transcript_with_speaker = '''
    [
        {"start": 0.0, "end": 5.5, "text": " Hello, and welcome to the podcast.", "speaker": "Host"},
        {"start": 6.0, "end": 10.2, "text": " This is a test segment.", "speaker": "Guest"}
    ]
    '''
    md_output_speaker = format_transcript_to_md(example_transcript_with_speaker)
    print("\n---" + " With Speaker ---" + "\n")
    print(md_output_speaker)
