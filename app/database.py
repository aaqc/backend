from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
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

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Make sure the database is running and that your connection properties is correct
Base.metadata.create_all(bind=engine)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


# def authenticate_user(fake_db, username: str, password: str):
#     user = get_user(fake_db, username)
#     if not user:
#         return False
#     if not verify_password(password, user.hashed_password):
#         return False
#     return user
