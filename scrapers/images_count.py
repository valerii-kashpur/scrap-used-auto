import re

from selenium.webdriver.common.by import By

from utils.logger import logger


def scrape_images_count(driver, url):
    try:
        images_text = driver.find_element(By.CSS_SELECTOR, "a.show-all.link-dotted").text
        images_count = int(re.search(r'\d+', images_text).group())
        return images_count
    except:
        logger.warning(f"Images count not found for {url}")
        return None
