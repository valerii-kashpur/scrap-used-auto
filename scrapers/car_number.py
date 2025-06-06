from selenium.webdriver.common.by import By

from utils.logger import logger


def scrape_car_number(driver, url):
    try:
        return driver.find_element(By.CSS_SELECTOR, "span.state-num").text
    except:
        logger.warning(f"Car number not found for {url}")
        return None
