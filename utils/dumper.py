import os
import subprocess
from datetime import datetime

from utils.logger import logger


def perform_dump():
    try:
        dump_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'dumps')
        os.makedirs(dump_dir, exist_ok=True)
        dump_file = os.path.join(dump_dir, f"dump_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql")
        os.environ['PGPASSWORD'] = 'autoria_pass'
        subprocess.run([
            'pg_dump',
            '-U', 'autoria_user',
            '-h', 'localhost',
            '-f', dump_file,
            'autoria'
        ], check=True)
        logger.info(f"Database dump created: {dump_file}")
    except Exception as e:
        logger.error(f"Error creating database dump: {e}")
