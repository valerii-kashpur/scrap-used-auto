from selenium.webdriver.common.by import By

from utils.logger import logger


def scrape_username(driver, url):
    try:
        return driver.find_element(By.CSS_SELECTOR, "div.seller_info_name").text
    except:
        logger.warning(f"Username not found for {url}")
        return None
