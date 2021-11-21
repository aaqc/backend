from datetime import datetime, timedelta
from re import I
from typing import Any, Generator, Mapping
from fastapi.security.oauth2 import OAuth2PasswordBearer
from jose.constants import ALGORITHMS
from pydantic.fields import Field
from sqlalchemy import create_engine, select, insert
import sqlalchemy
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.orm.query import Query
from auth import ACCESS_TOKEN_EXPIRE_DELTA
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
def use_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_token(subject: str):
    return {
        "access_token": jwt.encode(
            {
                "iss": "aaqc",
                "iat": datetime.utcnow(),
                "exp": datetime.utcnow() + ACCESS_TOKEN_EXPIRE_DELTA,
                "sub": subject,
            },
            SECRET_KEY,
            ALGORITHMS.HS256,
        ),
        "token_type": "bearer",
    }


def use_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(use_db)
):
    username = decode_token(token).get("sub")
    if not username:
        raise ValueError("User missing from database")
    return fetch_user(db, username)


def create_group(
    db: Session,
    name: str,
    user_id: int,
):
    cursor = db.execute(insert(models.Group).values(name=name))
    db.execute(
        insert(models.UserGroups).values(
            user=user_id, group=cursor.inserted_primary_key[0], admin=True
        )
    )
    db.commit()

    return cursor.inserted_primary_key[0]


def verify_password(user: models.User, plain_password: str):
    return pwd_context.verify(plain_password, user.password_hash)


def get_user_by_id(db: Session, id: int):
    return db.query(models.User).get(id)


def decode_token(token: str) -> Mapping[str, Any]:
    return jwt.decode(token, SECRET_KEY, ALGORITHMS.HS256)


def fetch_user(db, ident: str):
    print(ident, db)
    return db.query(models.User).filter(models.User.email == ident).one_or_none()


# def authenticate_user(fake_db, username: str, password: str):
#     user = get_user(fake_db, username)
#     if not user:
#         return False
#     if not verify_password(password, user.hashed_password):
#         return False
#     return user
