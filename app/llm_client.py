# app/llm_client.py
import json
import os
from typing import Any, Dict, Tuple


def is_hf_configured() -> bool:
    return bool(os.getenv("HF_API_KEY")) and bool(os.getenv("HF_MODEL"))


def call_hf_inference(
    prompt: str,
    max_new_tokens: int = 512,
) -> Tuple[str, Dict[str, Any]]:
    """
    Return (response_text, token_info).
    Uses a mock result when HF is not configured or MOCK_LLM=true.
    """

    if not is_hf_configured() or os.getenv("MOCK_LLM", "false").lower() == "true":
        diff_lines = [
            "diff --git a/example.py b/example.py",
            ("index 0000000..0000000 " "100644"),
            "--- a/example.py",
            "+++ b/example.py",
            "@@ -1,2 +1,2 @@",
            "-def add(a,b):",
            "-    return a+b",
            "+def add(a, b):",
            "+    return a + b",
        ]
        mock = {
            "diffs": [
                {"filepath": "example.py", "diff": "\n".join(diff_lines)},
            ],
            "test_stub": "",
            "explanation": "Mocked fix: format and spacing.",
            "token_usage": {"prompt": 1, "completion": 1},
        }
        return json.dumps(mock), mock.get("token_usage", {})

    # If you want a real HF call, implement it here.
    raise RuntimeError("HF model not configured in this environment")


# helper to produce string JSON if needed by other modules
def json_str(obj: Dict[str, Any]) -> str:
    return json.dumps(obj)
