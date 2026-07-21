import os
import json
import re
import httpx 
from typing import List, Dict, Set, Optional
from zhipuai import ZhipuAI
from openai import OpenAI
from utils.env import load_project_env

# 加载项目根目录环境变量
load_project_env()

LLM_API_KEY = os.getenv("LLM_API_KEY") or os.getenv("ZHIPU_API_KEY") or os.getenv("OPENROUTER_API_KEY")
LLM_API_URL = os.getenv("LLM_API_URL", "https://api.deepseek.com")
MODEL_NAME = os.getenv("LLM_MODEL", "deepseek-chat")

# ============ 配置区（与job_agent保持一致） ============
client = OpenAI(
    api_key=LLM_API_KEY,
    base_url=LLM_API_URL,
    http_client=httpx.Client(
        timeout=httpx.Timeout(
            connect=30.0,
            read=120.0,   # 读取超时延长到2分钟
            write=30.0,
            pool=30.0
        )
    )
)
# =====================================================

# 技能同义词映射表
SKILL_SYNONYMS = {
    # 语言/框架
    "javascript": ["js", "javascript", "ecmascript"],
    "typescript": ["ts", "typescript"],
    "python": ["python", "py"],
    "java": ["java", "j2se"],
    "c++": ["c++", "cpp", "cplusplus"],
    "c#": ["c#", "csharp"],
    "go": ["go", "golang"],
    
    # 前端框架
    "react": ["react", "react.js", "reactjs", "react-js"],
    "vue": ["vue", "vue.js", "vuejs", "vue-js"],
    "angular": ["angular", "angular.js", "angularjs"],
    
    # 后端框架
    "spring": ["spring", "spring boot", "spring-boot", "springboot"],
    "django": ["django", "django framework"],
    "flask": ["flask", "flask framework"],
    
    # 数据库
    "mysql": ["mysql", "my sql"],
    "postgresql": ["postgresql", "postgres", "pg"],
    "mongodb": ["mongodb", "mongo", "mongo-db"],
    "redis": ["redis", "redis cache"],
    
    # DevOps/云
    "docker": ["docker", "docker container"],
    "kubernetes": ["kubernetes", "k8s", "kube"],
    "aws": ["aws", "amazon web services"],
    "linux": ["linux", "linux os", "unix"],
    
    # 数据/AI
    "pandas": ["pandas", "pd"],
    "numpy": ["numpy", "np"],
    "scikit-learn": ["scikit-learn", "sklearn", "scikit"],
    "tensorflow": ["tensorflow", "tf"],
    "pytorch": ["pytorch", "torch", "py-torch"],
    
    # 工具
    "git": ["git", "git-scm"],
    "jenkins": ["jenkins", "jenkins-ci"],
}

# 支持相对导入和绝对导入两种方式
try:
    from .job_agent import parse_jd  # 相对导入（作为包运行时）
except ImportError:
    from job_agent import parse_jd   # 绝对导入（直接运行时）

# ============ 匹配度计算（核心算法） ============
def normalize_skill(skill: str) -> str:
    """标准化技能名称，包含同义词映射"""
    # 1. 转小写并去除空格
    skill = skill.lower().strip()
    
    # 2. 移除常见修饰词（原有的）
    skill = re.sub(r'^(熟悉|掌握|精通|了解|熟练使用|有.*经验|.*开发经验|.*经验)\s*', '', skill)
    
    # 3. 移除版本号（如 Python3.8 → Python）
    skill = re.sub(r'[\d.]+$', '', skill)
    skill = skill.rstrip('.-')
    
    # 4. 同义词映射
    for canonical, variants in SKILL_SYNONYMS.items():
        if skill in variants:
            return canonical
    
    return skill

