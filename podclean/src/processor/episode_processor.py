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
from src.config.config import AppConfig
from src.transcribe.full_whisper import full_transcribe
from src.transcribe.md_formatter import format_transcript_to_md
import logging

logger = logging.getLogger(__name__)

app_cfg: AppConfig = load_app_config()
# Define the base directory for cleaned audio files
CLEANED_DIR = os.path.join(app_cfg.PODCLEAN_MEDIA_BASE_PATH, 'cleaned')
TRANSCRIPTS_DIR = os.path.join(app_cfg.PODCLEAN_MEDIA_BASE_PATH, 'transcripts')

def perform_full_transcription(episode_id: int):
    with get_session() as session:
        episode = session.query(Episode).filter_by(id=episode_id).first()
        if not episode:
            logger.error(f"Episode with ID {episode_id} not found for full transcription.")
            return
        if episode.status == 'transcribed':
            logger.info(f"Episode {episode.id} already fully transcribed. Skipping.")
            return
        if not episode.cleaned_file_path or not os.path.exists(episode.cleaned_file_path):
            logger.warning(f"Cleaned audio file not found for episode ID {episode.id}. Cannot perform full transcription.")
            episode.status = 'full_transcription_failed' # Or a more appropriate error status
            session.add(episode)
            session.commit()
            return

        app_cfg = load_app_config() # Reload config for latest settings

        if app_cfg.FULL_PASS_ENABLED:
            logger.info(f"Initiating full transcription for episode: {episode.title}")
            full_model_size = app_cfg.FULL_MODEL
            full_vad = app_cfg.FULL_VAD
            full_beam = app_cfg.FULL_BEAM
            full_word_ts = app_cfg.FULL_WORD_TS

            transcription_results = full_transcribe(
                episode.cleaned_file_path, 
                model_size=full_model_size, 
                vad=full_vad, 
                beam_size=full_beam, 
                word_timestamps=full_word_ts
            )

            if transcription_results:
                episode.transcript_json = json.dumps(transcription_results)
                episode.status = 'transcribed'
                # Save JSON transcript to file
                if not os.path.exists(TRANSCRIPTS_DIR):
                    os.makedirs(TRANSCRIPTS_DIR)
                transcript_filename = f"{os.path.splitext(os.path.basename(episode.cleaned_file_path))[0]}.json"
                transcript_filepath = os.path.join(TRANSCRIPTS_DIR, transcript_filename)
                with open(transcript_filepath, 'w') as f:
                    json.dump(transcription_results, f, indent=4)
                logger.info(f"Full JSON transcript saved to: {transcript_filepath}")

                # Generate and save Markdown transcript
                md_content = format_transcript_to_md(episode.transcript_json)
                md_filename = f"{os.path.splitext(os.path.basename(episode.cleaned_file_path))[0]}.md"
                md_filepath = os.path.join(TRANSCRIPTS_DIR, md_filename)
                with open(md_filepath, 'w') as f:
                    f.write(md_content)
                episode.md_transcript_file_path = md_filepath
                logger.info(f"Markdown transcript saved to: {md_filepath}")
            else:
                episode.status = 'full_transcription_failed'
                logger.error(f"Full transcription failed for episode ID {episode.id}.")

            session.add(episode)
            session.commit()
            session.refresh(episode)
        else:
            logger.info(f"Full transcription pass is disabled for episode {episode.id}.")


def process_episode(episode_id: int):
    with get_session() as session:
        episode = session.query(Episode).filter_by(id=episode_id).first()
        if not episode:
            logger.error(f"Episode with ID {episode_id} not found.")
            return

        if not episode.original_file_path or not os.path.exists(episode.original_file_path):
            logger.warning(f"Original audio file not found for episode ID {episode_id}. Skipping processing.")
            episode.status = 'original_missing'
            session.add(episode)
            session.commit()
            return

        logger.info(f"Processing episode: {episode.title}")
        app_cfg = load_app_config()

        # 1. Ad Detection (Fast Pass)
        # Pass episode.show_name as show_slug for config loading
        ad_cuts = detect_ads_fast(episode.original_file_path, episode, episode.show_name)
        episode.ad_segments_json = json.dumps(ad_cuts) # Store detected ad segments
        episode.fast_transcript_json = json.dumps(episode.fast_transcript_json) # Convert fast transcript to JSON string
        session.add(episode)
        session.commit()
        session.refresh(episode)

        # 2. Build Keep Segments
        if not episode.original_duration:
            logger.warning(f"original_duration not set for episode {episode.id}. Cannot accurately plan cuts. Using dummy duration.")
            # TODO: Implement audio duration extraction (e.g., using ffprobe) if not already done by rss_poll
            # For now, let's assume a dummy duration for testing purposes if not set
            episode.original_duration = 3600 # Dummy 1 hour for testing
            session.add(episode)
            session.refresh(episode)

        keep_segments = build_keep_segments(episode.original_duration, ad_cuts)

        # 3. Cut with FFmpeg
        if not os.path.exists(CLEANED_DIR):
            os.makedirs(CLEANED_DIR)
        
        # Generate a unique filename for the cleaned audio
        original_filename_with_query = os.path.basename(episode.original_file_path)
        original_filename_base = os.path.splitext(original_filename_with_query.split('?')[0])[0]
        file_extension = os.path.splitext(original_filename_with_query.split('?')[0])[1] or ".mp3"
        cleaned_filename = f"{original_filename_base}_CLEAN{file_extension}"
        cleaned_output_path = os.path.join(CLEANED_DIR, cleaned_filename)

        codec = app_cfg.encoding.codec
        bitrate = app_cfg.encoding.bitrate
        normalize_loudness = app_cfg.encoding.normalize_loudness

        success = cut_with_ffmpeg(episode.original_file_path, keep_segments, cleaned_output_path, codec=codec, bitrate=bitrate, normalize_loudness=normalize_loudness)

        if success:
            episode.cleaned_file_path = cleaned_output_path
            episode.status = 'cut_ready_for_serving' # <--- NEW STATUS
            logger.info(f"Cleaned audio saved to: {cleaned_output_path}")
        else:
            episode.status = 'cut_failed'
            logger.error(f"Failed to cut audio for episode ID {episode_id}.")
        
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
            logger.info(f"Chapters adjusted for episode ID {episode_id}.")

        logger.info(f"Finished initial processing for episode: {episode.title} with status: {episode.status}")

if __name__ == "__main__":
    # Example usage (requires a populated database and audio files)
    # from src.store.db import init_db
    # init_db()
    # process_episode(1) # Replace 1 with an actual episode ID
    logger.info("This script is intended to be called by other modules, e.g., a job worker.")
