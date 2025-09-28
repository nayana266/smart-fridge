from fastapi import APIRouter
router = APIRouter()

@router.get("/presign/ping")
def ping():
    return {"ok": True}