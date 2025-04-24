import os

from selenium import webdriver
from selenium.webdriver.chrome.service import Service


def launch_driver():
    # Automatically find the ChromeDriver path
    chrome_driver_path = os.path.abspath("Resources/chromedriver.exe")

    if chrome_driver_path is None:
        raise Exception("ChromeDriver not found. Ensure it is installed and added to PATH.")

    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    # Enable headless mode (Add this line)
    options.add_argument("--headless=new")

    # Optional (Recommended) – Avoid loading images to speed up scraping
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    service = Service(chrome_driver_path)
    driver = webdriver.Chrome(service=service, options=options)

    return driver
