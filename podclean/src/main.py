import argparse
import uvicorn
import os

from src.store.db import init_db
from src.ingest.rss_poll import poll_feed
from src.serve.api import app as api_app # Import the FastAPI app

def main():
    parser = argparse.ArgumentParser(description="Podemos CLI for podcast processing.")
    parser.add_argument("--init-db", action="store_true", help="Initialize the database schema.")
    parser.add_argument("--poll-feed", type=str, help="Poll a given RSS feed URL.")
    parser.add_argument("--process-episode", type=int, help="Process a specific episode by ID.")
    parser.add_argument("--serve", action="store_true", help="Start the FastAPI server.")

    args = parser.parse_args()

    if args.init_db:
        print("Initializing database...")
        init_db()
        print("Database initialized.")

    if args.poll_feed:
        print(f"Polling feed: {args.poll_feed}")
        poll_feed(args.poll_feed)
        print("Feed polling complete.")

    if args.process_episode:
        print(f"Processing episode ID: {args.process_episode}")
        from src.processor.episode_processor import process_episode
        process_episode(args.process_episode)
        print("Episode processing complete.")

    if args.serve:
        print("Starting FastAPI server...")
        # Ensure the data/originals directory exists for FileResponse
        originals_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..\', 'data\', 'originals')
        if not os.path.exists(originals_dir):
            os.makedirs(originals_dir)
        uvicorn.run(api_app, host="0.0.0.0", port=8080)

if __name__ == "__main__":
    main()
