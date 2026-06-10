from fastapi import APIRouter, Depends, HTTPException

from src.api.middleware.auth import APIKey, key_db, validate_api_key

router = APIRouter()
@router.post("/generate_key", response_model=str)
def generate_key(api_key: APIKey = Depends(validate_api_key)) -> str:
    new_key = key_db.generate_key(role="user")
    return new_key.key

@router.get("/list_keys", response_model=list[str])
def list_keys(api_key: APIKey = Depends(validate_api_key)) -> list[str]:
    if api_key.role != "admin":
        raise HTTPException(status_code=403, detail="Only admin can list API keys")
    active_keys = key_db.list_active_keys()
    return [key.key for key in active_keys] 

@router.delete("/deactivate_key")
def deactivate_key(key: str, api_key: APIKey = Depends(validate_api_key)):
    key_db.deactivate_key(key)
    return {"detail": "Key deactivated"}

