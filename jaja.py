import time
import json
import pandas as pd
import streamlit as st
import tempfile
import shutil
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# Function to get match data and save to CSV
def get_match_data_and_save_csv(match_id, file_name):
    # Create a temporary directory for user data
    user_data_dir = tempfile.mkdtemp()

    # Set up Selenium WebDriver options
    options = webdriver.ChromeOptions()
    options.add_argument(f"--user-data-dir={user_data_dir}")  # Set a unique user data directory
    options.set_capability("goog:loggingPrefs", {"performance": "ALL", "browser": "ALL"})

    # Initialize the WebDriver
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    driver.set_page_load_timeout(10)

    try:
        driver.get(f"https://www.scoresway.com/en_GB/soccer/superliga-2024-2025/1zqurbs9rmwtk30us5y1v1rtg/match/view/{match_id}/player-stats")
    except Exception as e:
        st.error(f"Failed to load page: {e}")
        driver.quit()
        return

    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    
    # Allow time for the logs to populate
    time.sleep(1.5)
    
    logs = driver.get_log('performance')
    match_log = None

    for log in logs:
        if f'{match_id}?_rt=c&_lcl=en&_fmt=jsonp' in log['message']:
            match_log = log['message']
            break

    if match_log is None:
        st.error(f"No log found for match ID {match_id}")
        driver.quit()
        return

    try:
        request_id_start = match_log.find('"requestId":"') + len('"requestId":"')
        request_id_end = match_log.find('"', request_id_start)
        request_id = match_log[request_id_start:request_id_end]

        response = driver.execute_cdp_cmd('Network.getResponseBody', {'requestId': request_id})

        with open(file_name, 'w') as f:
            json.dump(response, f)

        with open(file_name, 'r') as f:
            data = json.load(f)

        body_content = data['body']
        start_index = body_content.find('(')
        end_index = body_content.rfind(')')
        json_data = body_content[start_index + 1:end_index]

        match_details = json.loads(json_data)
        live_data = match_details['liveData']
        live_data_flat = pd.json_normalize(live_data['event'])
        live_data_flat.to_csv(file_name, index=False)
        st.success(f"CSV file {file_name} saved successfully!")
    except Exception as e:
        st.error(f"An error occurred while processing the match: {e}")
    finally:
        driver.quit()
        # Clean up the temporary user data directory
        shutil.rmtree(user_data_dir)

# Streamlit UI
st.title('Soccer Match Data Extractor')

# Get match ID from user
match_id = st.text_input("Enter Match ID", "djkc8rfolq78jxkqouq6btc7o")

# Input for file name
file_name = st.text_input("Enter Filename for CSV", "match_data.csv")

if st.button("Get Match Data"):
    if match_id and file_name:
        with st.spinner("Fetching data..."):
            get_match_data_and_save_csv(match_id, file_name)
    else:
        st.warning("Please enter a valid match ID and file name.")
