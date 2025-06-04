import scrapy
import psycopg2
from datetime import datetime
import logging
from urllib.parse import urljoin


class AutoriaSpider(scrapy.Spider):
    name = 'autoria_spider'
    start_urls = ['https://auto.ria.com/uk/car/used/']
    custom_settings = {
        'CONCURRENT_REQUESTS': 16,
        'DOWNLOAD_DELAY': 1,
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    def __init__(self, *args, **kwargs):
        super(AutoriaSpider, self).__init__(*args, **kwargs)

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(AutoriaSpider, cls).from_crawler(crawler, *args,
                                                        **kwargs)
        spider.conn = psycopg2.connect(
            host=crawler.settings.get('POSTGRES_HOST'),
            port=crawler.settings.get('POSTGRES_PORT'),
            dbname=crawler.settings.get('POSTGRES_DB'),
            user=crawler.settings.get('POSTGRES_USER'),
            password=crawler.settings.get('POSTGRES_PASSWORD')
        )
        spider.cursor = spider.conn.cursor()
        spider.create_table()
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

    def parse(self, response):
        # Extract car links
        car_links = response.css(
            'div.content-bar a.m-link-ticket::attr(href)').getall()
        for link in car_links:
            yield response.follow(link, callback=self.parse_car)

        # Follow pagination
        next_page = response.css('a.page-link::attr(href)').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_car(self, response):
        url = response.url
        self.cursor.execute("SELECT url FROM cars WHERE url = %s", (url,))
        if self.cursor.fetchone():
            self.logger.info(f"Skipping duplicate: {url}")
            return

        title = response.css('h1.head::text').get(default='').strip()

        price_usd = response.css('div.price_value strong::text').get(
            default='0')
        price_usd = int(''.join(filter(str.isdigit, price_usd)))

        odometer = response.css('div.base-information span::text').get(
            default='0')
        odometer = int(''.join(filter(str.isdigit,
                                      odometer))) * 1000 if 'тис.' in odometer else int(
            ''.join(filter(str.isdigit, odometer)))

        username = response.css('div.seller_info_name a.sellerPro::text').get(
            default='').strip()
        if not username:
            username = response.css('div.seller_info_name::text').get(
                default='').strip()

        phone_script = response.css('script:contains("phone")::text').get()
        phone_number = ''
        if phone_script:
            import re
            phone_match = re.search(r'\+380\d{9}', phone_script)
            if phone_match:
                phone_number = phone_match.group()

        image_url = response.css('img.picture::attr(src)').get(default='')
        images_count = len(response.css('img.picture').getall())

        car_number = response.css('span.state-num::text').get(
            default='').strip()
        car_vin = response.css('span.vin-code::text').get(default='').strip()

        item = {
            'url': url,
            'title': title,
            'price_usd': price_usd,
            'odometer': odometer,
            'username': username,
            'phone_number': phone_number,
            'image_url': image_url,
            'images_count': images_count,
            'car_number': car_number,
            'car_vin': car_vin,
            'datetime_found': datetime.now()
        }

        self.save_to_db(item)
        yield item

    def save_to_db(self, item):
        insert_query = """
        INSERT INTO cars (url, title, price_usd, odometer, username, phone_number, 
                        image_url, images_count, car_number, car_vin, datetime_found)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        self.cursor.execute(insert_query, (
            item['url'], item['title'], item['price_usd'], item['odometer'],
            item['username'], item['phone_number'], item['image_url'],
            item['images_count'], item['car_number'], item['car_vin'],
            item['datetime_found']
        ))
        self.conn.commit()

    def closed(self, reason):
        self.cursor.close()
        self.conn.close()