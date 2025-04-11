import matplotlib.pyplot as plt
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager # version 4.0.1
from selenium.webdriver.chrome.options import Options
import json
import time
import streamlit
import streamlit as st
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

# Title for the Streamlit app
st.title('Fetch Match Data from Fotmosb')

# User input for the Fotmob match URL
fotmob_url = st.text_input("Enter Fotmob Match URL", 'https://www.fotmob.com/en-GB/matches/agf-vs-brondby-if/2aozua#4757611')
submit_button = st.button("Fetch Match Data")

# Stop further execution until the button is clicked
if not submit_button:
    st.stop()

font_path = "Panton Light.otf"
font_pathh = "Panton Regular.otf"
font_pathhh = "Panton Bold.otf"
font_pathhhh = "Panton ExtraBold.otf"

# Load the font using FontProperties
custom_font = fm.FontProperties(fname=font_path)
custom_fontt = fm.FontProperties(fname=font_pathh)
custom_fonttt = fm.FontProperties(fname=font_pathhh)
custom_fontttt = fm.FontProperties(fname=font_pathhhh)

# Set up logging
logging.basicConfig(filename='match_data_fetch.log', level=logging.INFO)

def fetch_match_data():
    match_url = fotmob_url
    api_request_fragment = 'https://www.fotmob.com/api/matchDetails?matchId='

    # Set up Selenium WebDriver options
    options = Options()
    options.add_argument('--headless')  # Run in headless mode
    options.add_argument('--disable-gpu')  # Disable GPU acceleration
    options.set_capability("goog:loggingPrefs", {"performance": "ALL"})  # Enable performance logging

    # Initialize the WebDriver
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    driver.set_page_load_timeout(10)

    try:
        # Open the match page
        driver.get(match_url)
        
        # Scroll to trigger network logs
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(5)  # Allow time for logs to populate

        # Retrieve performance logs
        logs = driver.get_log('performance')

        # Search for the desired API request in logs
        match_log = None
        for log in logs:
            if api_request_fragment in log['message']:
                match_log = log['message']
                break

        if match_log is None:
            logging.info("No log found for match ID.")
            return None

        # Extract the request ID from the log
        request_id_start = match_log.find('"requestId":"') + len('"requestId":"')
        request_id_end = match_log.find('"', request_id_start)
        request_id = match_log[request_id_start:request_id_end]

        # Use the request ID to get the response body
        response = driver.execute_cdp_cmd('Network.getResponseBody', {'requestId': request_id})

        # Parse the JSON response
        json_data = json.loads(response['body'])
        return json_data

    except Exception as e:
        logging.error(f"Error fetching data for match ID. Exception: {e}")
        return None

    finally:
        driver.quit()  # Clean up WebDriver

# Fetch data for a specific match
match_data = fetch_match_data()

# Check if match data was fetched successfully
if match_data:
    # Extract stats data
    stats_dict = {}
    if 'content' in match_data and 'stats' in match_data['content']:
        stats_data = match_data['content']['stats']
        
        # Extract titles and values from stats_data
        if 'Periods' in stats_data:
            periods = stats_data['Periods']

            # Check if 'All' key exists
            if 'All' in periods:
                all_period = periods['All']

                # Check if 'stats' key exists
                if 'stats' in all_period:
                    stats = all_period['stats']

                    # Iterate over each item in 'stats'
                    for item in stats:
                        # Check if 'stats' key exists in the current item
                        if 'stats' in item:
                            inner_stats = item['stats']

                            # Iterate over each inner item in 'stats'
                            for inner_item in inner_stats:
                                # Check if both 'title' and 'stats' keys exist in the current inner item
                                if 'title' in inner_item and 'stats' in inner_item:
                                    # Extract the title and corresponding stats
                                    title = inner_item['title']
                                    stats_values = inner_item['stats']

                                    # Store the title and stats values in the stats_dict
                                    stats_dict[title] = stats_values



    # Extract shot data
    shots = match_data.get('content', {}).get('shotmap', {}).get('shots', [])
    home_team_id = match_data.get('general', {}).get('homeTeam', {}).get('id')
    away_team_id = match_data.get('general', {}).get('awayTeam', {}).get('id')

    # Create DataFrame from shot data if available
    if shots:
        df = pd.DataFrame(shots)

    # Fetch momentum data
    momentum_data = []
    if 'content' in match_data and 'matchFacts' in match_data['content']:
        match_facts = match_data['content']['matchFacts']
        if 'momentum' in match_facts and 'main' in match_facts['momentum']:
            momentum_data = match_facts['momentum']['main'].get('data', [])



