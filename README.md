# AutoRia Scraper

## Description

This is a web scraping application that collects data about used cars from AutoRia.com using Selenium and stores it in a
PostgreSQL database. The application runs daily at 12:00 EEST, creates database dumps, and logs activities. It is
containerized using Docker and scheduled via `cron`.

## Project Structure

- `main.py`: Entry point, orchestrates scraping and database dumps.
- `utils/`: Utility modules.
    - `database.py`: Database initialization and data insertion.
    - `dumper.py`: Creates PostgreSQL database dumps.
    - `logger.py`: Configures logging to `logs/scraper.log`.
- `scrapers/`: Modules for scraping specific data fields (e.g., `title.py`, `price.py`).
- `Dockerfile`: Docker configuration for the scraper.
- `docker-compose.yml`: Docker Compose configuration for `db` (PostgreSQL) and `app` (scraper).
- `cron_script.sh`: Script executed by `cron` to run `main.py`.
- `.env`: Environment variables.
- `requirements.txt`: Python dependencies.
- `logs/`: Directory for logs (`scraper.log`).
- `dumps/`: Directory for database dumps (`autoria_dump_YYYYMMDD.sql`).

## Prerequisites

- Docker Desktop (Windows/Mac) or Docker (Linux).
- Docker Compose.
- Git (optional, for cloning the repository).

## Setup and Running

### 1. Clone the Repository

```bash
git clone --branch selenium https://github.com/valerii-kashpur/scrap-used-auto.git
cd scrap-used-auto
```

### 2. Create Environment File

Create a `.env` file in the project root with the following content:

```
POSTGRES_HOST=db
POSTGRES_PORT=5432
POSTGRES_DB=autoria
POSTGRES_USER=autoria_user
POSTGRES_PASSWORD=autoria_pass
SCRAPING_TIME=12:00
```

### 3. Create Directories for Logs and Dumps

```bash
mkdir logs dumps
```

### 4. Build and Run the Application

Build and start the containers in detached mode:

```bash
docker-compose build
docker-compose up -d
```

The application will:

- Run the scraper daily at 12:00 EEST (configured via `cron`).
- Store data in the PostgreSQL database (`car_listings` table).
- Create database dumps daily at 12:00 EEST in `dumps/autoria_dump_YYYYMMDD.sql`.
- Log activities to `logs/scraper.log`.

### 5. Verify Containers

Check that the containers are running:

```bash
docker ps
```

Expected output:

```
CONTAINER ID   IMAGE                     COMMAND                  STATUS         PORTS      NAMES
<id>           postgres:16               "docker-entrypoint.s…"   Up             5432/tcp   scrap-used-auto_db_1
<id>           scrap-used-auto_app       "cron -f"                Up                        scrap-used-auto_app_1
```

## Checking Logs and Dump (Manual Test)

To verify that the scraper works without waiting for 12:00, run `main.py` manually and check the logs and dump.

### 1. Run the Scraper Manually

```bash
docker exec scrap-used-auto_app_1 python /app/main.py
```

Observe console output, e.g.:

```
Navigating to page 0: https://auto.ria.com/uk/search/?lang_id=4&countpage=100&indexName=auto&custom=1&abroad=2&page=0
Found 100 listing URLs on page 0
Navigating to https://auto.ria.com/uk/auto_peugeot_traveller_38248641.html
title text: Peugeot Traveller 2020
...
```

### 2. Check Logs

Verify that `scraper.log` was created and contains the expected entries:

```bash
dir logs
type logs\scraper.log
```

Expected content:

```
2025-06-06 16:45:00,123 INFO: Selenium driver initialized in headless mode
2025-06-06 16:45:01,124 INFO: Navigating to page 0: https://auto.ria.com/uk/search/?lang_id=4&countpage=100&indexName=auto&custom=1&abroad=2&page=0
...
2025-06-06 16:50:00,126 INFO: Selenium driver and database connection closed
2025-06-06 16:50:00,127 INFO: Starting database dump
2025-06-06 16:50:00,128 INFO: Creating dump file: /app/dumps/autoria_dump_20250606.sql
2025-06-06 16:50:00,129 INFO: Dump created successfully: /app/dumps/autoria_dump_20250606.sql
2025-06-06 16:50:00,130 INFO: Database dump completed
```

### 3. Check Database Dump

Verify that the dump file was created:

```bash
dir dumps
type dumps\autoria_dump_20250606.sql
```

Expected content:

```
CREATE TABLE car_listings (
    id SERIAL PRIMARY KEY,
    url TEXT UNIQUE,
    ...
);
INSERT INTO car_listings (url, title, ...) VALUES ('https://auto.ria.com/...', 'Peugeot Traveller 2020', ...);
```

## Stopping the Application

To stop and remove the containers:

```bash
docker-compose down
```

## Database Schema

The application stores data in a PostgreSQL table `car_listings` with the following fields:

- `id` (SERIAL, PRIMARY KEY)
- `url` (TEXT, UNIQUE)
- `title` (TEXT)
- `price_usd` (INTEGER)
- `odometer` (INTEGER)
- `username` (TEXT)
- `phone_number` (TEXT)
- `image_url` (TEXT)
- `images_count` (INTEGER)
- `car_number` (TEXT)
- `car_vin` (TEXT)
- `datetime_found` (TIMESTAMP)

## Troubleshooting

- **No logs created**:
    - Check container logs: `docker logs scrap-used-auto-app-1`.
    - Verify `utils/logger.py` uses `/app/logs`.
    - Check permissions: `icacls logs`.

- **No dump created**:
    - Check `logs/scraper.log` for errors after `Starting database dump`.
    - Verify `pg_dump` version: `docker exec scrap-used-auto_app-1 pg_dump --version` (should be 16.9+).
    - Test database connection: `docker exec scrap-used-auto_app-1 psql -h db -U autoria_user -d autoria -c "SELECT 1"`.

- **Cron not running**:
    - Check cron configuration: `docker exec scrap-used-auto-app-1 crontab -l`.
    - Check cron logs: `docker exec scrap-used-auto-app-1 cat /app/logs/cron.log`.