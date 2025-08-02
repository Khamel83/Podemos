# Podemos Project Roadmap

The development of the Podemos project will follow a phased approach, building upon a solid foundation and progressively integrating with the Atlas system.

## Phase 1: Core `podclean` Functionality (Milestones A, B, C)

**Goal:** Establish the fundamental podcast cleaning and fast transcription capabilities.

*   **Milestone A (No-cut baseline):**
    *   Implement RSS polling and original audio download to `data/originals/`.
    *   Build meta-feed from originals only.
    *   Verify basic feed subscription.
*   **Milestone B (Chapters-only cuts):**
    *   Enable and implement chapter-based ad detection (`detector.use_chapters`).
    *   Verify `ffmpeg` plan for cleaned files and chapter rewriting.
    *   Sample and validate end-to-end processing for a few shows.
*   **Milestone C (FAST ad cut):**
    *   Enable and implement text rules for fast ad detection (using `FAST_MODEL`).
    *   Implement non-destructive skip-chapters output for initial verification.
    *   Enable destructive cuts, confirming padding and audio integrity.

## Phase 2: Learning Loop and Full Transcription (Milestones D, E)

**Goal:** Introduce mechanisms for continuous improvement and high-quality transcription.

*   **Milestone D (Learning loop):**
    *   Expose `/mark` correction endpoint for user feedback.
    *   Implement storage for overrides and re-triggering of cuts.
    *   Add per-show rules and aggressiveness tuning.
*   **Milestone E (FULL transcription):**
    *   Enable full pass transcription job post-publish.
    *   Store transcripts and cleaned text for Project B (Atlas).

## Phase 3: Atlas Integration

**Goal:** Seamlessly integrate Podemos as the primary podcast pre-processor for Atlas.

*   **Redefine Podcast Ingestion Ownership:**
    *   Modify Atlas's `podcast_ingestor.py` to consume from Podemos's API.
    *   Implement Podemos API endpoints for new episodes, cleaned audio, and full transcripts.
*   **Centralize Transcription:**
    *   Update Atlas's transcription logic to source podcast transcripts directly from Podemos.
*   **Integrate Data Storage and Paths:**
    *   Configure Podemos's output paths to be accessible by Atlas.
    *   Update Atlas's `path_manager` to reference Podemos's output directories.
*   **Synchronize Metadata:**
    *   Implement enriched metadata transfer from Podemos to Atlas.
    *   Update Atlas's `metadata_manager.py` to store Podemos-generated metadata.
*   **Align Configuration:**
    *   Configure Atlas to connect to Podemos's API endpoint.

## Phase 4: Refinements and Enhancements

**Goal:** Improve robustness, user experience, and overall polish.

*   **Enhanced Configuration Loading and Merging:** Implement a more robust configuration system.
*   **Loudness Normalization (Post-Cut):** Add optional loudness normalization.
*   **Intelligent Chapter Rewriting:** Ensure accurate re-indexing and timestamp adjustment of chapters.
*   **Basic Monitoring Dashboard:** Develop a simple web-based dashboard for system status.

This roadmap provides a structured approach to developing Podemos and integrating it effectively with Atlas.