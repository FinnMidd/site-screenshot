from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import json
import os
from variables import initial_folder, secondary_folder, json_file_path, subfolders, viewports, non_matching_files
from functions import clear_and_create_folders, parallel_capture_screenshots, compare_screenshots #? review which are needed

# ------------------------ Define variables ------------------------ #



# ----------------------- Reset directory ----------------------- #

clear_and_create_folders(secondary_folder)

# ------------------------ Run functions ------------------------ #

# Initialize the Chrome WebDriver options with headless option
options = webdriver.ChromeOptions()
options.add_argument("--headless")

# Load the JSON file
with open(json_file_path, 'r') as json_file:
    data = json.load(json_file)

# Rescan all sites and capture new screenshots for desktop view
desktop_folder_path = os.path.join(secondary_folder, "desktop")
viewport = viewports["desktop"]
urls_to_capture = [entry["url"] for entry in data]

results = parallel_capture_screenshots(urls_to_capture, options, desktop_folder_path, viewport)
for entry in data:
    url = entry["url"]
    entry["secondary_desktop_screenshot"] = results[url]

# Save the updated data to the JSON file
with open(json_file_path, 'w') as json_file:
    json.dump(data, json_file, indent=4)

# Rescan all sites and capture new screenshots for mobile view
mobile_folder_path = os.path.join(secondary_folder, "mobile")
viewport = viewports["mobile"]
results = parallel_capture_screenshots(urls_to_capture, options, mobile_folder_path, viewport)
for entry in data:
    url = entry["url"]
    entry["secondary_mobile_screenshot"] = results[url]

# Save the updated data to the JSON file
with open(json_file_path, 'w') as json_file:
    json.dump(data, json_file, indent=4)

# Rescan all sites and capture new screenshots for tablet view
tablet_folder_path = os.path.join(secondary_folder, "tablet")
viewport = viewports["tablet"]
results = parallel_capture_screenshots(urls_to_capture, options, tablet_folder_path, viewport)
for entry in data:
    url = entry["url"]
    entry["secondary_tablet_screenshot"] = results[url]

# Save the updated data to the JSON file
with open(json_file_path, 'w') as json_file:
    json.dump(data, json_file, indent=4)

# Compare screenshots and print the results
for subfolder in subfolders:
    non_matching_files.extend(compare_screenshots(initial_folder, secondary_folder, subfolder))

# ------------------------ End of task ------------------------ #

if non_matching_files:
    #? Review if this output is needed
    print(f"\033[38;5;214mThe following files do not match:\033[0m")
    for file_name in non_matching_files:
        device, filename = file_name.split(': ')
        initial_path = os.path.join(initial_folder, device, filename)
        secondary_path = os.path.join(secondary_folder, device, filename)
        url = filename.replace('_', '/').replace('.png', '')
        print(f"{device} | {url} | {initial_path} | {secondary_path}")
else:
    print(f"\033[92mCongratulations, all webpages match!\033[0m")