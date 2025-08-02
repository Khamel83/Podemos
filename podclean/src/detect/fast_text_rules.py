import re

def contains_phrases(text: str, phrases: list) -> bool:
    """
    Checks if the text contains any of the given phrases (case-insensitive).
    """
    text_lower = text.lower()
    return any(p.lower() in text_lower for p in phrases)

def has_url_or_price(text: str, url_patterns: list, price_patterns: list) -> bool:
    """
    Checks if the text contains any URL or price patterns.
    """
    for pattern in url_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    for pattern in price_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False

if __name__ == "__main__":
    # Example Usage
    test_text = "Visit our website at example.com for a 20% discount!"
    test_phrases = ["visit our website", "discount"]
    test_url_patterns = ["\\bhttps?://[\\w\\.-]+\\.[a-z]{2,}\\S*", "\\b[A-Za-z0-9.-]+\\.(com|io|ai|net)\\b"]
    test_price_patterns = ["\\b\\$\d+", "\\b\\d+%\\s*off\\b"]

    print(f"Contains phrases: {contains_phrases(test_text, test_phrases)}")
    print(f"Has URL or price: {has_url_or_price(test_text, test_url_patterns, test_price_patterns)}")

    test_text_no_match = "This is a regular sentence."
    print(f"Contains phrases (no match): {contains_phrases(test_text_no_match, test_phrases)}")
    print(f"Has URL or price (no match): {has_url_or_price(test_text_no_match, test_url_patterns, test_price_patterns)}")
