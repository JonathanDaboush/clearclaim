"""
PostgreSQL connection pool for ClearClaim.

Reads DATABASE_URL from the environment (set by docker-compose).
Format: postgresql+psycopg2://user:password@host:port/dbname
Falls back to clear_case on localhost for local development.

Main DB:   clear_case
Test DB:   clear_case_test  (set DATABASE_URL env var to point at it)
"""
import os
import pathlib
from contextlib import contextmanager
from typing import Any, Dict, Generator, List, Optional, Tuple
from urllib.parse import urlparse

import psycopg2  # type: ignore[import-untyped]
import psycopg2.extras  # type: ignore[import-untyped]
from psycopg2.pool import ThreadedConnectionPool  # type: ignore[import-untyped]

_pool: Optional[ThreadedConnectionPool] = None


def _kwargs() -> Dict[str, Any]:
    """Parse DATABASE_URL into psycopg2 keyword args."""
    raw = os.environ.get(
        "DATABASE_URL",
        "postgresql+psycopg2://postgres:password@localhost:5432/clear_case",
    ).replace("postgresql+psycopg2://", "postgresql://")
    p = urlparse(raw)
    return {
        "host": p.hostname or "localhost",
        "port": p.port or 5432,
        "dbname": (p.path or "/clear_case").lstrip("/") or "clear_case",
        "user": p.username or "postgres",
        "password": p.password or "password",
    }


def _get_pool() -> ThreadedConnectionPool:
    global _pool
    if _pool is None:
        _pool = ThreadedConnectionPool(minconn=1, maxconn=10, **_kwargs())
    return _pool


@contextmanager
def get_conn() -> Generator[Any, None, None]:
    """Yield a psycopg2 connection from the pool, returning it afterward."""
    pool = _get_pool()
    conn = pool.getconn()
    try:
        yield conn
    except Exception:
        conn.rollback()
        raise
    finally:
        pool.putconn(conn)


def query(sql: str, params: Tuple[Any, ...] = ()) -> List[Dict[str, Any]]:
    """Execute a SELECT and return all rows as plain dicts."""
    with get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(sql, params)
            return [dict(r) for r in cur.fetchall()]


def execute(sql: str, params: Tuple[Any, ...] = ()) -> None:
    """Execute an INSERT / UPDATE / DELETE without returning rows."""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
        conn.commit()


def execute_returning(sql: str, params: Tuple[Any, ...] = ()) -> Optional[Dict[str, Any]]:
    """Execute INSERT … RETURNING and return the first row as a dict."""
    with get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(sql, params)
            row = cur.fetchone()
        conn.commit()
        return dict(row) if row else None


def init_schema() -> None:
    """Create all tables (idempotent — every statement uses IF NOT EXISTS)."""
    schema_path = pathlib.Path(__file__).parent / "sql" / "schema.sql"
    sql = schema_path.read_text()
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
        conn.commit()
    print("[db] Schema initialised.")
    _seed_roles()


_ROLES = {
    "worker_manager": ["create_contract", "revise_contract", "approve_revision", "add_evidence", "delete_evidence", "sign_contract", "manage_workers", "view"],
    "worker":         ["create_contract", "revise_contract", "approve_revision", "add_evidence", "sign_contract", "view"],
    "legal_rep":      ["approve_revision", "add_evidence", "sign_contract", "view"],
    "client":         ["sign_contract", "view"],
    "guest":          ["view"],
}


def _seed_roles() -> None:
    """Ensure the standard roles exist in the DB (idempotent)."""
    import uuid, json
    for name, perms in _ROLES.items():
        existing = query("SELECT id FROM roles WHERE name = %s", (name,))
        if not existing:
            execute(
                "INSERT INTO roles (id, name, permissions) VALUES (%s, %s, %s)",
                (str(uuid.uuid4()), name, json.dumps(perms)),
            )
    print("[db] Roles seeded.")
