import scrapy
import psycopg2
from datetime import datetime
import re
from urllib.parse import urlencode, parse_qs, urlparse


class AutoriaSpider(scrapy.Spider):
    name = "autoria_spider"
    start_urls = [
        "https://auto.ria.com/uk/search/?lang_id=4&page=0&countpage=100&indexName=auto&custom=1&abroad=2"
    ]

    custom_settings = {
        "CONCURRENT_REQUESTS": 8,
        "DOWNLOAD_DELAY": 3,
        "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "DEFAULT_REQUEST_HEADERS": {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        },
    }

    def __init__(self, *args, **kwargs):
        super(AutoriaSpider, self).__init__(*args, **kwargs)

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(AutoriaSpider, cls).from_crawler(crawler, *args, **kwargs)
        spider.conn = psycopg2.connect(
            host=crawler.settings.get("POSTGRES_HOST"),
            port=crawler.settings.get("POSTGRES_PORT"),
            dbname=crawler.settings.get("POSTGRES_DB"),
            user=crawler.settings.get("POSTGRES_USER"),
            password=crawler.settings.get("POSTGRES_PASSWORD"),
        )
        spider.cursor = spider.conn.cursor()
        spider.create_table()
        spider.clear_table()
        return spider

    def create_table(self):
        create_table_query = """
        CREATE TABLE IF NOT EXISTS cars (
            url TEXT PRIMARY KEY,
            title TEXT,
            price_usd INTEGER,
            odometer INTEGER,
            username TEXT,
            phone_number TEXT,
            image_url TEXT,
            images_count INTEGER,
            car_number TEXT,
            car_vin TEXT,
            datetime_found TIMESTAMP
        )
        """
        self.cursor.execute(create_table_query)
        self.conn.commit()

    def clear_table(self):
        self.logger.info("Clearing table 'cars' before scraping")
        self.cursor.execute("TRUNCATE TABLE cars")
        self.conn.commit()

    def parse(self, response):
        try:
            car_links = response.css(
                "div.content-bar a.m-link-ticket::attr(href)"
            ).getall()
            self.logger.info(
                f"Found {len(car_links)} car links on page: {response.url}"
            )
            for link in car_links:
                yield response.follow(link, callback=self.parse_car)

            next_page_disabled = response.css("a.page-link.js-next.disabled").get()
            if next_page_disabled:
                self.logger.info("Next page button is disabled, stopping pagination")
                return

            parsed_url = urlparse(response.url)
            params = parse_qs(parsed_url.query)
            current_page = int(params.get("page", ["0"])[0])
            next_page = current_page + 1

            params["page"] = [str(next_page)]
            next_page_url = parsed_url._replace(
                query=urlencode(params, doseq=True)
            ).geturl()
            self.logger.info(f"Following next page: {next_page_url}")
            yield response.follow(next_page_url, callback=self.parse)

        except Exception as e:
            self.logger.error(f"Error in parse: {str(e)}")

    def parse_car(self, response):
        try:
            url = response.url
            self.cursor.execute("SELECT url FROM cars WHERE url = %s", (url,))
            if self.cursor.fetchone():
                self.logger.info(f"Skipping duplicate: {url}")
                return

            title = response.css("h1.head::text").get(default="").strip()

            price_usd = response.css("div.price_value strong::text").get(default="0")
            price_usd = int("".join(filter(str.isdigit, price_usd)))

            odometer_raw = response.css("div.base-information span::text").get(
                default="0"
            )
            odometer = int("".join(filter(str.isdigit, odometer_raw))) * 1000

            username = (
                response.css("div.seller_info_area h4.seller_info_name a::text")
                .get(default="")
                .strip()
            )
            if not username:
                username = (
                    response.css("div.seller_info_name a.sellerPro::text")
                    .get(default="")
                    .strip()
                )
                if not username:
                    username = (
                        response.css("div.seller_info_name::text")
                        .get(default="")
                        .strip()
                    )

            phone_script = response.css('script:contains("phone")::text').get()
            phone_number = ""
            if phone_script:
                phone_match = re.search(r"\+380\d{9}", phone_script)
                if phone_match:
                    phone_number = phone_match.group()
                else:
                    self.logger.warning(
                        f"No phone number pattern found in script for URL: {url}"
                    )

            image_url = response.css("div.photo-620x465 picture img::attr(src)").get(
                default=""
            )

            images_count_text = response.css("a.show-all.link-dotted::text").get(
                default=""
            )
            images_count = (
                int(re.search(r"\d+", images_count_text).group())
                if re.search(r"\d+", images_count_text)
                else 0
            )

            car_number = response.css("span.state-num::text").get(default="").strip()

            car_vin = response.css("span.label-vin::text").get(default="").strip()
            if not car_vin:
                car_vin_elements = response.css("span.label-vin *::text").getall()
                car_vin = "".join(filter(None, car_vin_elements)).strip()
            if not car_vin:
                car_vin = response.css("span.vin-code::text").get(default="").strip()

            item = {
                "url": url,
                "title": title,
                "price_usd": price_usd,
                "odometer": odometer,
                "username": username,
                "phone_number": phone_number,
                "image_url": image_url,
                "images_count": images_count,
                "car_number": car_number,
                "car_vin": car_vin,
                "datetime_found": datetime.now(),
            }

            self.save_to_db(item)
            yield item

        except Exception as e:
            self.logger.error(f"Error in parse_car for URL {response.url}: {str(e)}")

    def save_to_db(self, item):
        insert_query = """
        INSERT INTO cars (url, title, price_usd, odometer, username, phone_number, 
                        image_url, images_count, car_number, car_vin, datetime_found)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        self.cursor.execute(
            insert_query,
            (
                item["url"],
                item["title"],
                item["price_usd"],
                item["odometer"],
                item["username"],
                item["phone_number"],
                item["image_url"],
                item["images_count"],
                item["car_number"],
                item["car_vin"],
                item["datetime_found"],
            ),
        )
        self.conn.commit()

    def closed(self, reason):
        self.cursor.close()
        self.conn.close()
