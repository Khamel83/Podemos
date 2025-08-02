# Core `podclean` Functionality Specification (Condensed)

This specification outlines the core features of the `podclean` component, covering podcast ingestion, ad detection, audio cleaning, and basic feed generation (Milestones A, B, C).

**Key Features:**
*   **Podcast Ingestion:** Poll RSS feeds, download audio to `data/originals/`, and extract metadata.
*   **Ad Detection (Fast Pass):** Combine chapter data and text rules (from fast transcription) to identify ad segments, using confidence thresholds and time priors.
*   **Audio Cleaning:** Generate `ffmpeg` cut plans based on detected ads, execute cuts, apply padding, and store cleaned audio in `data/cleaned/`.
*   **Meta-Feed Generation:** Create an RSS feed (`/feed.xml`) of cleaned podcasts, serving audio via `/audio/<sha>.mp3`, with optional chapter rewriting.

**Configuration:** Uses `app.yaml`, `default.rules.yaml`, and per-show rule overrides.

**Data Storage:** Utilizes `db.sqlite3` for metadata, and dedicated directories for originals, cleaned audio, transcripts, and chapters.

**Performance:** Aims for ~0.5–1.0× realtime for fast pass, with parallel processing for downloads and transcription.

**Failure Rules:** Includes safeguards like reverting to skip-chapters if confidence is low or cuts are excessive, and retaining originals for rollback.