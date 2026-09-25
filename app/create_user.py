from __future__ import annotations

import argparse
from getpass import getpass

from app.auth import create_user


def main() -> None:
    parser = argparse.ArgumentParser(description="Create or update a dashboard user")
    parser.add_argument("email")
    parser.add_argument("role", choices=("admin", "analyst", "viewer"))
    args = parser.parse_args()

    password = getpass("Password (minimum 8 characters): ")
    confirmation = getpass("Confirm password: ")
    if password != confirmation:
        raise SystemExit("Passwords do not match")

    create_user(args.email, password, args.role)
    print(f"User {args.email} is ready with role {args.role}.")


if __name__ == "__main__":
    main()
