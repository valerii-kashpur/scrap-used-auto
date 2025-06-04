import os
import logging
import subprocess
from datetime import datetime
from dotenv import load_dotenv
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from apscheduler.schedulers.blocking import BlockingScheduler

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

load_dotenv()

def run_spider():
    logger.info("Starting scraping process")
    process = CrawlerProcess(get_project_settings())
    process.crawl('autoria_spider')
    process.start()  # Blocking call

def create_db_dump():
    logger.info("Creating database dump")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dump_file = f"dumps/autoria_dump_{timestamp}.sql"
    os.makedirs('dumps', exist_ok=True)

    command = (
        f"pg_dump -h {os.getenv('POSTGRES_HOST')} "
        f"-U {os.getenv('POSTGRES_USER')} "
        f"-p {os.getenv('POSTGRES_PORT')} "
        f"{os.getenv('POSTGRES_DB')} > {dump_file}"
    )

    try:
        subprocess.run(command, shell=True, check=True, env={
            'PGPASSWORD': os.getenv('POSTGRES_PASSWORD')
        })
        logger.info(f"Database dump created: {dump_file}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to create database dump: {e}")

if __name__ == "__main__":
    scheduler = BlockingScheduler()

    scraping_time = os.getenv('SCRAPING_TIME', '12:00')
    scheduler.add_job(run_spider, 'cron', hour=int(scraping_time.split(':')[0]), minute=int(scraping_time.split(':')[1]))

    dump_time = os.getenv('DUMP_TIME', '12:00')
    scheduler.add_job(create_db_dump, 'cron', hour=int(dump_time.split(':')[0]), minute=int(dump_time.split(':')[1]))

    logger.info(f"Scheduler started. Scraping at {scraping_time}, Dumping at {dump_time}")
    scheduler.start()