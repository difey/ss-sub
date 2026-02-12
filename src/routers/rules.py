from fastapi import APIRouter, Body, HTTPException
from src.services.storage import storage_service

router = APIRouter(
    prefix="/rules",
    tags=["rules"],
)

@router.get("/")
async def get_custom_rules():
    return {"rules": storage_service.get_custom_rules()}

@router.post("/update")
async def update_custom_rules(rules: str = Body(..., media_type="text/plain")):
    try:
        storage_service.save_custom_rules(rules)
        return {"message": "Custom rules updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
