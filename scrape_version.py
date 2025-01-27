import requests
import re

BUKKIT_URL = "https://dev.bukkit.org/projects/nccasino"

def fetch_page_content():
    """Fetch the page content from the Bukkit project URL."""
    try:
        response = requests.get(BUKKIT_URL, timeout=5)
        response.raise_for_status()  # Raise an error for bad status codes
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching page content: {e}")
        return None

def parse_version_from_html(html_content):
    """Extract the latest version from the HTML content using regex."""
    pattern = re.compile(r"nccasino-(\d+\.\d+\.\d+)\.jar")
    match = pattern.search(html_content)
    return match.group(1) if match else None

async def get_latest_version():
    """Fetch and parse the latest version from the Bukkit site."""
    html_content = fetch_page_content()
    if html_content:
        return parse_version_from_html(html_content)
    return None
