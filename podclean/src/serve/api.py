from fastapi import FastAPI, Response, HTTPException, Request, Form
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from src.feed.meta_feed import build_meta_feed
from src.store.db import init_db, get_session
from src.store.models import Episode
from src.processor.episode_processor import process_episode, perform_full_transcription # Import both
from fastapi import FastAPI, Response, HTTPException, Request, Form, Depends
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from src.feed.meta_feed import build_meta_feed
from src.store.db import init_db, get_session
from src.store.models import Episode
from src.processor.episode_processor import process_episode, perform_full_transcription # Import both
from src.config.config_loader import load_app_config, add_feed_to_config, remove_feed_from_config # Import config loader and feed management functions
from src.config.config import AppConfig # Import AppConfig
from fastapi.staticfiles import StaticFiles # Import StaticFiles
from sqlalchemy import func # Import func for counting

app = FastAPI()

templates = Jinja2Templates(directory="podclean/src/serve/templates")

# Mount static files directory
app.mount("/static", StaticFiles(directory="podclean/src/serve/static"), name="static")

# Basic Authentication setup
security = HTTPBasic()

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
    app_cfg: AppConfig = load_app_config()
    app.base_url = app_cfg.PODCLEAN_BASE_URL # Load base URL from config

async def verify_feed_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    app_cfg = load_app_config()
    if app_cfg.feed_auth_enabled:
        if not (credentials.username == app_cfg.feed_username and credentials.password == app_cfg.feed_password):
            raise HTTPException(status_code=401, detail="Unauthorized")
    return True

@app.get("/feed.xml")
async def get_feed(auth_ok: bool = Depends(verify_feed_credentials)):
    # In a real application, base_url would come from config
    base_url = app.base_url # Use the base_url from app state
    feed_content = build_meta_feed(base_url)
    return Response(content=feed_content, media_type="application/xml")
from src.config.config import AppConfig # Import AppConfig
from fastapi.staticfiles import StaticFiles # Import StaticFiles
from sqlalchemy import func # Import func for counting

app = FastAPI()

templates = Jinja2Templates(directory="podclean/src/serve/templates")

# Mount static files directory
app.mount("/static", StaticFiles(directory="podclean/src/serve/static"), name="static")

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
    app_cfg: AppConfig = load_app_config()
    app.base_url = app_cfg.PODCLEAN_BASE_URL # Load base URL from config

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

@app.get("/chapters/{episode_guid}.json")
async def get_chapters(episode_guid: str):
    with get_session() as session:
        episode = session.query(Episode).filter_by(source_guid=episode_guid).first()
        if not episode or not episode.cleaned_chapters_json:
            raise HTTPException(status_code=404, detail="Chapters not found.")
        
        return Response(content=episode.cleaned_chapters_json, media_type="application/json")

@app.get("/transcripts/{episode_guid}.md")
async def get_md_transcript(episode_guid: str):
    with get_session() as session:
        episode = session.query(Episode).filter_by(source_guid=episode_guid).first()
        if not episode or not episode.md_transcript_file_path or not os.path.exists(episode.md_transcript_file_path):
            raise HTTPException(status_code=404, detail="Markdown transcript not found.")
        
        with open(episode.md_transcript_file_path, 'r') as f:
            content = f.read()
        return Response(content=content, media_type="text/markdown")

@app.get("/new_episodes")
async def get_new_episodes(limit: int = 10, offset: int = 0):
    with get_session() as session:
        # For now, return episodes that have been processed (cut or transcribed)
        # In a real scenario, this might involve a 'published' flag or a timestamp
        episodes = session.query(Episode).filter(Episode.status.in_(['cut', 'transcribed']))\
                                        .order_by(Episode.pub_date.desc())\
                                        .offset(offset).limit(limit).all()
        
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


@app.get("/status")
async def get_status():
    with get_session() as session:
        episode_counts = session.query(Episode.status, func.count(Episode.id)).group_by(Episode.status).all()
        return {"episode_counts": dict(episode_counts)}

@app.get("/")
async def read_root(request: Request):
    with get_session() as session:
        episodes = session.query(Episode).order_by(Episode.pub_date.desc()).all()
        return templates.TemplateResponse("index.html", {"request": request, "episodes": episodes})

