import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Auth Google Sheets
def authenticate_google_sheets():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("nba-fantasy-sheets.json", scope)
    client = gspread.authorize(creds)
    return client

# est Google Sheets Connection
def test_connection(sheet_name):
    try:
        client = authenticate_google_sheets()
        sheet = client.open(sheet_name)  # Try to open the sheet
        print(f"✅ Successfully connected to: {sheet_name}")
        return True
    except Exception as e:
        print(f"ERROR: Failed to connect to Google Sheets. Check API credentials!\n{e}")
        return False

# Run Test
if __name__ == "__main__":
    test_connection("NBA Fantasy Waiver Wire")  # Replace with your sheet name
