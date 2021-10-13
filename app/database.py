from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config_handler import CONFIG
from models import Column, Drone, Flighpath, Group, User, UserGroup, Waypoint, Base
from passlib.context import CryptContext
from urllib.parse import quote


DATABASE_URL = f"mysql+pymysql://{quote(CONFIG['db_user'])}:{quote(CONFIG['db_password'])}@{CONFIG['db_host']}/{CONFIG['db_name']}?charset=utf8mb4"
engine = create_engine(DATABASE_URL)
db = sessionmaker(autocommit=False, autoflush=False, bind=engine)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        # return UserInDB(**user_dict)


if __name__ == "__main__":
    print(db().query(User).all()[0].__dict__)