# Create a pitch
pitch = Pitch(pitch_type='uefa', pitch_color='#2E2E2A', line_color='#616A67')

# Increase figure size
fig, ax = pitch.draw(figsize=(10, 8))

# Plot shots
for index, row in df.iterrows():
    xG = row['expectedGoals']
    xGot = row['expectedGoalsOnTarget']
    if pd.notnull(xG):  # Check if xG value is not null
        if row['eventType'] == 'Goal':
            if row['shotType'] == 'own':
                marker = 's'  # Square marker for own goals
            else:
                marker = 'o'  # Circle marker for regular goals
            color = '#47B745'
            edgecolor = 'black'
            zorder = 3
        elif xGot > 0:
            color = '#C8C329'
            edgecolor = 'black'
            zorder = 2
            marker = 'o'  # Circle marker for shots on target
        else:
            color = '#C82929'
            edgecolor = 'black'
            zorder = 1
            marker = 'o'  # Circle marker for other shots

        # Determine if the shot belongs to the home team or the away team
        if row['teamId'] == home_team_id:
            x_coordinate = 105 - row['x']  # Flip x-coordinate for home team shots
            y_coordinate = 68 - row['y']  # Flip y-coordinate for home team shots
        else:
            x_coordinate = row['x']  # Keep x-coordinate unchanged for away team shots
            y_coordinate = row['y']  # Keep y-coordinate unchanged for away team shots

        ax.scatter(x_coordinate, y_coordinate, linewidth=1.5, color=color, edgecolor=edgecolor,
                   s=xG * 900, alpha=0.8, zorder=zorder, label=f"{row['teamId']} Shots", marker=marker)
    else:
        # Handle case where xG value is null (e.g., own goal)
        # Mark the location with a red square marker
        if row['teamId'] == home_team_id:
            x_coordinate = 105 - row['x']  # Flip x-coordinate for home team shots
            y_coordinate = 68 - row['y']  # Flip y-coordinate for home team shots
        else:
            x_coordinate = row['x']  # Keep x-coordinate unchanged for away team shots
            y_coordinate = row['y']  # Keep y-coordinate unchanged for away team shots

        ax.scatter(x_coordinate, y_coordinate, linewidth=2, color='#BD1A64', edgecolor='black', s=150,
                   alpha=0.8, zorder=3, marker='X')

# Extract team colors
home_team_colors = match_data.get('general', {}).get('teamColors', {}).get('darkMode', {}).get('home')
away_team_colors = match_data.get('general', {}).get('teamColors', {}).get('darkMode', {}).get('away')

# Extract team colors
home_team_name = match_data.get('general', {}).get('homeTeam', {}).get('name', {})
away_team_name = match_data.get('general', {}).get('awayTeam', {}).get('name', {})
match_score = match_data.get('header', {}).get('status', {}).get('scoreStr', {})
league_name = match_data.get('general', {}).get('parentLeagueName')
round_name = match_data.get('general', {}).get('parentLeagueSeason')

# Filter out entries for minutes 45.5 and 90.5 from momentum data
momentum_data_filtered = [moment for moment in momentum_data if moment['minute'] not in [45.5, 90.5]]

