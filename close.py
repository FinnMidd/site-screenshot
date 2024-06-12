import os
import shutil

# ------------------------ Define variables ------------------------ #

# Define subfolder names
subfolders = ["desktop", "mobile", "tablet"]

# Define the folder paths and JSON file path
screenshot_folder = "screenshots"
initial_folder = os.path.join(screenshot_folder, "initial")
secondary_folder = os.path.join(screenshot_folder, "secondary")
json_file_path = os.path.join(screenshot_folder, 'screenshots_data.json')

# ------------------------ Run functions ------------------------ #

# Function to clear and create subfolders
def clear_and_create_subfolders(base_folder): #? Can I replace this with the functions.py version?
    for subfolder in subfolders:
        folder = os.path.join(base_folder, subfolder)
        if os.path.exists(folder):
            shutil.rmtree(folder)
        os.makedirs(folder)
        print(f"Cleared the {folder} folder.")

# Function to clean the directories
def clean_directory(): #? Can I move this to functions.py?
    # Check if the initial folder exists and delete its contents
    if os.path.exists(initial_folder):
        shutil.rmtree(initial_folder)
        os.makedirs(initial_folder)
        print(f"Cleared the {initial_folder} folder.")
    else:
        os.makedirs(initial_folder)
        print(f"Created the {initial_folder} folder.")

    # Clear and create subfolders in the initial folder
    clear_and_create_subfolders(initial_folder)

    # Check if the secondary folder exists and delete its contents
    if os.path.exists(secondary_folder):
        shutil.rmtree(secondary_folder)
        os.makedirs(secondary_folder)
        print(f"Cleared the {secondary_folder} folder.")
    else:
        os.makedirs(secondary_folder)
        print(f"Created the {secondary_folder} folder.")

    # Clear and create subfolders in the secondary folder
    clear_and_create_subfolders(secondary_folder)

    # Clear the JSON file
    with open(json_file_path, 'w') as json_file:
        json_file.write('[]')
        print(f"Cleared the {json_file_path} file.")

# Run the clean_directory function
if __name__ == "__main__":
    clean_directory()
    print(f"\033[92mDirectory now reset!\033[0m")
