from __future__ import annotations

import argparse

from app.market_api import fetch_fund
from app.market_db import get_recent_nav, one_year_min_max_nav, save_fund


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch and store mutual fund NAV history")
    parser.add_argument("scheme_code", nargs="?", default="119551")
    args = parser.parse_args()

    fund = fetch_fund(args.scheme_code)
    fund_id = save_fund(fund)
    recent_nav = get_recent_nav(fund_id)

    print(f"Fund: {fund.scheme_name}")
    print(f"Scheme code: {fund.scheme_code}")
    print(f"Stored NAV records: {len(fund.nav_records)}")
    print("Recent NAV:")
    for nav_date, nav in recent_nav:
        print(f"  {nav_date}: {nav}")

    one_year_low_high = one_year_min_max_nav(fund_id, end_date='2025-10-31')
    print("\nOne-year low and high NAVs:")
    for max_nav, min_nav, fund_id in one_year_low_high:
        print(f"  Fund {fund_id}: low={min_nav:.6f}, high={max_nav:.6f}")


if __name__ == "__main__":
    main()