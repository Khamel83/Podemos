podclean/
  README.md

# Podemos: Your Personal Podcast Processor

Podemos is a self-hosted, open-source solution designed to give you full control over your podcast listening experience. It automatically processes your subscribed podcasts, removes ads, generates transcripts, and serves them via a private RSS feed, accessible from your favorite podcast client like Overcast.

## Key Features

*   **Automated Podcast Ingestion:** Polls RSS feeds, downloads audio, and stores metadata.
*   **Intelligent Ad Detection & Removal:** Identifies and removes ad segments using a fast transcription pass and text-based rules, creating a clean, ad-free audio experience.
*   **Decoupled Processing for Speed:** Ad-free audio is made available in your feed almost immediately after cutting, with full transcription running as a separate background task.
*   **Comprehensive Transcription:** Generates both JSON and human-readable Markdown transcripts for easy reading and analysis.
*   **Smart File Naming:** Organizes audio files with clear, descriptive names (e.g., `podcast_name-episode_name-download_date_CLEAN.mp3`).
*   **Automated Backlog Prioritization:** Configurable strategies to prioritize processing of newer episodes for news-based podcasts, or to process a specific number of the latest episodes.
*   **Automated Cleanup & Retention:** Manages disk space by automatically deleting old processed files and database entries based on configurable limits (e.g., keep only the X most recent episodes per show, or delete episodes older than Y days).
*   **Web-based Management Interface:** A simple, intuitive web dashboard to monitor episodes, manage podcast feeds (add/remove), and configure show-specific settings.
*   **Secure Private Feed:** Your personal podcast feed can be secured with basic authentication, ensuring privacy.
*   **M-series Mac Optimization:** Leverages `whisper.cpp` and Apple's Metal/Core ML for significantly faster transcription on Apple Silicon.

## Getting Started

To get Podemos up and running quickly, use the `install.sh` script. This script automates the setup of `whisper.cpp`, downloads necessary models, and installs Python dependencies.

1.  **Clone the repository:**
    `git clone [repository_url]`
    `cd Podemos`

2.  **Run the installer script:**
    `./install.sh`

    *The installer will guide you through the initial setup and ensure all prerequisites are met.*

## Manual Setup (Advanced)

If you prefer a manual setup or need to troubleshoot, follow these steps:

### Prerequisites

*   **FFmpeg:** Ensure `ffmpeg` is installed and accessible in your system's PATH.
    *   **macOS (Homebrew):** `brew install ffmpeg`
    *   **Other OS:** Refer to the [official FFmpeg documentation](https://ffmpeg.org/download.html).
*   **whisper.cpp:** For accelerated transcription on Apple Silicon, `whisper.cpp` is used. Follow the build instructions in the `whisper.cpp` repository's README.

### Setup Steps

1.  **Navigate to `podclean` directory:**
    `cd podclean`

2.  **Install Python dependencies:**
    `pip install -r requirements.txt`

3.  **Configure:**
    Copy `env.template` to `.env` and adjust as needed.
    Review `config/app.yaml` and `config/shows/default.rules.yaml` for application-wide and default show-specific settings.

4.  **Initialize Database:**
    `PYTHONPATH=./podclean python3 src/main.py --init-db`

5.  **Manage Feeds (CLI Examples):**
    *   **Add a feed:** `PYTHONPATH=./podclean python3 src/main.py --add-feed "http://example.com/new_feed.xml"`
    *   **Remove a feed:** `PYTHONPATH=./podclean python3 src/main.py --remove-feed "http://example.com/old_feed.xml"`
    *   **Import from OPML:** `PYTHONPATH=./podclean python3 src/main.py --import-opml "/path/to/your/overcast.opml" --poll-limit 5`

6.  **Process an Episode (CLI Example):**
    `PYTHONPATH=./podclean python3 src/main.py --process-episode 1`

7.  **Run the Server:**
    `PYTHONPATH=./podclean python3 src/main.py --serve`
    *When running with `--serve`, an internal scheduler will automatically poll configured feeds and process new episodes based on your `config/app.yaml` settings.*

## Usage

Once the server is running:

*   **Web Dashboard:** Access the management interface at `http://localhost:8080/` (or your remote machine's IP/domain).
*   **Podcast Feed:** Subscribe to your private feed at `http://<YOUR_MACHINE_IP_OR_DOMAIN>:8080/feed.xml` in your podcast client. If authentication is enabled in `config/app.yaml`, use the format `http://username:password@<YOUR_MACHINE_IP_OR_DOMAIN>:8080/feed.xml`.

## Development Notes

*   **Database:** Uses SQLite (`data/db.sqlite3`) for episode metadata.
*   **Audio Storage:** Original and cleaned audio files are stored in `data/originals` and `data/cleaned` respectively.
*   **Transcripts:** Transcripts are stored in `data/transcripts`.
*   **Configuration:** Application settings are loaded from `config/app.yaml` and show-specific rules from `config/shows/`.

## Troubleshooting

*   **FFmpeg not found:** Ensure `ffmpeg` is installed and in your PATH.
*   **Database errors:** Try re-initializing the database (`--init-db`).
*   **Transcription issues:** Ensure `whisper.cpp` is built and its models are downloaded. Check the `whisper.cpp` build output for any errors related to Metal/CoreML.
*   **Feed not accessible remotely:** Verify your remote machine's IP address, port forwarding, and firewall settings. Ensure `feed_auth_enabled` is correctly configured in `app.yaml` if using authentication.

## Future Enhancements

*   **Advanced Monitoring & Alerting:** More detailed health checks and notification systems.
*   **Enhanced Web Interface:** More interactive features for episode management, detailed logs, and user feedback.
*   **Apple Podcasts API Integration:** Supplement RSS feed data with structured information from Apple Podcasts.
*   **Full-Text Search:** Implement search capabilities across transcripts.
*   **Cloud Deployment Options:** Guides and tools for deploying Podemos on cloud platforms.
