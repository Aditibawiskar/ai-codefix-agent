# app/main.py
import logging
import os
import tempfile
from pathlib import Path
from typing import Any, Dict

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.api import routes
from app.llm_client import call_hf_inference, is_hf_configured
from app.prompt_templates import PROMPT
from app.schemas import CodeDiff, CodeFixRequest, CodeFixResponse
from app.utils import extract_json, run_checks, run_shell, validate_patch_text

app = FastAPI(title="AI Code-Fix Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # later you can restrict this to your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger = logging.getLogger("uvicorn.error")
app = FastAPI(title="AI Code-Fix Agent")


app.include_router(routes.router)


@app.get("/")
async def root() -> Dict[str, str]:
    return {"status": "ok", "service": "ai-codefix-agent"}


@app.post("/fix", response_model=CodeFixResponse)
async def fix_code(req: CodeFixRequest):
    prompt = PROMPT.format(code_block=req.code)
    try:
        resp_text, token_info = call_hf_inference(prompt, max_new_tokens=512)
    except Exception as exc:
        # use the exception variable so linters don't complain
        raise HTTPException(status_code=500, detail=f"LLM error: {exc}")

    json_obj, json_err = extract_json(resp_text)
    if json_err:
        raise HTTPException(
            status_code=500,
            detail=("LLM output invalid JSON: " f"{json_err}\nRaw: {resp_text[:500]}"),
        )

    diffs = []
    for d in json_obj.get("diffs", []):
        diffs.append(
            CodeDiff(
                filepath=d.get("filepath", req.file_path or "unknown"),
                diff=d.get("diff", ""),
            )
        )

    model_used = "mock" if not is_hf_configured() else os.getenv("HF_MODEL", "unknown")
    token_usage = json_obj.get("token_usage")

    logger.info(
        "fix called; model=%s token_usage=%s",
        model_used,
        token_usage,
    )

    return CodeFixResponse(
        diffs=diffs,
        test_stub=json_obj.get("test_stub", ""),
        explanation=json_obj.get("explanation", ""),
        model_used=model_used,
        token_usage=token_usage,
    )


@app.post("/validate_patch")
def validate_patch(payload: Dict[str, str]) -> Dict[str, Any]:
    patch = payload.get("patch", "")
    if not patch:
        raise HTTPException(status_code=400, detail="patch is required")
    res = validate_patch_text(patch)
    logger.info(
        "validate_patch received type=%s; len=%d",
        type(patch).__name__,
        len(patch),
    )
    return res


@app.post("/apply_patch")
def apply_patch(payload: Dict[str, str]) -> Dict[str, Any]:
    patch = payload.get("patch", "")
    if not patch:
        raise HTTPException(status_code=400, detail="patch is required")

    tmp = Path(tempfile.mkdtemp())
    (tmp / "example.py").write_text("def add(a,b):\n    return a+b\n")
    pfile = tmp / "patch.diff"
    pfile.write_text(patch, encoding="utf-8")

    code, out, err = run_shell(f"git apply {pfile}", cwd=tmp)
    if code != 0:
        return {"applied": False, "stdout": out, "stderr": err}

    checks = run_checks(tmp)
    return {"applied": True, "checks": checks}
