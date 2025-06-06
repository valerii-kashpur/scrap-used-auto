from selenium.webdriver.common.by import By

from utils.logger import logger


def scrape_image_url(driver, url):
    try:
        return driver.find_element(
            By.CSS_SELECTOR, "div.photo-620x465.loaded img"
        ).get_attribute("src")
    except:
        logger.warning(f"Image URL not found for {url}")
        return None
