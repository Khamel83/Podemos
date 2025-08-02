# Day 0
- [ ] Fill env.template → .env
- [ ] Provide OPML export; run scripts/bootstrap.sh to import feeds
- [ ] Start server (`src/serve/api.py`) and queue (`jobs/worker.py`)

# Milestone A (No-cut baseline)
- [ ] Poll feeds, download originals to data/originals/
- [ ] Build meta feed from originals only
- [ ] Subscribe in Overcast to /feed.xml (private URL with token)

# Milestone B (Chapters-only cuts)
- [ ] Enable detector.use_chapters
- [ ] Verify ffmpeg plan -> cleaned files; chapters rewritten sans ads
- [ ] Sample 5 shows end-to-end

# Milestone C (FAST ad cut)
- [ ] Enable text rules (FAST model)
- [ ] Output skip-chapters (non-destructive) for 10 episodes; spot-check
- [ ] Enable destructive cuts; confirm padding & audio integrity

# Milestone D (Learning loop)
- [ ] Expose /mark correction endpoint
- [ ] Store overrides and retrigger cut
- [ ] Add per-show rules; tune aggressiveness

# Milestone E (FULL transcription)
- [ ] Enable full pass job post-publish
- [ ] Store transcripts & cleaned text for Project B
