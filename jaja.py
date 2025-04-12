import matplotlib.pyplot as plt
from selenium import webdriver
import streamlit as st
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager # version 4.0.1
from selenium.webdriver.chrome.options import Options
import json
import time
import os
import logging
import requests
import matplotlib.patches as patches
import matplotlib.font_manager as fm
from scipy.interpolate import interp1d
import urllib.request
from PIL import Image
import numpy as np
import matplotlib.patheffects as path_effects
from matplotlib.patches import FancyArrowPatch
from matplotlib.font_manager import FontProperties
import requests
import pandas as pd
from mplsoccer.pitch import Pitch
from mplsoccer.pitch import VerticalPitch
from scipy.interpolate import interp1d
import urllib.request
from PIL import Image
import numpy as np
import json
import numpy as np
from mplsoccer.pitch import Pitch, VerticalPitch  # Added VerticalPitch
from scipy.stats import gaussian_kde
import matplotlib.colors as mcolors
from io import BytesIO

home_team_id = '9qsmopgutr7ut5g6workk8w4i'
away_team_id = '5rz9enoyknpg8ji78za5b82p0'

font_path = "Panton Light.otf"
font_pathh = "Panton Regular.otf"
font_pathhh = "Panton Bold.otf"
font_pathhhh = "Panton ExtraBold.otf"

# Load the font using FontProperties
custom_font = fm.FontProperties(fname=font_path)
custom_fontt = fm.FontProperties(fname=font_pathh)
custom_fonttt = fm.FontProperties(fname=font_pathhh)
custom_fontttt = fm.FontProperties(fname=font_pathhhh)

