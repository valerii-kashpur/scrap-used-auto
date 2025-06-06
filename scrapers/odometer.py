from selenium.webdriver.common.by import By

from utils.logger import logger


def scrape_odometer(driver, url):
    try:
        odometer_text = driver.find_element(By.CSS_SELECTOR, "div.base-information.bold").text
        if 'тис.' in odometer_text:
            number = float(odometer_text.split()[0].replace(',', '.'))
            return int(number * 1000)
        else:
            return int(odometer_text.replace(',', '').split()[0])
    except:
        logger.warning(f"Odometer not found for {url}")
        return None
