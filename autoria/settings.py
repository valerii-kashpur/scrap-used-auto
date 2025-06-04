BOT_NAME = 'autoria'

SPIDER_MODULES = ['autoria.spiders']
NEWSPIDER_MODULE = 'autoria.spiders'

ROBOTSTXT_OBEY = True
CONCURRENT_REQUESTS = 8
DOWNLOAD_DELAY = 3
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'

import os
POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'localhost')
POSTGRES_PORT = os.getenv('POSTGRES_PORT', '5432')
POSTGRES_DB = os.getenv('POSTGRES_DB', 'autoria')
POSTGRES_USER = os.getenv('POSTGRES_USER', 'autoria_user')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'autoria_pass')

LOG_LEVEL = 'INFO'
LOG_FILE = 'scraper.log'