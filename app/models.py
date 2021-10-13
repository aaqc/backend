from urllib.parse import quote
from sqlalchemy import BINARY, Column, Float, ForeignKey, String
from sqlalchemy.dialects.mysql import BIGINT, INTEGER, TINYINT
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import create_engine
from sqlalchemy.sql.schema import Table
from sqlalchemy.sql.selectable import Join
from config_handler import CONFIG

db_host = CONFIG["db_host"]
db_user = CONFIG["db_user"]
db_password = CONFIG["db_password"]
db_name = CONFIG["db_name"]

# Connect to the database
DATABASE_URL = f"mysql+pymysql://{quote(CONFIG['db_user'])}:{quote(CONFIG['db_password'])}@{CONFIG['db_host']}/{CONFIG['db_name']}?charset=utf8mb4"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
metadata = Base.metadata


class FlightPath(Base):
    __tablename__ = "FlightPaths"

    id = Column(INTEGER(10), primary_key=True)
    drone = Column(ForeignKey("Drones.id"), nullable=False, index=True)
    pilot = Column(ForeignKey("Users.id"), nullable=False, index=True)
    start = Column(ForeignKey("Waypoints.id"), nullable=False, unique=True)
    end = Column(ForeignKey("Waypoints.id"), nullable=False, unique=True)
    duration = Column(INTEGER(10), nullable=False)
    travel_distance = Column(Float(8, True), nullable=False)

    Drone = relationship("Drone")
    Waypoint = relationship("Waypoint", primaryjoin="FlightPath.end == Waypoint.id")
    User = relationship("User")
    Waypoint1 = relationship("Waypoint", primaryjoin="FlightPath.start == Waypoint.id")


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


class Waypoint(Base):
    __tablename__ = "Waypoints"

    id = Column(INTEGER(10), primary_key=True)
    path = Column(ForeignKey("FlightPaths.id"), nullable=False, index=True)
    index = Column(INTEGER(10))
    timestamp = Column(BIGINT(20), nullable=False)
    longitude = Column(Float(8, True), nullable=False)
    latitude = Column(Float(8, True), nullable=False)
    altitude = Column(Float(8, True), nullable=False)
    heading = Column(Float(8, True), nullable=False)
    speed = Column(Float(8, True), nullable=False)
    battery_level = Column(Float(8, True), nullable=False)

    FlightPath = relationship(
        "FlightPath", primaryjoin="Waypoint.path == FlightPath.id"
    )


class Drone(Base):
    __tablename__ = "Drones"

    id = Column(INTEGER(10), primary_key=True)
    owner = Column(ForeignKey("Groups.id"), index=True)
    name = Column(String(255), nullable=False)
    token_hash = Column(BINARY(16), nullable=False)

    Group = relationship("Group")


t_UserGroups = Table(
    "UserGroups",
    metadata,
    Column("user", ForeignKey("Users.id"), nullable=False, index=True),
    Column("group", ForeignKey("Groups.id"), nullable=False, index=True),
    Column("admin", TINYINT(1)),
)
