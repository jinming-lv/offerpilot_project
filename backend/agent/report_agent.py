"""
============================================================
 ReportAgent — 统一报告生成 Agent
============================================================

整合各 Agent 输出，生成统一 JSON 供前端：
  • ECharts 图表渲染（雷达图 / 柱状图 / 仪表盘）
  • PDF 导出（pdfmake）
  • 报告页面展示

上游 Agent 依赖：
  ResumeAgent   → 简历解析结果
  JobAgent      → JD 解析结果
  MatchAgent    → 匹配度 + 雷达图数据
  InterviewAgent → 面试题 + 评分
  LearningAgent  → 学习路线
============================================================
"""

import json
import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from datetime import datetime

try:
    from utils.logger import get_logger
    logger = get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)
    logger.warning("[ReportAgent] 独立运行模式，使用标准 logging")

# ============================================================
# 标准数据结构定义
# ============================================================

@dataclass
class CandidateInfo:
    """候选人基本信息 ⬅ 来自 ResumeAgent"""
    name: str = ""
    gender: str = ""
    education: str = ""
    major: str = ""
    email: str = ""
    phone: str = ""
    total_skills: int = 0
    project_count: int = 0
    experience_count: int = 0


@dataclass
class SkillItem:
    """技能评价项"""
    skill: str = ""
    level: str = ""  # 精通 / 熟练 / 掌握 / 了解


@dataclass
class WeaknessItem:
    """能力差距项"""
    skill: str = ""
    gap: str = ""  # 差距描述


@dataclass
class DimensionScore:
    """维度得分（供雷达图 / 柱状图）"""
    name: str = ""
    value: float = 0.0


@dataclass
class StudyPlanItem:
    """学习计划条目（供 14 天时间线）"""
    days: str = ""       # 如 "Day 1-2"
    topic: str = ""
    priority: str = "medium"  # high / medium / low


@dataclass
class ReportData:
    """
    标准报告数据结构 —— 供前端 reportData 直接映射
    与 frontend/src/views/ReportView.vue 的 reportData 字段一一对应
    """
    # -- 候选人信息 --
    candidate_info: CandidateInfo = field(default_factory=CandidateInfo)

    # -- 岗位信息 --
    job_title: str = ""
    job_company: str = ""
    job_tags: List[str] = field(default_factory=list)

    # -- 匹配数据 --
    match_score: float = 0.0
    matched_skills: List[str] = field(default_factory=list)
    missing_skills: List[str] = field(default_factory=list)

    # -- 分析项 --
    strengths: List[SkillItem] = field(default_factory=list)
    weaknesses: List[WeaknessItem] = field(default_factory=list)
    analysis_summary: str = ""

    # -- 图表数据 --
    dimension_scores: List[DimensionScore] = field(default_factory=list)
    radar_data: Optional[Dict[str, Any]] = None  # match_agent 原始雷达数据

    # -- 学习规划 --
    study_plan: List[StudyPlanItem] = field(default_factory=list)

    # -- 面试 --
    interview_questions: List[str] = field(default_factory=list)
    interview_summary: Optional[str] = None

    # -- 元信息 --
    generated_at: str = ""
    version: str = "1.0"


# ============================================================
# ReportAgent 主类
# ============================================================