def calculate_match(
    resume_skills: List[str], 
    job_required_skills: List[str],
    job_preferred_skills: List[str] = None
) -> Dict:
    """
    计算简历技能与岗位技能的匹配度
    
    Args:
        resume_skills: 简历中的技能列表
        job_required_skills: 岗位必须技能列表
        job_preferred_skills: 岗位加分技能列表（可选）
        
    Returns:
        Dict: 匹配结果
    """
    job_preferred_skills = job_preferred_skills or []
    
    # 标准化技能
    resume_normalized = [normalize_skill(s) for s in resume_skills]
    job_required_normalized = [normalize_skill(s) for s in job_required_skills]
    job_preferred_normalized = [normalize_skill(s) for s in job_preferred_skills]
    
    resume_set = set(resume_normalized)
    required_set = set(job_required_normalized)
    preferred_set = set(job_preferred_normalized)
    
    # 计算匹配情况
    matched_required = resume_set & required_set
    missing_required = required_set - resume_set
    
    matched_preferred = resume_set & preferred_set
    missing_preferred = preferred_set - resume_set
    
    # 计算匹配度分数（必须技能权重100%，加分技能额外加分）
    # 基础分 = 必须技能匹配数 / 必须技能总数 * 100
    if len(required_set) == 0:
        base_score = 0
    else:
        base_score = len(matched_required) / len(required_set) * 100
    
    # 加分项：匹配到加分技能，每个加2分，最多加10分
    bonus = min(len(matched_preferred) * 2, 10)
    
    final_score = min(base_score + bonus, 100)
    
    return {
        "match_score": round(final_score, 1),
        "base_score": round(base_score, 1),
        "bonus": round(bonus, 1),
        "matched_required": list(matched_required),
        "missing_required": list(missing_required),
        "matched_preferred": list(matched_preferred),
        "missing_preferred": list(missing_preferred),
        "total_required": len(required_set),
        "total_preferred": len(preferred_set),
        "matched_required_count": len(matched_required),
        "matched_preferred_count": len(matched_preferred)
    }


# ============ LLM生成匹配分析 ============
def generate_analysis(
    resume_skills: List[str],
    job_title: str,
    match_result: Dict
) -> str:
    """用LLM生成匹配分析报告"""
    
    prompt = f"""
你是职业规划顾问。请根据以下匹配数据，生成一段针对求职者的匹配分析报告。

岗位名称：{job_title}
简历技能：{resume_skills}
匹配分数：{match_result['match_score']}分
已匹配的必须技能：{match_result['matched_required']}
缺失的必须技能：{match_result['missing_required']}
已匹配的加分技能：{match_result['matched_preferred']}
缺失的加分技能：{match_result['missing_preferred']}

请输出以下格式（200字以内）：
【整体评价】一句话总结匹配情况
【核心优势】求职者在哪些方面符合岗位要求
【主要差距】求职者最需要补充哪些技能
【建议】简单建议
"""
    
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "你是职业规划顾问，擅长分析求职者与岗位的匹配度。输出简洁、专业、有针对性。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"生成分析失败: {e}")
        # 返回一个简单的兜底分析
        missing = match_result.get('missing_required', [])
        if missing:
            return f"你与该岗位匹配度为{match_result['match_score']}分。核心优势是匹配了{len(match_result['matched_required'])}项关键技能。建议重点补充：{', '.join(missing[:3])}。"
        else:
            return f"你与该岗位匹配度为{match_result['match_score']}分。所有必须技能均已匹配，建议进一步提升加分技能以获得更大优势。"


# ============ 生成雷达图数据 ============
def get_radar_data(
    resume_skills: List[str],
    job_required_skills: List[str],
    job_preferred_skills: List[str] = None
) -> Dict:
    """
    生成雷达图数据（供前端ECharts使用）
    
    将技能分为几个维度，计算简历在每个维度的覆盖程度
    """
    job_preferred_skills = job_preferred_skills or []
    
    # 合并所有技能
    all_skills = list(set(
        [normalize_skill(s) for s in resume_skills] +
        [normalize_skill(s) for s in job_required_skills] +
        [normalize_skill(s) for s in job_preferred_skills]
    ))
    
    # 去重后限制最多显示10个技能，避免雷达图太挤
    if len(all_skills) > 10:
        # 优先保留岗位必须技能
        required_set = set([normalize_skill(s) for s in job_required_skills])
        preferred_set = set([normalize_skill(s) for s in job_preferred_skills])
        resume_set = set([normalize_skill(s) for s in resume_skills])
        
        # 必须技能优先
        priority_skills = list(required_set)
        # 再从加分技能和简历技能中补充
        extra = [s for s in (preferred_set | resume_set) if s not in priority_skills]
        all_skills = priority_skills + extra[:10 - len(priority_skills)]
    
    resume_normalized = set([normalize_skill(s) for s in resume_skills])
    
    # 计算每个技能的值：简历有就是1，没有就是0
    resume_values = [1 if s in resume_normalized else 0 for s in all_skills]
    # 岗位期望值：必须技能为1，加分技能为0.5，不相关的为0
    required_set = set([normalize_skill(s) for s in job_required_skills])
    preferred_set = set([normalize_skill(s) for s in job_preferred_skills])
    
    job_values = []
    for s in all_skills:
        if s in required_set:
            job_values.append(1)
        elif s in preferred_set:
            job_values.append(0.5)
        else:
            job_values.append(0)
    
    return {
        "dimensions": all_skills,
        "resume": resume_values,
        "job_required": job_values
    }


