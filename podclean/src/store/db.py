from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.store.models import Base

DATABASE_URL = "sqlite:///podclean/data/db.sqlite3"

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
