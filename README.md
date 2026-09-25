# Market Data Tracker

A small Python and PostgreSQL project that demonstrates:

`API -> Python transformation -> PostgreSQL -> output`

The first component creates the database foundation for mutual fund NAV data.

## Local setup

Create a virtual environment and install dependencies:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Copy `.env.example` to `.env` and set the password for the local `analyst` user. The defaults target:

- Database: `postgres`
- Host: `localhost`
- Port: `5432`
- Schema: `finance`

Initialize the tracker tables:

```powershell
python -m app.init_db
```

This creates `finance.funds` and `finance.nav_prices` without changing an existing `finance.portfolio` table.

Fetch and store one fund's NAV history:

```powershell
python -m app.ingest 119551
```

The command is idempotent: rerunning it updates the fund metadata and does not create duplicate NAV dates.

Create an HTML chart from the stored NAV history:

```powershell
python -m app.report 119551
```

Open `data/nav_view.html` in a browser to view the graph. This reporting layer reads from PostgreSQL and can later be extended with additional views.

See [COMMANDS.txt](COMMANDS.txt) for the complete command reference, including setup, ingestion, reporting, and troubleshooting.

The frontend login page is available at [frontend/login.html](frontend/login.html). For a real authenticated experience, start the Flask application below instead of opening the HTML file directly.

```powershell
Start-Process .\frontend\login.html
```

For real authentication and role-based dashboards, initialize the users table, create a user, and start Flask:

```powershell
python -m app.init_db
python -m app.create_user admin@example.com admin
python -m app.web
```

Then open `http://127.0.0.1:5000`. The user's database role determines the Admin, Analyst, or Viewer dashboard.
