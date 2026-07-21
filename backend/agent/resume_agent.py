import json
import os
import uuid
from typing import Dict, Any, Optional
from datetime import datetime

from utils.pdf_parser import extract_text_from_pdf
from utils.docx_parser import extract_text_from_docx
from utils.llm import chat
from utils.logger import get_logger

logger = get_logger(__name__)

class ResumeAgent:
    """
    简历处理代理类
    负责解析简历文件，提取结构化信息
    """
    
    def __init__(self, save_to_file: bool = True):
        """
        初始化简历代理
        
        Args:
            save_to_file: 是否将解析结果保存到文件
        """
        self.save_to_file = save_to_file
        self.dataset_dir = "dataset/parsed_resume"
        
        # 确保保存目录存在
        if self.save_to_file:
            os.makedirs(self.dataset_dir, exist_ok=True)
    
    def parse_resume(self, file_path: str, original_filename: str = None) -> Dict[str, Any]:
        """
        解析简历文件
        
        Args:
            file_path: 简历文件路径
            original_filename: 原始文件名（用于生成ID）
        
        Returns:
            包含resume_id和提取数据的字典
        """
        # 1. 提取文件扩展名
        file_extension = os.path.splitext(file_path)[1].lower()
        
        # 2. 提取文本内容
        logger.info(f"开始解析简历: {file_path}")
        
        if file_extension == '.pdf':
            text = extract_text_from_pdf(file_path)
        elif file_extension == '.docx':
            text = extract_text_from_docx(file_path)
        else:
            raise ValueError(f"不支持的文件格式: {file_extension}")
        
        if not text or len(text.strip()) < 10:
            raise ValueError("提取的文本内容过少，可能文件损坏或为图片型PDF")
        
        logger.info(f"成功提取文本，长度: {len(text)} 字符")
        
        # 3. 生成简历ID
        resume_id = self._generate_resume_id(original_filename)
        
        # 4. 调用LLM提取结构化信息
        structured_data = self._extract_with_llm(text)
        
        # 5. 添加resume_id
        structured_data["resume_id"] = resume_id
        
        # 6. 保存到文件（可选）
        if self.save_to_file:
            self._save_resume_data(resume_id, structured_data)
        
        logger.info(f"简历解析完成: {resume_id}")
        
        return {
            "resume_id": resume_id,
            "data": structured_data
        }
    
    def _extract_with_llm(self, text: str) -> Dict[str, Any]:
        """
        使用LLM提取结构化信息
        
        Args:
            text: 简历文本内容
        
        Returns:
            结构化JSON数据
        """
        # 加载prompt模板
        prompt = self._load_prompt()
        
        # 替换文本占位符
        prompt = prompt.replace("{{RESUME_TEXT}}", text)
        
        # 调用LLM
        logger.info("正在调用LLM提取信息...")
        response = chat(prompt, model="qwen")  # 使用Qwen模型
        
        # 解析JSON
        try:
            # 尝试提取JSON部分（处理markdown代码块）
            data = self._extract_json_from_response(response)
            return data
        except json.JSONDecodeError as e:
            logger.error(f"JSON解析失败: {e}")
            logger.error(f"LLM响应: {response[:500]}...")
            raise ValueError("LLM返回的数据格式不正确")
    
    def _load_prompt(self) -> str:
        """
        加载prompt模板
        
        Returns:
            prompt字符串
        """
        prompt_file = "prompts/resume_extract.txt"
        
        if not os.path.exists(prompt_file):
            # 如果文件不存在，使用默认prompt
            logger.warning(f"Prompt文件不存在: {prompt_file}，使用默认prompt")
            return self._get_default_prompt()
        
        with open(prompt_file, 'r', encoding='utf-8') as f:
            return f.read()
    
    def _get_default_prompt(self) -> str:
        """
        获取默认prompt（当文件不存在时使用）
        """
        return """
你是一位专业的HR，擅长从简历中提取关键信息。

请根据以下简历内容，提取结构化信息，并严格按照JSON格式输出。

简历内容：
{{RESUME_TEXT}}

请提取以下信息：
1. basic_info: 包含 name(姓名), gender(性别), education(学历), major(专业), email(邮箱), phone(电话)
2. skills: 技能列表，数组格式
3. projects: 项目列表，每个项目包含 project_name(项目名称), role(角色), description(描述), tech_stack(技术栈)
4. experience: 工作经历列表，每个经历包含 company(公司), position(职位), duration(时间)

输出格式示例：
{
  "basic_info": {
    "name": "张三",
    "gender": "男",
    "education": "本科",
    "major": "计算机科学与技术",
    "email": "zhangsan@example.com",
    "phone": "138xxxx"
  },
  "skills": ["Python", "Java", "MySQL"],
  "projects": [
    {
      "project_name": "校园交易平台",
      "role": "后端开发",
      "description": "负责后端API开发和数据库设计",
      "tech_stack": ["Flask", "MySQL", "Redis"]
    }
  ],
  "experience": [
    {
      "company": "ABC科技",
      "position": "实习生",
      "duration": "2025.07-2025.09"
    }
  ]
}

请只输出JSON，不要包含其他内容。
"""
    
    def _extract_json_from_response(self, response: str) -> Dict[str, Any]:
        """
        从LLM响应中提取JSON
        
        Args:
            response: LLM响应文本
        
        Returns:
            解析后的JSON字典
        """
        # 尝试移除markdown代码块
        response = response.strip()
        
        # 如果包含```json或```，提取其中的内容
        if "```json" in response:
            start = response.find("```json") + 7
            end = response.find("```", start)
            if end != -1:
                response = response[start:end].strip()
        elif "```" in response:
            start = response.find("```") + 3
            end = response.find("```", start)
            if end != -1:
                response = response[start:end].strip()
        
        # 解析JSON
        return json.loads(response)
    
    def _generate_resume_id(self, filename: Optional[str] = None) -> str:
        """
        生成简历ID
        
        Args:
            filename: 原始文件名
        
        Returns:
            简历ID
        """
        if filename:
            # 从文件名生成ID
            base = os.path.splitext(os.path.basename(filename))[0]
            # 移除特殊字符
            base = ''.join(c for c in base if c.isalnum() or c in ('_', '-'))
            if base:
                return f"resume_{base}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # 使用UUID生成
        return f"resume_{uuid.uuid4().hex[:8]}"
    
    def _save_resume_data(self, resume_id: str, data: Dict[str, Any]) -> None:
        """
        保存简历数据到文件
        
        Args:
            resume_id: 简历ID
            data: 简历数据
        """
        file_path = os.path.join(self.dataset_dir, f"{resume_id}.json")
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"简历数据已保存: {file_path}")
    
    def load_resume_data(self, resume_id: str) -> Optional[Dict[str, Any]]:
        """
        从文件加载简历数据
        
        Args:
            resume_id: 简历ID
        
        Returns:
            简历数据，如果不存在则返回None
        """
        file_path = os.path.join(self.dataset_dir, f"{resume_id}.json")
        
        if not os.path.exists(file_path):
            return None
        
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)