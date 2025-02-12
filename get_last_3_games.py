import requests
import pandas as pd
import time
from fuzzywuzzy import process
from upload_sheets import upload_to_sheets  # Google Sheets upload function
import numpy as np
# NBA API to get all player IDs
NBA_PLAYERS_URL = "https://stats.nba.com/stats/commonallplayers?LeagueID=00&Season=2023-24&IsOnlyCurrentSeason=1"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Referer": "https://www.nba.com/",
    "Connection": "keep-alive"
}

# Fetch all NBA player IDs
def get_nba_player_ids():
    response = requests.get(NBA_PLAYERS_URL, headers=HEADERS)
    
    if response.status_code != 200:
        print("Failed to fetch NBA player list")
        return {}

    data = response.json()
    player_list = data["resultSets"][0]["rowSet"]

    # Create dictionary {Player Name (lowercased) -> Player ID}
    player_id_map = {player[2].lower(): player[0] for player in player_list}  
    print(f"Found {len(player_id_map)} NBA Player IDs.")
    return player_id_map

# Get 25 most added players from waiver wire
def get_most_added_players():
    waiver_df = pd.read_csv("waiver_wire_data.csv")  # Load waiver wire data
    
    if "Player" not in waiver_df.columns:
        print("ERROR: Waiver wire data is missing 'Player' column.")
        return []

    players = waiver_df["Player"].tolist()[:25]  # Get top 25 players
    print(f"Found 25 most added players: {players}")
    return players

# Match waiver wire names to NBA.com names using fuzzy matching I FIXED THIS TOO MANY TIMES HOLY SHIT HELP
def match_player_name(waiver_player, nba_player_list):
    waiver_player = waiver_player.lower().replace("'", "")  # Remove apostrophes for better matching
    match, score = process.extractOne(waiver_player, nba_player_list)
    if score > 75:  # Lower threshold slightly for better matches
        return match
    return None

# Scrape last 3 games using NBA API
def get_last_3_games(player_name, player_id):
    url = f"https://stats.nba.com/stats/playergamelog?PlayerID={player_id}&Season=2023-24&SeasonType=Regular%20Season"
    response = requests.get(url, headers=HEADERS)

    if response.status_code != 200:
        print(f"Failed to fetch last 3 games for {player_name}")
        return None

    data = response.json()
    games = data["resultSets"][0]["rowSet"]

    if len(games) < 3:
        print(f"Less than 3 games found for {player_name}")
        return None

    # Convert to DataFrame and compute averages
    df = pd.DataFrame(games, columns=data["resultSets"][0]["headers"])
    last_3 = df.head(3).copy()
    averages = last_3.mean(numeric_only=True).round(1).to_dict()
    
    averages["Player"] = player_name  # Add player name
    return averages

def scrape_and_upload_most_added():
    espn_ids = get_nba_player_ids()
    players = get_most_added_players()
    player_stats = []

    for name in players:
        if name in espn_ids:
            averages = get_last_3_games(name, espn_ids[name])
            if averages:
                player_stats.append(averages)
        else:
            print(f"❌ No NBA ID found for {name}")

    df = pd.DataFrame(player_stats)

    if not df.empty:
        # ✅ Fix JSON upload issue by replacing NaN and Infinite values
        df.replace([np.inf, -np.inf], np.nan, inplace=True)  # Replace infinite values with NaN
        df.fillna(0, inplace=True)  # Replace NaN with 0

        print("\n📊 Last 3-Game Averages for 25 Most Added Players:")
        print(df)
        upload_to_sheets(df, "NBA Fantasy Waiver Wire")  # ✅ Append to existing sheet
    else:
        print("❌ No valid player data found.")

# Run the function
if __name__ == "__main__":
    scrape_and_upload_most_added()
