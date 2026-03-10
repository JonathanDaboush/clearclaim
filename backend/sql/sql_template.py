import psycopg2  # type: ignore[import-untyped]
from typing import Dict, Any, List, Tuple


class SQLTemplate:
    def __init__(self, db_config: Dict[str, Any]):
        """Open a PostgreSQL connection from the provided config dict."""
        self.connection = psycopg2.connect(**db_config)
        self.connection.autocommit = False

    def execute_query(self, query: str, params: Tuple[Any, ...] = ()) -> List[Dict[str, Any]]:
        """Execute a parameterised SELECT query and return all rows as a list of dicts."""
        with self.connection.cursor() as cur:
            cur.execute(query, params)
            columns = [desc[0] for desc in cur.description] if cur.description else []
            return [dict(zip(columns, row)) for row in cur.fetchall()]

    def insert(self, table: str, data: Dict[str, Any]) -> str:
        """Insert a row into the given table and return the auto-generated id."""
        columns = ", ".join(data.keys())
        placeholders = ", ".join(["%s"] * len(data))
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders}) RETURNING id"
        with self.connection.cursor() as cur:
            cur.execute(query, tuple(data.values()))
            row_id = cur.fetchone()[0]
        self.connection.commit()
        return str(row_id)

    def update(self, table: str, data: Dict[str, Any], where: Dict[str, Any]) -> bool:
        """Update rows in the given table matching the where clause. Returns True on success."""
        set_clause = ", ".join(f"{k} = %s" for k in data.keys())
        where_clause = " AND ".join(f"{k} = %s" for k in where.keys())
        query = f"UPDATE {table} SET {set_clause} WHERE {where_clause}"
        with self.connection.cursor() as cur:
            cur.execute(query, tuple(data.values()) + tuple(where.values()))
        self.connection.commit()
        return True

    def delete(self, table: str, where: Dict[str, Any]) -> bool:
        """Delete rows in the given table matching the where clause. Returns True on success."""
        where_clause = " AND ".join(f"{k} = %s" for k in where.keys())
        query = f"DELETE FROM {table} WHERE {where_clause}"
        with self.connection.cursor() as cur:
            cur.execute(query, tuple(where.values()))
        self.connection.commit()
        return True
