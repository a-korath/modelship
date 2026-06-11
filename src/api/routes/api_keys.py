from fastapi import APIRouter, Depends, HTTPException

from src.api.middleware.auth import APIKey, key_db, require_admin

router = APIRouter()


@router.post("/generate_key", response_model=str)
def generate_key(role: str = "user", api_key: APIKey = Depends(require_admin)) -> str:
    new_key = key_db.generate_key(role)
    return new_key.key


@router.get("/list_keys", response_model=list[str])
def list_keys(api_key: APIKey = Depends(require_admin)) -> list[str]:
    active_keys = key_db.list_active_keys()
    return [key.key for key in active_keys]


@router.delete("/deactivate_key")
def deactivate_key(key: str, api_key: APIKey = Depends(require_admin)):
    if api_key.key == key:
        raise HTTPException(status_code=403, detail="Cannot deactivate your own key")
    key_db.deactivate_key(key)
    return {"detail": "Key deactivated"}
