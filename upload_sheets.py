import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

# Auth with Google Sheets
def authenticate_google_sheets():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("nba-fantasy-sheets.json", scope)
    client = gspread.authorize(creds)
    return client

# Upload to Google Sheets (Preserves Waiver Wire Stats)
def upload_to_sheets(new_df, sheet_name):
    client = authenticate_google_sheets()
    sheet = client.open(sheet_name).sheet1

    # Get Existing Sheet Data (Including Waiver Wire Stats)
    existing_data = sheet.get_all_values()
    
    if not existing_data or len(existing_data) == 0:
        print("⚠️ Google Sheet is EMPTY. Uploading all data from scratch.")
        data = [new_df.columns.values.tolist()] + new_df.values.tolist()  # Add column headers
        sheet.update(data)
        print(f"✅ Successfully repopulated {sheet_name} from scratch!")
        return

    # Convert Existing Data to DataFrame (Keep Waiver Wire Stats)
    existing_df = pd.DataFrame(existing_data[1:], columns=existing_data[0])  # Skip header row

    # Normalize Column Names (Lowercase, No Spaces)
    existing_df.columns = existing_df.columns.str.strip().str.lower()
    new_df.columns = new_df.columns.str.strip().str.lower()

    # Ensure "player" and "waiver increase" columns exist
    if "player" not in existing_df.columns:
        print("⚠️ Warning: 'Player' column missing in existing data. Uploading from scratch.")
        data = [new_df.columns.values.tolist()] + new_df.values.tolist()
        sheet.update(data)
        print(f"✅ Successfully restored {sheet_name}!")
        return

    if "player" not in new_df.columns:
        print("❌ Error: 'Player' column is missing in the last 3-game stats data.")
        return

    if "waiver increase" not in existing_df.columns:
        print("⚠️ Warning: 'Waiver Increase' column is missing. Check Google Sheets!")

    # Ensure All Player Names Are Strings
    existing_df["player"] = existing_df["player"].astype(str).str.strip()
    new_df["player"] = new_df["player"].astype(str).str.strip()

    # Round to 1 Decimal Place
    numeric_cols = new_df.select_dtypes(include=["float64", "int64"]).columns
    new_df[numeric_cols] = new_df[numeric_cols].round(1)

    # Merge Waiver Wire & Last 3 Game Stats (Keep Waiver Wire Data)
    merged_df = existing_df.merge(new_df, on="player", how="left", suffixes=("", "_new"))

    # Keep Waiver Increase Values (If They Exist)
    if "waiver increase_new" in merged_df.columns:
        merged_df["waiver increase"] = merged_df["waiver increase_new"].fillna(merged_df["waiver increase"])
        merged_df.drop(columns=["waiver increase_new"], inplace=True)

    # Remove Duplicate `_x` and `_y` Columns
    for col in merged_df.columns:
        if col.endswith("_new"):
            original_col = col.replace("_new", "")
            merged_df[original_col] = merged_df[col]  # Replace original values with new
            merged_df.drop(columns=[col], inplace=True)  # Remove duplicate columns

    # Upload Merged Data Back to Google Sheets
    data = [merged_df.columns.values.tolist()] + merged_df.values.tolist()
    sheet.update(data)
    print(f"✅ Successfully merged waiver increases & last 3-game stats into {sheet_name}!")
