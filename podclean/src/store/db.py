from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.store.models import Base
from src.config.config_loader import load_app_config
import os

app_config = load_app_config()
MEDIA_BASE_PATH = app_config.get('PODCLEAN_MEDIA_BASE_PATH', os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data')))
DATABASE_URL = f"sqlite:///{os.path.join(MEDIA_BASE_PATH, 'db.sqlite3')}"

engine = None
SessionLocal = None


def init_db(database_url: str = DATABASE_URL):
    global engine, SessionLocal
    engine = create_engine(database_url, connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_session():
    if SessionLocal is None:
        raise Exception("Database not initialized. Call init_db() first.")
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

def add_or_update_episode(session, episode_data):
    from src.store.models import Episode # Import here to avoid circular dependency
    episode = session.query(Episode).filter_by(source_guid=episode_data['source_guid']).first()
    if episode:
        # Update existing episode
        for key, value in episode_data.items():
            setattr(episode, key, value)
    else:
        # Add new episode
        episode = Episode(**episode_data)
        session.add(episode)
    session.commit()
    session.refresh(episode)
    return episode
