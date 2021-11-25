from typing import Optional
from jose import jwt
from jose.constants import ALGORITHMS
from passlib.context import CryptContext
from .database import fetch_user
from config_handler import CONFIG
from datetime import datetime, timedelta

ACCESS_TOKEN_EXPIRE_DELTA = timedelta(days=90)


hasher = CryptContext(schemes=["bcrypt"], deprecated="auto")
secret = CONFIG["jwt_secret"]


def hash_password(password: str):
    return hasher.hash(password)


def verify_password(password: str, password_hash: bytes) -> bool:
    return hasher.verify(password, password_hash)


def create_token(subject: str, scope: str = "bearer"):
    return jwt.encode(
        {
            "iss": "aaqc",
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + ACCESS_TOKEN_EXPIRE_DELTA,
            "sub": subject,
            "scope": scope,
        },
        secret,
        ALGORITHMS.HS256,
    )


def decode_token(token: str, scope: str = "bearer") -> Optional[str]:
    try:
        data = jwt.decode(token, secret, algorithms=[ALGORITHMS.HS256])

        if data["iss"] != "aaqc":
            raise ValueError("Token issuer is not correct")
        if data["scope"] != scope:
            raise ValueError("Token is of incorrect type")
    except:
        return None
    return data["sub"]
