import feedparser
import os
from datetime import datetime
from sqlalchemy.orm import Session
from src.store.db import get_session, add_or_update_episode
from src.dl.fetcher import download_file

# Define the base directory for original audio files
ORIGINALS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'data', 'originals')

def poll_feed(feed_url: str):
    feed = feedparser.parse(feed_url)
    for entry in feed.entries:
        episode_data = {
            "source_guid": entry.guid,
            "title": entry.title,
            "show_name": feed.feed.title,
            "pub_date": datetime.fromtimestamp(entry.published_parsed.mktime()),
            "original_audio_url": entry.enclosures[0].href if entry.enclosures else None,
            "original_file_size": int(entry.enclosures[0].length) if entry.enclosures and hasattr(entry.enclosures[0], 'length') else None,
            "description": entry.summary,
            "image_url": entry.image.href if hasattr(entry, 'image') and hasattr(entry.image, 'href') else None,
            "show_image_url": feed.feed.image.href if hasattr(feed.feed, 'image') and hasattr(feed.feed.image, 'href') else None,
            "show_author": feed.feed.author if hasattr(feed.feed, 'author') else None,
        }
        # Basic validation for required fields
        if not all([episode_data['source_guid'], episode_data['title'], episode_data['original_audio_url']]):
            print(f"Skipping entry due to missing required data: {entry.title}")
            continue

        with get_session() as session:
            episode = add_or_update_episode(session, episode_data)
            print(f"Processed episode: {episode.title} from {episode.show_name}")

            # Download audio if not already downloaded
            if episode.original_audio_url and not episode.original_file_path:
                print(f"Attempting to download: {episode.original_audio_url}")
                downloaded_path = download_file(episode.original_audio_url, ORIGINALS_DIR)
                if downloaded_path:
                    episode.original_file_path = downloaded_path
                    episode.status = 'downloaded'
                    session.add(episode)
                    session.commit()
                    session.refresh(episode)
                    print(f"Downloaded and updated path for {episode.title}")
                else:
                    episode.status = 'download_failed'
                    session.add(episode)
                    session.commit()
                    session.refresh(episode)
                    print(f"Failed to download {episode.title}")

if __name__ == "__main__":
    # Example usage (will be replaced by main runner)
    # This requires 'feedparser' and 'requests' to be installed: pip install feedparser requests
    # And a test RSS feed URL
    print("This script is intended to be run as part of the main application.")
    print("Please ensure 'feedparser' and 'requests' are installed if you intend to test it directly.")
    # Example: poll_feed("http://www.example.com/podcast.rss")

