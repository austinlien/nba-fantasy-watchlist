import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from upload_waiver_data import upload_waiver_data  # Upload function

WAIVER_WIRE_URL = "https://www.fantasysp.com/waiver-wire/basketball"

def scrape_waiver_wire():
    print(f"🔍 Launching Chrome WebDriver to fetch waiver wire data...")

    # Set up Chrome options for headless scraping
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run Chrome in headless mode
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # Initialize WebDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        # Load the website
        driver.get(WAIVER_WIRE_URL)
        time.sleep(5)  # Wait for JavaScript to load content

        # Find the waiver wire table
        table = driver.find_element(By.TAG_NAME, "table")
        rows = table.find_elements(By.TAG_NAME, "tr")[1:]  # Skip header row

        data = []
        for row in rows:
            cols = row.find_elements(By.TAG_NAME, "td")
            if len(cols) < 5:
                continue  # Skip incomplete rows

            player = cols[1].text.strip()
            team = cols[2].text.strip()
            position = cols[3].text.strip()
            waiver_increase = cols[4].text.strip()

            data.append([player, team, position, waiver_increase])

        driver.quit()  # Close the browser

        # Convert to DataFrame
        df = pd.DataFrame(data, columns=["Player", "Team", "Position", "Waiver Increase", "Percent Change", "Ownage"])
        
        # 🔍 **Check if data is empty**
        if df.empty:
            print("ERROR: Waiver wire data is EMPTY in `scrape_waiver_wire()` ")
        else:
            print(f"Successfully scraped {len(df)} players.")
            print(df.head())  # Print first few rows for debugging

        # Save locally as CSV
        df.to_csv("waiver_wire_data.csv", index=False)

        # Upload to Google Sheets
        upload_waiver_data(df, "NBA Fantasy Waiver Wire")

        return df  # Ensure function returns DataFrame

    except Exception as e:
        print(f"Error during scraping: {e}")
        driver.quit()
        return None  # Return None if scraping fails

        
    

# Run script
if __name__ == "__main__":
    scrape_waiver_wire()
