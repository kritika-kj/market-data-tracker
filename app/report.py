from __future__ import annotations

import argparse
import json
from pathlib import Path

from app.market_db import get_fund_id, get_nav_history


PROJECT_ROOT = Path(__file__).resolve().parent.parent
REPORT_FILE = PROJECT_ROOT / "data" / "nav_view.html"


def create_nav_view(scheme_code: str) -> Path:
    fund_id = get_fund_id(scheme_code)
    history = get_nav_history(fund_id)
    if not history:
        raise ValueError(f"No NAV history is stored for scheme {scheme_code}")

    labels = [nav_date.isoformat() for nav_date, _ in history]
    values = [float(nav) for _, nav in history]
    html = _build_html(scheme_code, labels, values)
    REPORT_FILE.parent.mkdir(exist_ok=True)
    REPORT_FILE.write_text(html, encoding="utf-8")
    return REPORT_FILE


def _build_html(scheme_code: str, labels: list[str], values: list[float]) -> str:
    labels_json = json.dumps(labels)
    values_json = json.dumps(values)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>NAV View - {scheme_code}</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 0; background: #f5f7fb; color: #172033; }}
    main {{ max-width: 1100px; margin: 40px auto; padding: 28px; background: white; border-radius: 12px; }}
    h1 {{ margin-top: 0; }}
    .chart-container {{ height: 520px; }}
  </style>
</head>
<body>
  <main>
    <h1>NAV history</h1>
    <p>Scheme code: <strong>{scheme_code}</strong></p>
    <div class="chart-container"><canvas id="navChart"></canvas></div>
  </main>
  <script>
    new Chart(document.getElementById('navChart'), {{
      type: 'line',
      data: {{
        labels: {labels_json},
        datasets: [{{
          label: 'NAV',
          data: {values_json},
          borderColor: '#2563eb',
          backgroundColor: 'rgba(37, 99, 235, 0.12)',
          fill: true,
          pointRadius: 0,
          tension: 0.2
        }}]
      }},
      options: {{
        responsive: true,
        maintainAspectRatio: false,
        scales: {{
          x: {{ title: {{ display: true, text: 'Date' }} }},
          y: {{ title: {{ display: true, text: 'NAV' }} }}
        }}
      }}
    }});
  </script>
</body>
</html>
"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Create an HTML NAV chart from stored data")
    parser.add_argument("scheme_code", nargs="?", default="119551")
    args = parser.parse_args()
    report_file = create_nav_view(args.scheme_code)
    print(f"Created NAV view: {report_file}")


if __name__ == "__main__":
    main()