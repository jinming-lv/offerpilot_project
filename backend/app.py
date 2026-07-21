"""
OfferPilot - CareerPilot 后端入口
FastAPI + DeepSeek
"""

import asyncio
import os
import sys
from typing import List, Optional

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from agent.resume_agent import ResumeAgent
from agent.job_agent import parse_jd
from agent.match_agent import match_full
from agent.report_agent import ReportAgent, generate_unified_report
from agents.interview.interview_agent import (
    generate_question_text,
    generate_summary,
    score_answer,
    start_interview,
)
from agents.learning.learning_planner import generate_learning_plan
from agents.utils.knowledge_loader import get_question_count
from api.resume import router as resume_router
from utils.env import load_project_env
from utils.logger import get_logger

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

load_project_env()

app = FastAPI(title="CareerPilot - OfferPilot", version="1.0")
logger = get_logger(__name__)
resume_store = ResumeAgent(save_to_file=True)

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


class BasicInfo(BaseModel):
    name: str
    gender: Optional[str] = ""
    education: Optional[str] = ""
    major: Optional[str] = ""
    email: Optional[str] = ""
    phone: Optional[str] = ""


class Project(BaseModel):
    project_name: str
    role: Optional[str] = ""
    description: Optional[str] = ""
    tech_stack: Optional[List[str]] = []


class Experience(BaseModel):
    company: str
    position: str
    duration: Optional[str] = ""


class ResumeData(BaseModel):
    resume_id: str
    basic_info: BasicInfo
    skills: List[str]
    projects: List[Project]
    experience: List[Experience]


class MatchRequest(BaseModel):
    resume_id: str = ""
    job_text: str
    resume_data: Optional[dict] = None


class JDTextRequest(BaseModel):
    job_text: str


class ReportRequest(BaseModel):
    """统一报告生成请求"""
    resume_data: Optional[dict] = None
    job_data: Optional[dict] = None
    match_data: Optional[dict] = None
    interview_questions: Optional[list] = None
    interview_summary: Optional[str] = None
    learning_plan: Optional[dict] = None


def adapt_resume_to_match(resume_data: ResumeData) -> dict:
    basic = resume_data.basic_info

    edu_parts = []
    if basic.education:
        edu_parts.append(basic.education)
    if basic.major:
        edu_parts.append(basic.major)
    education = "-".join(edu_parts) if edu_parts else "未知"

    project_names = [p.project_name for p in resume_data.projects if p.project_name]

    exp_parts = []
    for e in resume_data.experience:
        parts = []
        if e.company:
            parts.append(e.company)
        if e.position:
            parts.append(e.position)
        if e.duration:
            parts.append(e.duration)
        exp_parts.append(" - ".join(parts) if parts else "无")
    exp_summary = "；".join(exp_parts) if exp_parts else "无工作经历"

    return {
        "name": basic.name if basic.name else "未知",
        "skills": resume_data.skills if resume_data.skills else [],
        "education": education,
        "projects": project_names,
        "experience": exp_summary,
    }


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
    try:
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
    except Exception:
        logger.exception("Failed to generate interview questions")
        raise HTTPException(status_code=500, detail="面试题生成失败")


@app.post("/api/interview/score")
def interview_score(req: ScoreRequest):
    try:
        score = score_answer(req.question, req.answer)
        return {"success": True, "data": score}
    except Exception:
        logger.exception("Failed to score interview answer")
        raise HTTPException(status_code=500, detail="面试评分失败")


@app.post("/api/interview/summary")
def interview_summary(req: SummaryRequest):
    try:
        summary = generate_summary(req.records)
        return {"success": True, "data": {"summary": summary}}
    except Exception:
        logger.exception("Failed to generate interview summary")
        raise HTTPException(status_code=500, detail="面试总结生成失败")


