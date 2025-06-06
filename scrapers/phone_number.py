import time

from selenium.webdriver.common.by import By

from utils.logger import logger


def scrape_phone_number(driver, url):
    try:
        show_phone_button = driver.find_element(By.CSS_SELECTOR, "span.phone.bold")
        print("before click: ", show_phone_button)
        show_phone_button.click()
        print("after click: ", show_phone_button)
        print("tel: ", driver.find_element(By.CSS_SELECTOR, "span.phone.bold").text)
        time.sleep(0.1)
        # WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, "dev.popup-show-phone")))
        return driver.find_element(By.CSS_SELECTOR, "span.phone.bold").text
    except:
        logger.warning(f"Phone number not found for {url}")
        return None