class ReportAgent:
    """
    统一报告生成代理

    使用示例::

        agent = ReportAgent()
        report = agent.generate_report(
            resume_data=resume_agent_result,
            match_data=match_agent_result,
            interview_questions_list=[...],
            learning_plan=learning_agent_result,
        )
        json_output = agent.to_json(report)        # 标准 JSON 字符串
        frontend_payload = agent.to_frontend(report) # 前端可直接绑定
    """

    def __init__(self, save_to_file: bool = False):
        """
        Args:
            save_to_file: 是否将报告保存到磁盘
        """
        self.save_to_file = save_to_file
        self.dataset_dir = "dataset/reports"
        if self.save_to_file:
            os.makedirs(self.dataset_dir, exist_ok=True)

    # ---------------------------------------------------------
    # 核心方法：生成报告
    # ---------------------------------------------------------
    def generate_report(
        self,
        resume_data: Optional[Dict[str, Any]] = None,
        job_data: Optional[Dict[str, Any]] = None,
        match_data: Optional[Dict[str, Any]] = None,
        interview_questions_list: Optional[List[Dict[str, Any]]] = None,
        interview_summary_text: Optional[str] = None,
        learning_plan: Optional[Dict[str, Any]] = None,
    ) -> ReportData:
        """
        整合所有 Agent 输出，生成统一报告。

        Args:
            resume_data:   ResumeAgent.parse_resume() 的返回值
            job_data:      JobAgent.parse_jd() 的返回值
            match_data:    MatchAgent.match_full() 的返回值
            interview_questions_list: 面试题列表
            interview_summary_text:   面试总结文本
            learning_plan:            LearningAgent.generate_learning_plan() 返回值

        Returns:
            ReportData 标准数据结构
        """
        report = ReportData()
        report.generated_at = datetime.now().isoformat()

        # ---- 1. 候选人信息 ⬅ ResumeAgent ----
        if resume_data:
            self._merge_candidate_info(report, resume_data)

        # ---- 2. 岗位信息 ⬅ JobAgent / MatchAgent ----
        if job_data:
            self._merge_job_info(report, job_data)
        if match_data:
            self._merge_match_info(report, match_data)

        # ---- 3. 匹配分析 ⬅ MatchAgent ----
        if match_data:
            self._merge_match_detail(report, match_data)

        # ---- 4. 优势 / 差距 ⬅ MatchAgent ----
        if match_data:
            self._merge_strengths_weaknesses(report, match_data)

        # ---- 5. 雷达图 / 维度得分 ⬅ MatchAgent ----
        if match_data:
            self._merge_chart_data(report, match_data)

        # ---- 6. 学习规划 ⬅ LearningAgent ----
        if learning_plan:
            self._merge_study_plan(report, learning_plan)

        # ---- 7. 面试题 + 总结 ⬅ InterviewAgent ----
        if interview_questions_list:
            self._merge_interview_questions(report, interview_questions_list)
        if interview_summary_text:
            report.interview_summary = interview_summary_text

        # ---- 8. 可选：保存到文件 ----
        if self.save_to_file:
            self._save_report(report)

        logger.info(f"报告生成完成: match_score={report.match_score}, "
                     f"strengths={len(report.strengths)}, "
                     f"study_plan={len(report.study_plan)}")
        return report

    # ---------------------------------------------------------
    # 各 Agent 数据合并逻辑（私有方法）
    # ---------------------------------------------------------

    def _merge_candidate_info(self, report: ReportData, resume_data: Dict[str, Any]):
        """从简历数据提取候选人信息"""
        # 兼容两种输入格式：
        #   (A) 直接 resume_dict（match_agent 的入参格式）
        #   (B) {"data": {...}} 包裹（ResumeAgent 的返回值）
        inner = resume_data.get("data", resume_data)
        basic = inner.get("basic_info", {})
        skills = inner.get("skills", [])
        projects = inner.get("projects", [])
        experience = inner.get("experience", [])

        report.candidate_info = CandidateInfo(
            name=basic.get("name", ""),
            gender=basic.get("gender", ""),
            education=basic.get("education", ""),
            major=basic.get("major", ""),
            email=basic.get("email", ""),
            phone=basic.get("phone", ""),
            total_skills=len(skills),
            project_count=len(projects),
            experience_count=len(experience),
        )

    def _merge_job_info(self, report: ReportData, job_data: Dict[str, Any]):
        """从 JD 解析结果提取岗位信息"""
        report.job_title = job_data.get("job_title", report.job_title)

        # 构建岗位标签
        tags = []
        if job_data.get("experience_level"):
            tags.append(job_data["experience_level"])
        if job_data.get("education"):
            tags.append(job_data["education"])
        if job_data.get("location"):
            tags.append(job_data["location"])
        report.job_tags = tags

    def _merge_match_info(self, report: ReportData, match_data: Dict[str, Any]):
        """从匹配结果补充岗位信息（match_data.job_info 优先级 > job_data）"""
        job_info = match_data.get("job_info", {})
        if job_info.get("job_title"):
            report.job_title = job_info["job_title"]

        # 构建岗位标签
        tags = list(report.job_tags)  # 保留已有
        if job_info.get("experience_level"):
            tags.append(job_info["experience_level"])
        if job_info.get("education"):
            tags.append(job_info["education"])

        # 去重
        seen = set()
        unique_tags = []
        for t in tags:
            if t not in seen:
                seen.add(t)
                unique_tags.append(t)
        report.job_tags = unique_tags

    def _merge_match_detail(self, report: ReportData, match_data: Dict[str, Any]):
        """从匹配结果提取匹配数据"""
        match = match_data.get("match", {})
        report.match_score = match.get("match_score", 0)
        report.matched_skills = match.get("matched_required", match.get("matched_skills", []))
        report.missing_skills = match.get("missing_required", match.get("missing_skills", []))

        # 分析摘要
        analysis = match_data.get("analysis", "")
        if isinstance(analysis, str):
            report.analysis_summary = analysis
        elif isinstance(analysis, dict):
            report.analysis_summary = analysis.get("summary", "")

    def _merge_strengths_weaknesses(self, report: ReportData, match_data: Dict[str, Any]):
        """从匹配结果生成优势/差距列表"""
        match = match_data.get("match", {})

        # 优势 = 已匹配技能
        matched_skills = match.get("matched_required", match.get("matched_skills", []))
        for i, skill in enumerate(matched_skills):
            report.strengths.append(SkillItem(
                skill=skill,
                level="精通" if i < 2 else "熟练"
            ))

        # 差距 = 缺失技能
        missing_skills = match.get("missing_required", match.get("missing_skills", []))
        for skill in missing_skills:
            report.weaknesses.append(WeaknessItem(
                skill=skill,
                gap=f"建议补充 {skill} 的实战经验"
            ))

    def _merge_chart_data(self, report: ReportData, match_data: Dict[str, Any]):
        """从匹配结果生成图表维度分"""
        radar = match_data.get("radar", {})

        # 1. 保存原始雷达数据（前端可直接使用）
        report.radar_data = radar

        # 2. 生成统一的 dimension_scores（供前端柱状图 / 雷达图）
        dimensions = radar.get("dimensions", [])
        resume_values = radar.get("resume", [])
        job_required = radar.get("job_required", [])

        report.dimension_scores = []
        for i, dim in enumerate(dimensions):
            resume_val = resume_values[i] if i < len(resume_values) else 0
            job_val = job_required[i] if i < len(job_required) else 0
            # 归一化为 0-100 分（原值为 0-1）
            score = round(resume_val * 100)
            report.dimension_scores.append(DimensionScore(
                name=dim,
                value=score
            ))

        # 补充：如果雷达数据为空，使用默认维度
        if not report.dimension_scores:
            report.dimension_scores = [
                DimensionScore(name="核心技能", value=report.match_score),
                DimensionScore(name="项目经验", value=min(report.match_score + 5, 100)),
            ]

    def _merge_study_plan(self, report: ReportData, learning_plan: Dict[str, Any]):
        """从学习规划数据提取学习计划条目"""
        roadmap = learning_plan.get("roadmap", [])
        study_plan_list = learning_plan.get("studyPlan", learning_plan.get("study_plan", []))

        items = roadmap or study_plan_list
        for item in items:
            report.study_plan.append(StudyPlanItem(
                days=item.get("days", item.get("day", f"Day {item.get('day', '')}")),
                topic=item.get("topic", item.get("content", "")),
                priority=item.get("priority", "medium"),
            ))

    def _merge_interview_questions(
        self, report: ReportData, questions: List[Dict[str, Any]]
    ):
        """从面试题列表提取问题文本"""
        for q in questions:
            if isinstance(q, str):
                report.interview_questions.append(q)
            elif isinstance(q, dict):
                text = q.get("interviewer_text") or q.get("question") or q.get("title") or q.get("description", "")
                report.interview_questions.append(text)

    # ---------------------------------------------------------
    # 输出方法
    # ---------------------------------------------------------

    def to_dict(self, report: ReportData) -> Dict[str, Any]:
        """
        转为标准字典（供 FastAPI JSONResponse 序列化）。

        Returns:
            与前端 reportData 的字段完全对齐:
            {
              candidate_info: {...},
              job_title: "...",
              job_company: "...",
              job_tags: [...],
              match_score: ...,
              matched_skills: [...],
              missing_skills: [...],
              strengths: [{skill, level}, ...],
              weaknesses: [{skill, gap}, ...],
              analysis_summary: "...",
              dimension_scores: [{name, value}, ...],
              radar_data: {...} | null,
              study_plan: [{days, topic, priority}, ...],
              interview_questions: [...],
              interview_summary: "..." | null,
              generated_at: "...",
              version: "1.0",
            }
        """
        return {
            "candidate_info": asdict(report.candidate_info),
            "job_title": report.job_title,
            "job_company": report.job_company,
            "job_tags": report.job_tags,
            "match_score": report.match_score,
            "matched_skills": report.matched_skills,
            "missing_skills": report.missing_skills,
            "strengths": [asdict(s) for s in report.strengths],
            "weaknesses": [asdict(w) for w in report.weaknesses],
            "analysis_summary": report.analysis_summary,
            "dimension_scores": [asdict(d) for d in report.dimension_scores],
            "radar_data": report.radar_data,
            "study_plan": [asdict(p) for p in report.study_plan],
            "interview_questions": report.interview_questions,
            "interview_summary": report.interview_summary,
            "generated_at": report.generated_at,
            "version": report.version,
        }

    def to_json(self, report: ReportData, indent: int = 2) -> str:
        """
        转为 JSON 字符串。

        Args:
            report: ReportData 实例
            indent: JSON 缩进（默认 2 空格）
        """
        return json.dumps(self.to_dict(report), ensure_ascii=False, indent=indent)

    def to_frontend(self, report: ReportData) -> Dict[str, Any]:
        """
        输出前端可以直接绑定到 reportData 的扁平化字典。

        前端 ReportView.vue 的 reportData 字段映射:

        reportData.overallMatch  ← match_score
        reportData.jobTitle      ← job_title
        reportData.jobCompany    ← job_company
        reportData.candidateName ← candidate_info.name
        reportData.candidateEdu  ← education · major
        reportData.candidateExpYears ← inferred from experience_count
        reportData.jobTags       ← job_tags
        reportData.strengths     ← strengths
        reportData.weaknesses    ← weaknesses
        reportData.dimensionScores ← dimension_scores
        reportData.studyPlan     ← study_plan
        reportData.interviewQuestions ← interview_questions
        """
        ci = report.candidate_info
        return {
            "overallMatch": report.match_score,
            "jobTitle": report.job_title,
            "jobCompany": report.job_company or "OfferPilot 智能匹配",
            "candidateName": ci.name,
            "candidateEdu": " · ".join(filter(None, [ci.education, ci.major])) or "未知",
            "candidateExpYears": ci.experience_count,
            "jobTags": report.job_tags,
            "strengths": [asdict(s) for s in report.strengths],
            "weaknesses": [asdict(w) for w in report.weaknesses],
            "dimensionScores": [asdict(d) for d in report.dimension_scores],
            "analysisSummary": report.analysis_summary,
            "studyPlan": [asdict(p) for p in report.study_plan],
            "interviewQuestions": report.interview_questions,
            "interviewSummary": report.interview_summary,
            "radarData": report.radar_data,
            "matchedSkills": report.matched_skills,
            "missingSkills": report.missing_skills,
            "generatedAt": report.generated_at,
        }

    # ---------------------------------------------------------
    # 辅助方法
    # ---------------------------------------------------------

    def _save_report(self, report: ReportData) -> str:
        """保存报告到磁盘"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"report_{timestamp}.json"
        filepath = os.path.join(self.dataset_dir, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(self.to_json(report))

        logger.info(f"报告已保存: {filepath}")
        return filepath

    def generate_empty_report(self) -> ReportData:
        """生成空白报告模板（前端默认值兜底）"""
        report = ReportData()
        report.generated_at = datetime.now().isoformat()
        report.candidate_info = CandidateInfo(name="待解析")
        report.job_title = "待输入岗位"
        report.match_score = 0
        report.strengths = []
        report.weaknesses = []
        report.dimension_scores = [
            DimensionScore(name="核心技能", value=0),
            DimensionScore(name="项目经验", value=0),
        ]
        report.study_plan = [
            StudyPlanItem(days="Day 1-2", topic="请先完成简历解析", priority="high"),
        ]
        report.interview_questions = ["请先完成匹配分析，再开始模拟面试"]
        return report


# ============================================================
# 便捷函数（无需实例化 ReportAgent 即可使用）
# ============================================================

# 全局单例
_default_agent: Optional[ReportAgent] = None


def get_report_agent(save_to_file: bool = False) -> ReportAgent:
    """获取 ReportAgent 单例"""
    global _default_agent
    if _default_agent is None:
        _default_agent = ReportAgent(save_to_file=save_to_file)
    return _default_agent


def generate_unified_report(
    resume_data: Optional[Dict] = None,
    job_data: Optional[Dict] = None,
    match_data: Optional[Dict] = None,
    interview_questions: Optional[List[Dict]] = None,
    interview_summary: Optional[str] = None,
    learning_plan: Optional[Dict] = None,
) -> Dict[str, Any]:
    """
    一行代码生成统一报告（便捷函数）

    用法::

        from agent.report_agent import generate_unified_report
        result = generate_unified_report(
            resume_data=resume_agent_result,
            match_data=match_agent_result,
            interview_questions=questions,
            learning_plan=plan,
        )
        # result 可直接返回给前端
    """
    agent = get_report_agent()
    report = agent.generate_report(
        resume_data=resume_data,
        job_data=job_data,
        match_data=match_data,
        interview_questions_list=interview_questions,
        interview_summary_text=interview_summary,
        learning_plan=learning_plan,
    )
    return agent.to_frontend(report)


# ============================================================
# 测试代码
# ============================================================
if __name__ == "__main__":
    # 确保可以独立运行（添加 backend/ 到 sys.path，与 app.py 行为一致）
    import sys as _sys
    import os as _os
    _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))

    # ======== 模拟各 Agent 输出 ========

    # 1. 模拟 ResumeAgent 输出
    mock_resume = {
        "data": {
            "basic_info": {
                "name": "张三",
                "gender": "男",
                "education": "本科",
                "major": "计算机科学与技术",
                "email": "zhangsan@example.com",
                "phone": "138xxxx",
            },
            "skills": ["Python", "Django", "MySQL", "Linux", "Git"],
            "projects": [
                {"project_name": "电商平台", "role": "后端开发"},
                {"project_name": "数据可视化", "role": "全栈"},
            ],
            "experience": [
                {"company": "ABC科技", "position": "Python开发", "duration": "2024.01-2025.06"},
            ],
        }
    }

    # 2. 模拟 MatchAgent 输出
    mock_match = {
        "job_info": {
            "job_title": "Python 后端开发工程师",
            "required_skills": ["Python", "Django", "MySQL", "Redis", "Docker"],
            "preferred_skills": ["K8s", "消息队列"],
            "experience_level": "3-5年",
            "education": "本科及以上",
        },
        "match": {
            "match_score": 72.5,
            "matched_required": ["Python", "Django", "MySQL"],
            "missing_required": ["Redis", "Docker"],
            "matched_preferred": [],
            "missing_preferred": ["K8s", "消息队列"],
        },
        "analysis": "你与岗位匹配度为 72.5 分。核心优势是匹配了 Python、Django、MySQL 等 3 项关键技能。建议重点补充 Redis、Docker。",
        "radar": {
            "dimensions": ["Python", "Django", "MySQL", "Redis", "Docker", "K8s"],
            "resume": [1, 1, 1, 0, 0, 0],
            "job_required": [1, 1, 1, 1, 1, 0.5],
        },
    }

    # 3. 模拟 InterviewAgent 输出
    mock_interview_questions = [
        {"question": "请介绍你的项目经验", "interviewer_text": "请简要介绍你最近的项目经验和技术栈。"},
        {"question": "数据库设计", "interviewer_text": "你如何设计高并发场景下的数据库方案？"},
        {"question": "缓存策略", "interviewer_text": "请谈谈 Redis 缓存策略及常见问题。"},
    ]
    mock_interview_summary = "面试综合评分 4.0/5.0。优势：项目经验表述清晰。提升：需要加强缓存和高并发场景的经验。"

    # 4. 模拟 LearningAgent 输出
    mock_learning_plan = {
        "duration": "14天",
        "roadmap": [
            {"day": 1, "topic": "Redis 核心数据结构与缓存策略", "priority": "high", "content": "学习 Redis 五种数据结构"},
            {"day": 2, "topic": "Redis 缓存穿透/雪崩解决方案", "priority": "high", "content": ""},
            {"day": 3, "topic": "Docker 基础与镜像构建", "priority": "high", "content": ""},
            {"day": 4, "topic": "Docker Compose 多容器编排", "priority": "medium", "content": ""},
            {"day": 5, "topic": "消息队列基础", "priority": "medium", "content": ""},
        ],
    }

    # ======== 测试 ReportAgent ========
    agent = ReportAgent(save_to_file=False)
    report = agent.generate_report(
        resume_data=mock_resume,
        match_data=mock_match,
        interview_questions_list=mock_interview_questions,
        interview_summary_text=mock_interview_summary,
        learning_plan=mock_learning_plan,
    )

    print("=" * 60)
    print("[TEST] to_dict")
    print("=" * 60)
    print(agent.to_json(report))

    print("\n" + "=" * 60)
    print("[TEST] to_frontend")
    print("=" * 60)
    frontend_payload = agent.to_frontend(report)
    print(json.dumps(frontend_payload, ensure_ascii=False, indent=2))

    print("\n" + "=" * 60)
    print("[TEST] generate_unified_report")
    print("=" * 60)
    quick_result = generate_unified_report(
        resume_data=mock_resume,
        match_data=mock_match,
    )
    print(f"OK: match_score={quick_result['overallMatch']}, "
          f"candidate={quick_result['candidateName']}, "
          f"strengths={len(quick_result['strengths'])}")
    print("[PASS] All tests completed.")
