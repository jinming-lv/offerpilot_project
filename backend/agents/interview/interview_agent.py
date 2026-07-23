"""
模拟面试 Agent —— 主流程
"""

import json
import sys
import os



from agents.utils.algo_loader import pick_by_difficulty_mix, pick_questions
from agents.utils.llm_api import chat
from agents.interview.prompts import (
    SYSTEM_PROMPT,
    QUESTION_PROMPT,
    FOLLOWUP_PROMPT,
    SCORE_PROMPT,
    SUMMARY_PROMPT,
)


def start_interview(position="后端开发工程师", difficulty="medium", tags=None):
    """
    开始一轮模拟面试
    返回: {questions: 题目列表, session_id: 会话ID}
    """
    if difficulty == "easy":
        easy, medium, hard = 2, 1, 0
    elif difficulty == "hard":
        easy, medium, hard = 0, 1, 2
    else:
        easy, medium, hard = 1, 2, 0

    questions = pick_by_difficulty_mix(easy=easy, medium=medium, hard=hard)

    if tags:
        tagged = pick_questions(tags=tags, count=3)
        questions.extend(tagged)

    return questions


def generate_question_text(question_data, position="后端开发", difficulty="中等"):
    """用 LLM 把题目转成面试官口吻的出题语"""
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

    questions = start_interview(difficulty="easy")
    print(f"抽到 {len(questions)} 道题:\n")
    for q in questions:
        print(f"  [{q['difficulty']}] {q['id']}. {q['title']}")
        print(f"      标签: {', '.join(q['tags'])}\n")

    print("\n生成面试官话术...")
    text = generate_question_text(questions[0])
    print(text[:500])
