import requests
import re

GITHUB_URL = "https://github.com/njm25/NCCasino/releases/latest"

async def get_latest_version():
    """Fetch the latest release version by following the redirect from GitHub."""
    try:
        response = requests.get(GITHUB_URL, timeout=5, allow_redirects=True)
        response.raise_for_status()

        latest_url = response.url  # Get the final redirected URL
        match = re.search(r"/tag/(\d+\.\d+\.\d+)", latest_url)

        return match.group(1) if match else None

    except requests.RequestException as e:
        print(f"Error fetching latest version: {e}")
        return None
