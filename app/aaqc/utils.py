from fastapi.exceptions import HTTPException
from starlette.requests import Request
from . import models
from typing import Generator, Optional
from sqlalchemy.orm.session import Session
from fastapi import Depends
from starlette.status import HTTP_401_UNAUTHORIZED
from .auth import Auth
from .database import fetch_user

auth = Auth()


class Token:
    def __init__(self, scope: str):
        self.scope = scope

    async def __call__(self, request: Request) -> str:
        authorization: str = request.headers.get("Authorization")
        if not authorization:
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                detail="Missing valid authentication header",
                headers={"WWW-Authenticate": "Bearer"},
            )
        scope, param = authorization.split(" ")
        if scope != self.scope:
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                detail="Authentication header is not containing a bearer token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return param


bearer = Token("bearer")
refresh = Token("refresh")


def use_db() -> Generator[Session, None, None]:
    db = models.SessionLocal()

    try:
        yield db
    finally:
        db.close()


def use_current_user(token: str = Depends(bearer), db: Session = Depends(use_db)):
    username = auth.decode_access_token(token)

    if not username:
        raise ValueError("Token invalid")
    return fetch_user(db, username)
