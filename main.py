from datetime import datetime

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from scrapers.car_number import scrape_car_number
from scrapers.car_vin import scrape_car_vin
from scrapers.image_url import scrape_image_url
from scrapers.images_count import scrape_images_count
from scrapers.odometer import scrape_odometer
from scrapers.phone_number import scrape_phone_number
from scrapers.price import scrape_price
from scrapers.title import scrape_title
from scrapers.username import scrape_username
from utils.database import init_database, insert_into_database
from utils.dumper import perform_dump
from utils.logger import logger


def scrape_car_page(driver, url):
    try:
        driver.get(url)
        data = {
            'url': url,
            'title': scrape_title(driver, url),
            'price_usd': scrape_price(driver, url),
            'odometer': scrape_odometer(driver, url),
            'username': scrape_username(driver, url),
            'phone_number': scrape_phone_number(driver, url),
            'image_url': scrape_image_url(driver, url),
            'images_count': scrape_images_count(driver, url),
            'car_number': scrape_car_number(driver, url),
            'car_vin': scrape_car_vin(driver, url),
            'datetime_found': datetime.now()
        }
        logger.info(f"Scraped data for {url}: {data}")
        return data
    except Exception as e:
        logger.error(f"Error scraping {url}: {e}")
        return None


def main():
    try:
        chrome_options = Options()
        # chrome_options.add_argument('--headless=new')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        driver = webdriver.Chrome(options=chrome_options)
        logger.info("Selenium driver initialized in headless mode")

        conn, existing_urls = init_database()

        initial_url = "https://auto.ria.com/uk/search/?lang_id=4&page=0&countpage=100&indexName=auto&custom=1&abroad=2"
        driver.get(initial_url)
        logger.info(f"Navigated to initial URL: {initial_url}")

        while True:
            urls = [a.get_attribute('href') for a in
                    driver.find_elements(By.XPATH, '//a[contains(@href, "/uk/auto_") and contains(@href, ".html")]')]
            logger.info(f"Found {len(urls)} listing URLs on current page")

            for url in urls:
                if url not in existing_urls:
                    data = scrape_car_page(driver, url)
                    if data and any(value is not None for key, value in data.items() if key != 'datetime_found'):
                        insert_into_database(conn, data)
                        existing_urls.add(url)

            try:
                next_button = driver.find_element(By.CSS_SELECTOR, ".page-item.next.text-r a.page-link.js-next")
                if "disabled" not in next_button.get_attribute("class"):
                    next_button.click()
                    WebDriverWait(driver, 10).until(EC.staleness_of(driver.find_element(By.TAG_NAME, "body")))
                    logger.info("Moved to next page")
                else:
                    logger.info("No more pages to scrape")
                    break
            except:
                logger.info("Next button not found, stopping pagination")
                break

        driver.quit()
        conn.close()
        logger.info("Selenium driver and database connection closed")
        perform_dump()
    except Exception as e:
        logger.error(f"Error in main function: {e}")
        if 'driver' in locals():
            driver.quit()
        if 'conn' in locals():
            conn.close()


if __name__ == "__main__":
    main()