@app.post("/process_episode")
async def process_episode_web(episode_id: int = Form(...)):
    process_episode(episode_id)
    return RedirectResponse(url="/", status_code=303)

@app.post("/perform_full_transcription")
async def perform_full_transcription_web(episode_id: int = Form(...)):
    perform_full_transcription(episode_id)
    return RedirectResponse(url="/", status_code=303)

@app.get("/feeds", response_class=HTMLResponse)
async def manage_feeds(request: Request, message: str = None, message_type: str = None):
    app_config = load_app_config()
    feeds = app_config.feeds if hasattr(app_config, 'feeds') else []
    return templates.TemplateResponse("feeds.html", {"request": request, "feeds": feeds, "message": message, "message_type": message_type})

@app.post("/feeds/add", response_class=RedirectResponse, status_code=303)
async def add_feed_web(feed_url: str = Form(...)):
    try:
        add_feed_to_config(feed_url)
        return RedirectResponse(url="/feeds?message=Feed added successfully&message_type=success", status_code=303)
    except Exception as e:
        return RedirectResponse(url=f"/feeds?message=Error adding feed: {e}&message_type=error", status_code=303)

@app.post("/feeds/remove", response_class=RedirectResponse, status_code=303)
async def remove_feed_web(feed_url: str = Form(...)):
    try:
        remove_feed_from_config(feed_url)
        return RedirectResponse(url="/feeds?message=Feed removed successfully&message_type=success", status_code=303)
    except Exception as e:
        return RedirectResponse(url=f"/feeds?message=Error removing feed: {e}&message_type=error", status_code=303)

@app.post("/feeds/remove", response_class=RedirectResponse, status_code=303)
async def remove_feed_web(feed_url: str = Form(...)):
    try:
        remove_feed_from_config(feed_url)
        return RedirectResponse(url="/feeds?message=Feed removed successfully&message_type=success", status_code=303)
    except Exception as e:
        return RedirectResponse(url=f"/feeds?message=Error removing feed: {e}&message_type=error", status_code=303)

@app.get("/feeds/{show_name}/settings", response_class=HTMLResponse)
async def get_show_settings(request: Request, show_name: str, message: str = None, message_type: str = None):
    show_rules = load_show_rules(show_name) # Load show-specific rules
    return templates.TemplateResponse("show_settings.html", {"request": request, "show_name": show_name, "show_rules": show_rules, "message": message, "message_type": message_type})

@app.post("/feeds/{show_name}/settings", response_class=RedirectResponse, status_code=303)
async def post_show_settings(
    show_name: str,
    backlog_strategy: str = Form(...),
    last_n_episodes_count: int = Form(...),
    aggressiveness: str = Form(...)
):
    try:
        # Update show-specific rules in config/shows/{show_name}.rules.yaml
        # This requires a new function in config_loader.py to save show rules
        from src.config.config_loader import save_show_rules
        save_show_rules(show_name, backlog_strategy, last_n_episodes_count, aggressiveness)

        return RedirectResponse(url=f"/feeds/{show_name}/settings?message=Settings saved successfully&message_type=success", status_code=303)
    except Exception as e:
        return RedirectResponse(url=f"/feeds/{show_name}/settings?message=Error saving settings: {e}&message_type=error", status_code=303)

@app.get("/health")
async def health_check():
    try:
        with get_session() as session:
            # Try to get a simple count to check DB connection
            episode_count = session.query(Episode).count()
        return {"status": "ok", "database_connection": "successful", "episode_count": episode_count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {e}")

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
    # Ensure the media base directory exists
    app_cfg = load_app_config()
    media_base_path = app_cfg.PODCLEAN_MEDIA_BASE_PATH
    if not os.path.exists(media_base_path):
        os.makedirs(media_base_path)
    
    # Ensure specific subdirectories exist
    for sub_dir in ['originals', 'cleaned', 'transcripts', 'chapters']:
        path = os.path.join(media_base_path, sub_dir)
        if not os.path.exists(path):
            os.makedirs(path)

    uvicorn.run(app, host="0.0.0.0", port=8080)



