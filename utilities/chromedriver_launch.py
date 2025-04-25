import os

from selenium import webdriver
from selenium.webdriver.chrome.service import Service


def launch_driver():
    # Get the absolute path to the ChromeDriver executable located in the "Resources" folder
    chrome_driver_path = os.path.abspath("Resources/chromedriver.exe")

    # Raise an error if the ChromeDriver path isn't found (basic check)
    if chrome_driver_path is None:
        raise Exception("ChromeDriver not found. Ensure it is installed and added to PATH.")

    # Create an instance of ChromeOptions to customize browser behavior
    options = webdriver.ChromeOptions()
    # Launch the browser in maximized window mode
    options.add_argument("--start-maximized")
    # Prevent Selenium from being detected as an automation bot
    options.add_argument("--disable-blink-features=AutomationControlled")
    # Enable headless mode (browser runs in background without UI)
    options.add_argument("--headless=new")

    # Optional (Recommended) – Avoid loading images to speed up scraping
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    service = Service(chrome_driver_path)
    driver = webdriver.Chrome(service=service, options=options)

    return driver
