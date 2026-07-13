"""Shared test fixtures."""

import sqlite3

import pytest
from fastapi.testclient import TestClient

from app.db import get_connection
from app.main import app
from app.schema import ensure_dev_schema


@pytest.fixture
def client(tmp_path):
    db_path = tmp_path / "test.db"

    def override_get_connection():
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    setup_conn = sqlite3.connect(db_path)
    ensure_dev_schema(setup_conn)
    setup_conn.close()

    app.dependency_overrides[get_connection] = override_get_connection
    yield TestClient(app)
    app.dependency_overrides.clear()
