import json
import os

def load_chapters_from_json(json_string: str):
    """
    Loads chapters from a JSON string.
    Expected format: [{'start': 0, 'end': 10, 'title': 'Intro'}, ...]
    """
    if not json_string:
        return []
    try:
        chapters = json.loads(json_string)
        # Basic validation for chapter structure
        if not isinstance(chapters, list):
            return []
        for chapter in chapters:
            if not all(k in chapter for k in ['start', 'end', 'title']):
                return [] # Invalid chapter format
        return chapters
    except json.JSONDecodeError:
        return []

def load_chapters_from_file(file_path: str):
    """
    Loads chapters from a JSON file.
    """
    if not os.path.exists(file_path):
        return []
    with open(file_path, 'r') as f:
        return load_chapters_from_json(f.read())

def matches_ad_chapter(chapter_title: str) -> bool:
    """
    Checks if a chapter title indicates an ad segment.
    """
    ad_keywords = ["ad", "sponsor", "promo", "advertisement", "commercial"]
    return any(keyword in chapter_title.lower() for keyword in ad_keywords)
