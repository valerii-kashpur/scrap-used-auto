import time

from selenium.webdriver.common.by import By

from utils.logger import logger


def scrape_phone_number(driver, url):
    try:
        show_phone_button = driver.find_element(By.CSS_SELECTOR, "span.phone.bold")
        show_phone_button.click()
        time.sleep(0.1)
        return driver.find_element(By.CSS_SELECTOR, "span.phone.bold").text
    except:
        logger.warning(f"Phone number not found for {url}")
        return None
