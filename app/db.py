from pathlib import Path
import os

import psycopg
from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")


def get_connection() -> psycopg.Connection:
    """Open a PostgreSQL connection using the project's environment settings."""
    return psycopg.connect(
        host=os.environ.get("DB_HOST", "localhost"),
        port=int(os.environ.get("DB_PORT", "5432")),
        dbname=os.environ.get("DB_NAME", "postgres"),
        user=os.environ.get("DB_USER", "analyst"),
        password=os.environ.get("DB_PASSWORD", "abcd"),
    )
