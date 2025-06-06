from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from utils.logger import logger


def scrape_phone_number(driver, url):
    try:
        show_phone_button = driver.find_element(By.CSS_SELECTOR, ".show-phone-button")
        show_phone_button.click()
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".phone")))
        return driver.find_element(By.CSS_SELECTOR, ".phone").text
    except:
        logger.warning(f"Phone number not found for {url}")
        return None
