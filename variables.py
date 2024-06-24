import os

# ------------------------ Define variables ------------------------ #

# Define the base folder paths
base_screenshot_folder = "screenshots"
initial_folder = os.path.join(base_screenshot_folder, "initial")
secondary_folder = os.path.join(base_screenshot_folder, "secondary")
json_file_path = os.path.join(base_screenshot_folder, 'screenshots_data.json')

# Define subfolder names
subfolders = ["desktop", "mobile", "tablet"]

# Viewport sizes for mobile and desktop
viewports = {
    "mobile": (375, 812),
    "desktop": (1920, 1080),
    "tablet": (768, 1024)
}

# Initialize data storage for the JSON file
data = []

# Initialize array for non matching files
non_matching_files = []

