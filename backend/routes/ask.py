from fastapi import APIRouter
from schemas import ask
from services import ask_service

router = APIRouter()


@router.post("/ask")
def ask(req: ask.AskRequest):
    ask_service.ProcessRequest(req.question)
    return {"ok": True}
