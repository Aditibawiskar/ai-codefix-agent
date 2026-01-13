import json
import os
from typing import Any, Dict, Tuple

from huggingface_hub import InferenceClient


def is_hf_configured() -> bool:
    return bool(os.getenv("HF_TOKEN")) and bool(os.getenv("HF_MODEL"))


def call_hf_inference(
    prompt: str,
    max_new_tokens: int = 512,
) -> Tuple[str, Dict[str, Any]]:
    """
    Return (response_text, token_info).
    Uses InferenceClient with strict chat_completion (required for Qwen/Zephyr).
    """

    # 1. Check for MOCK mode
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
            "diffs": [{"filepath": "example.py", "diff": "\n".join(diff_lines)}],
            "test_stub": "# Mock test stub",
            "explanation": "Mocked response (MOCK_LLM=true).",
            "token_usage": {"prompt": 1, "completion": 1},
        }
        return json.dumps(mock), mock.get("token_usage", {})

    # 2. REAL AI CALL
    try:
        model_id = os.getenv("HF_MODEL")
        token = os.getenv("HF_TOKEN")

        # Initialize client
        client = InferenceClient(token=token)

        print(f"DEBUG: Calling Chat Completion on {model_id}...")

        # STRICT CHAT MODE
        # We do NOT use text_generation because providers for Qwen reject it.
        messages = [{"role": "user", "content": prompt}]

        response = client.chat_completion(
            messages=messages,
            model=model_id,
            max_tokens=max_new_tokens,
            temperature=0.2,
            stream=False,
        )

        # Extract content
        content = response.choices[0].message.content

        # Extract Usage
        usage = {"prompt": 0, "completion": len(content)}
        if hasattr(response, "usage"):
            usage = {
                "prompt": response.usage.prompt_tokens,
                "completion": response.usage.completion_tokens,
            }

        return content, usage

    except Exception as e:
        print(f"CRITICAL HF ERROR: {e}")
        # If the 7B model also fails, we raise the error to see it in logs
        raise e


def json_str(obj: Dict[str, Any]) -> str:
    return json.dumps(obj)
