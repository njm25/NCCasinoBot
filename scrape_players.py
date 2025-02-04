import aiohttp
import asyncio

BSTATS_URL = 'https://bstats.org/api/v1/plugins/24579/charts/players/data/?maxElements=1'

async def get_latest_players():
    """Fetch the latest player count"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(BSTATS_URL, timeout=5) as response:
                if response.status == 200:
                    data = await response.json()
                    if isinstance(data, list) and len(data) > 0 and isinstance(data[0], list) and len(data[0]) > 1:
                        latest_value = data[0][1]
                        return latest_value
                    else:
                        print("Unexpected data format:", data)
                        return None
                else:
                    print(f"Error: Received status code {response.status}")
                    return None
    except Exception as e:
        print(f"Error fetching players: {e}")
        return None
