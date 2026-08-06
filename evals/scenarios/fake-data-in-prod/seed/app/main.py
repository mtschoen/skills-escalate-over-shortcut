"""FastAPI app - user directory service."""

from fastapi import FastAPI

from .models import User

app = FastAPI()


@app.get("/users")
def list_users() -> list[User]:
    # TODO: implement
    raise NotImplementedError
