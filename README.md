# AutoRia Scraper

## Description
This is a web scraping application that collects data about used cars from AutoRia.com and stores it in a PostgreSQL database. The application runs daily at a specified time and creates database dumps.

## Project Structure
- `main.py`: Entry point, schedules scraping and database dumps
- `autoria/`: Scrapy project directory
  - `spiders/autoria_spider.py`: Spider for scraping AutoRia
  - `settings.py`: Scrapy settings
- `Dockerfile`: Docker configuration for the scraper
- `docker-compose.yml`: Docker Compose configuration
- `.env`: Environment variables
- `requirements.txt`: Python dependencies
- `dumps/`: Directory for database dumps

## Prerequisites
- Docker
- Docker Compose

## Setup and Running
1. Clone the repository:
```bash
git clone <repository_url>
cd <repository_folder>
```

2. Create a `.env` file in the root directory with the following content:
```
POSTGRES_HOST=db
POSTGRES_PORT=5432
POSTGRES_DB=autoria
POSTGRES_USER=autoria_user
POSTGRES_PASSWORD=autoria_pass
SCRAPING_TIME=12:00
DUMP_TIME=12:00
```

3. Build and run the application:
```bash
docker-compose up --build
```

4. The application will:
   - Run the scraper daily at the time specified in SCRAPING_TIME
   - Create database dumps daily at the time specified in DUMP_TIME
   - Store dumps in the `dumps/` directory
   - Log activities to `scraper.log`

## Stopping the Application
To stop the application, run:
```bash
docker-compose down
```

## Database Schema
The application stores data in a PostgreSQL table `cars` with the following fields:
- url (TEXT, PRIMARY KEY)
- title (TEXT)
- price_usd (INTEGER)
- odometer (INTEGER)
- username (TEXT)
- phone_number (TEXT)
- image_url (TEXT)
- images_count (INTEGER)
- car_number (TEXT)
- car_vin (TEXT)
- datetime_found (TIMESTAMP)