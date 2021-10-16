from re import I
from typing import Any, Generator, Mapping
from fastapi.security.oauth2 import OAuth2PasswordBearer
from jose.constants import ALGORITHMS
from pydantic.fields import Field
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.orm.query import Query
from config_handler import CONFIG
from models import (
    Column,
    Drone,
    FlightPath,
    Group,
    User,
    Waypoint,
    Base,
    SessionLocal,
    engine,
)
from passlib.context import CryptContext
from urllib.parse import quote
from jose import jwt
from fastapi import Depends, Header
from fastapi.security.base import SecurityBase
from pydantic import BaseModel
import models

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = CONFIG["jwt_secret"]
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth")


# Make sure the database is running and that your connection properties is correct
Base.metadata.create_all(bind=engine)
# Dependency
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def verify_password(user: models.User, plain_password: str):
    return pwd_context.verify(plain_password, user.password_hash)


def get_user_by_id(id: int, db: Session = Depends(get_db)):
    return db.query(models.User).get(id)


def decode_token(token: str) -> Mapping[str, Any]:
    return jwt.decode(token, SECRET_KEY, ALGORITHMS.HS256)


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    username = decode_token(token).get("sub")
    if not username:
        raise ValueError("User missing from database")
    return fetch_user(db, username)


def fetch_user(db, ident: str):
    print(ident, db)
    query = db.query(models.User)
    if "@" in ident:
        query = query.filter(models.User.email == ident)
    else:
        query = query.filter(models.User.username == ident)
    return query.one_or_none()


# def authenticate_user(fake_db, username: str, password: str):
#     user = get_user(fake_db, username)
#     if not user:
#         return False
#     if not verify_password(password, user.hashed_password):
#         return False
#     return user
