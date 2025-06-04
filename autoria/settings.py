BOT_NAME = 'autoria'

SPIDER_MODULES = ['autoria.spiders']
NEWSPIDER_MODULE = 'autoria.spiders'

ROBOTSTXT_OBEY = True
CONCURRENT_REQUESTS = 16
DOWNLOAD_DELAY = 1
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'

POSTGRES_HOST = 'localhost'
POSTGRES_PORT = '5432'
POSTGRES_DB = 'autoria'
POSTGRES_USER = 'autoria_user'
POSTGRES_PASSWORD = 'autoria_pass'

LOG_LEVEL = 'INFO'
LOG_FILE = 'scraper.log'