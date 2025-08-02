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
