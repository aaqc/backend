from fastapi.security import oauth2
from .errortypes import AuthFailure
from . import models
from typing import Generator
from sqlalchemy.orm.session import Session
from fastapi import Depends
from .auth import verify_password, decode_token
from .database import fetch_user

oauth2_scheme = oauth2.OAuth2PasswordBearer(tokenUrl="auth")


def use_db() -> Generator[Session, None, None]:
    db = models.SessionLocal()

    try:
        yield db
    finally:
        db.close()


def check_login(db: Session, ident: str, password: str):
    user = fetch_user(db, ident)

    if user:
        password_correct = verify_password(password, user.password_hash)
        if not password_correct:
            raise AuthFailure
        return True
    return False


def use_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(use_db)
):
    subject = decode_token(token)

    if not subject:
        raise ValueError("Token invalid")
    return fetch_user(db, subject)
