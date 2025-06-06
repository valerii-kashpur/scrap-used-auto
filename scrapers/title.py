from selenium.webdriver.common.by import By

from utils.logger import logger


def scrape_title(driver, url):
    print("title")
    try:
        elem = driver.find_element(By.CSS_SELECTOR, "h1.head")
        print("title elem:", elem)
        text = driver.find_element(By.CSS_SELECTOR, "h1.head").text
        print("title text:", text)
        return text
    except:
        print("no title")
        logger.warning(f"Title not found for {url}")
        return None
