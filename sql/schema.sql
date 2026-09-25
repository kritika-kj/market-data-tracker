select current_user;
CREATE SCHEMA IF NOT EXISTS finance;

CREATE TABLE IF NOT EXISTS finance.users (
    id BIGSERIAL PRIMARY KEY,
    email VARCHAR(320) NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('admin', 'analyst', 'viewer')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS finance.funds (
    id BIGSERIAL PRIMARY KEY,
    scheme_code VARCHAR(30) NOT NULL UNIQUE,
    scheme_name TEXT NOT NULL,
    fund_house TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS finance.nav_prices (
    id BIGSERIAL PRIMARY KEY,
    fund_id BIGINT NOT NULL REFERENCES finance.funds(id),
    nav_date DATE NOT NULL,
    nav NUMERIC(18, 6) NOT NULL CHECK (nav >= 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (fund_id, nav_date)
);

CREATE INDEX IF NOT EXISTS ix_nav_prices_fund_date
    ON finance.nav_prices (fund_id, nav_date DESC);
