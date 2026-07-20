from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn
import httpx
import os
import asyncio
from concurrent.futures import ThreadPoolExecutor
from fastapi.concurrency import run_in_threadpool  # 引入 FastAPI 自带的同步转异步工具
from agent.match_agent import match_full
from agent.job_agent import parse_jd

# ============ 数据模型（遵循A的API文档） ============

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
    resume_id: str
    job_text: str

class JDTextRequest(BaseModel):
    job_text: str

# ============ 适配函数：A的格式 → match_full 需要的格式 ============

def adapt_resume_to_match(resume_data: ResumeData) -> dict:
    """将A的简历格式适配为 match_full 需要的格式"""
    
    basic = resume_data.basic_info
    
    # 1. 合并教育信息
    edu_parts = []
    if basic.education:
        edu_parts.append(basic.education)
    if basic.major:
        edu_parts.append(basic.major)
    education = "-".join(edu_parts) if edu_parts else "未知"
    
    # 2. 提取项目名称列表
    project_names = [p.project_name for p in resume_data.projects if p.project_name]
    
    # 3. 提取经历摘要
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
        "experience": exp_summary
    }

# ============ FastAPI 应用 ============

app = FastAPI(title="OfferPilot - Match API", version="1.0")

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# A的简历服务地址（实际运行时改成A的地址）
RESUME_SERVICE_URL = os.getenv("RESUME_SERVICE_URL", "http://localhost:8001/api/resume/upload")

# ============ 接口定义 ============


@app.post("/api/match")
async def match_endpoint(request: MatchRequest):
    try:
        # 直接使用模拟数据，不尝试连接任何外部服务
        use_mock = True
        resume_data = {
            "resume_id": "mock_001",
            "basic_info": {
                "name": "张三",
                "education": "本科",
                "major": "计算机科学与技术"
            },
            "skills": ["Python", "Django", "MySQL", "Linux", "Git"],
            "projects": [
                {"project_name": "电商平台开发", "role": "后端开发"},
                {"project_name": "数据可视化系统", "role": "全栈"}
            ],
            "experience": [
                {"company": "ABC科技", "position": "Python开发", "duration": "2024.01-2025.06"}
            ]
        }
        
        # 适配数据
        adapted_resume = adapt_resume_to_match(ResumeData(**resume_data))
        
        # 调用匹配引擎
        match_result = match_full(adapted_resume, request.job_text)
        
        return {
            "success": True,
            "data": {
                "match": match_result.get("match"),
                "analysis": match_result.get("analysis"),
                "radar": match_result.get("radar"),
                "job_info": match_result.get("job_info"),
                "_meta": {"use_mock": True}
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.post("/api/match/test")
async def match_test():
    """测试接口：用模拟简历数据，不依赖A的服务"""
    try:
        # 模拟简历数据（A格式）
        mock_resume = {
            "resume_id": "test_001",
            "basic_info": {
                "name": "张三",
                "education": "本科",
                "major": "计算机科学与技术"
            },
            "skills": ["Python", "Django", "MySQL", "Linux", "Git"],
            "projects": [
                {"project_name": "电商平台开发", "role": "后端开发"},
                {"project_name": "数据可视化系统", "role": "全栈"}
            ],
            "experience": [
                {"company": "ABC科技", "position": "Python开发", "duration": "2024.01-2025.06"}
            ]
        }
        
        # 模拟JD文本
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
        
        # 适配数据
        adapted = adapt_resume_to_match(ResumeData(**mock_resume))
        
        # 调用匹配引擎（90秒超时保护）
        loop = asyncio.get_running_loop()
        result = await asyncio.wait_for(
            loop.run_in_executor(
                None,
                lambda: match_full(adapted, mock_jd)
            ),
            timeout=90.0
        )
        
        return {
            "success": True,
            "data": {
                "match": result.get("match"),
                "analysis": result.get("analysis"),
                "radar": result.get("radar"),
                "job_info": result.get("job_info")
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))






@app.post("/api/parse_jd")
async def parse_jd_endpoint(request: JDTextRequest):
    """解析JD文本（测试用）"""
    try:
        result = parse_jd(request.job_text)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "service": "OfferPilot Match API"}


@app.get("/api/health/full")
async def full_health_check():
    """完整健康检查（包含依赖服务）"""
    status = {"match_api": "ok"}
    
    # 检查A的服务是否可达
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(RESUME_SERVICE_URL.replace("/upload", "/health"))
            status["resume_service"] = "ok" if resp.status_code == 200 else "unavailable"
    except:
        status["resume_service"] = "unreachable"
    
    return status


if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True,           # ← 开启热重载
        reload_dirs=["agent"]  # ← 只监控 agent 目录的变化（可选）
    )