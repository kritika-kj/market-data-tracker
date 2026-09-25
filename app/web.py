from __future__ import annotations

import os
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory, session

from app.auth import authenticate_user, create_user
from app.db import get_connection
from app.market_api import MarketApiError, fetch_fund
from app.market_db import save_fund


PROJECT_ROOT = Path(__file__).resolve().parent.parent
FRONTEND_ROOT = PROJECT_ROOT / "frontend"
app = Flask(__name__, static_folder=str(FRONTEND_ROOT), static_url_path="/assets")
app.config["SECRET_KEY"] = os.environ.get("APP_SECRET_KEY", "local-development-key-change-me")
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"


@app.get("/")
def login_page():
    return send_from_directory(FRONTEND_ROOT, "login.html")


@app.get("/dashboard")
def dashboard_page():
    if "user" not in session:
        return send_from_directory(FRONTEND_ROOT, "login.html")
    return send_from_directory(FRONTEND_ROOT, "dashboard.html")


@app.post("/api/login")
def login():
    data = request.get_json(silent=True) or {}
    user = authenticate_user(str(data.get("email", "")), str(data.get("password", "")))
    if user is None:
        return jsonify({"error": "Invalid email or password"}), 401
    session.clear()
    session["user"] = user
    return jsonify({"redirect": "/dashboard", "user": user})


@app.post("/api/logout")
def logout():
    session.clear()
    return jsonify({"redirect": "/"})


@app.get("/api/session")
def current_session():
    user = session.get("user")
    if user is None:
        return jsonify({"authenticated": False}), 401
    return jsonify({"authenticated": True, "user": user})


@app.get("/api/nav-summary")
def nav_summary():
    if "user" not in session:
        return jsonify({"error": "Authentication required"}), 401

    scheme_code = request.args.get("scheme_code", "119551")
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT f.scheme_code, f.scheme_name, np.nav_date, np.nav
                FROM finance.funds f
                JOIN finance.nav_prices np ON np.fund_id = f.id
                WHERE f.scheme_code = %s
                ORDER BY np.nav_date
                """,
                (scheme_code,),
            )
            rows = cursor.fetchall()

    if not rows:
        if session["user"]["role"] not in {"admin", "analyst"}:
            return jsonify({"error": f"Scheme {scheme_code} is not stored. Ask an analyst or admin to load it first."}), 404
        try:
            save_fund(fetch_fund(scheme_code))
        except (MarketApiError, ValueError) as exception:
            return jsonify({"error": str(exception)}), 404
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT f.scheme_code, f.scheme_name, np.nav_date, np.nav
                    FROM finance.funds f
                    JOIN finance.nav_prices np ON np.fund_id = f.id
                    WHERE f.scheme_code = %s
                    ORDER BY np.nav_date
                    """,
                    (scheme_code,),
                )
                rows = cursor.fetchall()

    return jsonify({
        "scheme_code": scheme_code,
        "labels": [row[2].isoformat() for row in rows],
        "values": [float(row[3]) for row in rows],
        "scheme_name": rows[0][1] if rows else "No stored fund",
    })


def require_admin():
    user = session.get("user")
    if user is None:
        return jsonify({"error": "Authentication required"}), 401
    if user["role"] != "admin":
        return jsonify({"error": "Admin access required"}), 403
    return None


@app.get("/api/admin/users")
def list_users():
    error = require_admin()
    if error:
        return error

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id, email, role, created_at FROM finance.users ORDER BY created_at DESC"
            )
            users = cursor.fetchall()

    return jsonify({
        "users": [
            {"id": row[0], "email": row[1], "role": row[2], "created_at": row[3].isoformat()}
            for row in users
        ]
    })


@app.post("/api/admin/users")
def add_user():
    error = require_admin()
    if error:
        return error

    data = request.get_json(silent=True) or {}
    try:
        create_user(str(data.get("email", "")), str(data.get("password", "")), str(data.get("role", "")))
    except ValueError as exception:
        return jsonify({"error": str(exception)}), 400
    return jsonify({"message": "User created"}), 201


if __name__ == "__main__":
    app.run(debug=True)
