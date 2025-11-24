# app/schemas.py
from typing import Optional

from pydantic import BaseModel


class CodeFixRequest(BaseModel):
    repo: Optional[str] = None  # optional: repo/branch info
    file_path: Optional[str] = None
    code: str
    language: Optional[str] = "python"
    test_command: Optional[str] = None


class CodeDiff(BaseModel):
    filepath: str
    diff: str  # unified diff text


class CodeFixResponse(BaseModel):
    diffs: list[CodeDiff]
    test_stub: Optional[str]
    explanation: str
    model_used: str
    token_usage: Optional[int] = None
