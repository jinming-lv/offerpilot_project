"""
学习规划 Agent —— 根据面试结果生成学习路线
"""

import json
import sys
import os



from agents.utils.knowledge_loader import load_all, get_question_count
from agents.utils.llm_api import chat
from agents.interview.prompts import LEARNING_PROMPT


def analyze_weaknesses(interview_records):
    """分析面试记录，找出薄弱知识点"""
    weak_tags = {}

    for record in interview_records:
        score = record.get("score", {})
        total = score.get("total_score", 0)
        question = record.get("question_data", {})
        tags = question.get("tags", [])

        if total < 70:
            for tag in tags:
                weak_tags[tag] = weak_tags.get(tag, 0) + 1

    sorted_weak = sorted(weak_tags.items(), key=lambda x: -x[1])

    return {
        "weak_tags": [t for t, _ in sorted_weak],
        "total_questions": len(interview_records),
        "passed": sum(1 for r in interview_records if r.get("score", {}).get("total_score", 0) >= 70),
        "failed": sum(1 for r in interview_records if r.get("score", {}).get("total_score", 0) < 70),
    }


def generate_learning_plan(position, level, interview_records, duration="14天"):
    """生成学习计划"""
    analysis = analyze_weaknesses(interview_records)
    weaknesses = ", ".join(analysis["weak_tags"]) if analysis["weak_tags"] else "基础知识"

    all_questions = load_all()
    available_tags = set()
    for q in all_questions:
        for t in q.get("tags", []):
            available_tags.add(t)
    tags_str = ", ".join(sorted(available_tags))

    prompt = LEARNING_PROMPT.format(
        position=position,
        level=level,
        weaknesses=weaknesses,
        available_tags=tags_str,
        duration=duration,
    )

    result = chat([
        {"role": "system", "content": "你是一个学习规划导师。始终返回JSON。"},
        {"role": "user", "content": prompt},
    ], temperature=0.7)

    try:
        clean = result.replace("```json", "").replace("```", "").strip()
        plan = json.loads(clean)
        return plan
    except json.JSONDecodeError:
        return {
            "duration": duration,
            "roadmap": [
                {"day": 1, "topic": "无法自动生成", "content": result[:200], "practice": "", "estimated_hours": 2}
            ]
        }


if __name__ == "__main__":
    print("学习规划 Agent 测试")
    print(f"知识库统计: {get_question_count()}")
