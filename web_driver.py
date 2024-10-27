from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import random
import time

from assets import HEADLESS_OPTIONS, HEADLESS_OPTIONS_DOCKER, USER_AGENTS
from utils import is_running_in_docker

def setup_selenium(attended_mode: bool = False) -> webdriver.Chrome:
    """Set up and configure Selenium WebDriver."""
    options = Options()
    service = Service(ChromeDriverManager().install())
    
    # Apply appropriate headless options
    headless_options = HEADLESS_OPTIONS_DOCKER if is_running_in_docker() else HEADLESS_OPTIONS
    for option in headless_options:
        options.add_argument(option)
    
    # Set random user agent
    options.add_argument(f'user-agent={random.choice(USER_AGENTS)}')
    
    return webdriver.Chrome(service=service, options=options)

def fetch_page_content(url: str, driver: webdriver.Chrome = None, attended_mode: bool = False) -> str:
    """Fetch page content using Selenium."""
    should_quit = False
    if driver is None:
        driver = setup_selenium(attended_mode)
        should_quit = True
    
    try:
        if not attended_mode:
            driver.get(url)
            # Simulate realistic scrolling
            scroll_positions = [2, 1.2, 1]
            for pos in scroll_positions:
                driver.execute_script(f"window.scrollTo(0, document.body.scrollHeight/{pos});")
                time.sleep(random.uniform(1.1, 1.8))
        
        return driver.page_source
    finally:
        if should_quit:
            driver.quit()