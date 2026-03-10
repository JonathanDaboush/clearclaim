import re


class SQLCleanup:
    @staticmethod
    def cleanup_sql(sql_query: str) -> str:
        """Strip leading/trailing whitespace and collapse internal whitespace for safe, clean SQL."""
        return re.sub(r"\s+", " ", sql_query.strip())
