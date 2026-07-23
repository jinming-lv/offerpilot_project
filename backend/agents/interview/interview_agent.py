"""
模拟面试 Agent —— 主流程
"""

import json
import sys
import os


from agents.utils.algo_loader import pick_by_difficulty_mix, pick_questions
from agents.utils.concept_loader import pick_questions as pick_concept
from agents.utils.llm_api import chat
from agents.interview.prompts import (
    SYSTEM_PROMPT,
    QUESTION_PROMPT,
    PROJECT_PROMPT,
    FOLLOWUP_PROMPT,
    SCORE_PROMPT,
    SUMMARY_PROMPT,
)


def start_interview(position="后端开发工程师", difficulty="medium", tags=None):
    """
    开始一轮模拟面试
    返回 6 道题：
      1. 八股概念题（从 concept_loader 随机抽）
      2-4. 算法题（从 algo_loader 混合难度抽）
      5. 项目经验题（LLM 基于 position 生成）
      6. 综合追问（LLM 生成，基于薄弱点）
    """
    questions = []

    # 1. 八股概念题 — 随机抽 1 道
    concept_pool = pick_concept(count=1)
    if concept_pool:
        concept_pool[0]["question_type"] = "concept"
        questions.append(concept_pool[0])

    # 2-4. 算法题 — 混合难度抽 3 道
    algo_questions = pick_by_difficulty_mix(easy=1, medium=1, hard=1)
    for q in algo_questions:
        q["question_type"] = "algorithm"
    questions.extend(algo_questions)

    # 5. 项目经验题 — 用 LLM 基于岗位生成
    project_q = _generate_project_question(position, tags)
    if project_q:
        project_q["question_type"] = "project"
        questions.append(project_q)

    # 6. 综合追问 — 用 LLM 生成（贴合岗位技能）
    followup_q = _generate_followup_question(position, tags, algo_questions, concept_pool)
    if followup_q:
        followup_q["question_type"] = "followup"
        questions.append(followup_q)

    return questions


def _generate_project_question(position, tags=None):
    """用 LLM 生成一道项目经验题"""
    tag_hint = ""
    if tags:
        tag_hint = f"（重点关注候选人是否掌握：{', '.join(tags[:5])}）"

    prompt = PROJECT_PROMPT.format(position=position, tag_hint=tag_hint)

    result = chat([
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": prompt},
    ], temperature=0.8)

    return {
        "id": "project_001",
        "title": f"{position}项目经验",
        "difficulty": "Medium",
        "tags": tags or ["项目经验"],
        "description": prompt,
        "interviewer_text": result,
        "question_type": "project",
        "hints": ["请用 STAR 法则组织回答", "突出你在项目中的角色和贡献"],
    }


def _generate_followup_question(position, tags=None, algo_questions=None, concept_questions=None):
    """用 LLM 生成一道综合追问"""
    tag_summary = ", ".join(tags[:5]) if tags else "基础编程能力"

    prompt = f"""你是一个{position}岗位的面试官。

前面已经考了基础概念和算法题。现在请出一道高质量的追问/综合题，考察候选人对岗位核心技能的深度理解。

岗位：{position}
核心技术要求：{tag_summary}

要求：
1. 题目要结合算法和实际工程场景，考察综合能力
2. 难度中等偏上，引导候选人展示思考过程
3. 用口语化的面试官口吻提问
4. 不直接问八股，而是给一个实际场景让候选人分析和解决

请直接以面试官口吻说出题目。"""

    result = chat([
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": prompt},
    ], temperature=0.8)

    return {
        "id": "followup_001",
        "title": f"{position}综合追问",
        "difficulty": "Medium",
        "tags": tags or ["综合"],
        "description": prompt,
        "interviewer_text": result,
        "question_type": "followup",
        "hints": ["先分析问题再给出方案", "关注思路清晰度和表达能力"],
    }


def generate_question_text(question_data, position="后端开发", difficulty="中等"):
    """用 LLM 把题目转成面试官口吻的出题语"""
    # 项目题和追问题已经包含了 interviewer_text，直接返回
    if question_data.get("question_type") in ("project", "followup"):
        return question_data.get("interviewer_text", "")

    languages = "Python, C++, Java, JavaScript"

    q_info = f"""
题号：{question_data.get('id', '')}
标题：{question_data.get('title', '')}
难度：{question_data.get('difficulty', '')}
标签：{', '.join(question_data.get('tags', []))}
题目描述：{question_data.get('description', '')[:500]}
提示：{(question_data.get("hints") or ["无"])[0]}
"""

    prompt = QUESTION_PROMPT.format(
        position=position,
        experience="应届生/实习生",
        difficulty=difficulty,
        question_data=q_info,
        languages=languages,
    )

    result = chat([
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": prompt},
    ], temperature=0.8)

    return result


def score_answer(question_data, answer):
    """评分"""
    hints = "\n".join(question_data.get("hints", ["无提示"]))

    prompt = SCORE_PROMPT.format(
        question=question_data.get("title", ""),
        hints=hints,
        answer=answer,
    )

    result = chat([
        {"role": "system", "content": "你是一个严格的面试评分员。始终返回纯JSON。"},
        {"role": "user", "content": prompt},
    ], temperature=0.3)

    try:
        clean = result.replace("```json", "").replace("```", "").strip()
        score_data = json.loads(clean)
        return score_data
    except json.JSONDecodeError:
        return {
            "correctness": 5,
            "completeness": 5,
            "clarity": 5,
            "code_quality": 5,
            "total_score": 50,
            "strengths": [],
            "weaknesses": ["评分解析失败，请人工复核"],
            "suggestion": "系统评分异常，建议人工评估",
        }


def generate_summary(records):
    """生成面试总结"""
    records_text = ""
    for i, r in enumerate(records, 1):
        records_text += f"\n第{i}题：{r.get('question', '')}\n"
        records_text += f"候选人的回答：{r.get('answer', '')[:300]}\n"
        records_text += f"评分：{json.dumps(r.get('score', {}), ensure_ascii=False)}\n"

    prompt = SUMMARY_PROMPT.format(interview_records=records_text)

    result = chat([
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": prompt},
    ], temperature=0.7)

    return result


if __name__ == "__main__":
    print("=" * 50)
    print("模拟面试测试")
    print("=" * 50)

    questions = start_interview(difficulty="medium")
    print(f"抽到 {len(questions)} 道题:\n")
    for q in questions:
        qtype = q.get("question_type", "algo")
        print(f"  [{qtype}] {q['id']}. {q['title']}")
        print(f"      难度: {q['difficulty']}, 标签: {', '.join(q['tags'])}\n")
