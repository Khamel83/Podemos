import feedparser
from datetime import datetime
from sqlalchemy.orm import Session
from src.store.db import get_session, add_or_update_episode

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
            add_or_update_episode(session, episode_data)
            print(f"Processed episode: {episode_data['title']} from {episode_data['show_name']}")

if __name__ == "__main__":
    # Example usage (will be replaced by main runner)
    # This requires 'feedparser' to be installed: pip install feedparser
    # And a test RSS feed URL
    print("This script is intended to be run as part of the main application.")
    print("Please ensure 'feedparser' is installed if you intend to test it directly.")
