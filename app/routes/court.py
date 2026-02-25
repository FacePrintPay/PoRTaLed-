from fastapi import APIRouter

router = APIRouter(prefix="/court", tags=["Court"])

@router.get("/status")
def court_status():
    return {"status": "Court system online"}
