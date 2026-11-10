from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def ask():
    return {"ok": True}
