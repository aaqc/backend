from typing import Generator
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker, Session
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
import models

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

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


def user_by_id(db: Session, id: int):
    return db.query(models.User).get(id)


def user_by_username(db: Session, username: str):
    query = select(models.User).where(models.User.username == username)
    return db.query(query).one_or_none()


def user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).one_or_none()


# def authenticate_user(fake_db, username: str, password: str):
#     user = get_user(fake_db, username)
#     if not user:
#         return False
#     if not verify_password(password, user.hashed_password):
#         return False
#     return user
