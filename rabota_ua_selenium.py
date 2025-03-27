import time
import os

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up logging
from utils.logger import setup_logger
logger = setup_logger()

USERNAME = os.getenv("ROBOTA_USERNAME")
PASSWORD = os.getenv("ROBOTA_PASSWORD")
PROFILE_NAME = "Dan Chuzhov"  # Profile name to check

chrome_options = Options()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
# Put the path to your chromedriver file here
service = Service("C:/Users/reach/Downloads/chromedriver-win32/chromedriver.exe")

try:
    logger.info("Starting browser")
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    logger.info(f"Navigating to login page")
    driver.get('https://robota.ua/auth/login')
    time.sleep(5)  # Let the page load

    try:
        # Input username
        logger.info("Entering username")
        username_input = driver.find_element(By.ID, 'otp-username')
        username_input.send_keys(USERNAME)
        username_input.send_keys('\n')  # Press Enter to validate the email
        time.sleep(5)  # Wait for the password field to appear

        # Input password
        logger.info("Entering password")
        password_input = driver.find_element(By.CSS_SELECTOR, 'input[type="password"]')
        password_input.send_keys(PASSWORD)

        # Submit the login form
        logger.info("Clicking login button")
        login_button = driver.find_element(By.CSS_SELECTOR, 'button[type="button"]')
        login_button.click()
        time.sleep(5)  # Let the page load after login

    except NoSuchElementException as e:
        logger.error(f"Element not found during login: {e}")
        raise

    # =======================================================================================

    try:
        logger.info("Navigating to profile page")
        driver.get('https://robota.ua/my/profile')
        time.sleep(5)  # Let the page load after login
        
        logger.info("Looking for 'Підняти в пошуку' buttons")
        buttons = driver.find_elements(By.XPATH, "//button[contains(text(), 'Підняти в пошуку')]")
        
        if not buttons:
            logger.info("No 'Підняти в пошуку' buttons found")
        else:
            logger.info(f"Found {len(buttons)} 'Підняти в пошуку' buttons")
            
        for button in buttons:
            driver.execute_script("arguments[0].scrollIntoView(true);", button)
            time.sleep(1)  # Wait for the element to be in view
            driver.execute_script("arguments[0].click();", button)
            logger.info('Clicked "Підняти в пошуку" button')
            time.sleep(2)  # Wait a bit between clicks
            
    except NoSuchElementException as e:
        logger.error(f"Element not found on profile page: {e}")
        raise

except Exception as e:
    logger.error(f"An error occurred: {str(e)}", exc_info=True)
    raise

finally:
    time.sleep(5)  # Let the user actually see something!
    try:
        logger.info("Closing browser")
        driver.quit()
    except Exception as e:
        logger.error(f"Error while closing browser: {str(e)}")