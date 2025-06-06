from selenium.webdriver.common.by import By

from utils.logger import logger


def scrape_car_vin(driver, url):
    selectors = [".label-vin", ".vin-code"]
    for selector in selectors:
        try:
            elem = driver.find_element(By.CSS_SELECTOR, selector)
            text = elem.text.strip()
            if text:
                return text
        except:
            continue
    logger.warning(f"Car VIN not found for {url}")
    return None
