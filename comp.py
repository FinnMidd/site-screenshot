import os
from functions import compare_screenshots, subfolders

# ------------------------ Define variables ------------------------ #

# Define the folder paths and JSON file path
screenshot_folder = "screenshots"
initial_folder = os.path.join(screenshot_folder, "initial")
secondary_folder = os.path.join(screenshot_folder, "secondary")
json_file_path = os.path.join(screenshot_folder, 'screenshots_data.json')

# Initialize array for non matching files
non_matching_files = []

# ------------------------ Run functions ------------------------ #

# Compare screenshots and print the results
for subfolder in subfolders:
    non_matching_files.extend(compare_screenshots(initial_folder, secondary_folder, subfolder))

# ------------------------ End of task ------------------------ #

if non_matching_files:
    print("The following files do not match:")
    for file_name in non_matching_files:
        device, filename = file_name.split(': ')
        initial_path = os.path.join(initial_folder, device, filename)
        secondary_path = os.path.join(secondary_folder, device, filename)
        url = filename.replace('_', '/').replace('.png', '')
        print(f"{device} | {url} | {initial_path} | {secondary_path}")
else:
    print(f"\033[92mCongratulations, all webpages match!\033[0m")