# ============ 完整匹配流程 ============
def match_full(resume_dict: Dict, jd_text: str) -> Dict:
    """
    完整的匹配流程：一次LLM调用完成 JD解析 + 匹配分析
    """
    # 1. 提取简历信息
    resume_skills = resume_dict.get("skills", [])
    resume_projects = resume_dict.get("projects", [])
    resume_experience = resume_dict.get("experience", "")
    
    # 2. 构建一次调用的大Prompt
    prompt = f"""
你是一个资深的HR技术招聘专家。请根据以下简历和岗位JD，完成两个任务。

=== 简历信息 ===
技能：{resume_skills}
项目经历：{resume_projects}
工作经历：{resume_experience}

=== 岗位JD ===
{jd_text}

=== 任务 ===
请严格按照以下JSON格式输出（不要输出其他任何内容）：

{{
    "job_info": {{
        "job_title": "岗位名称",
        "required_skills": ["必须技能1", "必须技能2", ...],
        "preferred_skills": ["加分技能1", "加分技能2", ...],
        "responsibilities": ["职责1", "职责2", ...],
        "experience_level": "经验要求",
        "education": "学历要求"
    }},
    "match": {{
        "matched_skills": ["简历中匹配到的技能"],
        "missing_skills": ["简历中缺失的必须技能"],
        "extra_skills": ["简历中有但JD没要求的技能"],
        "match_score": 85
    }},
    "analysis": {{
        "summary": "整体评价（一句话）",
        "advantages": "核心优势",
        "gap": "主要差距",
        "suggestion": "简短建议"
    }}
}}

注意：
1. match_score 取值范围 0-100
2. 技能名称统一用英文
3. 分析要简洁，每条不超过30字
"""
    
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "你是HR技术招聘专家，擅长简历筛选和岗位匹配。只输出JSON。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
        )
        
        content = response.choices[0].message.content
        content = re.sub(r'```json\s*', '', content)
        content = re.sub(r'```\s*', '', content)
        content = content.strip()
        
        result = json.loads(content)
        
        # 转换为原有数据格式
        job_info = result.get("job_info", {})
        match_data = result.get("match", {})
        analysis_data = result.get("analysis", {})
        
        # 构建匹配结果（兼容原有格式）
        match_result = {
            "match_score": match_data.get("match_score", 0),
            "matched_required": match_data.get("matched_skills", []),
            "missing_required": match_data.get("missing_skills", []),
            "matched_preferred": [],
            "missing_preferred": [],
            "total_required": len(job_info.get("required_skills", [])),
            "total_preferred": 0,
            "matched_required_count": len(match_data.get("matched_skills", [])),
            "matched_preferred_count": 0
        }
        
        # 合并分析报告
        analysis = f"【整体评价】{analysis_data.get('summary', '')}\n【核心优势】{analysis_data.get('advantages', '')}\n【主要差距】{analysis_data.get('gap', '')}\n【建议】{analysis_data.get('suggestion', '')}"
        
        # 生成雷达图数据
        radar_data = get_radar_data(
            resume_skills=resume_skills,
            job_required_skills=job_info.get("required_skills", []),
            job_preferred_skills=job_info.get("preferred_skills", [])
        )
        
        return {
            "job_info": job_info,
            "match": match_result,
            "analysis": analysis,
            "radar": radar_data
        }
        
    except Exception as e:
        print(f"调用失败: {e}")
        print("⚠️ LLM调用失败，使用本地计算结果+模板分析快速降级")
        return _build_template_result(resume_dict, jd_text, str(e))


