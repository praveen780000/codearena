"""
Client for CodeArena's FastAPI judge service.

NOTE ON SECURITY: this is a plain internal HTTP POST via `requests`, with
no JWT / API-key auth — see README "Known limitations & next steps".
"""
import requests
from django.conf import settings


class JudgeServiceError(Exception):
    pass


def judge_code(code, sample_input, expected_output, other_submissions):
    """
    other_submissions: list of {"username": str, "code": str}
    Returns dict: {"output", "status", "similarity_score", "most_similar_user"}
    """
    url = f"{settings.FASTAPI_SERVICE_URL}/judge"
    payload = {
        "code": code,
        "sample_input": sample_input or "",
        "expected_output": expected_output or "",
        "other_submissions": other_submissions,
    }
    try:
        resp = requests.post(url, json=payload, timeout=10)
        resp.raise_for_status()
    except requests.exceptions.RequestException as exc:
        raise JudgeServiceError(str(exc)) from exc
    return resp.json()
