import datetime as dt
import logging
import os
import secrets

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

logger = logging.getLogger(__name__)

JWT_SECRET = os.environ.get("JWT_SECRET", "dev-secret-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRY_MINUTES = 30


class APIKey:
    def __init__(
        self, created_at: dt.datetime, key: str, role: str, is_active: bool = True
    ):
        self.created_at = created_at
        self.key = key
        self.role = role
        self.is_active = is_active

class InMemoryAPIKeyStore:
    def __init__(self):
        self.keys = {}
    
    def generate_key(self, role: str) -> APIKey:
        new_key = APIKey(
            created_at=dt.datetime.now(), key=secrets.token_urlsafe(32), role=role
        )
        self.add_key(new_key)
        return new_key

    def add_key(self, api_key: APIKey):
        self.keys[api_key.key] = api_key

    def get_key(self, key: str) -> APIKey | None:
        api_key = self.keys.get(key)
        return api_key if api_key and api_key.is_active else None
    
    def list_active_keys(self) -> list[APIKey]:
        return [key for key in self.keys.values() if key.is_active]

    def deactivate_key(self, key: str):
        if key in self.keys:
            self.keys[key].is_active = False

def create_jwt(subject: str, role: str) -> str:
    expire = dt.datetime.now(dt.timezone.utc) + dt.timedelta(minutes=JWT_EXPIRY_MINUTES)
    payload = {"sub": subject, "role": role, "exp": expire}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_jwt(token: str) -> dict:
    return jwt.decode(
        token,
        JWT_SECRET,
        algorithms=[JWT_ALGORITHM],
        options={"require": ["exp", "sub"]},
    )


key_db = InMemoryAPIKeyStore()
auth_scheme = HTTPBearer()


def validate_api_key(
    credentials: HTTPAuthorizationCredentials = Depends(auth_scheme),
) -> APIKey:
    token = credentials.credentials

    # Try JWT first
    try:
        payload = decode_jwt(token)
        return APIKey(
            created_at=dt.datetime.now(dt.timezone.utc),
            key=token,
            role=payload.get("role", "user"),
        )
    except JWTError:
        pass

    # Fall back to API key lookup
    key = key_db.get_key(token)
    if not key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or inactive API key",
        )
    return key


def require_admin(principal: APIKey = Depends(validate_api_key)) -> APIKey:
    if principal.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin role required",
        )
    return principal