from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


API_URL = "https://api.mfapi.in/mf/{scheme_code}"


class MarketApiError(RuntimeError):
    """Raised when the mutual fund API response is unavailable or invalid."""


@dataclass(frozen=True)
class NavRecord:
    nav_date: date
    nav: Decimal


@dataclass(frozen=True)
class FundData:
    scheme_code: str
    scheme_name: str
    fund_house: str | None
    nav_records: list[NavRecord]


def fetch_fund(scheme_code: str, timeout: int = 30) -> FundData:
    if not scheme_code.strip():
        raise ValueError("scheme_code must not be empty")

    request = Request(
        API_URL.format(scheme_code=scheme_code.strip()),
        headers={"Accept": "application/json", "User-Agent": "market-data-tracker/1.0"},
    )
    try:
        with urlopen(request, timeout=timeout) as response:
            payload = json.load(response)
        with open ("data/response.json", 'w' ) as f :
            json.dump(payload, f, indent=4)
            
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as error:
        raise MarketApiError(f"Unable to fetch scheme {scheme_code}: {error}") from error

    if payload.get("status") != "SUCCESS":
        raise MarketApiError(payload.get("message") or "The API returned an unsuccessful response")

    metadata = payload.get("meta")
    raw_records = payload.get("data")
    if not isinstance(metadata, dict) or not isinstance(raw_records, list):
        raise MarketApiError("The API response is missing meta or data")

    records = [_parse_nav_record(record) for record in raw_records]
    if not records:
        raise MarketApiError(f"Scheme {scheme_code} returned no NAV records")

    return FundData(
        scheme_code=str(metadata.get("scheme_code") or scheme_code).strip(),
        scheme_name=_required_text(metadata, "scheme_name"),
        fund_house=_optional_text(metadata.get("fund_house")),
        nav_records=records,
    )


def _parse_nav_record(record: object) -> NavRecord:
    if not isinstance(record, dict):
        raise MarketApiError("A NAV record is not an object")

    try:
        nav_date = datetime.strptime(str(record["date"]), "%d-%m-%Y").date()
        nav = Decimal(str(record["nav"]))
    except (KeyError, TypeError, ValueError, InvalidOperation) as error:
        raise MarketApiError(f"Invalid NAV record: {record}") from error

    if nav < 0:
        raise MarketApiError(f"NAV cannot be negative: {record}")
    return NavRecord(nav_date=nav_date, nav=nav)


def _required_text(values: dict[str, object], field: str) -> str:
    value = _optional_text(values.get(field))
    if value is None:
        raise MarketApiError(f"The API response is missing {field}")
    return value


def _optional_text(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None