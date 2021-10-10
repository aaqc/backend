from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config_handler import CONFIG
from models import Column, Drone, Flighpath, Group, User, UserGroup, Waypoint

DATABASE_URL = f"mysql+pymysql://{CONFIG['db_user']}:{CONFIG['db_password']}@{CONFIG['db_host']}/{CONFIG['db_name']}?charset=utf8mb4"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