# Define the run functions
def run():

    # Set up Selenium WebDriver options
    options = webdriver.ChromeOptions()
    options.set_capability(
        "goog:loggingPrefs", {"performance": "ALL", "browser": "ALL"}
    )
    
    # Initialize the WebDriver
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    driver.set_page_load_timeout(10)
    
    # Function to get match data and save to CSV
    def get_match_data_and_save_csv(file_name):
        try:
            driver.get("https://www.scoresway.com/en_GB/soccer/superliga-2024-2025/1zqurbs9rmwtk30us5y1v1rtg/match/view/djkc8rfolq78jxkqouq6btc7o/player-stats")
        except:
            pass
        
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        
        # Allow time for the logs to populate
        time.sleep(1.5)
        
        logs = driver.get_log('performance')
    
        match_log = None
        for log in logs:
            if '?_rt=c&_lcl=en&_fmt=jsonp' in log['message']:
                match_log = log['message']
                break
    
        if match_log is None:
            print("No log found for match ID")
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
        print(f"CSV file {file_name} saved successfully!")
    
    # Process the match ID for the given fixture description
    file_name = 'sldk.csv'
    get_match_data_and_save_csv(file_name)
    time.sleep(1.5)  # Add a delay between processing each match
    
    # Close the driver
    driver.quit()
    
    # Define the CSV file path
    csv = 'sldk.csv'
    
    # Define the contestantIds for the two teams
    team1_contestantId = home_team_id
    team2_contestantId = away_team_id
    
    # Provided xT data for the 8x12 grid
    xT_data = np.array([
        [0.00638303,0.00779616,0.00844854,0.00977659,0.01126267,0.01248344,0.01473596,0.0174506,0.02122129,0.02756312,0.03485072,0.0379259],
        [0.00750072,0.00878589,0.00942382,0.0105949,0.01214719,0.0138454,0.01611813,0.01870347,0.02401521,0.02953272,0.04066992,0.04647721],
        [0.0088799,0.00977745,0.01001304,0.01110462,0.01269174,0.01429128,0.01685596,0.01935132,0.0241224,0.02855202,0.05491138,0.06442595],
        [0.00941056,0.01082722,0.01016549,0.01132376,0.01262646,0.01484598,0.01689528,0.0199707,0.02385149,0.03511326,0.10805102,0.25745362],
        [0.00941056,0.01082722,0.01016549,0.01132376,0.01262646,0.01484598,0.01689528,0.0199707,0.02385149,0.03511326,0.10805102,0.25745362],
        [0.0088799,0.00977745,0.01001304,0.01110462,0.01269174,0.01429128,0.01685596,0.01935132,0.0241224,0.02855202,0.05491138,0.06442595],
        [0.00750072,0.00878589,0.00942382,0.0105949,0.01214719,0.0138454,0.01611813,0.01870347,0.02401521,0.02953272,0.04066992,0.04647721],
        [0.00638303,0.00779616,0.00844854,0.00977659,0.01126267,0.01248344,0.01473596,0.0174506,0.02122129,0.02756312,0.03485072,0.0379259]
    ])
    
    # Load the pass data from the CSV file
    pass_df = pd.read_csv(csv)
    
    first_type18_team1 = pass_df.loc[(pass_df['contestantId'] == team1_contestantId) & (pass_df['typeId'] == 18), 'timeMin'].min()
    first_type18_team2 = pass_df.loc[(pass_df['contestantId'] == team2_contestantId) & (pass_df['typeId'] == 18), 'timeMin'].min()
    
    # Exclude passes for each contestantId from the point of the first typeId 18 event onwards
    pass_df = pass_df[~((pass_df['contestantId'] == team1_contestantId) & (pass_df['timeMin'] >= first_type18_team1))]
    pass_df = pass_df[~((pass_df['contestantId'] == team2_contestantId) & (pass_df['timeMin'] >= first_type18_team2))]
    
    # Convert relevant columns to numeric data types
    pass_df['x'] = pd.to_numeric(pass_df['x'], errors='coerce')
    pass_df['y'] = pd.to_numeric(pass_df['y'], errors='coerce')
    
    # Initialize end coordinates
    pass_df['endX'] = 0.0
    pass_df['endY'] = 0.0
    
    # Calculate endX and endY using the provided code
    for i, pass_action in pass_df.iterrows():
        qualifier_str = pass_action['qualifier']
        qualifiers = json.loads(qualifier_str.replace("'", '"'))
        for qualifier in qualifiers:
            if qualifier['qualifierId'] == 140:
                pass_df.at[i, 'endX'] = float(qualifier['value'])
            elif qualifier['qualifierId'] == 141:
                pass_df.at[i, 'endY'] = float(qualifier['value'])
    
    # Filter rows where typeId is 1 and outcome is 1
    filtered_df = pass_df[(pass_df['typeId'] == 1) & (pass_df['outcome'] == 1)]
    
    # List of qualifier IDs to exclude (corner kick types)
    exclude_qualifier_ids = [5, 6, 107, 124]
    
    # Define a function to check if a pass is a corner kick
    def is_corner(row):
        qualifiers = json.loads(row['qualifier'].replace("'", '"'))
        return any(q['qualifierId'] in exclude_qualifier_ids for q in qualifiers)
    
    # Apply the is_corner function to exclude corner kicks
    filtered_df = filtered_df[~filtered_df.apply(is_corner, axis=1)]
    
    # Function to get xT value based on x and y coordinates
    def get_xT_value(x, y):
        row_idx = int((y / 100) * 8) if y < 100 else 7
        col_idx = int((x / 100) * 12) if x < 100 else 11
        return xT_data[row_idx, col_idx]
    
    # Add xT column to the filtered DataFrame
    filtered_df['start_xT'] = filtered_df.apply(lambda row: get_xT_value(row['x'], row['y']), axis=1)
    filtered_df['end_xT'] = filtered_df.apply(lambda row: get_xT_value(row['endX'], row['endY']), axis=1)
    filtered_df['xT_difference'] = filtered_df['end_xT'] - filtered_df['start_xT']
    
    # Replace negative xT difference with zeros
    filtered_df['xT_difference'] = filtered_df['xT_difference'].clip(lower=0)
    
    # Print the total xT values, average positions, and team for each player
    for player, group in filtered_df.groupby('playerName'):
        total_xT = group['xT_difference'].sum()
        average_x = group['x'].mean()
        average_y = group['y'].mean()
        team = group['contestantId'].iloc[0]  # Get the team from the first row of the group
        # Extract player initials
        initials = ''.join([name[0].upper() for name in player.split()])
        print(f"Player: {initials} | Team: {team} | Total xT: {total_xT} | Average Position: (x={average_x}, y={average_y})")
    
    # Group players by contestantId and calculate average position and xT sum value
    player_summary = filtered_df.groupby(['contestantId', 'playerName']).agg({'x': 'mean', 'y': 'mean', 'xT_difference': 'sum'}).reset_index()
    
    # Create DataFrames for each team
    team1_df = player_summary[player_summary['contestantId'] == team1_contestantId].copy()
    team2_df = player_summary[player_summary['contestantId'] == team2_contestantId].copy()
    
    # Flip Team 1's coordinates
    team1_indices = filtered_df['contestantId'] == team1_contestantId
    filtered_df.loc[team1_indices, 'x'] = 100 - filtered_df.loc[team1_indices, 'x']
    filtered_df.loc[team1_indices, 'y'] = 100 - filtered_df.loc[team1_indices, 'y']
    filtered_df.loc[team1_indices, 'endX'] = 100 - filtered_df.loc[team1_indices, 'endX']
    filtered_df.loc[team1_indices, 'endY'] = 100 - filtered_df.loc[team1_indices, 'endY']
    
    # Group players by contestantId and calculate pass frequency
    pass_frequency_dict = {}
    
    for _, group in filtered_df.groupby('contestantId'):
        for i in range(len(group) - 1):
            passer = group.iloc[i]['playerName']
            receiver = group.iloc[i + 1]['playerName']
            pass_key = (passer, receiver)
            if pass_key in pass_frequency_dict:
                pass_frequency_dict[pass_key] += 1
            else:
                pass_frequency_dict[pass_key] = 1
    
    # Calculate pass counts for each player
    pass_counts = filtered_df['playerName'].value_counts()
    
    # Create figure and axes for Team 1
    fig1, ax1 = plt.subplots(figsize=(6, 6), dpi=200)
    pitch1 = Pitch(pitch_type='opta', pitch_color='#2E2E2A', line_color='#616A67')
    pitch1.draw(ax=ax1)
    ax1.set_title(f"Home Pass Network & xT via Passes (1' - {first_type18_team1}')", y=0.96, fontproperties=custom_fonttt, fontsize=14, color='white')
    
    # Plot Team 1 data with circle sizes based on pass counts
    scatter1 = ax1.scatter(100 - team1_df['x'], 100 - team1_df['y'], c=team1_df['xT_difference'], cmap='summer_r',
                           s=500,  # Scale the circle size based on pass counts
                           edgecolors='black', alpha=1, zorder=2)
    
    # Plot lines between players based on pass frequency
    for pass_key, pass_count in pass_frequency_dict.items():
        passer, receiver = pass_key
        if passer in team1_df['playerName'].tolist() and receiver in team1_df['playerName'].tolist():
            passer_data = filtered_df[(filtered_df['playerName'] == passer) & (filtered_df['contestantId'] == team1_contestantId)]
            receiver_data = filtered_df[(filtered_df['playerName'] == receiver) & (filtered_df['contestantId'] == team1_contestantId)]
            if not passer_data.empty and not receiver_data.empty:
                x_start = passer_data['x'].mean()
                y_start = passer_data['y'].mean()
                x_end = receiver_data['x'].mean()
                y_end = receiver_data['y'].mean()
                ax1.plot([x_start, x_end], [y_start, y_end], color='#EEEDE0', linewidth=pass_count / 3,
                         alpha=min(1, pass_count / 15), zorder=1)
    
    # Annotate player initials at the center of the circles with a black outline
    for idx, player in team1_df.iterrows():
        initials = ''.join([name[0].upper() for name in player['playerName'].split()])
        pass_count = pass_counts[player['playerName']]
        fontsize = 10
        alpha = 1
        ax1.annotate(initials, (100 - player['x'], 100 - player['y']), color='black', fontsize=fontsize, alpha=alpha, weight='bold', ha='center', va='center')
    
    # Add colorbar below the pitch for Team 1
    cbar1 = fig1.colorbar(scatter1, ax=ax1, shrink=0.2, orientation='horizontal', pad=0, aspect=5)
    
    # Create figure and axes for Team 2
    fig2, ax2 = plt.subplots(figsize=(6, 6), dpi=200)
    pitch2 = Pitch(pitch_type='opta', pitch_color='#2E2E2A', line_color='#616A67')
    pitch2.draw(ax=ax2)
    ax2.set_title(f"Away Pass Network & xT via Passes (1' - {first_type18_team2}')", y=0.96, fontproperties=custom_fonttt, fontsize=14, color='white')
    
    # Plot Team 2 data with circle sizes based on pass counts
    scatter2 = ax2.scatter(team2_df['x'], team2_df['y'], c=team2_df['xT_difference'], cmap='summer_r',
                           s=500,  # Scale the circle size based on pass counts
                           edgecolors='black', alpha=1, zorder=2)
    
    # Plot lines between players based on pass frequency for Team 2
    for pass_key, pass_count in pass_frequency_dict.items():
        passer, receiver = pass_key
        if passer in team2_df['playerName'].tolist() and receiver in team2_df['playerName'].tolist():
            passer_data = filtered_df[(filtered_df['playerName'] == passer) & (filtered_df['contestantId'] == team2_contestantId)]
            receiver_data = filtered_df[(filtered_df['playerName'] == receiver) & (filtered_df['contestantId'] == team2_contestantId)]
            if not passer_data.empty and not receiver_data.empty:
                x_start = passer_data['x'].mean()
                y_start = passer_data['y'].mean()
                x_end = receiver_data['x'].mean()
                y_end = receiver_data['y'].mean()
                ax2.plot([x_start, x_end], [y_start, y_end], color='#EEEDE0', linewidth=pass_count / 3,
                         alpha=min(1, pass_count / 15), zorder=1)
    
    # Annotate player initials at the center of the circles with a black outline
    for idx, player in team2_df.iterrows():
        initials = ''.join([name[0].upper() for name in player['playerName'].split()])
        pass_count = pass_counts[player['playerName']]
        fontsize = 10
        alpha = 1
        ax2.annotate(initials, (player['x'], player['y']), color='black', fontsize=fontsize, alpha=alpha, weight='bold', ha='center', va='center')
    
    # Add colorbar below the pitch for Team 2
    cbar2 = fig2.colorbar(scatter2, ax=ax2, shrink=0.2, orientation='horizontal', pad=0, aspect=5)
    
    # Add labels to colorbars
    cbar1.set_label(' Low xT                             High xT', labelpad=-10, color='white', fontproperties=custom_fonttt, fontsize=12, alpha=0.8)
    cbar1.ax.xaxis.set_label_position('top')
    cbar1.ax.xaxis.label.set_color('white')
    
    cbar2.set_label(' Low xT                              High xT', labelpad=-10, color='white', fontproperties=custom_fonttt, fontsize=12, alpha=0.8)
    cbar2.ax.xaxis.set_label_position('top')
    cbar2.ax.xaxis.label.set_color('white')
    
    # Set the facecolor of fig1 to match the pitch color
    fig1.set_facecolor('#2E2E2A')
    
    # Set the facecolor of fig2 to match the pitch color
    fig2.set_facecolor('#2E2E2A')
    
    # Remove ticks and labels from colorbar for Team 1
    cbar1.ax.set_xticks([])
    cbar1.ax.set_xticklabels([])
    
    # Remove ticks and labels from colorbar for Team 2
    cbar2.ax.set_xticks([])
    cbar2.ax.set_xticklabels([])
    
    # Display the plot in the Streamlit app
    st.pyplot(fig1)
    st.pyplot(fig2)

# Finally, call thee run function to execute the app
if __name__ == "__main__":
    run()
