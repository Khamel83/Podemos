# Core `podclean` Functionality Specification

## 1. Introduction
This specification details the core functionalities of the `podclean` component of the Podemos project, focusing on podcast ingestion, ad detection, audio cleaning, and basic feed generation. This covers Milestones A, B, and C of the project roadmap.

## 2. Goals
*   To reliably ingest podcast episodes from RSS feeds.
*   To accurately detect and remove ad segments from podcast audio.
*   To generate cleaned audio files with preserved integrity.
*   To provide a meta-feed of cleaned podcasts.

## 3. Features

### 3.1. Podcast Ingestion
*   **RSS Feed Polling:** Periodically poll configured RSS feeds for new episodes.
*   **Audio Download:** Download original podcast audio files to `data/originals/`.
*   **Metadata Extraction:** Extract relevant metadata (title, show, duration, image, etc.) from RSS feeds.

### 3.2. Ad Detection (Fast Pass)
*   **Chapter-Based Detection:** Utilize Podcasting 2.0 chapter data to identify ad segments based on chapter titles (e.g., "ad", "sponsor", "promo").
*   **Transcript Rules-Based Detection:** Employ a fast transcription model (`FAST_MODEL`) to generate transcripts and apply predefined text rules (phrases, URL patterns, price patterns) to identify ad content.
*   **Fusion Logic:** Combine signals from chapter data and transcript rules to determine ad segments, applying confidence thresholds and requiring a minimum number of signals (`require_signals`).
*   **Time Priors:** Incorporate time-based priors (pre-roll, mid-roll, post-roll) to influence ad detection.

### 3.3. Audio Cleaning
*   **Cut Plan Generation:** Based on detected ad segments, generate a plan for `ffmpeg` to cut and concatenate the non-ad portions of the audio.
*   **FFmpeg Execution:** Execute `ffmpeg` commands to perform the audio cutting, ensuring proper codec (`TARGET_CODEC`) and bitrate (`TARGET_BITRATE`) are applied.
*   **Padding:** Apply specified padding (`PADDING_SECONDS`) around cut segments to ensure smooth transitions.
*   **Output Management:** Store cleaned audio files in `data/cleaned/`.
*   **Integrity Checks:** Ensure audio integrity after cutting (e.g., no abrupt cuts, consistent audio quality).

### 3.4. Meta-Feed Generation
*   **RSS Feed Construction:** Generate an RSS feed (`/feed.xml`) containing cleaned podcast episodes.
*   **Enclosure Information:** Provide correct enclosure URLs (`/audio/<sha>.mp3`), file sizes, and MIME types for cleaned audio.
*   **Chapter Rewriting:** (Optional, but desired) Rewrite podcast chapters to reflect the cleaned audio, removing ad-related chapters and adjusting timestamps for remaining chapters.

## 4. Configuration
*   Utilize `config/app.yaml` for global settings and `config/shows/default.rules.yaml` for default ad detection rules.
*   Support `config/shows/{show_slug}.rules.yaml` for per-show rule overrides.
*   Environment variables (from `env.template`) for sensitive information and performance tuning.

## 5. Data Storage
*   `data/db.sqlite3`: For storing episode metadata, processing status, and ad segment information.
*   `data/originals/`: For original downloaded audio files.
*   `data/cleaned/`: For cleaned audio files.
*   `data/transcripts/`: For fast-pass transcripts (full-pass transcripts will be handled in a later spec).
*   `data/chapters/`: For Podcasting 2.0 chapter sidecar files.

## 6. API Endpoints (Initial)
*   `/feed.xml`: The main meta-feed for cleaned podcasts.
*   `/audio/<sha>.mp3`: Endpoint to serve cleaned audio files.

## 7. Performance Considerations
*   **Fast Pass Realtime:** Aim for ~0.5–1.0× realtime for the fast pass ad detection and cutting on target hardware.
*   **Parallel Processing:** Support `MAX_PARALLEL_DOWNLOADS` and `MAX_PARALLEL_TRANSCRIBE` for concurrent operations.

## 8. Failure Rules
*   If confidence in ad detection is below `MIN_CONFIDENCE`, do not cut; instead, emit skip-chapters.
*   If a cut removes more than 30% of audio or results in content spans less than 5 seconds, revert to skip-chapters and flag for review.
*   Always retain original files for N days for rollback capability.
