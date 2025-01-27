import requests
from dotenv import load_dotenv
import os
import json
import re
import time

# Load environment variables from .env file
load_dotenv()

def fetch_spigot_download_count(url, retries=10, delay=2):

    # Get the Zyte API key from the environment
    api_key = os.getenv("ZYTE_API_KEY")
    
    if not api_key:
        print("Zyte API key not found. Please set it in the .env file.")
        return None

    # Zyte API endpoint
    zyte_url = "https://api.zyte.com/v1/extract"

    for attempt in range(retries):
        try:
            # Fetch the page using Zyte
            response = requests.post(
                zyte_url,
                auth=(api_key, ""),  # Zyte requires basic auth with API key as the username
                json={"url": url, "browserHtml": True},
            )
            
            if response.status_code == 200:
                data = response.json()

                # Extract total downloads
                total_downloads = None

                if "browserHtml" in data:
                    html_content = data["browserHtml"]

                    # Adjust regex to find the number after "Total Downloads:"
                    match = re.search(r'Total Downloads:</dt>\s*<dd>([\d,]+)</dd>', html_content)

                    if match:
                        total_downloads = match.group(1)
                        return int(total_downloads.replace(",", ""))  # Convert to integer
                    else:
                        print(f"Total downloads not found in the extracted HTML. Retry {attempt + 1}/{retries}")

                else:
                    print("No browser HTML found in the response.")

            else:
                print(f"Failed to retrieve data. Status code: {response.status_code}. Retry {attempt + 1}/{retries}")

        except Exception as e:
            print(f"Error occurred: {e}. Retry {attempt + 1}/{retries}")

        # Wait before retrying
        time.sleep(delay)

    print("Failed to retrieve the download count after retries.")
    return None