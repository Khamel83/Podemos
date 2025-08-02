def build_keep_segments(duration: float, cuts: list) -> list:
    """
    Builds a list of audio segments to keep, given the total duration and a list of ad cuts.
    Cuts are expected to be dictionaries with 'start' and 'end' keys.
    """
    # Sort cuts by start time and merge overlapping cuts
    if not cuts:
        return [[0.0, duration]]

    sorted_cuts = sorted(cuts, key=lambda x: x['start'])
    merged_cuts = []

    for cut in sorted_cuts:
        if not merged_cuts or cut['start'] > merged_cuts[-1]['end']:
            merged_cuts.append([cut['start'], cut['end']])
        else:
            merged_cuts[-1]['end'] = max(merged_cuts[-1]['end'], cut['end'])

    keeps = []
    cursor = 0.0
    for seg in merged_cuts:
        if seg[0] > cursor + 0.001:  # Add a small epsilon to avoid floating point issues
            keeps.append([cursor, seg[0]])
        cursor = max(cursor, seg[1])

    if duration > cursor + 0.001:
        keeps.append([cursor, duration])

    return keeps

if __name__ == "__main__":
    # Example usage
    duration = 300.0 # 5 minutes
    cuts = [
        {'start': 10.0, 'end': 20.0, 'type': 'ad'},
        {'start': 18.0, 'end': 25.0, 'type': 'ad'},
        {'start': 100.0, 'end': 120.0, 'type': 'ad'},
        {'start': 250.0, 'end': 260.0, 'type': 'ad'}
    ]

    keep_segments = build_keep_segments(duration, cuts)
    print(f"Keep segments: {keep_segments}")
    # Expected: [[0.0, 10.0], [25.0, 100.0], [120.0, 250.0], [260.0, 300.0]]

    cuts_no_overlap = [
        {'start': 10.0, 'end': 20.0, 'type': 'ad'},
        {'start': 30.0, 'end': 40.0, 'type': 'ad'},
    ]
    keep_segments_no_overlap = build_keep_segments(duration, cuts_no_overlap)
    print(f"Keep segments (no overlap): {keep_segments_no_overlap}")
    # Expected: [[0.0, 10.0], [20.0, 30.0], [40.0, 300.0]]

    cuts_empty = []
    keep_segments_empty = build_keep_segments(duration, cuts_empty)
    print(f"Keep segments (empty cuts): {keep_segments_empty}")
    # Expected: [[0.0, 300.0]]
