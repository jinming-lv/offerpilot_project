"""
LLM 调用封装 —— 支持 DeepSeek / 智谱 / 任意 OpenAI 兼容 API
从项目根目录 .env 文件读取配置，各人可自选厂商
"""

import os
import sys
from openai import OpenAI
from dotenv import load_dotenv

# 项目根目录
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# 加载 .env
env_path = os.path.join(BASE_DIR, ".env")
load_dotenv(env_path)

# ===== 从 .env 读取配置（各人可自定义） =====
API_KEY = os.getenv("LLM_API_KEY", "")
API_URL = os.getenv("LLM_API_URL", "https://api.deepseek.com")
MODEL = os.getenv("LLM_MODEL", "deepseek-chat")

# 打印当前使用的配置（隐藏 key 中间部分）
def mask_key(k):
    if len(k) < 8:
        return "***"
    return k[:6] + "..." + k[-4:]

print(f"  LLM 配置: {API_URL} | {MODEL} | Key: [configured]")

# ===== Key 校验 =====
if not API_KEY:
    print()
    print("=" * 60)
    print("  [OfferPilot] API Key 未配置")
    print("=" * 60)
    print()
    print("  请按以下步骤操作：")
    print()
    print(f"  1. 打开项目根目录的 .env 文件")
    print(f"  2. 填写 LLM_API_KEY，并根据需要修改 LLM_API_URL 和 LLM_MODEL")
    print()
    print("  常用配置示例：")
    print()
    print("  ┌─ DeepSeek ──────────────────────────────┐")
    print("  │  LLM_API_KEY=sk-xxx                      │")
    print("  │  LLM_API_URL=https://api.deepseek.com    │")
    print("  │  LLM_MODEL=deepseek-chat                 │")
    print("  └──────────────────────────────────────────┘")
    print()
    print("  ┌─ 智谱 GLM ──────────────────────────────┐")
    print("  │  LLM_API_KEY=xxx                        │")
    print("  │  LLM_API_URL=https://open.bigmodel.cn   │")
    print("  │  LLM_MODEL=glm-4-plus                   │")
    print("  └──────────────────────────────────────────┘")
    print()
    print("  ┌─ 通义千问 ──────────────────────────────┐")
    print("  │  LLM_API_KEY=sk-xxx                     │")
    print("  │  LLM_API_URL=https://dashscope.aliyun.. │")
    print("  │  LLM_MODEL=qwen-plus                    │")
    print("  └──────────────────────────────────────────┘")
    print()
    print(f"  .env 文件路径：{env_path}")
    print("  提示：.env 已加入 .gitignore，不会提交到仓库")
    print("=" * 60)
    sys.exit(1)

# ===== 创建客户端 =====
client = OpenAI(api_key=API_KEY, base_url=API_URL)


def chat(messages, temperature=0.7, max_tokens=2048):
    """
    调用 LLM 对话

    参数:
        messages: [{"role": "system", "content": "..."}, {"role": "user", "content": "..."}]
        temperature: 0-1, 越高越随机
        max_tokens: 最大输出长度

    返回: str 模型回答
    """
    try:
        resp = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return resp.choices[0].message.content
    except Exception as e:
        return f"【API 调用失败】{str(e)}"


if __name__ == "__main__":
    print()
    print("测试 LLM API...")
    result = chat([
        {"role": "system", "content": "你是一个面试官，请简短回答。"},
        {"role": "user", "content": "请出1道Python基础面试题"},
    ])
    print(result)
