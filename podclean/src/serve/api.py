import os
from fastapi import FastAPI, Response, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from src.feed.meta_feed import build_meta_feed
from src.store.db import init_db, get_session
from src.store.models import Episode
from src.processor.episode_processor import process_episode # To reprocess episode after mark
from src.config.config_loader import load_app_config # Import config loader

app = FastAPI()

# Pydantic model for the /mark endpoint payload
class MarkRequest(BaseModel):
    episode_id: int
    start: float
    end: float
    label: str # "ad" or "not_ad"

# Initialize the database when the application starts
@app.on_event("startup")
async def startup_event():
    init_db()
    app_cfg = load_app_config()
    app.base_url = app_cfg.get('PODCLEAN_BASE_URL', "http://localhost:8080") # Load base URL from config

@app.get("/feed.xml")
async def get_feed():
    # In a real application, base_url would come from config
    base_url = app.base_url # Use the base_url from app state
    feed_content = build_meta_feed(base_url)
    return Response(content=feed_content, media_type="application/xml")

@app.get("/audio/{episode_guid}.mp3")
async def get_audio(episode_guid: str):
    with get_session() as session:
        episode = session.query(Episode).filter_by(source_guid=episode_guid).first()
        if not episode or (not episode.cleaned_file_path and not episode.original_file_path):
            raise HTTPException(status_code=404, detail="Audio file not found.")
        
        file_path = episode.cleaned_file_path if episode.cleaned_file_path else episode.original_file_path
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Audio file not found on disk.")
        
        return FileResponse(path=file_path, media_type="audio/mpeg")

@app.get("/transcripts/{episode_guid}.json")
async def get_transcript(episode_guid: str):
    with get_session() as session:
        episode = session.query(Episode).filter_by(source_guid=episode_guid).first()
        if not episode or not episode.transcript_json:
            raise HTTPException(status_code=404, detail="Transcript not found.")
        
        return Response(content=episode.transcript_json, media_type="application/json")

@app.get("/new_episodes")
async def get_new_episodes(limit: int = 10, offset: int = 0):
    with get_session() as session:
        # For now, return episodes that have been processed (cut or transcribed)
        # In a real scenario, this might involve a 'published' flag or a timestamp
        episodes = session.query(Episode).filter(Episode.status.in_(['cut', 'transcribed']))\                                        .order_by(Episode.pub_date.desc())\                                        .offset(offset).limit(limit).all()
        
        # Return a simplified list of episode data for Atlas to consume
        return [
            {
                "id": ep.id,
                "source_guid": ep.source_guid,
                "title": ep.title,
                "show_name": ep.show_name,
                "pub_date": ep.pub_date.isoformat(),
                "cleaned_audio_url": f"{app.base_url}/audio/{ep.source_guid}.mp3" if ep.cleaned_file_path else None,
                "original_audio_url": f"{app.base_url}/audio/{ep.source_guid}.mp3" if ep.original_file_path and not ep.cleaned_file_path else None,
                "transcript_url": f"{app.base_url}/transcripts/{ep.source_guid}.json" if ep.transcript_json else None,
                "status": ep.status,
                "cleaned_duration": ep.cleaned_duration,
                "cleaned_file_size": ep.cleaned_file_size,
                "cleaned_ready_at": ep.cleaned_ready_at.isoformat() if ep.cleaned_ready_at else None,
                "image_url": ep.image_url,
                "show_image_url": ep.show_image_url,
                "show_author": ep.show_author,
            } for ep in episodes
        ]

@app.post("/mark")
async def post_mark(mark_request: MarkRequest):
    with get_session() as session:
        episode = session.query(Episode).filter_by(id=mark_request.episode_id).first()
        if not episode:
            raise HTTPException(status_code=404, detail="Episode not found.")

        # For now, just print the mark. In a real implementation, this would
        # store the mark and trigger a re-processing of the episode.
        print(f"Received mark for episode {mark_request.episode_id}: "
              f"start={mark_request.start}, end={mark_request.end}, label={mark_request.label}")
        
        # TODO: Store the mark in the database (e.g., in a new table or as part of episode.ad_segments_json)
        # For now, we'll just reprocess the episode to demonstrate the flow.
        # This will re-run ad detection and cutting with potentially updated rules/overrides.
        # In a more sophisticated system, marks would influence future detection.
        process_episode(mark_request.episode_id)

        return {"message": "Mark received and episode re-processing initiated."}

if __name__ == "__main__":
    import uvicorn
    # Ensure the data/originals directory exists for FileResponse
    originals_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'data', 'originals')
    if not os.path.exists(originals_dir):
        os.makedirs(originals_dir)
    
    uvicorn.run(app, host="0.0.0.0", port=8080)

