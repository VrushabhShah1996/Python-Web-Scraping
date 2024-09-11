import time
import logging
import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException


def init_driver():
    """Initialize and return a Selenium WebDriver with randomized user-agent."""
    options = Options()
    # options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")

    # Rotate user agents to avoid getting blocked
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36"
    ]
    options.add_argument(f"user-agent={random.choice(user_agents)}")

    retry_attempts = 3
    while retry_attempts > 0:
        try:
            logging.info("Initializing WebDriver...")
            driver = webdriver.Chrome(options=options)
            logging.info("WebDriver initialized successfully.")
            return driver
        except WebDriverException as e:
            logging.error(f"WebDriver initialization failed: {e}")
            retry_attempts -= 1
            logging.info(f"Retrying WebDriver initialization... {retry_attempts} attempts left.")
            time.sleep(5)

    raise RuntimeError("Failed to initialize WebDriver after multiple attempts.")
