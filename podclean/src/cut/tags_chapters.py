import json

def adjust_chapters_after_cut(original_chapters: list, keep_segments: list) -> list:
    """
    Adjusts chapter timestamps based on the kept audio segments after cutting.

    Args:
        original_chapters: List of original chapter dictionaries (e.g., from Podcasting 2.0 JSON).
                           Each chapter dict should have 'start' and 'end' in seconds.
        keep_segments: List of [start, end] segments that were kept from the original audio.

    Returns:
        A new list of chapter dictionaries with adjusted timestamps.
    """
    adjusted_chapters = []
    for original_chapter in original_chapters:
        chapter_start = original_chapter['start']
        chapter_end = original_chapter['end']
        adjusted_start = None
        adjusted_end = None
        current_offset = 0.0

        for k_start, k_end in keep_segments:
            segment_duration = k_end - k_start

            # Case 1: Chapter starts within this keep segment
            if k_start <= chapter_start < k_end:
                adjusted_start = current_offset + (chapter_start - k_start)

            # Case 2: Chapter ends within this keep segment
            if k_start < chapter_end <= k_end:
                adjusted_end = current_offset + (chapter_end - k_start)

            # Case 3: Chapter spans across this entire keep segment
            if chapter_start < k_start and chapter_end > k_end:
                # If chapter spans this segment, add its duration to the adjusted end if it's the first part
                # or if it's a continuation of a spanning chapter
                pass # Handled by start/end within segments, or by total duration if chapter spans multiple

            # If both start and end are found within the current segment or across segments
            if adjusted_start is not None and adjusted_end is not None:
                # Ensure adjusted_end is not before adjusted_start due to floating point or complex overlaps
                if adjusted_end < adjusted_start:
                    adjusted_end = adjusted_start + (chapter_end - chapter_start) # Approximate duration
                
                new_chapter = original_chapter.copy()
                new_chapter['start'] = adjusted_start
                new_chapter['end'] = adjusted_end
                adjusted_chapters.append(new_chapter)
                break # Move to the next original chapter
            
            current_offset += segment_duration

    return adjusted_chapters

def filter_ad_chapters(chapters: list) -> list:
    """
    Filters out chapters that are identified as ad segments.
    Assumes matches_ad_chapter function is available (from detect.chapters).
    """
    from src.detect.chapters import matches_ad_chapter # Import here to avoid circular dependency
    return [c for c in chapters if not matches_ad_chapter(c['title'])]

if __name__ == "__main__":
    # Example Usage
    original_chapters = [
        {"start": 0, "end": 10, "title": "Intro"},
        {"start": 10, "end": 20, "title": "Sponsor Ad"},
        {"start": 20, "end": 30, "title": "Main Content Part 1"},
        {"start": 30, "end": 40, "title": "Another Ad"},
        {"start": 40, "end": 50, "title": "Main Content Part 2"},
    ]
    
    # Assume cuts were [10, 20] and [30, 40]
    # And original audio duration was 50
    # So keep segments would be:
    keep_segments = [
        [0, 10],  # Intro
        [20, 30], # Main Content Part 1
        [40, 50]  # Main Content Part 2
    ]

    # Test adjust_chapters_after_cut
    adjusted = adjust_chapters_after_cut(original_chapters, keep_segments)
    print("Adjusted Chapters:")
    for c in adjusted:
        print(c)
    # Expected (approximately):
    # {'start': 0.0, 'end': 10.0, 'title': 'Intro'}
    # {'start': 10.0, 'end': 20.0, 'title': 'Main Content Part 1'}
    # {'start': 20.0, 'end': 30.0, 'title': 'Main Content Part 2'}

    # Test filter_ad_chapters
    filtered = filter_ad_chapters(original_chapters)
    print("\nFiltered Chapters (ads removed):")
    for c in filtered:
        print(c)
    # Expected:
    # {'start': 0, 'end': 10, 'title': 'Intro'}
    # {'start': 20, 'end': 30, 'title': 'Main Content Part 1'}
    # {'start': 40, 'end': 50, 'title': 'Main Content Part 2'}
