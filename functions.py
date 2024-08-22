import os
import re
import shutil
import random
import requests
import time
import json
from urllib.parse import urlparse
from PIL import Image
import numpy as np
from xml.etree import ElementTree as ET
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import concurrent.futures
from webdriver_manager.chrome import ChromeDriverManager
from skimage.metrics import structural_similarity
import cv2
from variables import subfolders, initial_folder, secondary_folder, json_file_path, viewports

# ------------------------ Define functions ------------------------ #

# Function to strip urls of formatting
def strip_url(url):
    parsed_url = urlparse(url)
    stripped = parsed_url.netloc
    return stripped

# Function to fetch the title of a webpage
def fetch_page_title(url, options):
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(url)
    title = driver.title
    driver.quit()
    return title

# Function to hide jd-hide
def hide_class(driver):
    class_name = 'jd-hide'
    script = f"""
    var elements = document.getElementsByClassName('{class_name}');
    for (var i = 0; i < elements.length; i++) {{
        elements[i].style.display = 'none';
    }}
    """
    driver.execute_script(script)

# ------------------------ Folder functions ------------------------ #

# Function to clear and create folders
def clear_and_create_folders(base_folder):
    for subfolder in subfolders:
        folder = os.path.join(base_folder, subfolder)
        if os.path.exists(folder):
            shutil.rmtree(folder)
        os.makedirs(folder)

# Function to clean the directories
def clean_directory():
    # Check if the initial folder exists and delete its contents
    if os.path.exists(initial_folder):
        shutil.rmtree(initial_folder)
        os.makedirs(initial_folder)
        print(f"Cleared the {initial_folder} folder.")
    else:
        os.makedirs(initial_folder)
        print(f"Created the {initial_folder} folder.")

    # Clear and create subfolders in the initial folder
    clear_and_create_folders(initial_folder)

    # Check if the secondary folder exists and delete its contents
    if os.path.exists(secondary_folder):
        shutil.rmtree(secondary_folder)
        os.makedirs(secondary_folder)
        print(f"Cleared the {secondary_folder} folder.")
    else:
        os.makedirs(secondary_folder)
        print(f"Created the {secondary_folder} folder.")

    # Clear and create subfolders in the secondary folder
    clear_and_create_folders(secondary_folder)

    # Clear/Create the JSON file
    reset_json(json_file_path)

# ------------------------ JSON functions ------------------------ #

# Function to update the JSON data structure
def update_json_data(data, url, title, desktop_screenshot_path, mobile_screenshot_path, tablet_screenshot_path):
    new_entry = {
        "title": title,
        "url": url,
        "initial_desktop_screenshot": desktop_screenshot_path if desktop_screenshot_path else 0,
        "initial_mobile_screenshot": mobile_screenshot_path if mobile_screenshot_path else 0,
        "initial_tablet_screenshot": tablet_screenshot_path if tablet_screenshot_path else 0,
        "secondary_desktop_screenshot": 0,
        "secondary_mobile_screenshot": 0,
        "secondary_tablet_screenshot": 0
    }
    data.append(new_entry)

# Function to initialize the JSON data structure
def initialize_json_entry(url, title):
    entry = {
        "title": title,
        "url": url,
        "initial": {"google": {}},
        "secondary": {"google": {}}
    }
    
    for device in viewports.keys():
        entry["initial"]["google"][f"{device}_screenshot"] = None
        entry["secondary"]["google"][f"{device}_screenshot"] = None
    
    return entry

# Function to clear JSON file
def reset_json(json_file_path):
    with open(json_file_path, 'w') as json_file:
        json.dump([], json_file)

# Function to write to JSON file
def add_json(json_file_path, data):
    with open(json_file_path, 'w') as json_file:
        json.dump(data, json_file, indent=4)

# ------------------------ Sitemap functions ------------------------ #

def load_site_and_children(file_path, selected_url):
    # Strip the selected URL for comparison
    selected_url = strip_url(selected_url)

    # Load the JSON file
    with open(file_path, 'r') as file:
        sites_data = json.load(file)
    
    # Find the selected site and build the array
    for site in sites_data['sites']:
        if strip_url(site['main_url']) == selected_url:
            # Create the array with the main URL and its children
            urls_to_check = [site['main_url']] + [f"{site['main_url']}{child}" for child in site['children']]
            return urls_to_check
    
    # If the selected URL is not found, print error message and return an empty array
    print(f"Error: The URL '{selected_url}' was not found in the JSON file.")
    return []

# Check that provided sitemap exists/is present
def sitemap_check(base_url, sitemap_name):
    full_url = base_url.rstrip('/') + '/' + sitemap_name.lstrip('/')
    try:
        response = requests.get(full_url)
        return response.status_code == 200
    except requests.RequestException as e:
        print(f"An error occurred: {e}")
        return False

