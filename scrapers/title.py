from selenium.webdriver.common.by import By

from utils.logger import logger


def scrape_title(driver, url):
    try:
        return driver.find_element(By.CSS_SELECTOR, "h1.head").text
    except:
        logger.warning(f"Title not found for {url}")
        return None
