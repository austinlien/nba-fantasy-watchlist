import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

# Authenticate Google Sheets
def authenticate_google_sheets():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("nba-fantasy-sheets.json", scope)
    client = gspread.authorize(creds)
    return client

# Upload Last 3-Game Stats
def upload_last_3_games(df, sheet_name):
    client = authenticate_google_sheets()
    sheet = client.open(sheet_name).worksheet("Last 3 Games")

    print("\n📊 Last 3-Game Stats to Upload:")
    print(df)

    data = [df.columns.values.tolist()] + df.values.tolist()
    sheet.update(data)
    print(f"Successfully uploaded {len(df)} rows to {sheet_name} - 'Last 3 Games' tab!")

# Run test
if __name__ == "__main__":
    test_data = pd.DataFrame({
        "Player": ["Test Player 1", "Test Player 2"],
        "MIN": [25.6, 32.0],
        "PTS": [14.0, 22.7]
    })
    upload_last_3_games(test_data, "NBA Fantasy Waiver Wire")
