import feedparser
import os
from datetime import datetime
from sqlalchemy.orm import Session
from src.store.db import get_session, add_or_update_episode
from src.dl.fetcher import download_file
from src.dl.integrity import get_audio_duration
from src.config.config_loader import load_app_config
from src.config.config import AppConfig
import time
import logging

logger = logging.getLogger(__name__)

app_config: AppConfig = load_app_config()
# Define the base directory for original audio files
ORIGINALS_DIR = os.path.join(app_config.PODCLEAN_MEDIA_BASE_PATH, 'originals')

def poll_feed(feed_url: str, limit: int = None):
    feed = feedparser.parse(feed_url)
    processed_count = 0
    for entry in feed.entries:
        if limit is not None and processed_count >= limit:
            logger.info(f"Reached limit of {limit} episodes. Stopping polling.")
            break
        # Convert time.struct_time to datetime object
        published_date = datetime.fromtimestamp(time.mktime(entry.published_parsed)) if entry.published_parsed else datetime.now()

        episode_data = {
            "source_guid": entry.guid,
            "title": entry.title,
            "show_name": feed.feed.title,
            "pub_date": published_date,
            "original_audio_url": entry.enclosures[0].href if entry.enclosures else None,
            "original_file_size": int(entry.enclosures[0].length) if entry.enclosures and hasattr(entry.enclosures[0], 'length') else None,
            "description": entry.summary,
            "image_url": entry.image.href if hasattr(entry, 'image') and hasattr(entry.image, 'href') else None,
            "show_image_url": feed.feed.image.href if hasattr(feed.feed, 'image') and hasattr(feed.feed.image, 'href') else None,
            "show_author": feed.feed.author if hasattr(feed.feed, 'author') else None,
            "chapters_json": json.dumps(entry.chapters) if hasattr(entry, 'chapters') else None, # Assuming chapters are directly available
        }
        # Basic validation for required fields
        if not all([episode_data['source_guid'], episode_data['title'], episode_data['original_audio_url']]):
            logger.warning(f"Skipping entry due to missing required data: {entry.title}")
            continue

        with get_session() as session:
            episode = add_or_update_episode(session, episode_data)
            logger.info(f"Processed episode: {episode.title} from {episode.show_name}")
            processed_count += 1

            # Download audio if not already downloaded
            if episode.original_audio_url and not episode.original_file_path:
                logger.info(f"Attempting to download: {episode.original_audio_url}")
                # Generate a unique filename using show name, episode title, and download date
                file_extension = os.path.splitext(os.path.basename(episode.original_audio_url).split('?')[0])[1] or ".mp3"
                # Sanitize title and show name for filename
                sanitized_title = "".join(c for c in episode.title if c.isalnum() or c in (' ', '-')).strip().replace(' ', '_')
                sanitized_show_name = "".join(c for c in episode.show_name if c.isalnum() or c in (' ', '-')).strip().replace(' ', '_')
                download_date_str = datetime.now().strftime("%m%d%y")
                unique_filename = f"{sanitized_show_name}-{sanitized_title}-{download_date_str}{file_extension}"
                downloaded_path = download_file(episode.original_audio_url, ORIGINALS_DIR, filename=unique_filename)
                if downloaded_path:
                    episode.original_file_path = downloaded_path
                    # Get duration after download
                    duration = get_audio_duration(downloaded_path)
                    if duration is not None:
                        episode.original_duration = duration
                    episode.status = 'downloaded'
                    session.add(episode)
                    session.commit()
                    session.refresh(episode)
                    logger.info(f"Downloaded and updated path for {episode.title}")
                else:
                    episode.status = 'download_failed'
                    session.add(episode)
                    session.commit()
                    session.refresh(episode)
                    logger.error(f"Failed to download {episode.title}")

if __name__ == "__main__":
    # Example usage (will be replaced by main runner)
    # This requires 'feedparser' and 'requests' to be installed: pip install feedparser requests
    # And a test RSS feed URL
    logger.info("This script is intended to be run as part of the main application.")
    logger.info("Please ensure 'feedparser' and 'requests' are installed if you intend to test it directly.")
    # Example: poll_feed("http://www.example.com/podcast.rss")


