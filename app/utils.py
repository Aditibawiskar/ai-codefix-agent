# app/utils.py
import json
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict, Optional, Tuple


def run_shell(cmd: str, cwd: Optional[Path] = None) -> Tuple[int, str, str]:
    proc = subprocess.Popen(
        cmd,
        cwd=str(cwd) if cwd is not None else None,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    out, err = proc.communicate()
    return proc.returncode, out, err


def extract_json(text: str) -> Tuple[Dict[str, Any] | None, Optional[str]]:
    try:
        obj = json.loads(text)
        return obj, None
    except Exception as exc:
        return None, str(exc)


def validate_patch_text(patch: str) -> Dict[str, Any]:
    tmp = Path(tempfile.mkdtemp())
    (tmp / "example.py").write_text("def add(a,b):\n    return a+b\n")
    (tmp / "patch.diff").write_text(patch, encoding="utf-8")

    code, out, err = run_shell(
        f"git apply --check {tmp/'patch.diff'}",
        cwd=tmp,
    )
    preview = patch[:1000]
    shutil.rmtree(tmp, ignore_errors=True)
    return {"ok": code == 0, "stdout": out, "stderr": err, "preview": preview}


def run_checks(repo_path: Path) -> Dict[str, Any]:
    flake_cmd = "flake8 app || true"
    pytest_cmd = "pytest -q || true"
    fcode, fout, ferr = run_shell(flake_cmd, cwd=repo_path)
    pcode, pout, perr = run_shell(pytest_cmd, cwd=repo_path)
    return {
        "flake8": {"ok": fcode == 0, "out": fout, "err": ferr},
        "pytest": {"ok": pcode == 0, "out": pout, "err": perr},
    }