# Function to process sitemap and take screenshots
#? Incorporate the sitemap_check function to check for sitemap_index
def process_sitemap(sitemap_url, driver_options, folder, max_screenshots, data, viewport):
    response = requests.get(sitemap_url)

    if response.status_code == 200:
        print(f"The sitemap file is present at {sitemap_url}.")

        # Parse the sitemap XML
        root = ET.fromstring(response.content)

        # Extract all loc elements
        loc_elements = [loc.text for loc in root.iter('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]

        # Randomly select up to max_screenshots loc elements
        selected_locs = random.sample(loc_elements, min(len(loc_elements), max_screenshots))

        urls = []
        for page_url in selected_locs:
            if page_url.endswith('.xml'):
                # If the URL is another XML file, process it recursively
                print(f"Found nested sitemap: {page_url}")
                urls.extend(process_sitemap(page_url, driver_options, folder, max_screenshots, data, viewport))
            else:
                urls.append(page_url)

        return urls
    else:
        print(f"The sitemap file is not present at {sitemap_url}.")
        return []

# ------------------------ Screenshot functions ------------------------ #

# Function to capture screenshot
def capture_screenshot(url, driver, folder, viewport):
    # Open the webpage
    driver.get(url)

    # Set the window size to the viewport dimensions
    driver.set_window_size(viewport[0], viewport[1])

    # Allow some time for the resizing to take effect
    time.sleep(2)

    # Hide class jd-hide
    hide_class(driver)

    # Hide the scroll bar
    driver.execute_script("document.body.style.overflow = 'hidden';")

    # Get the dimensions of the page
    total_width = driver.execute_script("return document.body.scrollWidth")
    total_height = driver.execute_script("return document.body.scrollHeight")

    # Set the window size to the dimensions of the entire page
    driver.set_window_size(total_width, total_height)

    # Allow some time for the resizing to take effect
    time.sleep(2)

    # Capture screenshot
    screenshot = driver.get_screenshot_as_png()

    # Create a valid filename from the URL, removing the protocol
    url_filename = re.sub(r'[^\w\-_\. ]', '_', url.replace("https://", "").replace("http://", "")) + ".png"
    screenshot_path = os.path.join(folder, url_filename)

    # Save the screenshot in the folder
    with open(screenshot_path, "wb") as file:
        file.write(screenshot)

    # Optionally, crop the image to remove any unwanted space
    image = Image.open(screenshot_path)
    image.save(screenshot_path)

    return screenshot_path

# Function to capture screenshots in parallel
def parallel_capture_screenshots(urls, driver_options, folder, viewport):
    def capture(url):
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=driver_options)
        screenshot_path = capture_screenshot(url, driver, folder, viewport)
        driver.quit()
        return url, screenshot_path

    results = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:  # Adjust max_workers based on your system's capacity
        future_to_url = {executor.submit(capture, url): url for url in urls}
        for future in concurrent.futures.as_completed(future_to_url):
            url, screenshot_path = future.result()
            results[url] = screenshot_path

    return results
    
# ------------------------ Comparison functions ------------------------ #

# Function to compare two images
def compare_images(image1_path, image2_path):
    try:
        # Read images
        image1 = cv2.imread(image1_path)
        image2 = cv2.imread(image2_path)

        # Check if images have the same dimensions
        if image1.shape == image2.shape:
            # Use SSIM method
            gray1 = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
            gray2 = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)

            (score, diff) = structural_similarity(gray1, gray2, full=True)
            print(f"SSIM: {score:.4f}")

            diff = (diff * 255).astype("uint8")
            thresh = cv2.threshold(diff, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
            contours = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            contours = contours[0] if len(contours) == 2 else contours[1]

            image_with_differences = image1.copy()

            for c in contours:
                area = cv2.contourArea(c)
                if area > 40:  # Adjust this threshold as needed
                    x, y, w, h = cv2.boundingRect(c)
                    cv2.rectangle(image_with_differences, (x, y), (x + w, y + h), (0, 255, 0), 2)

            method = "SSIM"
            threshold = 0.95  # Adjust this threshold as needed

        else:
            # Use cv2.absdiff method
            print("Image dimensions do not match. Using cv2.absdiff method.")
            
            # Resize image2 to match image1's dimensions
            image2 = cv2.resize(image2, (image1.shape[1], image1.shape[0]))
            
            gray1 = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
            gray2 = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)

            diff = cv2.absdiff(gray1, gray2)
            image_with_differences = 255 - diff
            
            # Calculate a simple similarity score based on mean pixel difference
            score = 1 - (np.mean(diff) / 255)
            print(f"Similarity score: {score:.4f}")

            method = "absdiff"
            threshold = 0.8  # Adjust this threshold as needed

        # Save the image with differences highlighted
        difference_image_path = image1_path.replace('.png', f'_diff_{method}.png')
        cv2.imwrite(difference_image_path, image_with_differences)

        if score < threshold:
            print(f"\033[91mDifference found in images: {image1_path}\033[0m")
            print(f"Difference image saved as: {difference_image_path}")
            return False, difference_image_path, method, score
        else:
            return True, None, method, score

    except Exception as e:
        print(f"\033[91mError comparing images:\033[0m {e}")
        return False, None, "error", 0

# Update the compare_screenshots function to handle the new return values
def compare_screenshots(initial_folder, secondary_folder, subfolder):
    initial_subfolder = os.path.join(initial_folder, subfolder)
    secondary_subfolder = os.path.join(secondary_folder, subfolder)
    initial_files = set(os.listdir(initial_subfolder))
    secondary_files = set(os.listdir(secondary_subfolder))

    common_files = initial_files.intersection(secondary_files)

    non_matching_files = []
    for file_name in common_files:
        initial_path = os.path.join(initial_subfolder, file_name)
        secondary_path = os.path.join(secondary_subfolder, file_name)
        match, diff_path, method, score = compare_images(initial_path, secondary_path)
        if not match:
            non_matching_files.append((f"{subfolder}: {file_name}", diff_path, method, score))

    return non_matching_files