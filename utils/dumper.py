import os
import subprocess
from datetime import datetime

from dotenv import load_dotenv

from utils.logger import logger

load_dotenv()


def perform_dump():
    try:
        db_name = os.getenv("POSTGRES_DB")
        db_user = os.getenv("POSTGRES_USER")
        db_password = os.getenv("POSTGRES_PASSWORD")
        db_host = os.getenv("POSTGRES_HOST")
        db_port = os.getenv("POSTGRES_PORT")

        if not all([db_name, db_user, db_password, db_host, db_port]):
            logger.error("Missing one or more PostgreSQL environment variables")
            return

        dump_dir = "/app/dumps"
        if not os.path.exists(dump_dir):
            os.makedirs(dump_dir)
            logger.info(f"Created directory {dump_dir}")

        dump_file = os.path.join(
            dump_dir, f"autoria_dump_{datetime.now().strftime('%Y%m%d')}.sql"
        )
        logger.info(f"Creating dump file: {dump_file}")

        try:
            result = subprocess.run(
                ["pg_dump", "--version"], capture_output=True, text=True, check=True
            )
            logger.info(f"pg_dump is available: {result.stdout.strip()}")
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            logger.error(f"pg_dump is not installed or not found: {e}")
            logger.info("Ensure pg_dump is installed in the Docker image")
            return

        command = [
            "pg_dump",
            f"--dbname=postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}",
            "-f",
            dump_file,
        ]

        result = subprocess.run(command, capture_output=True, text=True, check=True)
        logger.info(f"Dump created successfully: {dump_file}")
        logger.debug(f"pg_dump output: {result.stdout}")

    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to create dump: {e.stderr}")
    except Exception as e:
        logger.error(f"Unexpected error in perform_dump: {e}")
