from docx import Document
from typing import Optional
import os

def extract_text_from_docx(file_path: str) -> str:
    """
    从DOCX文件中提取文本
    
    Args:
        file_path: DOCX文件路径
    
    Returns:
        提取的文本内容
    
    Raises:
        ValueError: 如果文件不存在或无法读取
        Exception: 如果DOCX解析失败
    """
    if not os.path.exists(file_path):
        raise ValueError(f"文件不存在: {file_path}")
    
    try:
        doc = Document(file_path)
        text_parts = []
        
        # 提取段落文本
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                text_parts.append(paragraph.text)
        
        # 提取表格中的文本
        for table in doc.tables:
            for row in table.rows:
                row_text = []
                for cell in row.cells:
                    if cell.text.strip():
                        row_text.append(cell.text.strip())
                if row_text:
                    text_parts.append(" | ".join(row_text))
        
        full_text = "\n".join(text_parts)
        
        if not full_text.strip():
            raise ValueError("DOCX中未提取到任何文本内容")
        
        return full_text
    
    except Exception as e:
        raise Exception(f"DOCX解析失败: {str(e)}")

def extract_text_from_docx_with_structure(file_path: str) -> dict:
    """
    从DOCX文件中提取文本和结构信息
    
    Args:
        file_path: DOCX文件路径
    
    Returns:
        包含文本内容和结构信息的字典
    """
    if not os.path.exists(file_path):
        raise ValueError(f"文件不存在: {file_path}")
    
    try:
        doc = Document(file_path)
        
        paragraphs = []
        for para in doc.paragraphs:
            if para.text.strip():
                paragraphs.append({
                    "text": para.text,
                    "style": para.style.name if para.style else None
                })
        
        tables = []
        for table in doc.tables:
            table_data = []
            for row in table.rows:
                row_data = [cell.text.strip() for cell in row.cells]
                if any(row_data):
                    table_data.append(row_data)
            if table_data:
                tables.append(table_data)
        
        return {
            "paragraphs": paragraphs,
            "tables": tables,
            "full_text": "\n".join([p["text"] for p in paragraphs])
        }
    
    except Exception as e:
        raise Exception(f"DOCX解析失败: {str(e)}")