from selenium.webdriver.common.by import By

from utils.logger import logger


def scrape_car_vin(driver, url):
    try:
        return driver.find_element(By.CSS_SELECTOR, "span.label-vin").text
    except:
        logger.warning(f"Car VIN not found for {url}")
        return None
