import logging
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import db


def main():
    logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
    try:
        rows = db.run_query("SELECT now()")
        timestamp = rows[0][0] if rows else None
        print(f"Database connection OK: {timestamp}")
    except Exception as exc:
        print(f"Database connection failed: {exc}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
