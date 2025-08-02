# Podemos Project Key Decisions

This document outlines key architectural and integration decisions made for the Podemos project.

## 1. Project Naming and Scaffold
*   **Decision:** The project will be named "Podemos" and will utilize the provided `podclean` scaffold.
*   **Rationale:** The `podclean` scaffold offers a comprehensive and well-structured starting point for podcast processing, aligning with the project's goals.

## 2. Primary Podcast Ingestion Ownership
*   **Decision:** Podemos (`podclean`) will be the primary podcast ingestor, responsible for RSS polling, audio download, ad-cutting, and two-pass transcription.
*   **Rationale:** This centralizes complex podcast processing, offloading it from the Atlas project and avoiding duplication of ingestion and transcription logic.

## 3. Centralized Transcription
*   **Decision:** Podemos's "FULL pass transcription" will be the authoritative source for podcast transcripts for Atlas.
*   **Rationale:** Ensures high-quality, structured transcripts are generated once and consumed by Atlas, rather than Atlas performing its own transcription for podcasts.

## 4. Data Storage and Path Integration
*   **Decision:** Podemos's output directories (`data/cleaned/`, `data/transcripts/`) will be directly accessible by Atlas, assuming co-location on the same machine.
*   **Rationale:** Facilitates efficient data transfer between the two systems without requiring additional API calls for file content, improving performance and simplifying integration.

## 5. Metadata Synchronization
*   **Decision:** Podemos will generate and provide enriched metadata (e.g., `cleaned_duration`, `cleaned_bytes`, `cleaned_ready_at`, ad-cut timestamps) to Atlas.
*   **Rationale:** Ensures Atlas has comprehensive and accurate metadata for processed podcast episodes, enabling richer features and analysis.

## 6. API-Driven Integration with Atlas
*   **Decision:** Podemos will expose API endpoints for Atlas to discover new episodes, fetch cleaned audio, and retrieve full transcripts.
*   **Rationale:** Provides a clear and programmatic interface for Atlas to interact with Podemos, promoting loose coupling and scalability.

## 7. Configuration Alignment
*   **Decision:** Atlas will be configured to connect to Podemos's API endpoint, with minimal overlapping configuration.
*   **Rationale:** Simplifies deployment and management by clearly defining responsibilities and connection points between the two systems.

These decisions are designed to ensure a robust, efficient, and well-integrated solution for podcast processing within the broader Atlas ecosystem.