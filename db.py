import logging
import os
from contextlib import contextmanager

from psycopg import OperationalError
from psycopg_pool import ConnectionPool
from dotenv import load_dotenv

logger = logging.getLogger("db")
_pool = None

load_dotenv()


def _get_database_url():
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL is not set")
    return database_url


def get_pool():
    global _pool
    if _pool is None:
        _pool = ConnectionPool(
            conninfo=_get_database_url(),
            min_size=1,
            max_size=5,
            open=False,
        )
        logger.info("Database pool created")

    if _pool.closed:
        try:
            _pool.open()
            logger.info("Database pool opened")
        except OperationalError:
            logger.exception("Database connection failed")
            raise

    return _pool


@contextmanager
def get_connection():
    pool = get_pool()
    with pool.connection() as conn:
        yield conn


def close_pool():
    global _pool
    if _pool and not _pool.closed:
        _pool.close()
        logger.info("Database pool closed")


def run_query(query, params=None):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, params or ())
                if cur.description:
                    return cur.fetchall()
                return []
    except OperationalError:
        logger.exception("Database query failed")
        raise


def health_check():
    rows = run_query("SELECT 1")
    return bool(rows)
