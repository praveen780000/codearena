"""
FastAPI judging microservice for CodeArena.

Django (see django_app/submissions/services.py) POSTs a code submission,
the target question's sample input/expected output, and a list of other
users' submissions for the same question. This service runs the code,
scores it Pass/Fail/Error, and reports the highest similarity to any
other submission. No auth on this endpoint yet — see README.
"""
from typing import List

from fastapi import FastAPI
from pydantic import BaseModel

from judge import judge_submission, compute_similarity

app = FastAPI(
    title="CodeArena Judge Service",
    description="Executes submitted code and flags similarity to other submissions.",
    version="1.0.0",
)


class OtherSubmission(BaseModel):
    username: str
    code: str


class JudgeRequest(BaseModel):
    code: str
    sample_input: str = ""
    expected_output: str = ""
    other_submissions: List[OtherSubmission] = []


@app.get("/")
def root():
    return {"status": "ok", "service": "codearena-judge"}


@app.post("/judge")
def judge(payload: JudgeRequest):
    result = judge_submission(payload.code, payload.sample_input, payload.expected_output)
    similarity = compute_similarity(payload.code, [s.dict() for s in payload.other_submissions])
    result.update(similarity)
    return result
