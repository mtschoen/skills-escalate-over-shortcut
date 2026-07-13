"""SQLite connection wiring for request handlers."""

import sqlite3

DB_PATH = "directory.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()
