import logging
import os
import tempfile
import traceback  # <--- NEW: Helps print detailed errors
from pathlib import Path
from typing import Any, Dict

from dotenv import load_dotenv  # <--- NEW: Import this
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.api import routes
from app.llm_client import call_hf_inference, is_hf_configured
from app.prompt_templates import PROMPT
from app.schemas import CodeDiff, CodeFixRequest, CodeFixResponse
from app.utils import extract_json, run_checks, run_shell, validate_patch_text

# --- NEW: Load the .env file immediately ---
load_dotenv()

# --- SINGLE FastAPI instance ---
app = FastAPI(title="AI Code-Fix Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost",
        "http://127.0.0.1",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes.router)

logger = logging.getLogger("uvicorn.error")


@app.get("/")
def read_root():
    return {"status": "ok", "service": "ai-codefix-agent"}


@app.post("/fix", response_model=CodeFixResponse)
async def fix_code(req: CodeFixRequest):
    print("--- FIX ENDPOINT TRIGGERED ---")  # Debug print

    # 1. OPTIONAL: Check for Mock Mode (useful if you want to save API credits)
    if os.getenv("MOCK_LLM", "false").lower() == "true":
        print("Mode: MOCK (Skipping API call)")
        return CodeFixResponse(
            diffs=[],
            explanation="Mock Mode enabled. No API call made.",
            test_stub="# Mock test stub",
            model_used="mock",
            # CHANGE THIS LINE BELOW:
            token_usage=0,  # <--- Was {}, changed to 0 to fix the crash
        )

    prompt = PROMPT.format(code_block=req.code)

    # 2. Call the API with better error handling
    try:
        print(f"DEBUG: Calling Chat Completion on {os.getenv('HF_MODEL')}...")
        resp_text, token_info = call_hf_inference(prompt, max_new_tokens=1024)
        print("API Call Successful.")
    except Exception as exc:
        print(f"CRITICAL API ERROR: {exc}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"LLM error: {exc}")

    import re

    # Remove ```json or ``` at the start
    resp_text = re.sub(r"^```(?:json)?", "", resp_text.strip())
    # Remove ``` at the end
    resp_text = re.sub(r"```$", "", resp_text.strip())
    # Final trim to ensure no whitespace issues
    resp_text = resp_text.strip()
    # ----------------------------------------

    try:
        json_obj, json_err = extract_json(resp_text)
    except Exception as exc:
        print(f"JSON EXTRACTION CRASH: {exc}")
        raise HTTPException(status_code=500, detail=f"JSON parsing crashed: {exc}")

    if json_err:
        print(f"JSON INVALID: {json_err}")
        print(f"RAW TEXT RECEIVED: {resp_text}")  # See what the model actually said
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

    # --- FIX START: Handle token_usage safely ---
    raw_usage = json_obj.get("token_usage")
    token_usage = 0

    if isinstance(raw_usage, int):
        token_usage = raw_usage
    elif isinstance(raw_usage, dict):
        # If it's a dictionary like {'prompt': 1, 'completion': 1}, sum the values
        token_usage = sum(v for v in raw_usage.values() if isinstance(v, (int, float)))
    # --- FIX END ---

    logger.info("fix called; model=%s token_usage=%s", model_used, token_usage)

    return CodeFixResponse(
        diffs=diffs,
        test_stub=json_obj.get("test_stub", ""),
        explanation=json_obj.get("explanation", ""),
        model_used=model_used,
        token_usage=token_usage,  # Now guaranteed to be an int
    )


# ... (Keep validate_patch and apply_patch as they were) ...
@app.post("/validate_patch")
def validate_patch(payload: Dict[str, str]) -> Dict[str, Any]:
    patch = payload.get("patch", "")
    if not patch:
        raise HTTPException(status_code=400, detail="patch is required")
    res = validate_patch_text(patch)
    logger.info(
        "validate_patch received type=%s; len=%d", type(patch).__name__, len(patch)
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
