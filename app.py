import argparse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import json
import os
from functions import clear_and_create_folders, parallel_capture_screenshots, process_sitemap, viewports, initialize_json_entry

# Set up argument parsing
parser = argparse.ArgumentParser(description='Process some URLs.')
parser.add_argument('base_url', type=str, nargs='?', default='https://www.jaladesign.com.au/', help='The URL you wish to process')
args = parser.parse_args()

# Get the base URL from the arguments
base_url = args.base_url

# Define variable for maximum number of screenshots per child sitemap
MAX_SCREENSHOTS_PER_CHILD_SITEMAP = 6

# Define the base folder paths
base_screenshot_folder = "screenshots"
initial_folder = os.path.join(base_screenshot_folder, "initial")
secondary_folder = os.path.join(base_screenshot_folder, "secondary")
json_file_path = os.path.join(base_screenshot_folder, 'screenshots_data.json')

# Clear and create subfolders
clear_and_create_folders(initial_folder)
clear_and_create_folders(secondary_folder)

# Clear the JSON file
with open(json_file_path, 'w') as json_file:
    json.dump([], json_file)

# Initialize the Chrome WebDriver options with headless option
options = webdriver.ChromeOptions()
options.add_argument("--headless")

# Initialize data storage for the JSON file
data = []

# Function to fetch the title of a webpage
def fetch_page_title(url, options):
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(url)
    title = driver.title
    driver.quit()
    return title

# Open the base webpage, fetch the title, and take a screenshot for desktop view
desktop_folder_path = os.path.join(initial_folder, "desktop")
viewport = viewports["desktop"]
print(f"Taking screenshot of {base_url} for desktop view")

# Capture base URL screenshot
results = parallel_capture_screenshots([base_url], options, desktop_folder_path, viewport)
desktop_screenshot_path = results[base_url]

# Fetch the title of the base URL
base_title = fetch_page_title(base_url, options)

entry = initialize_json_entry(base_url, base_title)
entry["initial"]["google"]["desktop_screenshot"] = desktop_screenshot_path
data.append(entry)

# Check for the base sitemap and process it for desktop view
sitemap_url = base_url + "sitemap_index.xml"
urls_to_capture = process_sitemap(sitemap_url, options, desktop_folder_path, MAX_SCREENSHOTS_PER_CHILD_SITEMAP, data, viewport)

# Capture additional screenshots in parallel
results = parallel_capture_screenshots(urls_to_capture, options, desktop_folder_path, viewport)
for url, screenshot_path in results.items():
    entry = next((item for item in data if item['url'] == url), None)
    if entry:
        entry["initial"]["google"]["desktop_screenshot"] = screenshot_path
    else:
        # Fetch the title for the new page
        page_title = fetch_page_title(url, options)
        new_entry = initialize_json_entry(url, page_title)
        new_entry["initial"]["google"]["desktop_screenshot"] = screenshot_path
        data.append(new_entry)

# Save the data to a JSON file
with open(json_file_path, 'w') as json_file:
    json.dump(data, json_file, indent=4)

# Rescan all sites and capture new screenshots for mobile view
mobile_folder_path = os.path.join(initial_folder, "mobile")
viewport = viewports["mobile"]
urls_to_capture = [entry["url"] for entry in data]

results = parallel_capture_screenshots(urls_to_capture, options, mobile_folder_path, viewport)
for entry in data:
    url = entry["url"]
    entry["initial"]["google"]["mobile_screenshot"] = results[url]

# Save the updated data to the JSON file
with open(json_file_path, 'w') as json_file:
    json.dump(data, json_file, indent=4)

# Rescan all sites and capture new screenshots for tablet view
tablet_folder_path = os.path.join(initial_folder, "tablet")
viewport = viewports["tablet"]
urls_to_capture = [entry["url"] for entry in data]

results = parallel_capture_screenshots(urls_to_capture, options, tablet_folder_path, viewport)
for entry in data:
    url = entry["url"]
    entry["initial"]["google"]["tablet_screenshot"] = results[url]

# Save the updated data to the JSON file
with open(json_file_path, 'w') as json_file:
    json.dump(data, json_file, indent=4)

print(f"\033[92mAll initial screenshots now complete!\033[0m")
