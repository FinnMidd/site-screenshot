
# Website Screenshot


This project allows you to capture screenshots of websites using different devices and browsers, storing the results in a JSON file & allowing you to compare the results with previous screenshots taken at different times to identify visual changes.



## Features



- Capture screenshots for desktop, tablet, and mobile views.
- Currently supports Google Chrome.
- Store screenshot paths, url and webpage titles in a JSON file.
- Compare initial and secondary screenshots to detect changes.



## Prerequisites



- ```Python 3.6+```, ```Selenium```, ```Webdriver Manager for Chrome```, ```Pillow```, ```Requests```, ```NumPy```
- Currently only supported on Windows OS
- Each site requires a ```sitemap_index.xml``` file



## Installation



1.  **Clone the repository:**

```sh
git clone https://github.com/your-repo/screenshot-capture.git
```
```
cd screenshot-capture
```



2.  **Create a virtual environment:**

```sh
python -m venv venv
```



3.  **Activate the virtual environment:**

```sh
source venv\Scripts\activate
```




4.  **Install dependencies:**

```sh
pip install -r requirements.txt
```



## Usage



### Initial Screenshot Capture



Run the `app.py` script to capture initial screenshots.



```sh
python  app.py {input your site's url}
```


## Project Structure

- ``` app.py ``` Captures initial screenshots.
- ``` rerun.py ``` Captures secondary screenshots and compares them with the initial ones.
- ``` compare.py ``` Compares screenshots and identifies differences.
- ``` functions.py ``` Contains helper functions for entire project.
- ``` close.py ``` Clears the directory of all screenshots & screenshot data.
- ``` screenshots_data.json ``` Contains data on each page including, page title, URL & screenshot locations.

## Disclaimer

This project is currently a work in progress & is incomplete. Be careful installing & using these scripts.