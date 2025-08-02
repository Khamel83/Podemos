import os
from fastapi import FastAPI, Response, HTTPException
from fastapi.responses import FileResponse
from src.feed.meta_feed import build_meta_feed
from src.store.db import init_db, get_session
from src.store.models import Episode

app = FastAPI()

# Initialize the database when the application starts
@app.on_event("startup")
async def startup_event():
    init_db()

@app.get("/feed.xml")
async def get_feed():
    # In a real application, base_url would come from config
    base_url = "http://localhost:8080" # Placeholder
    feed_content = build_meta_feed(base_url)
    return Response(content=feed_content, media_type="application/xml")

@app.get("/audio/{episode_guid}.mp3")
async def get_audio(episode_guid: str):
    with get_session() as session:
        episode = session.query(Episode).filter_by(source_guid=episode_guid).first()
        if not episode or not episode.original_file_path:
            raise HTTPException(status_code=404, detail="Audio file not found.")
        
        file_path = episode.original_file_path
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Audio file not found on disk.")
        
        return FileResponse(path=file_path, media_type="audio/mpeg")

if __name__ == "__main__":
    import uvicorn
    # Ensure the data/originals directory exists for FileResponse
    originals_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..\', '..\', 'data\', 'originals')
    if not os.path.exists(originals_dir):
        os.makedirs(originals_dir)
    
    uvicorn.run(app, host="0.0.0.0", port=8080)
