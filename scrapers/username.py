from selenium.webdriver.common.by import By

from utils.logger import logger


def scrape_username(driver, url):
    selectors = [".seller_info_name", ".seller_info_title"]
    for selector in selectors:
        try:
            elem = driver.find_element(By.CSS_SELECTOR, selector)
            text = elem.text.strip()
            if text:
                return text
        except:
            continue
    logger.warning(f"Username not found for {url}")
    return None
