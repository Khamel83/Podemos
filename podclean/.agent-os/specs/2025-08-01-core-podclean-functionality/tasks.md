# Core `podclean` Functionality Implementation Tasks

This document outlines the implementation tasks for the core `podclean` functionality, corresponding to Milestones A, B, and C of the project roadmap.

## Milestone A: No-cut Baseline

### Task 1.1: Initial Project Setup
*   Create the basic directory structure as per the scaffold.
*   Set up `env.template` and `config/app.yaml`.
*   Initialize `data/db.sqlite3`.

### Task 1.2: RSS Feed Polling and Audio Download
*   Implement `src/ingest/rss_poll.py` to poll configured RSS feeds.
*   Implement `src/dl/fetcher.py` to download original audio files to `data/originals/`.
*   Implement `src/store/models.py` for basic episode metadata storage in `db.sqlite3`.
*   Implement `src/store/db.py` for database interactions.

### Task 1.3: Meta-Feed Generation (Originals Only)
*   Implement `src/feed/meta_feed.py` to generate an RSS feed from original episodes.
*   Implement `src/serve/api.py` to serve the `/feed.xml` endpoint.
*   Implement `src/serve/api.py` to serve `/audio/<sha>.mp3` for original audio.

### Task 1.4: Basic CLI Runner
*   Implement `src/main.py` as a basic CLI runner to trigger polling and feed generation.

## Milestone B: Chapters-only Cuts

### Task 2.1: Chapter Detection
*   Implement `src/detect/chapters.py` to load chapters from episode metadata (sidecar or embedded).
*   Implement `src/detect/fusion.py` to incorporate chapter-based ad detection logic (`matches_ad_chapter`).

### Task 2.2: Cut Plan Generation (Chapters Only)
*   Implement `src/cut/plan.py` to build `keep_segments` based on chapter-detected ad segments.

### Task 2.3: FFmpeg Execution for Cuts
*   Implement `src/cut/ffmpeg_exec.py` to execute `ffmpeg` commands for cutting and concatenating audio based on `keep_segments`.
*   Ensure cleaned audio is saved to `data/cleaned/`.

### Task 2.4: Chapter Rewriting and Feed Update
*   Implement logic in `src/cut/tags_chapters.py` to rewrite chapters for cleaned audio, removing ad chapters and adjusting timestamps.
*   Update `src/feed/meta_feed.py` to use cleaned audio and rewritten chapters.

## Milestone C: FAST Ad Cut

### Task 3.1: Fast Transcription Integration
*   Implement `src/transcribe/fast_whisper.py` to perform fast transcription with VAD and word timestamps.
*   Integrate fast transcription into the ad detection pipeline.

### Task 3.2: Text Rules Implementation
*   Implement `src/detect/fast_text_rules.py` to apply predefined text rules (phrases, URL patterns, price patterns) to transcripts.
*   Update `src/detect/fusion.py` to incorporate text rule scores and `require_signals` logic.

### Task 3.3: Time Priors Implementation
*   Implement logic in `src/detect/fusion.py` to incorporate time priors (`in_time_priors`) into ad detection scoring.

### Task 3.4: Confidence-Based Cutting and Failure Rules
*   Implement logic in `src/detect/fusion.py` to handle `MIN_CONFIDENCE` for cutting decisions.
*   Implement failure rules (e.g., `if cut removes >30% of audio`) to revert to skip-chapters and flag for review.
*   Ensure original files are retained as per `Failure Rules`.

### Task 3.5: Per-Show Rules
*   Implement logic to load and apply `config/shows/{show_slug}.rules.yaml` for per-show overrides.

## General Tasks (Ongoing)
*   Implement robust error handling and logging throughout the system.
*   Write unit tests for each implemented module (e.g., `test_detect_fast.py`, `test_cut_plan.py`, `test_feed.py`).
*   Refine configuration loading and merging (e.g., using Pydantic/Dynaconf).
