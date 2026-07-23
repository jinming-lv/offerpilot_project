"""
八股知识库加载器 —— 从 knowledge 目录加载八股题目
"""

import json
import os
import random

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
KB_DIR = os.path.join(BASE_DIR, "dataset", "knowledge")
KB_FILE = os.path.join(KB_DIR, "99_concept_base.json")


def load_all():
    """加载全部八股题库"""
    if not os.path.exists(KB_FILE):
        return []
    with open(KB_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def get_question_count():
    """获取八股题库统计"""
    questions = load_all()
    if not questions:
        return {"total": 0}

    diff_count = {"Easy": 0, "Medium": 0, "Hard": 0}
    tag_count = {}

    for q in questions:
        d = q.get("difficulty", "Unknown")
        if d in diff_count:
            diff_count[d] += 1
        for t in q.get("tags", []):
            tag_count[t] = tag_count.get(t, 0) + 1

    return {
        "total": len(questions),
        "by_difficulty": diff_count,
        "by_tag": dict(sorted(tag_count.items(), key=lambda x: -x[1])[:10]),
    }


def pick_questions(difficulty=None, tags=None, count=3):
    """按条件选题"""
    questions = load_all()
    if not questions:
        return []

    filtered = questions
    if difficulty:
        filtered = [q for q in filtered if q["difficulty"] == difficulty]
    if tags:
        filtered = [q for q in filtered if any(t in q.get("tags", []) for t in tags)]

    random.shuffle(filtered)
    return filtered[:count]


def pick_by_difficulty_mix(easy=1, medium=1, hard=0):
    """按难度组合选题"""
    result = []
    for diff, count in [("Easy", easy), ("Medium", medium), ("Hard", hard)]:
        picked = pick_questions(difficulty=diff, count=count)
        result.extend(picked)

    if len(result) < easy + medium + hard:
        remaining = load_all()
        existing_ids = {q["id"] for q in result}
        more = [q for q in remaining if q["id"] not in existing_ids]
        random.shuffle(more)
        result.extend(more[:easy + medium + hard - len(result)])

    return result


if __name__ == "__main__":
    print("八股知识库统计:", get_question_count())
    print("\n抽3道题:")
    for q in pick_by_difficulty_mix(easy=1, medium=1, hard=1):
        print(f"  [{q['difficulty']}] {q['id']}. {q['title']}")