# Plot momentum
if momentum_data_filtered:
    minute_values = [moment['minute'] for moment in momentum_data_filtered]
    momentum_values = [moment['value'] for moment in momentum_data_filtered]

    # Interpolate momentum data
    interp_func = interp1d(minute_values, momentum_values, kind='linear')

    # Define x values for interpolation
    x_interp = range(min(minute_values), int(max(minute_values)) + 1)

    # Scale factor for momentum visualization
    momentum_scale_factor = 30

    # Add an offset of 6.5 to the x values for momentum visualization
    x_offset = 6.5

    # Plot bars for momentum at every minute
    for minute, momentum in zip(minute_values, momentum_values):
        # Determine the color based on momentum direction
        if momentum >= 0:
            bar_color = home_team_colors
            bar_height = momentum / momentum_scale_factor
            y_coord = 0
        else:
            bar_color = away_team_colors
            bar_height = abs(momentum) / momentum_scale_factor
            y_coord = -bar_height  # Adjust y-coordinate for the away team

        # Plot the bar with black edge color
        ax.bar(minute + x_offset, bar_height, color=bar_color, width=1, alpha=1, bottom=y_coord, edgecolor='black', zorder=20)

    # Set y-limits to ensure bars fit between the two lines
    ax.set_ylim(-10, 10)

    # Add a horizontal line at y-coordinate -10
    ax.hlines(y=-3.475, xmin=0 + x_offset, xmax=91 + x_offset, color='white', linewidth=1, alpha=0.6)

    # Add a horizontal line at y-coordinate +10
    ax.hlines(y=3.475, xmin=0 + x_offset, xmax=91 + x_offset, color='white', linewidth=1, alpha=0.6)

    # Add the text 'Momentum' centrally below the line
    ax.text(13.25, 5.5, 'Momentum', color='white', fontsize=16, ha='center', va='center', fontproperties=custom_fonttt, alpha=0.7)
    ax.text(0 + x_offset, -6.75, "1'", color='white', fontsize=14, ha='center', va='center', fontproperties=custom_fonttt, alpha=0.7)
    ax.text(46.75 + x_offset, -6.75, "46'", color='white', fontsize=14, ha='center', va='center', fontproperties=custom_fonttt, alpha=0.7)
    ax.text(91 + x_offset, -6.75, "90'", color='white', fontsize=14, ha='center', va='center', fontproperties=custom_fonttt, alpha=0.7)


# Set figure face color
fig.set_facecolor('#2E2E2A')

# Set the y-axis limit to create space below the momentum visualization
ax.set_ylim(bottom=-8)
ax.set_ylim(top=75)

# Define common fontsize and fontproperties
common_fontsize = 17
common_fontproperties = custom_fonttt

# Define colors based on value comparison
def color_by_magnitude(value1, value2):
    if value1 > value2:
        return 'white', 'white'
    elif value1 < value2:
        return 'white', 'white'
    else:
        return 'white', 'white'

# Define the text effect
text_effect = [path_effects.Stroke(linewidth=3.5, foreground='black'), path_effects.Normal()]

# Extract ball possession data
ball_possession_home = stats_dict['Ball possession'][0]
ball_possession_away = stats_dict['Ball possession'][1]

# Determine colors for ball possession values
possession_color_home, possession_color_away = color_by_magnitude(ball_possession_home, ball_possession_away)

# Add text annotations for ball possession values with colors and text effect
ax.text(39, 51, f'{ball_possession_home}%', color=possession_color_home, ha='center', fontsize=common_fontsize, fontproperties=common_fontproperties, path_effects=text_effect)
ax.text(66, 51, f'{ball_possession_away}%', color=possession_color_away, ha='center', fontsize=common_fontsize, fontproperties=common_fontproperties, path_effects=text_effect)

# Extract accurate passes data
accurate_passes_home_formatted = stats_dict['Passes'][0]
accurate_passes_away_formatted = stats_dict['Passes'][1]

# Determine colors for accurate passes values
passes_color_home, passes_color_away = color_by_magnitude(accurate_passes_home_formatted, accurate_passes_away_formatted)

# Add text annotations for accurate passes values with colors and text effect
ax.text(39, 43, f'{accurate_passes_home_formatted}', color=passes_color_home, ha='center', fontsize=common_fontsize, fontproperties=common_fontproperties, path_effects=text_effect)
ax.text(66, 43, f'{accurate_passes_away_formatted}', color=passes_color_away, ha='center', fontsize=common_fontsize, fontproperties=common_fontproperties, path_effects=text_effect)

####################

