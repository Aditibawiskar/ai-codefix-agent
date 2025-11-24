# app/api/routes.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.llm_service import call_mock_llm

router = APIRouter()


class FixRequest(BaseModel):
    code: str | None = None


@router.post("/fix-code")
def fix_code(payload: FixRequest):
    if not payload.code:
        raise HTTPException(status_code=400, detail="code is required")
    result = call_mock_llm(payload.code)
    return {"fixed": True, "llm": result}
