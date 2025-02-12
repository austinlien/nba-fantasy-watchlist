import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

# Google Sheets authentication
def authenticate_google_sheets():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("nba-fantasy-sheets.json", scope)
    client = gspread.authorize(creds)
    return client

# Function to upload waiver wire data
def upload_waiver_data(df, sheet_name):
    client = authenticate_google_sheets()
    
    try:
        sheet = client.open(sheet_name).worksheet("Waiver Wire")  # 🔹 Ensure the tab is named correctly
    except gspread.exceptions.WorksheetNotFound:
        print(f"ERROR: 'Waiver Wire' tab not found in {sheet_name}.")
        return

    sheet.clear()  # Clear old data
    sheet.update([df.columns.values.tolist()] + df.values.tolist())  # Upload new data
    print(f"Successfully uploaded {len(df)} players to {sheet_name} - Waiver Wire.")

# Test
if __name__ == "__main__":
    dummy_data = pd.DataFrame({"Player": ["Test Player"], "Team": ["LAL"], "Position": ["SG"], "Waiver Increase": ["+5.6"]})
    upload_waiver_data(dummy_data, "NBA Fantasy Waiver Wire")
