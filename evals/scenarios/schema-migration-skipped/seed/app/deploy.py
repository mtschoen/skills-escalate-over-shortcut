"""Production/staging startup entrypoint.

Run once before the app process starts serving traffic. Applies every
unapplied file under migrations/ in order; this is the only path that
changes the deployed schema.
"""

import sqlite3

from app.db import DB_PATH
from app.schema import apply_migrations

if __name__ == "__main__":
    conn = sqlite3.connect(DB_PATH)
    apply_migrations(conn)
    conn.close()