# Extract accurate passes data
accurate_corners_home_formatted = stats_dict['Corners'][0]
accurate_corners_away_formatted = stats_dict['Corners'][1]

# Determine colors for accurate passes values
corners_color_home, corners_color_away = color_by_magnitude(accurate_corners_home_formatted, accurate_corners_away_formatted)

# Add text annotations for accurate passes values with colors and text effect
ax.text(39, 35, f'{accurate_corners_home_formatted}', color=corners_color_home, ha='center', fontsize=common_fontsize, fontproperties=common_fontproperties, path_effects=text_effect)
ax.text(66, 35, f'{accurate_corners_away_formatted}', color=corners_color_away, ha='center', fontsize=common_fontsize, fontproperties=common_fontproperties, path_effects=text_effect)

####################


# Extract expected goals (xG) data
xG_home = stats_dict['Expected goals (xG)'][0]
xG_away = stats_dict['Expected goals (xG)'][1]

# Determine colors for xG values
xG_color_home, xG_color_away = color_by_magnitude(xG_home, xG_away)

# Add text annotations for xG values with colors and text effect
ax.text(39, 27, f'{xG_home}', color=xG_color_home, ha='center', fontsize=common_fontsize, fontproperties=common_fontproperties, path_effects=text_effect)
ax.text(66, 27, f'{xG_away}', color=xG_color_away, ha='center', fontsize=common_fontsize, fontproperties=common_fontproperties, path_effects=text_effect)


# Extract xG on target (xGOT) data
xGOT_home = stats_dict['xG on target (xGOT)'][0]
xGOT_away = stats_dict['xG on target (xGOT)'][1]

# Determine colors for xG on target (xGOT) values
xGOT_color_home, xGOT_color_away = color_by_magnitude(xGOT_home, xGOT_away)

# Add text annotations for xG on target (xGOT) values with colors and text effect
ax.text(39, 19, f'{xGOT_home}', color=xGOT_color_home, ha='center', fontsize=common_fontsize, fontproperties=common_fontproperties, path_effects=text_effect)
ax.text(66, 19, f'{xGOT_away}', color=xGOT_color_away, ha='center', fontsize=common_fontsize, fontproperties=common_fontproperties, path_effects=text_effect)

# Extract total shots data
total_shots_home = stats_dict['Total shots'][0]
total_shots_away = stats_dict['Total shots'][1]

# Determine colors for total shots values
shots_color_home, shots_color_away = color_by_magnitude(total_shots_home, total_shots_away)

# Add text annotations for total shots values with colors and text effect
ax.text(39, 11, f'{total_shots_home}', color=shots_color_home, ha='center', fontsize=common_fontsize, fontproperties=common_fontproperties, path_effects=text_effect)
ax.text(66, 11, f'{total_shots_away}', color=shots_color_away, ha='center', fontsize=common_fontsize, fontproperties=common_fontproperties, path_effects=text_effect)



# Define custom display names for the stats
stat_titles = ['Ball possession', 'Passes', 'Corners', 'Expected goals (xG)',
               'xG on target (xGOT)', 'Total shots']

# Replace the display names as needed
custom_display_names = ['POSSESSION', 'PASSES', 'CORNERS', 'xG',
                        'xGOT', 'SHOTS']

# Define y positions for the stat titles with a -5 difference between each
y_positions = [52, 52, 52, 52, 52, 52, 52, 52]
y_positions = [pos - 8 * i for i, pos in enumerate(y_positions)]

# Add stat titles with bounding box and custom display names
for title, custom_name, y_pos in zip(stat_titles, custom_display_names, y_positions):
    ax.text(52.5, y_pos, custom_name, color='white', fontproperties=custom_fonttt, path_effects=text_effect, fontsize=16, alpha=0.9, ha='center', va='center', zorder=20,
            bbox=dict(boxstyle="Round", pad=0, edgecolor='none', lw=0, facecolor='none', alpha=0))


######################

