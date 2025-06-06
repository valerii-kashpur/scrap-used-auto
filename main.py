from datetime import datetime

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

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
            "url": url,
            "title": scrape_title(driver, url),
            "price_usd": scrape_price(driver, url),
            "odometer": scrape_odometer(driver, url),
            "username": scrape_username(driver, url),
            "phone_number": scrape_phone_number(driver, url),
            "image_url": scrape_image_url(driver, url),
            "images_count": scrape_images_count(driver, url),
            "car_number": scrape_car_number(driver, url),
            "car_vin": scrape_car_vin(driver, url),
            "datetime_found": datetime.now(),
        }
        logger.info(f"Scraped data for {url}: {data}")
        return data
    except Exception as e:
        logger.error(f"Error scraping {url}: {e}")
        return None


def scrape_page(driver, conn, existing_urls, base_url, page_num):
    try:
        url = f"{base_url}&page={page_num}"
        driver.get(url)
        urls = [
            a.get_attribute("href")
            for a in driver.find_elements(
                By.XPATH,
                '//a[contains(@href, "/uk/auto_") and contains(@href, ".html")]',
            )
        ]
        logger.info(f"Found {len(urls)} listing URLs on page {page_num}")

        if not urls:
            logger.info(f"No listings found on page {page_num}, stopping pagination")
            return

        for url in urls:
            if url not in existing_urls:
                data = scrape_car_page(driver, url)
                if data and any(
                    value is not None
                    for key, value in data.items()
                    if key != "datetime_found"
                ):
                    insert_into_database(conn, data)
                    existing_urls.add(url)

        scrape_page(driver, conn, existing_urls, base_url, page_num + 1)
    except Exception as e:
        logger.error(f"Error scraping page {page_num}: {e}")


def main():
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), options=chrome_options
        )
        logger.info("Selenium driver initialized in headless mode")

        conn, existing_urls = init_database()

        base_url = "https://auto.ria.com/uk/search/?lang_id=4&countpage=100&indexName=auto&custom=1&abroad=2"
        scrape_page(driver, conn, existing_urls, base_url, 0)

        driver.quit()
        conn.close()
        logger.info("Selenium driver and database connection closed")
        logger.info("Starting database dump")
        perform_dump()
        logger.info("Database dump completed")
    except Exception as e:
        logger.error(f"Error in main function: {e}")
        if "driver" in locals():
            driver.quit()
        if "conn" in locals():
            conn.close()


if __name__ == "__main__":
    main()
