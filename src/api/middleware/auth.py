import datetime as dt
import secrets
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials


class APIKey:
    def __init__(self, created_at: dt.datetime, key: str, role: str, is_active: bool = True):
        self.created_at = created_at
        self.key = key
        self.role = role
        self.is_active = is_active

class InMemoryAPIKeyStore:
    def __init__(self):
        self.keys = {}
    
    def generate_key(self, role: str) -> APIKey:
        new_key = APIKey(created_at=dt.datetime.now(), key=secrets.token_urlsafe(32), role=role)
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

key_db = InMemoryAPIKeyStore()
auth_scheme = HTTPBearer()

def validate_api_key(api_key: HTTPAuthorizationCredentials = Depends(auth_scheme)) -> APIKey:
    key = key_db.get_key(api_key.credentials)
    if not key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or inactive API key")
    return key