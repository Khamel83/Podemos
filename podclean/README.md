podclean/
  README.md
  checklists.md
  env.template
  config/
    app.yaml
    shows/
      default.rules.yaml
      {show_slug}.rules.yaml
  data/
    db.sqlite3
    originals/           # sha256/aa/bb/<sha>.mp3
    cleaned/             # sha256/cc/dd/<sha>_clean.mp3
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
