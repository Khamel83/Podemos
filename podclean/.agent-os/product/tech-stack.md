# Podemos Project Technology Stack

The Podemos project (`podclean`) is primarily built using Python, leveraging a set of established tools and libraries for efficient podcast processing.

**Core Technologies:**
*   **Python:** The primary programming language for the application logic.
*   **FFmpeg:** Utilized for audio manipulation, specifically for cutting ad segments and encoding cleaned audio.
*   **Whisper (via faster-whisper/whisper.cpp):** For high-performance audio transcription, supporting both fast and full transcription passes.
*   **SQLite:** Used as the local database for managing podcast metadata, episode information, and processing states.
*   **YAML:** For application and show-specific configuration.

**Anticipated Frameworks/Libraries (to be confirmed during implementation):**
*   **FastAPI/Flask:** For building the RESTful API (`src/serve/api.py`) to serve cleaned audio, feeds, and handle correction endpoints.
*   **Pydantic/Dynaconf:** For robust configuration loading and merging, as suggested in the enhancements.

**Integration Points:**
*   **Atlas Project:** Podemos is designed to integrate seamlessly with the Atlas project, acting as a pre-processor for podcast content. This integration will involve API communication and shared file system access for cleaned audio and transcripts.
