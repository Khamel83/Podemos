import os
import json
from sqlalchemy.orm import Session
from src.store.db import get_session
from src.store.models import Episode
from src.detect.fusion import detect_ads_fast
from src.cut.plan import build_keep_segments
from src.cut.ffmpeg_exec import cut_with_ffmpeg
from src.cut.tags_chapters import adjust_chapters_after_cut, filter_ad_chapters
from src.config.config_loader import load_app_config

# Define the base directory for cleaned audio files
CLEANED_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'data', 'cleaned')

def process_episode(episode_id: int):
    with get_session() as session:
        episode = session.query(Episode).filter_by(id=episode_id).first()
        if not episode:
            print(f"Episode with ID {episode_id} not found.")
            return

        if not episode.original_file_path or not os.path.exists(episode.original_file_path):
            print(f"Original audio file not found for episode ID {episode_id}. Skipping processing.")
            episode.status = 'original_missing'
            session.add(episode)
            session.commit()
            return

        print(f"Processing episode: {episode.title}")
        app_cfg = load_app_config()

        # 1. Ad Detection
        # Pass episode.show_name as show_slug for config loading
        ad_cuts = detect_ads_fast(episode.original_file_path, episode, episode.show_name)
        episode.ad_segments_json = json.dumps(ad_cuts) # Store detected ad segments
        session.add(episode)
        session.commit()
        session.refresh(episode)

        # 2. Build Keep Segments
        # For now, assuming original_duration is available. Will need to get it from audio file if not.
        # This is a placeholder for getting duration if not already present
        if not episode.original_duration:
            # TODO: Implement audio duration extraction (e.g., using ffprobe)
            print(f"Warning: original_duration not set for episode {episode.id}. Cannot accurately plan cuts.")
            # For now, let's assume a dummy duration for testing purposes if not set
            # In a real scenario, this would be a critical error or a step to extract duration
            episode.original_duration = 3600 # Dummy 1 hour for testing
            session.add(episode)
            session.commit()
            session.refresh(episode)

        keep_segments = build_keep_segments(episode.original_duration, ad_cuts)

        # 3. Cut with FFmpeg
        if not os.path.exists(CLEANED_DIR):
            os.makedirs(CLEANED_DIR)
        
        # Generate a unique filename for the cleaned audio
        cleaned_filename = f"{os.path.splitext(os.path.basename(episode.original_file_path))[0]}_cleaned.mp3"
        cleaned_output_path = os.path.join(CLEANED_DIR, cleaned_filename)

        codec = app_cfg.get('encoding', {}).get('codec', 'mp3')
        bitrate = app_cfg.get('encoding', {}).get('bitrate', 'v4')

        success = cut_with_ffmpeg(episode.original_file_path, keep_segments, cleaned_output_path, codec=codec, bitrate=bitrate)

        if success:
            episode.cleaned_file_path = cleaned_output_path
            episode.status = 'cut'
            # TODO: Update cleaned_duration and cleaned_file_size after cutting
            # This would require reading the metadata of the newly created file
            print(f"Cleaned audio saved to: {cleaned_output_path}")
        else:
            episode.status = 'cut_failed'
            print(f"Failed to cut audio for episode ID {episode_id}.")
        
        session.add(episode)
        session.commit()
        session.refresh(episode)

        # 4. Adjust Chapters
        if episode.chapters_json:
            original_chapters = json.loads(episode.chapters_json)
            filtered_chapters = filter_ad_chapters(original_chapters)
            adjusted_chapters = adjust_chapters_after_cut(filtered_chapters, keep_segments)
            episode.cleaned_chapters_json = json.dumps(adjusted_chapters)
            session.add(episode)
            session.commit()
            session.refresh(episode)
            print(f"Chapters adjusted for episode ID {episode_id}.")

        print(f"Finished processing episode: {episode.title} with status: {episode.status}")

if __name__ == "__main__":
    # Example usage (requires a populated database and audio files)
    # from src.store.db import init_db
    # init_db()
    # process_episode(1) # Replace 1 with an actual episode ID
    print("This script is intended to be called by other modules, e.g., a job worker.")
