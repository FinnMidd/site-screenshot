import os
from variables import initial_folder, secondary_folder, subfolders, non_matching_files
from functions import compare_screenshots

# ------------------------ Define variables ------------------------ #



# ------------------------ Run functions ------------------------ #

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