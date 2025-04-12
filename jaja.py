import streamlit as st
import time
import json
import pandas as pd
import matplotlib.font_manager as fm
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import tempfile
import os

# Function to set up the WebDriver with unique user data directory
def create_driver():
    # Create a temporary directory for Chrome's user data
    temp_dir = tempfile.mkdtemp()
    
    # Set up Chrome options
    options = webdriver.ChromeOptions()
    options.set_capability("goog:loggingPrefs", {"performance": "ALL", "browser": "ALL"})
    options.add_argument(f'--user-data-dir={temp_dir}')  # Specify the unique user data directory
    options.add_argument('--no-sandbox')  # Avoid sandbox issues in cloud environments
    options.add_argument('--headless')  # Run Chrome in headless mode (no GUI)
    
    # Create and return the WebDriver
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    driver.set_page_load_timeout(10)
    
    return driver

# Function to get match data and save it to a CSV
def get_match_data_and_save_csv(driver, match_id, file_name):
    try:
        driver.get(f"https://www.scoresway.com/en_GB/soccer/superliga-2024-2025/1zqurbs9rmwtk30us5y1v1rtg/match/view/{match_id}/player-stats")
    except:
        st.error("Error loading the page")
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
        return

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

# Streamlit app
st.title("Soccer Match Data Scraper")

# Input field for match ID
match_id = st.text_input("Enter Match ID", 'djkc8rfolq78jxkqouq6btc7o')

# File name input
file_name = st.text_input("Enter File Name to Save Data", 'match_data.csv')

# Button to trigger data scraping
if st.button("Get Match Data"):
    if not match_id:
        st.error("Please enter a valid Match ID.")
    elif not file_name:
        st.error("Please enter a valid file name.")
    else:
        driver = create_driver()
        get_match_data_and_save_csv(driver, match_id, file_name)
        driver.quit()

        # Provide the file for download
        with open(file_name, "rb") as file:
            st.download_button(
                label="Download CSV File",
                data=file,
                file_name=file_name,
                mime="text/csv"
            )

# Optionally, load custom fonts
font_path = "Panton Light.otf"
font_pathh = "Panton Regular.otf"
font_pathhh = "Panton Bold.otf"
font_pathhhh = "Panton ExtraBold.otf"

# Load the fonts using FontProperties
custom_font = fm.FontProperties(fname=font_path)
custom_fontt = fm.FontProperties(fname=font_pathh)
custom_fonttt = fm.FontProperties(fname=font_pathhh)
custom_fontttt = fm.FontProperties(fname=font_pathhhh)
