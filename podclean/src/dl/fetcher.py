import requests
import os
from urllib.parse import urlparse

def download_file(url: str, destination_folder: str, filename: str = None):
    """
    Downloads a file from a URL to a specified destination folder.
    If filename is not provided, it extracts it from the URL.
    """
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)

    if filename is None:
        parsed_url = urlparse(url)
        filename = os.path.basename(parsed_url.path)
        if not filename: # Fallback if path is empty
            filename = "downloaded_file"

    destination_path = os.path.join(destination_folder, filename)

    try:
        with requests.get(url, stream=True) as r:
            r.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
            with open(destination_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        print(f"Successfully downloaded {url} to {destination_path}")
        return destination_path
    except requests.exceptions.RequestException as e:
        print(f"Error downloading {url}: {e}")
        return None

if __name__ == "__main__":
    # Example usage (for testing purposes)
    test_url = "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3"
    test_folder = "../../data/originals"
    downloaded_path = download_file(test_url, test_folder)
    if downloaded_path:
        print(f"Test download complete: {downloaded_path}")
    else:
        print("Test download failed.")