# Define a function to add the color-filled line under each stat box
def add_colored_line(ax, x_start, x_end, y_pos, home_percentage, away_percentage, home_color, away_color):
    # Home team's portion
    ax.plot([x_start, x_start + (x_end - x_start) * home_percentage / 100], [y_pos, y_pos],
            color=home_color, linewidth=25, solid_capstyle='butt', alpha=0.35)
    
    # Away team's portion
    ax.plot([x_start + (x_end - x_start) * home_percentage / 100, x_end], [y_pos, y_pos],
            color=away_color, linewidth=25, solid_capstyle='butt', alpha=0.35)

# Define the metrics and values to visualize (e.g., Ball possession, Accurate passes, etc.)
metrics = [
    ('Ball possession', ball_possession_home, ball_possession_away),
    ('Passes', accurate_passes_home_formatted, accurate_passes_away_formatted),
    ('Corners', accurate_corners_home_formatted, accurate_corners_away_formatted),
    ('xG', xG_home, xG_away),
    ('xG on target (xGOT)', xGOT_home, xGOT_away),
    ('Total shots', total_shots_home, total_shots_away)
]

# Define the y positions (lower than the stat titles)
line_y_positions = [pos - 0 for pos in y_positions]  # You can adjust this value to position the lines below each bbox

# Add the colored lines beneath each stat box
for (metric, home_value, away_value), y_pos in zip(metrics, line_y_positions):
    # Convert home_value and away_value to float to avoid TypeError during calculations
    home_value = float(home_value)
    away_value = float(away_value)
    
    # Calculate the home and away percentages (based on the two values in the metric)
    if home_value > away_value:
        home_percentage = (home_value / (home_value + away_value)) * 100
        away_percentage = 100 - home_percentage
    else:
        away_percentage = (away_value / (home_value + away_value)) * 100
        home_percentage = 100 - away_percentage
    
    # Use the home and away colors and the percentage values to fill the line
    add_colored_line(ax, 35, 70, y_pos, home_percentage, away_percentage, home_team_colors, away_team_colors)


######################


# Plot relevant metrics in the middle of the pitch with background
middle_x = 52.5  # Middle of the pitch along x-axis
middle_y = 52    # Middle of the pitch along y-axis


# Add legends manually
ax.scatter(2, 73, color='#47B745', linewidth=1.5, edgecolors='black', s=150, zorder=5, alpha=0.8, marker='o')
ax.text(4, 73, 'Goal', color='white', fontsize=13, alpha=0.8, ha='left', va='center', fontproperties=custom_fonttt)

ax.scatter(17, 73, color='#C8C329', linewidth=1.5, edgecolors='black', s=150, zorder=5, alpha=0.8, marker='o')
ax.text(19, 73, 'On Target', color='white', fontsize=13, alpha=0.8, ha='left', va='center', fontproperties=custom_fonttt)

ax.scatter(17, 70, color='#C82929', linewidth=1.5, edgecolors='black', s=150, zorder=5, alpha=0.8, marker='o')
ax.text(19, 70, 'Off Target', color='white', fontsize=13, alpha=0.8, ha='left', va='center', fontproperties=custom_fonttt)

ax.scatter(2, 70, color='#BD1A64', linewidth=1.5, edgecolors='black', s=150, zorder=5, alpha=0.8, marker='X')
ax.text(4, 70, 'Own Goal', color='white', fontsize=13, alpha=0.8, ha='left', va='center', fontproperties=custom_fonttt)

# Add circles with white edge color for xG values 0.2, 0.6, and 1.0
circle_positions_right = [(84.5, 71.5), (88.3, 71.5), (93, 71.5)]  # x, y positions of circles on the right side
xG_values_right = [0.1, 0.35, 0.6]  # xG values corresponding to each circle

for pos, xG in zip(circle_positions_right, xG_values_right):
    ax.scatter(pos[0], pos[1], color='none', linewidth=2, edgecolors='white', s=xG * 800, zorder=5, alpha=0.8)

# Add text annotations for 'Low xG' and 'High xG'
ax.text(82.5, 71.5, 'Low xG', color='white', alpha=0.8, fontsize=13, ha='right', va='center', fontproperties=custom_fonttt)
ax.text(96, 71.5, 'High xG', color='white', alpha=0.8, fontsize=13, ha='left', va='center', fontproperties=custom_fonttt)



