import os
import json
import re
import httpx 
from typing import List, Dict, Optional
from dotenv import load_dotenv
from openai import OpenAI

# 加载环境变量
load_dotenv()

# ============ 配置区（根据你选的模型修改） ============
# 方式一：通义千问（阿里云百炼）
# client = OpenAI(
#    api_key=os.getenv("DASHSCOPE_API_KEY"),
    #base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
#)
#MODEL_NAME = "qwen-plus"

# 方式二：DeepSeek（备选）
# client = OpenAI(
#     api_key=os.getenv("DEEPSEEK_API_KEY"),
#     base_url="https://api.deepseek.com/v1"
# )
# MODEL_NAME = "deepseek-chat"

# 方式三：智谱GLM（备选）
client = OpenAI(
    api_key=os.getenv("ZHIPU_API_KEY"),
    base_url="https://open.bigmodel.cn/api/paas/v4/",
    http_client=httpx.Client(
        timeout=httpx.Timeout(
            connect=30.0,
            read=120.0,   # 读取超时延长到2分钟
            write=30.0,
            pool=30.0
        )
    )
)
MODEL_NAME = "glm-4-flash"
# =====================================================


# ============ Job Agent：解析JD ============
JOB_PROMPT_TEMPLATE = """
你是一位资深的HR技术招聘专家。请分析以下岗位JD，提取关键信息，并严格按照JSON格式输出。

岗位JD：
{jd_text}

请输出以下JSON格式（不要输出其他任何内容）：
{{
    "job_title": "岗位名称",
    "required_skills": ["必须技能1", "必须技能2", ...],
    "preferred_skills": ["加分技能1", "加分技能2", ...],
    "responsibilities": ["职责1", "职责2", ...],
    "experience_level": "经验要求（如：3-5年）",
    "education": "学历要求（如：本科及以上）",
    "location": "工作地点（如果有的话）"
}}

注意：
1. required_skills 只提取硬性技术技能，不包含"沟通能力""团队合作"等软技能
2. 技能名称统一用英文，如 Python、Java、MySQL、Docker
3. 如果某项信息在JD中没有明确提及，填 null
"""


def parse_jd(jd_text: str) -> Dict:
    """
    解析岗位JD，返回结构化信息
    
    Args:
        jd_text: 岗位JD的原始文本
        
    Returns:
        Dict: 结构化后的JD信息
    """
    prompt = JOB_PROMPT_TEMPLATE.format(jd_text=jd_text)
    
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "你是一个专业的HR技术招聘专家，擅长解析岗位需求。只输出JSON格式，不输出其他任何内容。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,  # 低温度保证输出稳定
        )
        
        # 提取返回内容
        content = response.choices[0].message.content
        
        # 尝试解析JSON
        # 有些模型可能返回带 ```json 标记的内容，需要清理
        content = re.sub(r'```json\s*', '', content)
        content = re.sub(r'```\s*', '', content)
        content = content.strip()
        
        result = json.loads(content)
        return result
        
    except json.JSONDecodeError as e:
        print(f"JSON解析失败: {e}")
        print(f"原始返回内容: {content}")
        # 返回一个默认结构，避免程序崩溃
        return {
            "job_title": "解析失败",
            "required_skills": [],
            "preferred_skills": [],
            "responsibilities": [],
            "experience_level": None,
            "education": None,
            "location": None
        }
    except Exception as e:
        print(f"调用LLM失败: {e}")
        return {
            "job_title": "解析失败",
            "required_skills": [],
            "preferred_skills": [],
            "responsibilities": [],
            "experience_level": None,
            "education": None,
            "location": None
        }


# ============ 批量解析 ============
def parse_jd_batch(jd_texts: List[str]) -> List[Dict]:
    """批量解析多条JD"""
    results = []
    for i, text in enumerate(jd_texts):
        print(f"正在解析第 {i+1}/{len(jd_texts)} 条JD...")
        results.append(parse_jd(text))
    return results


# ============ 测试代码 ============
if __name__ == "__main__":
    # 测试用JD
    test_jd = """
    岗位名称：Python后端开发工程师
    经验要求：3-5年
    学历要求：本科及以上
    
    岗位职责：
    1. 负责公司核心业务系统的后端开发与维护
    2. 参与系统架构设计和技术选型
    3. 编写高质量、可维护的代码
    
    任职要求：
    1. 计算机相关专业，本科及以上学历
    2. 3年以上Python开发经验
    3. 熟练掌握Django/Flask框架
    4. 熟悉MySQL、PostgreSQL等关系型数据库
    5. 熟悉Redis、消息队列（Kafka/RabbitMQ）
    6. 熟悉Linux环境，能独立部署服务
    
    加分项：
    - 有微服务架构经验
    - 熟悉Docker/K8s
    """
    
    result = parse_jd(test_jd)
    print("=" * 50)
    print("解析结果：")
    print(json.dumps(result, ensure_ascii=False, indent=2))