def _build_template_result(resume_dict: Dict, jd_text: str, error_reason: str = "") -> Dict:
    """LLM调用失败时的快速降级：纯本地计算，零LLM调用"""
    resume_skills = resume_dict.get("skills", [])

    job_info = {
        "job_title": "岗位(解析降级)",
        "required_skills": [],
        "preferred_skills": [],
        "responsibilities": [],
        "experience_level": None,
        "education": None,
    }

    jd_lower = jd_text.lower()
    for skill in resume_skills:
        if skill.lower() in jd_lower:
            job_info["required_skills"].append(skill)

    match_result = calculate_match(
        resume_skills=resume_skills,
        job_required_skills=job_info["required_skills"],
        job_preferred_skills=job_info["preferred_skills"],
    )

    missing = match_result.get("missing_required", [])
    if missing:
        analysis = f"【整体评价】LLM服务异常，以下为本地快速评估（{error_reason}）\n【核心优势】匹配了{len(match_result['matched_required'])}项技能\n【主要差距】建议补充：{', '.join(missing[:3])}\n【建议】请稍后重试或检查网络连接"
    else:
        analysis = f"【整体评价】LLM服务异常，以下为本地快速评估（{error_reason}）\n【核心优势】所有提取到的技能均已匹配\n【主要差距】暂无\n【建议】请稍后重试或检查网络连接"

    radar_data = get_radar_data(
        resume_skills=resume_skills,
        job_required_skills=job_info["required_skills"],
        job_preferred_skills=job_info["preferred_skills"],
    )

    return {
        "job_info": job_info,
        "match": match_result,
        "analysis": analysis,
        "radar": radar_data,
        "_meta": {"fallback": True, "error": error_reason},
    }

# ============ 测试代码 ============
if __name__ == "__main__":
    # 测试同义词映射
    print("=" * 60)
    print("测试技能同义词映射")
    print("=" * 60)
    
    test_pairs = [
        ("React.js", "react"),
        ("Python3.8", "python"),
        ("Spring Boot", "spring"),
        ("K8s", "kubernetes"),
        ("sklearn", "scikit-learn"),
        ("JavaScript", "javascript"),
    ]
    
    for raw, expected in test_pairs:
        result = normalize_skill(raw)
        status = "✅" if result == expected else "❌"
        print(f"{status} '{raw}' → '{result}' (期望: '{expected}')")
    
    print("\n" + "=" * 60)
    print("完整匹配流程测试（含同义词）")
    print("=" * 60)
    
    # 简历里写的是原始技能，JD里写的是变体
    test_resume = {
        "name": "李明",
        "skills": ["React", "Python", "Spring", "Kubernetes", "Scikit-learn"],
        "projects": ["智能物流管理系统"],
        "experience": "3年开发经验"
    }
    
    test_jd = """
    岗位名称：后端开发工程师
    任职要求：
    1. 熟悉 React.js
    2. 3年以上 Python3.8 开发经验
    3. 熟悉 Spring Boot
    4. 熟悉 K8s
    5. 熟悉 sklearn
    """
    
    result = match_full(test_resume, test_jd)
    print("=" * 60)
    print("完整匹配结果：")
    print("=" * 60)
    print(f"匹配分数: {result['match']['match_score']}分")
    print(f"匹配到的技能: {result['match']['matched_required']}")
    print(f"缺失的技能: {result['match']['missing_required']}")
    print(f"\n【匹配详情】")
    print(f"  必须技能总数：{result['match']['total_required']}")
    print(f"  已匹配必须技能：{result['match']['matched_required']}")
    print(f"  缺失必须技能：{result['match']['missing_required']}")
    print(f"  匹配加分技能：{result['match']['matched_preferred']}")
    print(f"\n【分析报告】\n{result['analysis']}")
    print(f"\n【雷达图数据】")
    print(json.dumps(result['radar'], ensure_ascii=False, indent=2))
   