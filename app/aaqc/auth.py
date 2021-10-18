from typing import Optional
from jose import jwt
from jose.constants import ALGORITHMS
from errortypes import APIError
from passlib.context import CryptContext
from config_handler import CONFIG
from datetime import datetime, timedelta

ACCESS_TOKEN_EXPIRE_DELTA = timedelta(minutes=30)
REFRESH_TOKEN_EXPIRE_DELTA = timedelta(days=90)


class Auth:
    hasher = CryptContext(schemes=["bcrypt"], deprecated="auto")
    secret = CONFIG["jwt_secret"]

    def hash_password(self, password: str):
        return self.hasher.hash(password)

    def verify_password(self, password: str, password_hash: bytes):
        return self.hasher.verify(password, password_hash)

    def _create_token(self, subject: str, scope: str):
        return jwt.encode(
            {
                "iss": "aaqc",
                "iat": datetime.utcnow(),
                "exp": datetime.utcnow() + ACCESS_TOKEN_EXPIRE_DELTA,
                "sub": subject,
                "scope": scope,
            },
            self.secret,
            ALGORITHMS.HS256,
        )

    def create_access_token(self, subject: str):
        return self._create_token(subject, "bearer")

    def create_refresh_token(self, subject: str):
        return self._create_token(subject, "refresh")

    def _decode_token(self, token: str, scope: str) -> Optional[str]:
        try:
            data = jwt.decode(token, self.secret, algorithms=[ALGORITHMS.HS256])

            if data["iss"] != "aaqc":
                raise ValueError("Token issuer is not correct")
            if data["scope"] != scope:
                raise ValueError("Token is of incorrect type")
        except:
            return None
        return data["sub"]

    def decode_access_token(self, token: str):
        return self._decode_token(token, "bearer")

    def decode_refresh_token(self, token: str):
        return self._decode_token(token, "refresh")
