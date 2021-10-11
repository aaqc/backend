from __future__ import annotations
from pydantic import BaseModel
from typing import Any, Optional


class AAQCBaseModel(BaseModel):
    id: int

    class Config:
        orm_mode = True


class User(AAQCBaseModel):
    id: int
    username: str
    email: str
    full_name: str
    groups: list[Group]  # Group


class UserCreate(BaseModel):
    username: str
    email: str
    full_name: str
    password: str


class Group(AAQCBaseModel):
    name: str
    members: list[User]


class Drone(AAQCBaseModel):
    owner: Optional[User]
    name: str
    history: list[FlightPath]  # Flightpath


class FlightPath(AAQCBaseModel):
    drone: Drone
    pilot: User
    start: Waypoint
    end: Waypoint
    duration: int
    travel_distance: float


class Waypoint(AAQCBaseModel):
    path: FlightPath
    index: int
    timestamp: int
    longitude: float
    latitude: float
    altitude: float
    heading: float
    speed: float
    battery_level: float


models: list[Any] = [User, UserCreate, Group, Drone, FlightPath, Waypoint]

for model in models:
    model.update_forward_refs()


# class ItemCreate(ItemBase):
#     pass


# class Item(ItemBase):
#     id: int
#     owner_id: int

#     class Config:
#         orm_mode = True


# class UserBase(BaseModel):
#     email: str


# class UserCreate(UserBase):
#     password: str


# class User(UserBase):
#     id: int
#     is_active: bool
#     items: List[Item] = []

#     class Config:
#         orm_mode = True
