from datetime import datetime
from sqlalchemy.orm import Session
from src.store.db import get_session
from src.store.models import Episode
from xml.etree.ElementTree import Element, SubElement, tostring

def build_meta_feed(base_url: str, max_items: int = 500):
    with get_session() as session:
        episodes = session.query(Episode).filter(Episode.original_file_path.isnot(None)).order_by(Episode.pub_date.desc()).limit(max_items).all()

    rss = Element('rss', {'version': '2.0', 'xmlns:itunes': 'http://www.itunes.com/dtds/podcast-1.0.dtd'})
    channel = SubElement(rss, 'channel')
    SubElement(channel, 'title').text = "Podemos - Clean Podcasts (Originals)"
    SubElement(channel, 'link').text = base_url
    SubElement(channel, 'description').text = "A feed of original podcast episodes processed by Podemos."
    SubElement(channel, 'language').text = "en-us"
    SubElement(channel, 'lastBuildDate').text = datetime.now().strftime("%a, %d %b %Y %H:%M:%S %z")

    for ep in episodes:
        item = SubElement(channel, 'item')
        SubElement(item, 'title').text = f"[{ep.show_name}] {ep.title}"
        SubElement(item, 'link').text = f"{base_url}/audio/{ep.source_guid}.mp3" # Using source_guid for now
        SubElement(item, 'guid').text = ep.source_guid
        SubElement(item, 'pubDate').text = ep.pub_date.strftime("%a, %d %b %Y %H:%M:%S %z")
        
        enclosure = SubElement(item, 'enclosure', {
            'url': f"{base_url}/audio/{ep.source_guid}.mp3", # Using source_guid for now
            'length': str(ep.original_file_size) if ep.original_file_size else "0",
            'type': 'audio/mpeg'
        })
        
        if ep.image_url:
            SubElement(item, '{http://www.itunes.com/dtds/podcast-1.0.dtd}image', {'href': ep.image_url})
        elif ep.show_image_url:
            SubElement(item, '{http://www.itunes.com/dtds/podcast-1.0.dtd}image', {'href': ep.show_image_url})

        if ep.show_author:
            SubElement(item, '{http://www.itunes.com/dtds/podcast-1.0.dtd}author').text = ep.show_author
        
        if ep.description:
            SubElement(item, 'description').text = ep.description

    return tostring(rss, encoding='utf-8', xml_declaration=True).decode()

if __name__ == "__main__":
    # Example usage (for testing purposes)
    # This requires the database to be initialized and populated with episodes
    from src.store.db import init_db
    init_db()
    # You would typically call this from your API endpoint
    # print(build_meta_feed("http://localhost:8080"))
    print("This script is intended to be run as part of the main application.")
