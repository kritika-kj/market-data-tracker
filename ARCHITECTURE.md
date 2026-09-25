# Architecture

The tracker is a small command-line ingestion pipeline. It fetches one mutual fund's NAV history, validates and transforms the response, stores it in PostgreSQL, and prints a recent-history report.

```mermaid
flowchart LR
    User[Developer runs<br/>python -m app.ingest 119551]

    subgraph Python[Python application]
        CLI[app.ingest<br/>CLI orchestrator]
        API[app.market_api<br/>HTTP client + validation]
        Models[FundData + NavRecord<br/>typed Python values]
        DBLayer[app.market_db<br/>upsert + recent query]
        Connection[app.db<br/>dotenv + psycopg connection]
    end

    subgraph External[External systems]
        MFAPI[MFAPI<br/>api.mfapi.in]
        PostgreSQL[(PostgreSQL<br/>finance schema)]
    end

    Output[Terminal report<br/>fund + recent NAV]

    User --> CLI
    CLI --> API
    API -->|GET scheme code| MFAPI
    MFAPI -->|JSON meta + data| API
    API -->|validated objects| Models
    Models --> DBLayer
    DBLayer --> Connection
    Connection -->|SQL| PostgreSQL
    PostgreSQL -->|recent NAV rows| DBLayer
    DBLayer --> CLI
    CLI --> Output

    classDef entry fill:#e8f1ff,stroke:#2f5d9f,stroke-width:2px,color:#102a43
    classDef app fill:#eef8f1,stroke:#3a7d44,stroke-width:1px,color:#173b1a
    classDef external fill:#fff4df,stroke:#b7791f,stroke-width:1px,color:#4a2b00
    classDef output fill:#f8edff,stroke:#7b4397,stroke-width:1px,color:#32143f

    class User entry
    class CLI,API,Models,DBLayer,Connection app
    class MFAPI,PostgreSQL external
    class Output output
```

## How the flow works

1. The user starts `app.ingest` with a mutual fund scheme code.
2. `app.market_api` calls MFAPI and validates the response status, metadata, dates, and NAV values.
3. The API response becomes typed `FundData` and `NavRecord` objects.
4. `app.market_db` upserts the fund and NAV history using the unique scheme code and `(fund_id, nav_date)` constraint.
5. The latest five NAV rows are queried and printed to the terminal.

## Database model

```mermaid
erDiagram
    FUNDS ||--o{ NAV_PRICES : contains

    FUNDS {
        bigint id PK
        varchar scheme_code UK
        text scheme_name
        text fund_house
        timestamptz created_at
    }

    NAV_PRICES {
        bigint id PK
        bigint fund_id FK
        date nav_date UK
        numeric nav
        timestamptz created_at
    }
```

The application deliberately leaves the existing `finance.portfolio` table unchanged. Re-running ingestion updates existing records instead of creating duplicate fund or date rows.
