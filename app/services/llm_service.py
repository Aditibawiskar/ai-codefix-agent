import os
from typing import Any, Dict

# Try to import the real inference function
try:
    from app.llm_client import call_hf_inference, is_hf_configured  # type: ignore
except Exception:
    call_hf_inference = None  # type: ignore

    def is_hf_configured() -> bool:  # type: ignore
        return False


def call_mock_llm(code: str, max_new_tokens: int = 256) -> Dict[str, Any]:
    """
    Call the real HF client if available; otherwise return a deterministic mock
    used for local development and tests.
    """
    if call_hf_inference is not None:
        # call real inference
        resp_text, token_info = call_hf_inference(
            code,
            max_new_tokens=max_new_tokens,  # type: ignore
        )
        return {
            "text": resp_text,
            "token_info": token_info,
            "model": os.getenv("HF_MODEL", "unknown"),
        }

    # Mock response (shortened lines for flake8 compliance)
    mock_text = (
        '{"diffs": [{"filepath": "example.py", "diff": "--- a/example.py\\n'
        '+++ b/example.py\\n@@\\n-1+1\\n"}],'
        '"test_stub": "", "explanation": "Mocked fix applied", '
        '"token_usage": {"total_tokens": 10}}'
    )

    return {
        "text": mock_text,
        "token_info": {"total_tokens": 10},
        "model": "mock",
    }
