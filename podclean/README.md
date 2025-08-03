podclean/
  README.md

# Prerequisites

*   **FFmpeg:** This project relies on `ffmpeg` for audio processing (cutting, normalization, duration extraction). Please ensure `ffmpeg` is installed and accessible in your system's PATH.
    *   **macOS (Homebrew):** `brew install ffmpeg`
    *   **Other OS:** Refer to the [official FFmpeg documentation](https://ffmpeg.org/download.html) for installation instructions.
*   **whisper.cpp:** For accelerated transcription on Apple Silicon, `whisper.cpp` is used. Follow the build instructions in the main project README.

  checklists.md
  env.template
  config/
    app.yaml
    shows/
      default.rules.yaml
      {show_slug}.rules.yaml
  data/
    db.sqlite3
    originals/           # podcast_name-episode_name-download_date.mp3
    cleaned/             # podcast_name-episode_name-download_date_CLEAN.mp3
    temp/
    transcripts/         # <episode_id>.json(.vtt)
    chapters/            # <episode_id>.json (p2.0 sidecar if fetched)
  scripts/
    bootstrap.sh
  src/
    __init__.py
    main.py              # runner / CLI
    ingest/
      opml_import.py
      rss_poll.py
    dl/
      fetcher.py
      integrity.py
    detect/
      chapters.py
      fast_text_rules.py
      audio_cues.py
      fusion.py
    cut/
      plan.py
      ffmpeg_exec.py
      tags_chapters.py
    feed/
      meta_feed.py
      per_show_feed.py
    store/
      db.py
      models.py
      paths.py
    serve/
      api.py             # /feed.xml, /audio/<hash>.mp3, /mark endpoints
    jobs/
      queue.py
      worker.py
    transcribe/
      fast_whisper.py    # small/medium, VAD on
      full_whisper.py    # larger model / better settings
      cleanup_llm.py     # optional, for project B
  tests/
    test_detect_fast.py
    test_cut_plan.py
    test_feed.py


# Setup

1.  **Clone the repository:**
    `git clone [repository_url]`
    `cd podclean`

2.  **Install Python dependencies:**
    `pip install -r requirements.txt`

3.  **Configure:**
    Copy `env.template` to `.env` and adjust as needed.
    Review `config/app.yaml` and `config/shows/default.rules.yaml` for application-wide and default show-specific settings.

4.  **Initialize Database:**
    `PYTHONPATH=./podclean python3 src/main.py --init-db`

5.  **Manage Feeds (Examples):**
    *   **Add a feed:** `PYTHONPATH=./podclean python3 src/main.py --add-feed "http://example.com/new_feed.xml"`
    *   **Remove a feed:** `PYTHONPATH=./podclean python3 src/main.py --remove-feed "http://example.com/old_feed.xml"`
    *   **Import from OPML:** `PYTHONPATH=./podclean python3 src/main.py --import-opml "/path/to/your/overcast.opml" --poll-limit 5`

6.  **Process an Episode (Example):**
    `PYTHONPATH=./podclean python3 src/main.py --process-episode 1`

7.  **Run the Server (Example):**
    `PYTHONPATH=./podclean python3 src/main.py --serve`
    Access the dashboard at `http://localhost:8080/`
    *When running with `--serve`, an internal scheduler will automatically poll configured feeds and process new episodes every 15 minutes, applying the `backlog_processing` strategy defined in `config/app.yaml`.*

# Features

*   **Podcast Ingestion:** Polls RSS feeds, downloads audio, and stores metadata.
*   **Ad Detection:** Identifies and marks ad segments within audio using a fast transcription pass and text-based rules.
*   **Audio Cutting:** Removes detected ad segments from audio files, creating a "cleaned" version.
*   **Chapter Adjustment:** Adjusts podcast chapters to align with the cleaned audio.
*   **Full Transcription:** Generates a complete transcript of the cleaned audio, including a human-readable Markdown version.
*   **Web Interface:** Provides a basic dashboard and serves processed audio and transcripts.

# Development Notes

*   **Database:** Uses SQLite (`data/db.sqlite3`) for episode metadata.
*   **Audio Storage:** Original and cleaned audio files are stored in `data/originals` and `data/cleaned` respectively, using a `podcast_name-episode_name-download_date.mp3` and `podcast_name-episode_name-download_date_CLEAN.mp3` naming convention.
*   **Transcripts:** Transcripts are stored in `data/transcripts`.
*   **Configuration:** Application settings are loaded from `config/app.yaml` and show-specific rules from `config/shows/`.

# Troubleshooting

*   **FFmpeg not found:** Ensure `ffmpeg` is installed and in your PATH.
*   **Database errors:** Try re-initializing the database (`--init-db`).
*   **Transcription issues:** Ensure `whisper.cpp` is built and its models are downloaded. Check the `whisper.cpp` build output for any errors related to Metal/CoreML.

# Future Enhancements

*   **Automated Backlog Prioritization:** Implement options to prioritize processing of newer episodes for news-based podcasts, or to process only a certain number of the latest episodes from a feed.
*   **Basic Cleanup/Retention Policy:** Automatically delete old processed files and database entries based on configurable limits (e.g., keep only the X most recent episodes per show, or delete episodes older than Y days).
*   **Improved Ad Detection:** More sophisticated techniques (e.g., audio fingerprinting, ML).
*   **User-Specific Rules:** Allow users to define custom ad detection rules.
*   **Enhanced Web Interface:** More interactive dashboard, user management.
*   **Apple Podcasts API Integration:** Supplement RSS feed data with structured information from Apple Podcasts.