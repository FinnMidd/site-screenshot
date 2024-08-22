import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import json
import os
from variables import initial_folder, secondary_folder, diffs_folder, json_file_path, viewports, non_matching_files
from functions import clear_and_create_folders, parallel_capture_screenshots, compare_screenshots

if __name__ == "__main__":

    # ------------------------ Define variables ------------------------ #



    # ----------------------- Reset directory ----------------------- #

    clear_and_create_folders(secondary_folder)
    clear_and_create_folders(diffs_folder)

    # ------------------------ Run functions ------------------------ #

    # Start the timer
    start_time = time.time()

    # Initialize the Chrome WebDriver options with headless option
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")

    # Load the JSON file
    with open(json_file_path, 'r') as json_file:
        data = json.load(json_file)

    # Get all URLs to capture
    urls_to_capture = [entry["url"] for entry in data]

    # Capture screenshots for each viewport
    for device, viewport in viewports.items():
        folder_path = os.path.join(secondary_folder, device)
        print(f"Capturing screenshots for {device} view")

        results = parallel_capture_screenshots(urls_to_capture, options, folder_path, viewport)
        
        for entry in data:
            url = entry["url"]
            entry["secondary"]["google"][f"{device}_screenshot"] = results[url]

        # Save the updated data to the JSON file after each viewport
        with open(json_file_path, 'w') as json_file:
            json.dump(data, json_file, indent=4)

    # Compare screenshots and print the results
    for device in viewports.keys():
        non_matching_files.extend(compare_screenshots(os.path.join("screenshots", "initial"), 
                                                    os.path.join("screenshots", "secondary"), 
                                                    device))

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

    if non_matching_files:
        print(f"\033[38;5;214mThe following files do not match:\033[0m")
        for file_info in non_matching_files:
            device_filename, diff_path, method, score = file_info
            device, filename = device_filename.split(': ')
            initial_path = os.path.join(initial_folder, device, filename)
            secondary_path = os.path.join(secondary_folder, device, filename)
            url = filename.replace('_', '/').replace('.png', '')
            print(f"{device} | {url} | {initial_path} | {secondary_path}")
            print(f"Comparison method: {method}")
            print(f"Similarity score: {score:.4f}")
            print(f"Difference image: {diff_path}")
            print("---")
    else:
        print(f"\033[92mCongratulations, all webpages match!\033[0m")