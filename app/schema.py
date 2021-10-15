from __future__ import annotations
from pydantic import BaseModel, validator
from typing import Any, List, Literal, Optional, Union
from pydantic import BaseModel
from typing import Any, Optional
import pydantic

from pydantic.networks import EmailStr


class AAQCBaseModel(BaseModel):
    id: int


class AAQCBaseModelOrm(AAQCBaseModel):
    class Config:
        orm_mode = True


class BaseUser(AAQCBaseModel):
    username: str
    email: EmailStr
    full_name: str


class CreateUser(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: str

    @validator("password")
    def validate_password(cls, value: str):
        if len(value) < 6:
            raise ValueError("Password too short, minimum length 6 characters")
        if not any(map(lambda x: x.isupper(), value)):
            raise ValueError(
                "Password needs to contain at least one uppercase character"
            )
        if not any(map(lambda x: not x.isupper(), value)):
            raise ValueError(
                "Password needs to contain at least one lowercase character"
            )
        if not any(map(lambda x: not x.isnumeric(), value)):
            raise ValueError("Password needs to contain at least one number")

        return value


# One user
class User(BaseUser):
    groups: List = []


# One group
class Group(AAQCBaseModel):
    name: str
    members: list = []


class UserLogin(BaseModel):
    password: str


class UserLoginEmail(UserLogin):
    email: EmailStr


class UserLoginUsername(UserLogin):
    username: str


class UserLoginFull(UserLoginEmail, UserLoginUsername):
    pass


class UserCreate(UserLoginFull):
    full_name: str


class BaseGroup(AAQCBaseModel):
    name: str


class Drone(AAQCBaseModel):
    owner: Optional[User] = None
    name: str
    history: list[FlightPath]


class Waypoint(AAQCBaseModel):
    timestamp: int
    longitude: float
    latitude: float
    altitude: float
    heading: float

    """speed of the drone when entering the waypoint in m/s"""
    speed: float
    """battery level of the drone when entering the waypoint in %"""
    battery_level: float


class FlightPath(AAQCBaseModel):
    drone: Drone
    pilot: User
    start: Waypoint
    end: Waypoint
    duration: int
    travel_distance: float
    waypoints: list[Waypoint]


class AuthResponse(BaseModel):
    token_type: Literal["bearer"]
    access_token: str


models: list[Any] = [User, UserCreate, Group, Drone, FlightPath, Waypoint, BaseGroup]

for model in models:
    model.update_forward_refs()
