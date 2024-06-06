from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import json
import os
from functions import clear_and_create_folders, parallel_capture_screenshots, compare_screenshots, viewports, subfolders

# Define the folder paths and JSON file path
screenshot_folder = "screenshots"
initial_folder = os.path.join(screenshot_folder, "initial")
secondary_folder = os.path.join(screenshot_folder, "secondary")
json_file_path = os.path.join(screenshot_folder, 'screenshots_data.json')

# Clear and create secondary subfolders
clear_and_create_folders(secondary_folder)

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
    entry["secondary"]["google"]["desktop_screenshot"] = results[url]

# Save the updated data to the JSON file
with open(json_file_path, 'w') as json_file:
    json.dump(data, json_file, indent=4)

# Rescan all sites and capture new screenshots for mobile view
mobile_folder_path = os.path.join(secondary_folder, "mobile")
viewport = viewports["mobile"]
results = parallel_capture_screenshots(urls_to_capture, options, mobile_folder_path, viewport)
for entry in data:
    url = entry["url"]
    entry["secondary"]["google"]["mobile_screenshot"] = results[url]

# Save the updated data to the JSON file
with open(json_file_path, 'w') as json_file:
    json.dump(data, json_file, indent=4)

# Rescan all sites and capture new screenshots for tablet view
tablet_folder_path = os.path.join(secondary_folder, "tablet")
viewport = viewports["tablet"]
results = parallel_capture_screenshots(urls_to_capture, options, tablet_folder_path, viewport)
for entry in data:
    url = entry["url"]
    entry["secondary"]["google"]["tablet_screenshot"] = results[url]

# Save the updated data to the JSON file
with open(json_file_path, 'w') as json_file:
    json.dump(data, json_file, indent=4)

# Compare screenshots and print the results
non_matching_files = []
for subfolder in subfolders:
    non_matching_files.extend(compare_screenshots(initial_folder, secondary_folder, subfolder))

if non_matching_files:
    print("The following files do not match:")
    for file_name in non_matching_files:
        device, filename = file_name.split(': ')
        initial_path = os.path.join(initial_folder, device, filename)
        secondary_path = os.path.join(secondary_folder, device, filename)
        url = filename.replace('_', '/').replace('.png', '')
        print(f"{device} | {url} | {initial_path} | {secondary_path}")
else:
    print("Congratulations, all webpages match!")
