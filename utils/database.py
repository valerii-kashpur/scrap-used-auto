import psycopg2
from utils.logger import logger


def create_table(conn):
    try:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS car_listings (
                id SERIAL PRIMARY KEY,
                url VARCHAR(255) UNIQUE,
                title VARCHAR(255),
                price_usd FLOAT,
                odometer INTEGER,
                username VARCHAR(255),
                phone_number VARCHAR(50),
                image_url VARCHAR(255),
                images_count INTEGER,
                car_number VARCHAR(50),
                car_vin VARCHAR(50),
                datetime_found TIMESTAMP
            );
        """)
        conn.commit()
        cur.close()
        logger.info("Table car_listings created or already exists")
    except Exception as e:
        logger.error(f"Error creating table: {e}")
        conn.rollback()


def init_database():
    try:
        conn = psycopg2.connect(
            dbname="autoria",
            user="autoria_user",
            password="autoria_pass",
            host="localhost",
            port="5432"
        )
        create_table(conn)
        cur = conn.cursor()
        cur.execute("SELECT url FROM car_listings")
        existing_urls = set(row[0] for row in cur.fetchall())
        cur.close()
        logger.info("Database initialized, retrieved existing URLs")
        return conn, existing_urls
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


def insert_into_database(conn, data):
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO car_listings (url, title, price_usd, odometer, username, phone_number, image_url, images_count, car_number, car_vin, datetime_found)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (data['url'], data['title'], data['price_usd'], data['odometer'], data['username'], data['phone_number'],
              data['image_url'], data['images_count'], data['car_number'], data['car_vin'], data['datetime_found']))
        conn.commit()
        cur.close()
        logger.info(f"Inserted data for {data['url']}")
    except Exception as e:
        logger.error(f"Error inserting data for {data['url']}: {e}")
        conn.rollback()
