import argparse
import uvicorn
import os
import logging
from apscheduler.schedulers.background import BackgroundScheduler

from src.store.db import init_db, get_session
from src.store.models import Episode
from src.ingest.rss_poll import poll_feed
from src.ingest.opml_import import import_opml
from src.serve.api import app as api_app # Import the FastAPI app
from src.processor.episode_processor import process_episode

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def scheduled_job():
    logger.info("Running scheduled podcast update...")
    # Get all feeds from app.yaml (assuming app.yaml has a 'feeds' list)
    from src.config.config_loader import load_app_config
    app_config = load_app_config()
    feeds = app_config.feeds # Assuming 'feeds' is a list of URLs in app.yaml

    for feed_url in feeds:
        try:
            logger.info(f"Polling feed: {feed_url}")
            poll_feed(feed_url) # Poll without limit to get all new episodes
        except Exception as e:
            logger.error(f"Error polling feed {feed_url}: {e}")

    # Process newly downloaded episodes
    with get_session() as session:
        new_episodes = session.query(Episode).filter_by(status='downloaded').all()
        if new_episodes:
            logger.info(f"Found {len(new_episodes)} new episodes to process.")
            for episode in new_episodes:
                try:
                    logger.info(f"Processing episode: {episode.title}")
                    process_episode(episode.id)
                except Exception as e:
                    logger.error(f"Error processing episode {episode.id}: {e}")
        else:
            logger.info("No new episodes to process.")

    # Run cleanup job
    from src.store.cleanup import cleanup_old_episodes
    cleanup_old_episodes()

def main():
    parser = argparse.ArgumentParser(description="Podemos CLI for podcast processing.")
    parser.add_argument("--init-db", action="store_true", help="Initialize the database schema.")
    parser.add_argument("--poll-feed", type=str, help="Poll a given RSS feed URL.")
    parser.add_argument("--poll-limit", type=int, help="Limit the number of episodes to poll.")
    parser.add_argument("--import-opml", type=str, help="Import podcasts from an OPML file.")
    parser.add_argument("--process-episode", type=int, help="Process a specific episode by ID.")
    parser.add_argument("--list-episodes", action="store_true", help="List all episodes in the database.")
    parser.add_argument("--serve", action="store_true", help="Start the FastAPI server.")

    args = parser.parse_args()

    # Always initialize the database
    logger.info("Initializing database...")
    init_db()
    logger.info("Database initialized.")

    if args.init_db:
        logger.info("Database already initialized by default.")

    if args.poll_feed:
        logger.info(f"Polling feed: {args.poll_feed}")
        poll_feed(args.poll_feed, limit=args.poll_limit)
        logger.info("Feed polling complete.")

    if args.import_opml:
        logger.info(f"Importing OPML from: {args.import_opml}")
        import_opml(args.import_opml, poll_limit=args.poll_limit)
        logger.info("OPML import complete.")

    if args.process_episode:
        logger.info(f"Processing episode ID: {args.process_episode}")
        process_episode(args.process_episode)
        logger.info("Episode processing complete.")

    if args.list_episodes:
        logger.info("Listing all episodes...")
        with get_session() as session:
            episodes = session.query(Episode).all()
            if not episodes:
                logger.info("No episodes found in the database.")
            for e in episodes:
                print(f'ID: {e.id}, Title: {e.title}, Show: {e.show_name}, Status: {e.status}')
        logger.info("Episode listing complete.")

    if args.serve:
        logger.info("Starting FastAPI server...")
        scheduler = BackgroundScheduler()
        # Schedule the job to run every 15 minutes (adjust as needed)
        scheduler.add_job(scheduled_job, 'interval', minutes=15)
        scheduler.start()
        logger.info("Scheduler started. Press Ctrl+C to exit.")
        # The API app handles directory creation based on PODCLEAN_MEDIA_BASE_PATH
        uvicorn.run(api_app, host="0.0.0.0", port=8080)

if __name__ == "__main__":
    main()