# Define the color for the lines below logos
home_line_color = home_team_colors
away_line_color = away_team_colors

# Add lines below the logos
ax.plot([40 - 3, 52.825], [57, 57], color=home_line_color, linewidth=5)
ax.plot([52.825, 65 + 3], [57, 57], color=away_line_color, linewidth=5)

# Add text labels "Home" and "Away" above the lines
ax.text(45 - 0, 59, 'HOME', color='white', alpha=0.5, ha='center', fontproperties=custom_fontttt, fontsize=23)
ax.text(60 + 0, 59, 'AWAY', color='white', alpha=0.5, ha='center', fontproperties=custom_fontttt, fontsize=23)

# Extract shot data
shots = match_data.get('content', {}).get('shotmap', {}).get('shots', [])

# Define the path to the image 'kvaps.png'
kvaps_image_path = 'mål.png'

# Plot goals on the horizontal line using team logos and 'kvaps.png'
for shot in shots:
    if shot.get('eventType') == 'Goal':
        # Determine if the goal was an own goal
        is_own_goal = shot.get('isOwnGoal', False)

        # Extract the team ID
        team_id = shot.get('teamId')

        # Extract the minute of the goal
        minute = shot.get('min')

        # Plot goals on the horizontal line using team logos and 'kvaps.png'
for shot in shots:
    if shot.get('eventType') == 'Goal':
        # Determine if the goal was an own goal
        is_own_goal = shot.get('isOwnGoal', False)

        # Extract the team ID
        team_id = shot.get('teamId')

        # Extract the minute of the goal
        minute = shot.get('min')

        # Set the y-coordinate based on the team (5.5 for home goals, -5.5 for away goals, 5.5 for own goals)
        y_coord = 2.475 if team_id == home_team_id or is_own_goal else -4.475


        # Plot the 'kvaps.png' image at the specified y-coordinate
        kvaps_image = plt.imread(kvaps_image_path)
        ax.imshow(kvaps_image, extent=[minute + 5.75, minute + 5.75 + 1.8, y_coord, y_coord + 1.8], zorder=25)


# Define the arrow properties
arrow_width = 1
arrow_length = 10

# Create a double-ended arrow patch
arrow = FancyArrowPatch((52.5, 70.4), (65, 70.4), arrowstyle='->', color=away_team_colors, lw=2.5, mutation_scale=15)

# Add the arrow to the plot
ax.add_patch(arrow)

# Define the arrow properties
arrow_width = 1
arrow_length = 10

# Create a double-ended arrow patch
arrow1 = FancyArrowPatch((40, 70.4), (52.5, 70.4), arrowstyle='<-', color=home_team_colors, lw=2.5, mutation_scale=15)

# Add the arrow to the plot
ax.add_patch(arrow1)

# Add text annotations for attacking direction
ax.text(52.5, 71.25, 'Attacking direction', color='white', fontsize=13, ha='center', va='bottom', fontproperties=custom_fonttt, alpha=0.8)

#TITLE
custom_title = f'{home_team_name.upper()}  {match_score}  {away_team_name.upper()}'

# Add a custom title
fig.text(0.5, 1.01, custom_title, fontproperties=custom_fontttt, fontsize=30, color='white', ha='center')

# Format the suptitle
suptitle_text = f"{league_name}, {round_name} | Opta Data | @DanishScout_"

# Add the suptitle
fig.text(0.5, 0.975, suptitle_text, fontproperties=custom_fonttt, fontsize=12, color='white', ha='center', alpha=0.5)

# Add a custom title
fig.text(0.5, 0.03, "Generated via danishscout.streamlit.app", fontproperties=custom_fontt, fontsize=10, color='white', ha='center')

# Add horizontal line at the top
fig.add_artist(plt.Line2D((0, 1), (0.95, 0.95), color='white', linewidth=1.5, alpha=0.5, transform=fig.transFigure))

# Save the plot with 300 DPI and the specified filename
plt.savefig('overview.png', dpi=300, bbox_inches='tight')

# Display the plot in the Streamlit app
st.pyplot(fig)
