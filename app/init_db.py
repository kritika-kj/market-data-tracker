from pathlib import Path

from app.db import get_connection


SCHEMA_FILE = Path(__file__).resolve().parent.parent / "sql" / "schema.sql"


def initialize_database() -> None:
    schema_sql = SCHEMA_FILE.read_text(encoding="utf-8")
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(schema_sql)

    print("Database schema is ready: finance.funds, finance.nav_prices")


if __name__ == "__main__":
    initialize_database()
