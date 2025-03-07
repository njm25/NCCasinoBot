import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
import os
import traceback
import asyncio
from fetch_downloads import get_total_downloads
from scrape_version import get_latest_version
from scrape_players import get_latest_players  # New import
from my_commands import register_commands

# Load environment variables
load_dotenv()

NCCASINO_TOKEN = os.getenv('NCCASINO_TOKEN')

# Set up intents
nccasino_intents = discord.Intents.default()
nccasino_intents.voice_states = True
nccasino_intents.messages = True

# Create bot instance
nccasino_bot = commands.Bot(command_prefix='?', intents=nccasino_intents)

# Global variables for rotating display
last_total_downloads = None  
latest_version = None
latest_players = None  # New variable for player count
display_state = 0  # 0: downloads, 1: version, 2: players

# Task to check downloads once per day
@tasks.loop(hours=24)
async def check_downloads():
    global last_total_downloads
    try:
        total_downloads = await get_total_downloads()
        if total_downloads and total_downloads != last_total_downloads:
            last_total_downloads = total_downloads
            print(f"Updated total downloads: {total_downloads}")
    except Exception as e:
        print(f"Error in check_downloads: {e}")
        traceback.print_exc()

# Task to check version once per hour
@tasks.loop(minutes=60)
async def check_version():
    global latest_version
    try:
        version = await get_latest_version()
        if version:
            latest_version = version
            print(f"Updated NCCASINO version: {latest_version}")
    except Exception as e:
        print(f"Error in check_version: {e}")
        traceback.print_exc()

# Task to check player count every 10 minutes
@tasks.loop(minutes=10)
async def check_players():
    global latest_players
    try:
        players = await get_latest_players()
        if players is not None:
            latest_players = players
            print(f"Updated NCCASINO players: {latest_players}")
    except Exception as e:
        print(f"Error in check_players: {e}")
        traceback.print_exc()

# Task to rotate display status every 15 seconds
@tasks.loop(seconds=15)
async def rotate_display():
    global display_state

    if last_total_downloads is None or latest_version is None or latest_players is None:
        print("Waiting for valid download count, version, and player count before updating presence.")
        return  

    display_state = (display_state + 1) % 3  # Cycle through 0, 1, 2
    if display_state == 0:
        status_text = f"Downloads: {last_total_downloads}"
    elif display_state == 1:
        status_text = f"Current Version: {latest_version}"
    else:
        status_text = f"Active Players: {latest_players}"  # New status

    await nccasino_bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=status_text))
    print(f"Updated bot presence: {status_text}")

@nccasino_bot.event
async def on_ready():
    print(f'NCCASINO logged in as {nccasino_bot.user}')
    
    # Sync slash commands globally
    await nccasino_bot.tree.sync()
    print("NCCASINO slash commands synced globally.")

    # Start background tasks
    check_downloads.start()
    check_version.start()
    check_players.start()  # Start fetching player stats

    # Wait until valid values are obtained before starting rotation
    while last_total_downloads is None or latest_version is None or latest_players is None:
        print("Waiting for initial values...")
        await asyncio.sleep(5)

    print("Initial values retrieved. Starting presence rotation.")
    rotate_display.start()

# Error handling
@nccasino_bot.event
async def on_error(event, *args, **kwargs):
    print(f"NCCASINO error occurred: {traceback.format_exc()}")

# Main function to run the bot
async def main():
    await nccasino_bot.start(NCCASINO_TOKEN)

if __name__ == '__main__':
    asyncio.run(main())
