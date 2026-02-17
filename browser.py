from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import os
from .colors import print_info, print_error, print_success

def init_browser(config):
    print_info("Initializing browser...")
    chrome_driver_path = config.get("chrome_driver_path")
    if not os.path.exists(chrome_driver_path):
        print_error(f"ChromeDriver not found at {chrome_driver_path}")
        return None

    options = Options()
    if config.get("headless", False):
        options.add_argument("--headless")

    options.add_argument("--start-maximized")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    # To enable printing to PDF later
    options.add_argument('--enable-print-browser')

    # Enable browser logging
    options.set_capability('goog:loggingPrefs', {'browser': 'ALL'})

    try:
        service = Service(executable_path=chrome_driver_path)
        driver = webdriver.Chrome(service=service, options=options)
        print_success("Browser initialized successfully.")
        return driver
    except Exception as e:
        print_error(f"Failed to initialize browser: {e}")
        return None

