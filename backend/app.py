"""
OfferPilot - CareerPilot 后端入口
FastAPI + DeepSeek
"""

import os
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from api.resume import router as resume_router
from agents.interview.interview_agent import (
    generate_question_text,
    generate_summary,
    score_answer,
    start_interview,
)
from agents.learning.learning_planner import generate_learning_plan
from agents.utils.knowledge_loader import get_question_count

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

app = FastAPI(title="CareerPilot - OfferPilot", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(resume_router, prefix="/api")


class InterviewRequest(BaseModel):
    resume_id: str = ""
    job_id: str = ""
    position: str = "后端开发工程师"
    difficulty: str = "medium"
    tags: list = []


class ScoreRequest(BaseModel):
    question: dict
    answer: str


class SummaryRequest(BaseModel):
    records: list


class LearningRequest(BaseModel):
    resume_id: str = ""
    job_id: str = ""
    position: str = "后端开发工程师"
    duration: str = "14天"


@app.get("/")
def root():
    return {"success": True, "message": "CareerPilot 运行中", "version": "1.0"}


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/api/questions/count")
def question_count():
    return {"success": True, "data": get_question_count()}


@app.post("/api/interview/questions")
def interview_questions(req: InterviewRequest):
    questions = start_interview(
        position=req.position,
        difficulty=req.difficulty,
        tags=req.tags if req.tags else None,
    )
    results = []
    for q in questions:
        question_text = generate_question_text(q, position=req.position)
        results.append(
            {
                "id": q.get("id"),
                "title": q.get("title"),
                "difficulty": q.get("difficulty"),
                "tags": q.get("tags"),
                "description": q.get("description", "")[:300],
                "interviewer_text": question_text,
                "code_templates": q.get("code_templates", {}),
                "leetcode_url": q.get("leetcode_url", ""),
            }
        )
    return {
        "success": True,
        "data": {
            "questions": results,
            "total": len(results),
            "position": req.position,
            "difficulty": req.difficulty,
        },
    }


@app.post("/api/interview/score")
def interview_score(req: ScoreRequest):
    score = score_answer(req.question, req.answer)
    return {"success": True, "data": score}


@app.post("/api/interview/summary")
def interview_summary(req: SummaryRequest):
    summary = generate_summary(req.records)
    return {"success": True, "data": {"summary": summary}}


@app.post("/api/learning/path")
def learning_path(req: LearningRequest):
    plan = generate_learning_plan(
        position=req.position,
        level="junior",
        interview_records=[],
        duration=req.duration,
    )
    return {"success": True, "data": plan}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
