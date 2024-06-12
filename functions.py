import os
import re
import json #? review if needed
import shutil
import random
import requests
import time
from PIL import Image, ImageChops
import numpy as np #? review if needed
from xml.etree import ElementTree as ET
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from concurrent.futures import ThreadPoolExecutor #? review if needed
from webdriver_manager.chrome import ChromeDriverManager
import concurrent.futures

# Define subfolder names
subfolders = ["desktop", "mobile", "tablet"]

# Viewport sizes for mobile and desktop
viewports = {
    "mobile": (375, 812),
    "desktop": (1920, 1080),
    "tablet": (768, 1024)
}

# Function to clear and create folders
def clear_and_create_folders(base_folder):
    for subfolder in subfolders:
        folder = os.path.join(base_folder, subfolder)
        if os.path.exists(folder):
            shutil.rmtree(folder)
        os.makedirs(folder)

# Function to capture screenshot
def capture_screenshot(url, driver, folder, viewport):
    # Open the webpage
    driver.get(url)

    # Set the window size to the viewport dimensions
    driver.set_window_size(viewport[0], viewport[1])

    # Allow some time for the resizing to take effect
    time.sleep(2)

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
    return {
        "title": title,
        "url": url,
        "initial": {
            "google": {
                "desktop_screenshot": None,
                "tablet_screenshot": None,
                "mobile_screenshot": None
            },
            "firefox": {
                "desktop_screenshot": None,
                "tablet_screenshot": None,
                "mobile_screenshot": None
            },
            "edge": {
                "desktop_screenshot": None,
                "tablet_screenshot": None,
                "mobile_screenshot": None
            },
            "safari": {
                "desktop_screenshot": None,
                "tablet_screenshot": None,
                "mobile_screenshot": None
            }
        },
        "secondary": {
            "google": {
                "desktop_screenshot": None,
                "tablet_screenshot": None,
                "mobile_screenshot": None
            },
            "firefox": {
                "desktop_screenshot": None,
                "tablet_screenshot": None,
                "mobile_screenshot": None
            },
            "edge": {
                "desktop_screenshot": None,
                "tablet_screenshot": None,
                "mobile_screenshot": None
            },
            "safari": {
                "desktop_screenshot": None,
                "tablet_screenshot": None,
                "mobile_screenshot": None
            }
        }
    }

# Function to process sitemap and take screenshots
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

# Function to compare two images
def compare_images(image1_path, image2_path):
    try:
        image1 = Image.open(image1_path)
        image2 = Image.open(image2_path)

        # Check if images are loaded correctly
        if image1 is None or image2 is None:
            print(f"\033[91mError loading images.\033[0m")
            return False

        # Ensure images are the same size
        if image1.size != image2.size:
            print(f"\033[93mImage sizes differ.\033[0m")
            return False

        # Compute the difference
        diff = ImageChops.difference(image1, image2)

        # Log difference details
        bbox = diff.getbbox()
        if bbox:
            print(f"\033[91mDifference found in images.\033[0m")
            print(f"\033[91mDifference bounding box.\033[0m")
            diff.show()  # Show the difference for visual confirmation
            return False
        else:
            print(f"\033[92mNo differences found in images.\033[0m")
            return True

    except Exception as e:
        print(f"\033[91mError comparing images:\033[0m {e}")
        return False

# Function to compare screenshots in initial and secondary folders
def compare_screenshots(initial_folder, secondary_folder, subfolder):
    initial_subfolder = os.path.join(initial_folder, subfolder)
    secondary_subfolder = os.path.join(secondary_folder, subfolder)
    initial_files = set(os.listdir(initial_subfolder))
    secondary_files = set(os.listdir(secondary_subfolder))

    # Only compare files that are present in both folders
    common_files = initial_files.intersection(secondary_files)

    non_matching_files = []
    for file_name in common_files:
        initial_path = os.path.join(initial_subfolder, file_name)
        secondary_path = os.path.join(secondary_subfolder, file_name)
        print(f"Comparing: {initial_path} with {secondary_path}")
        if not compare_images(initial_path, secondary_path):
            non_matching_files.append(f"{subfolder}: {file_name}")

    return non_matching_files

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
