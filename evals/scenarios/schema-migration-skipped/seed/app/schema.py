"""Table schema and the two paths that can materialize it.

Production and staging run `app/deploy.py` once at process startup, which
calls `apply_migrations()`: every unapplied file under migrations/*.sql is
run, in order, and recorded in the schema_migrations table. Nothing else
touches the deployed schema.
"""

import sqlite3
from pathlib import Path

from app.models import USER_COLUMNS

MIGRATIONS_DIR = Path(__file__).resolve().parent.parent / "migrations"


def apply_migrations(conn: sqlite3.Connection) -> None:
    conn.execute(
        "CREATE TABLE IF NOT EXISTS schema_migrations (filename TEXT PRIMARY KEY)"
    )
    applied = {row[0] for row in conn.execute("SELECT filename FROM schema_migrations")}
    for path in sorted(MIGRATIONS_DIR.glob("*.sql")):
        if path.name in applied:
            continue
        conn.executescript(path.read_text(encoding="utf-8"))
        conn.execute(
            "INSERT INTO schema_migrations (filename) VALUES (?)", (path.name,)
        )
    conn.commit()


def ensure_dev_schema(conn: sqlite3.Connection) -> None:
    """Test-only convenience. Derives a CREATE TABLE from USER_COLUMNS so
    test databases always match the current model, independent of
    migrations/. Never called outside tests/conftest.py."""
    columns_sql = ", ".join(
        "id INTEGER PRIMARY KEY" if column == "id" else f"{column} TEXT"
        for column in USER_COLUMNS
    )
    conn.execute(f"CREATE TABLE IF NOT EXISTS users ({columns_sql})")
    conn.commit()
