from fastapi import APIRouter, HTTPException
from schemas.ask import AskRequest
from services import ask_service

router = APIRouter()


@router.post("/ask")
def ask(req: AskRequest):
    try:
        return ask_service.process_request(req.question.strip())
    except Exception as error:
        print("[error]", repr(error))
        raise HTTPException(
            status_code=502,
            detail="The answer service didn't respond. Try again in a moment.",
        )
