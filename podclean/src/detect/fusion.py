from src.detect.chapters import load_chapters_from_json, matches_ad_chapter
from src.transcribe.fast_whisper import fast_transcribe
from src.detect.fast_text_rules import contains_phrases, has_url_or_price

def in_time_priors(timestamp: float, episode_duration: float, priors: dict) -> bool:
    """
    Checks if a timestamp falls within defined time priors (pre-roll, mid-roll, post-roll).
    """
    if not priors or not episode_duration:
        return False

    # Pre-roll
    pre_roll_max_s = priors.get('pre_roll_max_s', 0)
    if timestamp <= pre_roll_max_s:
        return True

    # Post-roll
    post_roll_last_s = priors.get('post_roll_last_s', 0)
    if timestamp >= (episode_duration - post_roll_last_s):
        return True

    # Mid-roll
    mid_roll_pct = priors.get('mid_roll_pct')
    if mid_roll_pct and len(mid_roll_pct) == 2:
        mid_roll_start = episode_duration * mid_roll_pct[0]
        mid_roll_end = episode_duration * mid_roll_pct[1]
        if mid_roll_start <= timestamp <= mid_roll_end:
            return True

    return False

    return False

def confident_enough(cuts: list, cfg: dict) -> bool:
    """
    Checks if the detected cuts are confident enough based on MIN_CONFIDENCE.
    """
    min_confidence = cfg.get('MIN_CONFIDENCE', 0.70) # Default from env.template
    if not cuts:
        return False
    return all(cut.get('confidence', 0) >= min_confidence for cut in cuts)

def merge_and_pad(cuts: list, padding_seconds: float) -> list:
    """
    Merges overlapping cuts and applies padding.
    """
    if not cuts:
        return []

    # Sort cuts by start time
    sorted_cuts = sorted(cuts, key=lambda x: x['start'])
    
    merged = []
    for cut in sorted_cuts:
        start = max(0.0, cut['start'] - padding_seconds)
        end = cut['end'] + padding_seconds

        if not merged or start > merged[-1]['end']:
            merged.append({'start': start, 'end': end})
        else:
            merged[-1]['end'] = max(merged[-1]['end'], end)
    return merged

def filter_by_policy(cuts: list) -> list:
    """
    Applies policy rules to filter cuts (e.g., remove very short cuts).
    For now, a placeholder.
    """
    return cuts

def slide(segments, size_s, step_s):
    """
    Slides a window over transcription segments.
    Yields a dictionary with 'text', 'start', 'end', and 'words' for the window.
    """
    if not segments:
        return

    # Flatten words for easier processing
    all_words = []
    for segment in segments:
        if 'words' in segment:
            all_words.extend(segment['words'])

    if not all_words:
        return

    # Sort words by start time
    all_words.sort(key=lambda x: x['start'])

    # Initialize window
    current_start = all_words[0]['start']
    current_end = current_start + size_s
    
    # Find the index of the first word that starts after current_end
    end_idx = 0
    while end_idx < len(all_words) and all_words[end_idx]['start'] < current_end:
        end_idx += 1

    while True:
        window_words = []
        window_text = []
        window_start = float('inf')
        window_end = float('-inf')

        # Collect words within the current window
        for word in all_words:
            if word['start'] >= current_start and word['end'] <= current_end:
                window_words.append(word)
                window_text.append(word['word'])
                window_start = min(window_start, word['start'])
                window_end = max(window_end, word['end'])
            elif word['start'] > current_end:
                break # Optimization: words are sorted

        if window_words:
            yield {
                'text': " ".join(window_text),
                'start': window_start,
                'end': window_end,
                'words': window_words
            }

        # Move the window
        current_start += step_s
        current_end = current_start + size_s

        # If the window has moved beyond all words, break
        if current_start >= all_words[-1]['end']:
            break

def detect_ads_fast(audio_path, episode_meta, show_profile, cfg):
    cuts = []

    # 1) Chapters pass (Podcasting 2.0)
    if hasattr(episode_meta, 'chapters_json') and episode_meta.chapters_json:
        chap = load_chapters_from_json(episode_meta.chapters_json)
        for c in chap:
            if matches_ad_chapter(c['title']):
                cuts.append({'start': c['start'], 'end': c['end'], 'type': "chapter", 'confidence': 0.99})

    if confident_enough(cuts, cfg):
        return merge_and_pad(cuts, cfg.get('detector', {}).get('padding_seconds', 8)) # Default padding from config

    # 2) Transcript rules (small model, VAD, word timestamps)
    # Assuming cfg.FAST_MODEL, cfg.FAST_VAD from config
    # Need to pass these from main config or env
    # For now, using hardcoded values or defaults
    tr = fast_transcribe(audio_path, model_size="small", vad=True, word_timestamps=True)

    # Assuming show_profile has phrases, url_patterns, price_patterns
    # And cfg.detector has require_signals
    # Need to load default.rules.yaml and merge with show_profile
    default_phrases = ["brought to you by", "presented by", "sponsor", "promo code", "use code", "visit", "slash", "free trial", "risk-free", "terms apply"]
    default_url_patterns = ["\\bhttps?://[\\w\\.-]+\\.[a-z]{2,}\\S*", "\\b[A-Za-z0-9.-]+\\.(com|io|ai|net)\\b"]
    default_price_patterns = ["\\b\$\\d+", "\\b\d+%\\s*off\\b"]

    # Combine show-specific rules with default rules
    all_phrases = list(set(show_profile.get('phrases', []) + default_phrases))
    all_url_patterns = list(set(show_profile.get('url_patterns', []) + default_url_patterns))
    all_price_patterns = list(set(show_profile.get('price_patterns', []) + default_price_patterns))

    require_signals = cfg.detector.get('require_signals', 2) # Default to 2 if not in config

    for win in slide(tr, size_s=20, step_s=5):
        score = 0
        if contains_phrases(win['text'], all_phrases): score += 1
        if has_url_or_price(win['text'], all_url_patterns, all_price_patterns): score += 1
        if in_time_priors(win['start'], episode_meta.original_duration, cfg.detector.get('priors', {})): score += 1
        
        if score >= require_signals:
            cuts.append({'start': win['start'], 'end': win['end'], 'type': "text", 'confidence': 0.7})

    # 3) (optional v2) audio cues / jingle match if still low recall
    # if cfg.detector.use_audio_cues and need_more_evidence(cuts):
    #     for m in match_jingles(audio_path, show_profile.jingles):
    #         cuts.append(range(m.start, m.end, "audio", conf=0.6))

    # TODO: Implement merge_and_pad and filter_by_policy
    return cuts

