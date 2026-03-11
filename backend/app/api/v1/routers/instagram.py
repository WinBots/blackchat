from fastapi import APIRouter

router = APIRouter()


@router.get("/ping")
def ping():
    return {"service": "instagram", "status": "ok"}
