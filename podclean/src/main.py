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

    # Process newly downloaded episodes based on backlog processing strategy
    backlog_strategy = app_config.backlog_processing.strategy
    last_n_episodes_count = app_config.backlog_processing.last_n_episodes_count

    with get_session() as session:
        # Process newly downloaded episodes (ad detection and cutting)
        new_episodes_for_initial_processing = session.query(Episode).filter_by(status='downloaded').all()
        if new_episodes_for_initial_processing:
            logger.info(f"Found {len(new_episodes_for_initial_processing)} episodes for initial processing.")
            for episode in new_episodes_for_initial_processing:
                try:
                    logger.info(f"Performing initial processing (ad detection, cutting) for episode: {episode.title}")
                    process_episode(episode.id)
                except Exception as e:
                    logger.error(f"Error during initial processing of episode {episode.id}: {e}")
        else:
            logger.info("No new episodes for initial processing.")

        # Process episodes ready for full transcription based on backlog strategy
        episodes_for_full_transcription = []
        if backlog_strategy == "newest_only":
            shows = session.query(Episode.show_name).distinct().all()
            for show_name_tuple in shows:
                show_name = show_name_tuple[0]
                newest_episode = session.query(Episode).filter_by(show_name=show_name, status='cut_ready_for_serving').order_by(Episode.pub_date.desc()).first()
                if newest_episode:
                    episodes_for_full_transcription.append(newest_episode)
        elif backlog_strategy == "last_n_episodes":
            shows = session.query(Episode.show_name).distinct().all()
            for show_name_tuple in shows:
                show_name = show_name_tuple[0]
                latest_n_episodes = session.query(Episode).filter_by(show_name=show_name, status='cut_ready_for_serving').order_by(Episode.pub_date.desc()).limit(last_n_episodes_count).all()
                episodes_for_full_transcription.extend(latest_n_episodes)
        else: # "all" strategy or any other unrecognized strategy
            episodes_for_full_transcription = session.query(Episode).filter_by(status='cut_ready_for_serving').all()

        if episodes_for_full_transcription:
            logger.info(f"Found {len(episodes_for_full_transcription)} episodes for full transcription based on backlog strategy '{backlog_strategy}'.")
            for episode in episodes_for_full_transcription:
                try:
                    logger.info(f"Performing full transcription for episode: {episode.title}")
                    perform_full_transcription(episode.id)
                except Exception as e:
                    logger.error(f"Error during full transcription of episode {episode.id}: {e}")
        else:
            logger.info("No episodes ready for full transcription.")

    # Run cleanup job
    from src.store.cleanup import cleanup_old_episodes
    cleanup_old_episodes()

def main():
    parser = argparse.ArgumentParser(description="Podemos CLI for podcast processing.")
    parser.add_argument("--init-db", action="store_true", help="Initialize the database schema.")
    parser.add_argument("--poll-feed", type=str, help="Poll a given RSS feed URL.")
    parser.add_argument("--poll-limit", type=int, help="Limit the number of episodes to poll.")
    parser.add_argument("--import-opml", type=str, help="Import podcasts from an OPML file.")
    parser.add_argument("--add-feed", type=str, help="Add a new RSS feed URL to the configuration.")
    parser.add_argument("--remove-feed", type=str, help="Remove an RSS feed URL from the configuration.")
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

    if args.add_feed:
        from src.config.config_loader import add_feed_to_config
        add_feed_to_config(args.add_feed)

    if args.remove_feed:
        from src.config.config_loader import remove_feed_from_config
        remove_feed_from_config(args.remove_feed)

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
