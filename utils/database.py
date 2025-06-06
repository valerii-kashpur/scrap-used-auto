import os

import psycopg2
from dotenv import load_dotenv

from utils.logger import logger

load_dotenv()


def init_database():
    try:
        conn = psycopg2.connect(
            dbname=os.getenv("POSTGRES_DB"),
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD"),
            host=os.getenv("POSTGRES_HOST", "db"),
            port=os.getenv("POSTGRES_PORT"),
        )
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS car_listings (
                id SERIAL PRIMARY KEY,
                url TEXT UNIQUE,
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
        """)
        conn.commit()

        cursor.execute("SELECT url FROM car_listings")
        existing_urls = {row[0] for row in cursor.fetchall()}

        logger.info("Database initialized successfully")
        return conn, existing_urls
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise


def insert_into_database(conn, data):
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO car_listings (
                url, title, price_usd, odometer, username, phone_number,
                image_url, images_count, car_number, car_vin, datetime_found
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
            (
                data["url"],
                data["title"],
                data["price_usd"],
                data["odometer"],
                data["username"],
                data["phone_number"],
                data["image_url"],
                data["images_count"],
                data["car_number"],
                data["car_vin"],
                data["datetime_found"],
            ),
        )
        conn.commit()
        logger.info(f"Inserted data for {data['url']}")
    except Exception as e:
        logger.error(f"Error inserting data for {data['url']}: {e}")
        conn.rollback()
