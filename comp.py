import time
import os
from variables import initial_folder, secondary_folder, non_matching_files, viewports
from functions import compare_screenshots

if __name__ == "__main__":

    # ------------------------ Define variables ------------------------ #



    # ------------------------ Run functions ------------------------ #

    # Start the timer
    start_time = time.time()

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