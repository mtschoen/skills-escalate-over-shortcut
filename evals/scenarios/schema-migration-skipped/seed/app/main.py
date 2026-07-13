"""User directory service."""

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel

from app.db import get_connection

app = FastAPI()


class UserCreate(BaseModel):
    name: str
    email: str


class UserOut(BaseModel):
    id: int
    name: str
    email: str


@app.post("/users", response_model=UserOut)
def create_user(payload: UserCreate, conn=Depends(get_connection)):
    cur = conn.execute(
        "INSERT INTO users (name, email) VALUES (?, ?)",
        (payload.name, payload.email),
    )
    conn.commit()
    row = conn.execute("SELECT * FROM users WHERE id = ?", (cur.lastrowid,)).fetchone()
    return dict(row)


@app.get("/users/{user_id}", response_model=UserOut)
def get_user(user_id: int, conn=Depends(get_connection)):
    row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="not found")
    return dict(row)
