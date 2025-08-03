import feedparser
import os
import logging
from src.ingest.rss_poll import poll_feed

logger = logging.getLogger(__name__)

def import_opml(opml_file_path: str, poll_limit: int = None):
    """
    Parses an OPML file and polls each RSS feed found within it.
    """
    if not os.path.exists(opml_file_path):
        logger.error(f"OPML file not found at: {opml_file_path}")
        return

    logger.info(f"Importing OPML file: {opml_file_path}")
    
    # feedparser can parse OPML files directly
    opml_data = feedparser.parse(opml_file_path)

    if not hasattr(opml_data, 'opml') or not opml_data.opml.get('body'):
        logger.error("Invalid OPML file format. Missing opml or body tag.")
        return

    for outline in opml_data.opml.body.outlines:
        if hasattr(outline, 'xmlUrl'):
            feed_url = outline.xmlUrl
            feed_title = outline.get('title', feed_url)
            logger.info(f"Found feed: {feed_title} ({feed_url})")
            try:
                poll_feed(feed_url, limit=poll_limit)
            except Exception as e:
                logger.error(f"Error polling feed {feed_url}: {e}")
        elif hasattr(outline, 'outlines'): # Handle nested outlines
            for nested_outline in outline.outlines:
                if hasattr(nested_outline, 'xmlUrl'):
                    feed_url = nested_outline.xmlUrl
                    feed_title = nested_outline.get('title', feed_url)
                    logger.info(f"Found nested feed: {feed_title} ({feed_url})")
                    try:
                        poll_feed(feed_url, limit=poll_limit)
                    except Exception as e:
                        logger.error(f"Error polling nested feed {feed_url}: {e}")

    logger.info("OPML import complete.")

if __name__ == "__main__":
    # Example usage (for testing purposes)
    # Create a dummy OPML file for testing:
    # with open("test.opml", "w") as f:
    #     f.write("""<?xml version="1.0" encoding="UTF-8"?>\n<opml version="1.0">\n  <head>\n    <title>Test Feeds</title>\n  </head>\n  <body>\n    <outline text="My Podcasts">\n      <outline text="Example Podcast 1" xmlUrl="http://www.example.com/feed1.xml"/>\n      <outline text="Example Podcast 2" xmlUrl="http://www.example.com/feed2.xml"/>\n    </outline>\n  </body>\n</opml>""")
    # import_opml("test.opml", poll_limit=1)
    logger.info("This script is intended to be called by other modules, e.g., main.py.")
