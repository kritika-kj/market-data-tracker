from __future__ import annotations

from datetime import date
from decimal import Decimal

from app.db import get_connection
from app.market_api import FundData


def save_fund(fund: FundData) -> int:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO finance.funds (scheme_code, scheme_name, fund_house)
                VALUES (%s, %s, %s)
                ON CONFLICT (scheme_code) DO UPDATE SET
                    scheme_name = EXCLUDED.scheme_name,
                    fund_house = EXCLUDED.fund_house
                RETURNING id
                """,
                (fund.scheme_code, fund.scheme_name, fund.fund_house),
            )
            fund_id = cursor.fetchone()[0]
            cursor.executemany(
                """
                INSERT INTO finance.nav_prices (fund_id, nav_date, nav)
                VALUES (%s, %s, %s)
                ON CONFLICT (fund_id, nav_date) DO UPDATE SET nav = EXCLUDED.nav
                """,
                [(fund_id, record.nav_date, record.nav) for record in fund.nav_records],
            )
    return fund_id

def get_recent_nav(fund_id: int, limit: int = 5) -> list[tuple[date, Decimal]]:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT nav_date, nav
                FROM finance.nav_prices
                WHERE fund_id = %s
                ORDER BY nav_date DESC
                LIMIT %s
                """,
                (fund_id, limit),
            )
            return cursor.fetchall()

def one_year_min_max_nav(fund_id: int, end_date: date = date(2025, 10, 31)):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT max(nav) as max_nav, min(nav) as min_nav,fund_id  
                FROM finance.nav_prices
				where nav_date > %s::date - INTERVAL '1 year' and nav_date<=%s
                and fund_id = %s
				GROUP BY fund_id;
                """,
                (end_date, end_date, fund_id),
            )
            return cursor.fetchall()