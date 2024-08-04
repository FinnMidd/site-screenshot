import time
import argparse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import json
import os
from variables import initial_folder, secondary_folder, json_file_path, viewports, data, subfolders
from functions import clear_and_create_folders, parallel_capture_screenshots, process_sitemap, initialize_json_entry, reset_json, add_json, fetch_page_title

if __name__ == "__main__":

    # -------------------- Set up argument parsing --------------------- #

    # Initiate argument parsing
    parser = argparse.ArgumentParser(description='Process some URLs.')
    parser.add_argument('base_url', type=str, nargs='?', default='https://www.jaladesign.com.au/', help='The URL you wish to process')
    args = parser.parse_args()

    # ------------------------ Define variables ------------------------ #

    # Define maximum amount of screenshots per child sitemap
    MAX_SCREENSHOTS_PER_CHILD_SITEMAP = 6

    # Get the base URL from the arguments
    base_url = args.base_url

    # ----------------------- Reset directory ----------------------- #

    # Clear and create subfolders
    clear_and_create_folders(initial_folder)
    clear_and_create_folders(secondary_folder)

    # Clear/Create the JSON file
    reset_json(json_file_path)

    # ------------------------ Run functions ------------------------ #

    # Start the timer
    start_time = time.time()

    # Initialize the Chrome WebDriver options with headless option
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")

    # Process base URL for each viewport
    for device, viewport in viewports.items():
        folder_path = os.path.join(initial_folder, device)
        print(f"Taking screenshot of {base_url} for {device} view")

        results = parallel_capture_screenshots([base_url], options, folder_path, viewport)
        screenshot_path = results[base_url]

        if not data:  # If data is empty, initialize it with base URL
            base_title = fetch_page_title(base_url, options)
            entry = initialize_json_entry(base_url, base_title)
            data.append(entry)

        data[0]["initial"]["google"][f"{device}_screenshot"] = screenshot_path

    # Process sitemap for each viewport
    sitemap_url = base_url + "sitemap_index.xml"
    for device, viewport in viewports.items():
        folder_path = os.path.join(initial_folder, device)
        urls_to_capture = process_sitemap(sitemap_url, options, folder_path, MAX_SCREENSHOTS_PER_CHILD_SITEMAP, data, viewport)

        results = parallel_capture_screenshots(urls_to_capture, options, folder_path, viewport)
        for url, screenshot_path in results.items():
            entry = next((item for item in data if item['url'] == url), None)
            if entry:
                entry["initial"]["google"][f"{device}_screenshot"] = screenshot_path
            else:
                page_title = fetch_page_title(url, options)
                new_entry = initialize_json_entry(url, page_title)
                new_entry["initial"]["google"][f"{device}_screenshot"] = screenshot_path
                data.append(new_entry)

        add_json(json_file_path, data)

    # ------------------------ End of task ------------------------ #

    # Stop the timer
    end_time = time.time()

    # Calculate the elapsed time
    elapsed_time = end_time - start_time

    # Convert elapsed time to minutes and seconds
    minutes, seconds = divmod(elapsed_time, 60)

    # Print the elapsed time in minutes and seconds
    if minutes > 0:
        print(f"Time taken to complete the script: {int(minutes)} minutes and {seconds:.2f} seconds")
    else:
        print(f"Time taken to complete the script: {seconds:.2f} seconds")

    # Print completion message
    print(f"\033[92mAll initial screenshots now complete!\033[0m")