@app.post("/api/learning/path")
def learning_path(req: LearningRequest):
    try:
        plan = generate_learning_plan(
            position=req.position,
            level="junior",
            interview_records=[],
            duration=req.duration,
        )
        return {"success": True, "data": plan}
    except Exception:
        logger.exception("Failed to generate learning path")
        raise HTTPException(status_code=500, detail="学习路径生成失败")


@app.post("/api/match")
async def match_endpoint(request: MatchRequest):
    """匹配接口 - 调用A的简历服务获取真实简历数据"""
    try:
        resume_payload = request.resume_data
        if not resume_payload and request.resume_id:
            resume_payload = resume_store.load_resume_data(request.resume_id)

        if not resume_payload:
            raise HTTPException(status_code=400, detail="缺少简历数据，请先上传简历")

        if "resume_id" not in resume_payload and request.resume_id:
            resume_payload["resume_id"] = request.resume_id

        adapted_resume = adapt_resume_to_match(ResumeData(**resume_payload))
        match_result = match_full(adapted_resume, request.job_text)
        
        return {
            "success": True,
            "data": {
                "match": match_result.get("match"),
                "analysis": match_result.get("analysis"),
                "radar": match_result.get("radar"),
                "job_info": match_result.get("job_info"),
                "_meta": {"use_mock": False},
            },
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




@app.post("/api/match/test")
async def match_test():
    try:
        mock_resume = {
            "resume_id": "test_001",
            "basic_info": {
                "name": "张三",
                "education": "本科",
                "major": "计算机科学与技术",
            },
            "skills": ["Python", "Django", "MySQL", "Linux", "Git"],
            "projects": [
                {"project_name": "电商平台开发", "role": "后端开发"},
                {"project_name": "数据可视化系统", "role": "全栈"},
            ],
            "experience": [
                {
                    "company": "ABC科技",
                    "position": "Python开发",
                    "duration": "2024.01-2025.06",
                }
            ],
        }

        mock_jd = """
        岗位名称：Python后端开发工程师
        经验要求：3-5年
        学历要求：本科及以上

        任职要求：
        1. 3年以上Python开发经验
        2. 熟练掌握Django/Flask框架
        3. 熟悉MySQL、Redis
        4. 熟悉Docker、Linux
        """

        adapted = adapt_resume_to_match(ResumeData(**mock_resume))

        loop = asyncio.get_running_loop()
        result = await asyncio.wait_for(
            loop.run_in_executor(None, lambda: match_full(adapted, mock_jd)),
            timeout=90.0,
        )

        return {
            "success": True,
            "data": {
                "match": result.get("match"),
                "analysis": result.get("analysis"),
                "radar": result.get("radar"),
                "job_info": result.get("job_info"),
            },
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/parse_jd")
async def parse_jd_endpoint(request: JDTextRequest):
    try:
        result = parse_jd(request.job_text)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "service": "OfferPilot Match API"}


RESUME_SERVICE_URL = os.getenv(
    "RESUME_SERVICE_URL", "http://localhost:8001/api/resume/upload"
)


@app.post("/api/report")
def generate_report_endpoint(req: ReportRequest):
    """
    统一报告生成接口
    接收各 Agent 输出，整合为前端可用的标准 JSON 报告
    """
    try:
        result = generate_unified_report(
            resume_data=req.resume_data,
            job_data=req.job_data,
            match_data=req.match_data,
            interview_questions=req.interview_questions,
            interview_summary=req.interview_summary,
            learning_plan=req.learning_plan,
        )
        return {"success": True, "data": result}
    except Exception as e:
        logger.exception("报告生成失败")
        raise HTTPException(status_code=500, detail=f"报告生成失败: {str(e)}")


@app.get("/api/health/full")
async def full_health_check():
    status = {"match_api": "ok"}

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(RESUME_SERVICE_URL.replace("/upload", "/health"))
            status["resume_service"] = (
                "ok" if resp.status_code == 200 else "unavailable"
            )
    except Exception:
        status["resume_service"] = "unreachable"

    return status


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
