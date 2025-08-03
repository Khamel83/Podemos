import os
import logging
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from src.store.db import get_session
from src.store.models import Episode
from src.config.config_loader import load_app_config

logger = logging.getLogger(__name__)

def cleanup_old_episodes():
    app_config = load_app_config()
    if not app_config.retention_policy.enabled:
        logger.info("Retention policy is disabled. Skipping cleanup.")
        return

    max_episodes_per_show = app_config.retention_policy.max_episodes_per_show
    max_days_per_episode = app_config.retention_policy.max_days_per_episode

    logger.info(f"Running cleanup job: max_episodes_per_show={max_episodes_per_show}, max_days_per_episode={max_days_per_episode} days.")

    with get_session() as session:
        # Group episodes by show
        shows = session.query(Episode.show_name).distinct().all()

        for show_name_tuple in shows:
            show_name = show_name_tuple[0]
            logger.info(f"Processing show: {show_name}")

            # Order episodes by publication date (newest first)
            episodes_for_show = session.query(Episode).filter_by(show_name=show_name).order_by(Episode.pub_date.desc()).all()

            # Apply max_episodes_per_show policy
            if len(episodes_for_show) > max_episodes_per_show:
                episodes_to_delete_by_count = episodes_for_show[max_episodes_per_show:]
                logger.info(f"  - Marking {len(episodes_to_delete_by_count)} episodes for deletion based on max_episodes_per_show policy.")
            else:
                episodes_to_delete_by_count = []

            # Apply max_days_per_episode policy
            cutoff_date = datetime.now() - timedelta(days=max_days_per_episode)
            episodes_to_delete_by_age = [e for e in episodes_for_show if e.pub_date < cutoff_date]
            logger.info(f"  - Marking {len(episodes_to_delete_by_age)} episodes for deletion based on max_days_per_episode policy.")

            # Combine and deduplicate episodes to delete
            all_episodes_to_delete = list(set(episodes_to_delete_by_count + episodes_to_delete_by_age))

            if all_episodes_to_delete:
                for episode in all_episodes_to_delete:
                    logger.info(f"  - Deleting episode: {episode.title} (ID: {episode.id})")
                    # Delete associated files
                    if episode.original_file_path and os.path.exists(episode.original_file_path):
                        os.remove(episode.original_file_path)
                        logger.info(f"    - Deleted original file: {episode.original_file_path}")
                    if episode.cleaned_file_path and os.path.exists(episode.cleaned_file_path):
                        os.remove(episode.cleaned_file_path)
                        logger.info(f"    - Deleted cleaned file: {episode.cleaned_file_path}")
                    if episode.md_transcript_file_path and os.path.exists(episode.md_transcript_file_path):
                        os.remove(episode.md_transcript_file_path)
                        logger.info(f"    - Deleted Markdown transcript: {episode.md_transcript_file_path}")
                    if episode.transcript_json: # Assuming JSON transcript is saved as a file
                        # Construct JSON transcript path (similar logic as episode_processor)
                        cleaned_filename_base = os.path.splitext(os.path.basename(episode.cleaned_file_path).split('?')[0])[0]
                        json_transcript_path = os.path.join(load_app_config().PODCLEAN_MEDIA_BASE_PATH, 'transcripts', f"{cleaned_filename_base}.json")
                        if os.path.exists(json_transcript_path):
                            os.remove(json_transcript_path)
                            logger.info(f"    - Deleted JSON transcript: {json_transcript_path}")

                    session.delete(episode)
                session.commit()
                logger.info(f"  - Deleted {len(all_episodes_to_delete)} episodes for show {show_name}.")
            else:
                logger.info(f"  - No episodes to delete for show {show_name}.")

    logger.info("Cleanup job complete.")

if __name__ == "__main__":
    # Example usage (requires a populated database and app.yaml configured)
    # from src.store.db import init_db
    # init_db()
    # cleanup_old_episodes()
    logger.info("This script is intended to be called by other modules, e.g., main.py or a scheduler.")
