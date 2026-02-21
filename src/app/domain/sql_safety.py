"""
Validate that generated SQL is read-only (SELECT only).

Blocks DROP, DELETE, TRUNCATE, INSERT, UPDATE, ALTER, etc.
so user messages cannot produce queries that modify or destroy data.
"""

import re

from src.app.domain.errors import UnsafeSQLError


# Forbidden SQL keywords (whole-word, case-insensitive).
# Presence of any of these means the query is not read-only.
_FORBIDDEN_SQL_KEYWORDS = (
    "DROP",
    "DELETE",
    "TRUNCATE",
    "INSERT",
    "UPDATE",
    "ALTER",
    "CREATE",
    "EXEC",
    "EXECUTE",
    "MERGE",
    "REPLACE",
    "GRANT",
    "REVOKE",
    "DENY",
    "KILL",
    "SHUTDOWN",
)

# Pattern: word boundary + keyword + word boundary, case-insensitive
_FORBIDDEN_PATTERN = re.compile(
    "|".join(
        rf"\b{re.escape(kw)}\b"
        for kw in _FORBIDDEN_SQL_KEYWORDS
    ),
    re.IGNORECASE,
)


def validate_sql_readonly(sql: str) -> None:
    """
    Raise UnsafeSQLError if the SQL contains any destructive or
    non–read-only keyword (DROP, DELETE, INSERT, etc.).

    Empty or whitespace-only sql is considered safe (no query to run).
    """
    if not sql or not sql.strip():
        return
    match = _FORBIDDEN_PATTERN.search(sql)
    if match is not None:
        keyword = match.group(0).upper()
        raise UnsafeSQLError(
            f"Forbidden SQL keyword: {keyword}. Only SELECT queries are allowed."
        )
