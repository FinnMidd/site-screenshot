import os
from settings import use_desktop, use_tablet, use_mobile

# ------------------------ Define variables ------------------------ #

# Define the base folder paths
base_screenshot_folder = "screenshots"
initial_folder = os.path.join(base_screenshot_folder, "initial")
secondary_folder = os.path.join(base_screenshot_folder, "secondary")
json_file_path = os.path.join(base_screenshot_folder, 'screenshots_data.json')

# Update subfolders based on settings
subfolders = []
if use_desktop:
    subfolders.append("desktop")
if use_mobile:
    subfolders.append("mobile")
if use_tablet:
    subfolders.append("tablet")

# Viewport sizes for mobile and desktop
viewports = {}
if use_desktop:
    viewports["desktop"] = (1920, 1080)
if use_mobile:
    viewports["mobile"] = (375, 812)
if use_tablet:
    viewports["tablet"] = (768, 1024)

# Initialize data storage for the JSON file
data = []

# Initialize array for non matching files
non_matching_files = []

