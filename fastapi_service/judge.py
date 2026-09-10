"""
Core judging logic for CodeArena.

Two responsibilities:
  1. Execute submitted Python code against a sample input/output pair
     and report Pass/Fail/Error.
  2. Compare the submission's code against other users' submissions for
     the same question and flag high textual similarity (a simple,
     non-ML plagiarism signal — not a robust anti-cheating system).

SECURITY WARNING: `run_code` executes arbitrary submitted Python with a
timeout as the only real protection. This is fine for a local demo/college
project but is NOT safe to expose publicly — see README "Known
limitations & next steps" for what real sandboxing would require
(containers, syscall filtering, resource limits, no network access).
"""
import subprocess
import sys
import tempfile
import os
from difflib import SequenceMatcher

EXECUTION_TIMEOUT_SECONDS = 5


def run_code(code: str, sample_input: str = ""):
    """Run `code` as a standalone Python script, feeding it sample_input via stdin."""
    fd, path = tempfile.mkstemp(suffix=".py")
    try:
        with os.fdopen(fd, "w") as f:
            f.write(code)
        result = subprocess.run(
            [sys.executable, path],
            input=sample_input,
            capture_output=True,
            text=True,
            timeout=EXECUTION_TIMEOUT_SECONDS,
        )
        return result.stdout, result.stderr, result.returncode
    except subprocess.TimeoutExpired:
        return "", f"Execution timed out ({EXECUTION_TIMEOUT_SECONDS}s limit).", -1
    finally:
        os.unlink(path)


def judge_submission(code: str, sample_input: str = "", expected_output: str = ""):
    """Run code and classify as Passed / Failed / Error."""
    stdout, stderr, returncode = run_code(code, sample_input)

    if returncode != 0:
        return {"output": (stderr or stdout).strip(), "status": "Error"}

    actual = stdout.strip()
    expected = (expected_output or "").strip()

    if expected:
        status = "Passed" if actual == expected else "Failed"
    else:
        # No expected output configured for this question — just confirm it ran.
        status = "Passed"

    return {"output": stdout, "status": status}


def compute_similarity(code: str, other_submissions):
    """
    other_submissions: list of {"username": str, "code": str}
    Returns the highest textual similarity (0-100) against any other submission.
    """
    best_score = 0.0
    best_username = None

    for other in other_submissions:
        other_code = other.get("code", "")
        if not other_code.strip():
            continue
        ratio = SequenceMatcher(None, code, other_code).ratio() * 100
        if ratio > best_score:
            best_score = ratio
            best_username = other.get("username")

    return {
        "similarity_score": round(best_score, 1),
        "most_similar_user": best_username,
    }
