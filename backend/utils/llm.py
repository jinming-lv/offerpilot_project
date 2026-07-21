import os
import json
from typing import Optional, Dict, Any
from openai import OpenAI
import logging
from utils.env import load_project_env

# 加载项目根目录 .env 文件
env_path = load_project_env()

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class LLMClient:
    """
    统一的LLM客户端
    支持多种模型：Qwen, DeepSeek, OpenAI, OpenRouter
    """
    
    def __init__(self):
        self.clients = {}
        self.primary_model_name = os.getenv("LLM_MODEL", "deepseek-chat")
        self._init_clients()
    
    def _init_clients(self):
        """初始化各个模型的客户端"""
        # 根目录 .env 的主配置：优先作为统一入口
        primary_api_key = os.getenv("LLM_API_KEY", "")
        primary_api_url = os.getenv("LLM_API_URL", "https://api.deepseek.com")
        if primary_api_key:
            primary_client = OpenAI(
                api_key=primary_api_key,
                base_url=primary_api_url,
            )
            self.clients["primary"] = primary_client
            self.clients["qwen"] = primary_client
            logger.info("主LLM客户端初始化成功")

        # Qwen (通义千问)
        qwen_api_key = os.getenv("DASHSCOPE_API_KEY", "")
        if qwen_api_key:
            self.clients["qwen"] = OpenAI(
                api_key=qwen_api_key,
                base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
            )
            logger.info("Qwen客户端初始化成功")
        
        # DeepSeek
        deepseek_api_key = os.getenv("DEEPSEEK_API_KEY", "")
        if deepseek_api_key:
            self.clients["deepseek"] = OpenAI(
                api_key=deepseek_api_key,
                base_url="https://api.deepseek.com/v1"
            )
            logger.info("DeepSeek客户端初始化成功")
        
        # OpenAI
        openai_api_key = os.getenv("OPENAI_API_KEY", "")
        if openai_api_key:
            self.clients["openai"] = OpenAI(
                api_key=openai_api_key,
                base_url="https://api.openai.com/v1"
            )
            logger.info("OpenAI客户端初始化成功")
        
        # OpenRouter（兼容 OpenAI API）
        openrouter_api_key = os.getenv("OPENROUTER_API_KEY", "")
        if openrouter_api_key:
            self.clients["openrouter"] = OpenAI(
                api_key=openrouter_api_key,
                base_url="https://openrouter.ai/api/v1"
            )
            logger.info("OpenRouter客户端初始化成功")
        
        if not self.clients:
            logger.warning("未配置任何LLM API密钥，将使用模拟模式")
    
    def chat(
        self,
        prompt: str,
        model: str = "openrouter",  # 默认使用 OpenRouter
        temperature: float = 0.1,
        max_tokens: int = 2000,
        system_prompt: Optional[str] = None
    ) -> str:
        """
        统一聊天接口
        """
        if model not in self.clients:
            available = list(self.clients.keys())
            if not available:
                logger.warning("没有可用的LLM模型，返回模拟响应")
                return self._mock_response(prompt)
            
            logger.warning(f"模型 {model} 不可用，使用 {available[0]}")
            model = available[0]
        
        client = self.clients[model]
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        model_name = self._get_model_name(model)
        
        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"LLM调用失败: {e}")
            raise Exception(f"LLM调用失败: {str(e)}")
    
    def _get_model_name(self, model: str) -> str:
        """获取实际的模型名称"""
        if model in {"primary", "qwen"} and self.clients.get("primary"):
            return self.primary_model_name

        model_map = {
            "qwen": "qwen-plus",
            "deepseek": "deepseek-chat",
            "openai": "gpt-3.5-turbo",
            "openrouter": "deepseek/deepseek-chat"  # 可根据需要修改
        }
        return model_map.get(model, model)
    
    def _mock_response(self, prompt: str) -> str:
        """模拟响应"""
        return json.dumps({
            "basic_info": {
                "name": "张三",
                "gender": "男",
                "education": "本科",
                "major": "计算机科学与技术",
                "email": "zhangsan@example.com",
                "phone": "13800000000"
            },
            "skills": ["Python", "Java", "MySQL", "Redis"],
            "projects": [
                {
                    "project_name": "校园交易平台",
                    "role": "后端开发工程师",
                    "description": "负责后端API开发、数据库设计、系统部署",
                    "tech_stack": ["Flask", "MySQL", "Redis", "Docker"]
                }
            ],
            "experience": [
                {
                    "company": "ABC科技有限公司",
                    "position": "实习生",
                    "duration": "2025.07-2025.09"
                }
            ]
        }, ensure_ascii=False)

# 全局实例
_llm_client = None

def get_llm_client() -> LLMClient:
    global _llm_client
    if _llm_client is None:
        _llm_client = LLMClient()
    return _llm_client

def chat(
    prompt: str,
    model: str = "openrouter",
    temperature: float = 0.1,
    max_tokens: int = 2000,
    system_prompt: Optional[str] = None
) -> str:
    client = get_llm_client()
    return client.chat(prompt, model, temperature, max_tokens, system_prompt)