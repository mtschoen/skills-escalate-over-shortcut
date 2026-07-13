"""User row shape.

USER_COLUMNS is the source of truth the app layer reads and writes
against - it does not drive the database schema. The schema is whatever
migrations/*.sql has created and applied (see app/schema.py).
"""

USER_COLUMNS = ["id", "name", "email"]
