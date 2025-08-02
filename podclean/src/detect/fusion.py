from src.detect.chapters import load_chapters_from_json, matches_ad_chapter

def detect_ads_fast(audio_path, episode_meta, show_profile, cfg):
    cuts = []

    # 1) Chapters pass (Podcasting 2.0)
    # Assuming episode_meta.chapters_json contains the chapter data as a JSON string
    if hasattr(episode_meta, 'chapters_json') and episode_meta.chapters_json:
        chap = load_chapters_from_json(episode_meta.chapters_json)
        for c in chap:
            if matches_ad_chapter(c['title']):
                # Store cuts as (start_time, end_time, type, confidence)
                cuts.append({'start': c['start'], 'end': c['end'], 'type': "chapter", 'confidence': 0.99})

    # TODO: Implement confident_enough, merge_and_pad, filter_by_policy
    # For now, just return the raw cuts
    return cuts
