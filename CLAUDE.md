# Market Data Tracker Project Context

## Project Goal

Build a small portfolio and market data tracker as a college project. The MVP must demonstrate this complete loop:

`Free API -> Python fetch and transform -> PostgreSQL -> Python output`

The initial use case is pulling daily NAV prices for mutual funds. The first version should remain small enough to complete in a few hours.
 
## Planned Technology

- Python
- PostgreSQL
- A free mutual fund NAV API
- `psycopg` for PostgreSQL access
- `python-dotenv` for local configuration

A candidate API for the next component is:

`https://api.mfapi.in/mf/{scheme_code}`

The API client should be verified against the live response format before finalizing its implementation.

## Local PostgreSQL Details

- Host: `localhost`
- Port: `5432`
- Database: `postgres`
- User: `analyst`
- Schema: `finance`
- Local database connection reference: `analyst_rw`

The user can connect successfully using pgAdmin 4. The PostgreSQL server was also confirmed to be listening on port `5432`.

Never commit the database password. It belongs only in the local `.env` file.

## Current Database Decision

An existing table named `finance.portfolio` is present, but it has not been modified. The tracker currently uses two new tables:

- `finance.funds`: mutual fund metadata keyed by `scheme_code`
- `finance.nav_prices`: daily NAV history linked to `finance.funds`

`finance.nav_prices` has a unique constraint on `(fund_id, nav_date)` so repeated ingestion runs do not create duplicate daily prices.

The schema is idempotent and can be run repeatedly.

## Current Project Structure

```text
market-data-tracker/
├── app/
│   ├── __init__.py
│   ├── db.py
│   └── init_db.py
├── sql/
│   └── schema.sql
├── .env.example
├── .gitignore
├── CLAUDE.md
├── README.md
└── requirements.txt
```

A local `.venv` has also been created and dependencies have been installed.

## Existing Components

### `app/db.py`

Loads `.env` from the project root and exposes `get_connection()`, which opens a PostgreSQL connection using these environment variables:

- `DB_HOST`
- `DB_PORT`
- `DB_NAME`
- `DB_USER`
- `DB_PASSWORD`

### `app/init_db.py`

Reads `sql/schema.sql` and applies it to PostgreSQL. Run it with:

```powershell
.\.venv\Scripts\python.exe -m app.init_db
```

### `sql/schema.sql`

Creates the `finance` schema, `finance.funds`, `finance.nav_prices`, and the NAV lookup index if they do not already exist.

## Local Setup

From `C:\Users\kriti\market-data-tracker`:

```powershell
Copy-Item .env.example .env
notepad .env
.\.venv\Scripts\python.exe -m app.init_db
```

The user must set the local PostgreSQL password in `.env` before running the initializer.

Dependencies are declared in `requirements.txt`:

```text
psycopg[binary]
python-dotenv
```

## Validation Already Completed

- PostgreSQL was detected on `localhost:5432`.
- Python modules compiled successfully with `py -m compileall -q app`.
- Dependencies installed successfully in `.venv`.
- `psycopg`, `dotenv`, and the application database module imported successfully.
- No editor diagnostics were reported for `app/db.py` or `app/init_db.py`.

The live schema initialization has not yet been run because the database password was intentionally not provided to the project files or assistant.

## MVP Scope

Keep the first version limited to:

1. Fetch one mutual fund's NAV history from the API.
2. Transform API data into typed Python values.
3. Upsert the fund metadata.
4. Insert new NAV records without duplicates.
5. Print the latest NAV and a small recent-history report.

Do not add authentication, a web UI, portfolio transactions, scheduling, cloud deployment, or advanced analytics until the basic loop works.

## Next Component

Implement the API client and pipeline layer:

1. Add an HTTP client using `requests` or the standard library.
2. Fetch a scheme by code.
3. Validate the response and parse NAV dates and values.
4. Add database write functions for `funds` and `nav_prices`.
5. Add a CLI command that runs API -> transform -> database -> output.
6. Test with one real scheme code.

Later extensions may include multiple funds, holdings and profit/loss calculations, scheduled ingestion, FastAPI endpoints, a Streamlit dashboard, data quality checks, and cloud deployment.

## Working Conventions

- Keep changes focused on the current MVP component.
- Preserve the existing `finance.portfolio` table unless explicitly asked to change it.
- Use parameterized SQL for values.
- Keep secrets out of source control.
- Prefer idempotent database operations.
- Validate each component before starting the next one.
