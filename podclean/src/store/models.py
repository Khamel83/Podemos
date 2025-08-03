from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()

class Episode(Base):
    __tablename__ = 'episodes'

    id = Column(Integer, primary_key=True)
    source_guid = Column(String, unique=True, nullable=False, index=True)
    title = Column(String, nullable=False)
    show_name = Column(String, nullable=False)
    pub_date = Column(DateTime, nullable=False)
    original_audio_url = Column(String, nullable=False)
    original_file_path = Column(String, unique=True)
    original_duration = Column(Float)
    original_file_size = Column(Integer)
    cleaned_file_path = Column(String, unique=True)
    cleaned_duration = Column(Float)
    cleaned_file_size = Column(Integer)
    cleaned_ready_at = Column(DateTime)
    status = Column(String, default='pending_download') # e.g., pending_download, downloaded, pending_cut, cut, pending_transcribe, transcribed, error
    image_url = Column(String)
    show_image_url = Column(String)
    show_author = Column(String)
    description = Column(Text)
    ad_segments_json = Column(Text) # JSON string of detected ad segments
    transcript_json = Column(Text) # JSON string of the full transcript
    fast_transcript_json = Column(Text) # JSON string of the fast transcript
    cleaned_chapters_json = Column(Text) # JSON string of adjusted chapters after cutting
    chapters_json = Column(Text) # Raw chapters JSON from RSS feed
    md_transcript_file_path = Column(String) # Path to the Markdown transcript file
    retry_count = Column(Integer, default=0) # Number of times processing has been retried
    last_error = Column(Text) # Stores the last error message

    def __repr__(self):
        return f"<Episode(title='{self.title}', show='{self.show_name}', status='{self.status}')>"
