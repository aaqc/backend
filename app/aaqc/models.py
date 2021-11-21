from urllib.parse import quote
from sqlalchemy import BINARY, Column, DateTime, Float, ForeignKey, String, Table
from sqlalchemy.dialects.mysql import INTEGER
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, backref, deferred
from sqlalchemy import create_engine
from sqlalchemy.sql.schema import Table
from sqlalchemy.sql.selectable import Join
from sqlalchemy.sql.sqltypes import BOOLEAN
from config_handler import CONFIG

db_host = CONFIG["db_host"]
db_user = CONFIG["db_user"]
db_password = CONFIG["db_password"]
db_name = CONFIG["db_name"]
DATABASE_URL: str
if not CONFIG["use_sqlite"]:
    DATABASE_URL = f"mysql+pymysql://{quote(CONFIG['db_user'])}:{quote(CONFIG['db_password'])}@{CONFIG['db_host']}/{CONFIG['db_name']}?charset=utf8mb4"
else:
    DATABASE_URL = f"sqlite:///database.db?check_same_thread=False"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Connect to the database
Base = declarative_base()
metadata = Base.metadata


UserGroups = Table(
    "UserGroups",
    metadata,
    Column("user", ForeignKey("Users.id"), nullable=False, index=True),
    Column("group", ForeignKey("Groups.id"), nullable=False, index=True),
    Column("admin", BOOLEAN),
)


class Group(Base):
    __tablename__ = "Groups"

    id = Column(INTEGER(10), primary_key=True)
    name = Column(String(255), nullable=False)
    members = relationship(
        "User",
        secondary=UserGroups,
        lazy="subquery",
        backref=backref("all_members", lazy=True),
    )


class User(Base):
    __tablename__ = "Users"

    id = Column(INTEGER(10), primary_key=True)
    email = Column(String(255), nullable=False, unique=True)
    password_hash = deferred(Column(BINARY(60), nullable=False))
    full_name = Column(String(255), nullable=False)
    groups = relationship(
        "Group",
        secondary=UserGroups,
        lazy="subquery",
        backref=backref("all_groups", lazy=True),
    )


class FlightPath(Base):
    __tablename__ = "FlightPaths"

    id = Column(INTEGER(10), primary_key=True)
    drone = Column(ForeignKey("Drones.id"), nullable=False)
    pilot = Column(ForeignKey("Users.id"), nullable=False)
    duration = Column(INTEGER(10), nullable=False)
    travel_distance = Column(Float(8, True), nullable=False)

    waypoints = relationship(
        "Waypoint",
        lazy="subquery",
        backref=backref("all_waypoints", lazy=True),
    )


class Waypoint(Base):
    __tablename__ = "Waypoints"

    id = Column(INTEGER(10), primary_key=True)
    path = Column(ForeignKey("FlightPaths.id"), nullable=False, index=True)
    point = Column(INTEGER(10), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    longitude = Column(Float(8, True), nullable=False)
    latitude = Column(Float(8, True), nullable=False)
    altitude = Column(Float(8, True), nullable=False)
    heading = Column(Float(8, True), nullable=False)
    speed = Column(Float(8, True), nullable=False)
    battery_level = Column(Float(8, True), nullable=False)


class Drone(Base):
    __tablename__ = "Drones"

    id = Column(INTEGER(10), primary_key=True)
    owner = Column(ForeignKey("Groups.id"), index=True)
    name = Column(String(255), nullable=False)
    token_hash = deferred(Column(BINARY(16), nullable=False))

    Group = relationship("Group")


metadata.create_all(engine)
