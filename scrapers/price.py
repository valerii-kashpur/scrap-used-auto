from selenium.webdriver.common.by import By

from utils.logger import logger


def scrape_price(driver, url):
    try:
        price_text = driver.find_element(By.CSS_SELECTOR, "div.price_value").text
        number = int(
            "".join(char for char in price_text.replace(" ", "") if char.isdigit())
        )
        return number
    except:
        logger.warning(f"Price not found for {url}")
        return None
