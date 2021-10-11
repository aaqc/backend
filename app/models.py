from sqlalchemy import BINARY, Column, Float, ForeignKey, String
from sqlalchemy.dialects.mysql import BIGINT, INTEGER, TINYINT
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from config_handler import CONFIG

db_host = CONFIG["db_host"]
db_user = CONFIG["db_user"]
db_password = CONFIG["db_password"]
db_name = CONFIG["db_name"]


SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"
# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/db"
SQLALCHEMY_DATABASE_URL = f"mysql://{db_user}@{db_host}:3306"

try:
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
except:
    print("Failed to connect to the database")

Base = declarative_base()
metadata = Base.metadata


class Flighpath(Base):
    __tablename__ = "Flighpaths"

    id = Column(INTEGER(10), primary_key=True)
    drone = Column(INTEGER(11), nullable=False)
    pilot = Column(ForeignKey("Users.id"), nullable=False, index=True)
    start = Column(ForeignKey("Waypoints.id"), nullable=False, unique=True)
    end = Column(ForeignKey("Waypoints.id"), nullable=False, unique=True)
    duration = Column(INTEGER(11), nullable=False)
    travel_distance = Column(Float(8, True), nullable=False)

    Waypoint = relationship("Waypoint", primaryjoin="Flighpath.end == Waypoint.id")
    User = relationship("User")
    Waypoint1 = relationship("Waypoint", primaryjoin="Flighpath.start == Waypoint.id")


class Group(Base):
    __tablename__ = "Groups"

    id = Column(INTEGER(10), primary_key=True)
    name = Column(String(255), nullable=False)


class User(Base):
    __tablename__ = "Users"

    id = Column(INTEGER(10), primary_key=True)
    username = Column(String(255), nullable=False, unique=True)
    email = Column(String(255), nullable=False, unique=True)
    password_hash = Column(BINARY(16), nullable=False)
    full_name = Column(String(255), nullable=False)


class UserGroup(User):
    __tablename__ = "UserGroups"

    user = Column(ForeignKey("Users.id"), primary_key=True)
    group = Column(ForeignKey("Groups.id"), nullable=False, index=True)
    admin = Column(TINYINT(1), nullable=False)

    Group = relationship("Group")


class Waypoint(Base):
    __tablename__ = "Waypoints"

    id = Column(INTEGER(10), primary_key=True)
    path = Column(ForeignKey("Flighpaths.id"), nullable=False, index=True)
    index = Column(INTEGER(10))
    timestamp = Column(BIGINT(20), nullable=False)
    longitude = Column(Float(8, True), nullable=False)
    latitude = Column(Float(8, True), nullable=False)
    altitude = Column(Float(8, True), nullable=False)
    heading = Column(Float(8, True), nullable=False)
    speed = Column(Float(8, True), nullable=False)
    battery_level = Column(Float(8, True), nullable=False)

    Flighpath = relationship("Flighpath", primaryjoin="Waypoint.path == Flighpath.id")


class Drone(Base):
    __tablename__ = "Drones"

    id = Column(INTEGER(10), primary_key=True)
    owner = Column(ForeignKey("Groups.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    history = Column(ForeignKey("Flighpaths.id"), nullable=False, index=True)

    Flighpath = relationship("Flighpath")
    Group = relationship("Group")
