import fitz  # PyMuPDF
from typing import Optional
import os

def extract_text_from_pdf(file_path: str) -> str:
    """
    从PDF文件中提取文本
    
    Args:
        file_path: PDF文件路径
    
    Returns:
        提取的文本内容
    
    Raises:
        ValueError: 如果文件不存在或无法读取
        Exception: 如果PDF解析失败
    """
    if not os.path.exists(file_path):
        raise ValueError(f"文件不存在: {file_path}")
    
    try:
        doc = fitz.open(file_path)
        text_parts = []
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()
            if text.strip():
                text_parts.append(text)
        
        doc.close()
        
        full_text = "\n".join(text_parts)
        
        if not full_text.strip():
            raise ValueError("PDF中未提取到任何文本内容，可能是扫描件或图片型PDF")
        
        return full_text
    
    except Exception as e:
        raise Exception(f"PDF解析失败: {str(e)}")

def extract_text_from_pdf_with_metadata(file_path: str) -> dict:
    """
    从PDF文件中提取文本和元数据
    
    Args:
        file_path: PDF文件路径
    
    Returns:
        包含文本内容和元数据的字典
    """
    if not os.path.exists(file_path):
        raise ValueError(f"文件不存在: {file_path}")
    
    try:
        doc = fitz.open(file_path)
        
        # 提取元数据
        metadata = doc.metadata
        
        # 提取文本
        text_parts = []
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()
            if text.strip():
                text_parts.append({
                    "page": page_num + 1,
                    "text": text
                })
        
        doc.close()
        
        return {
            "metadata": metadata,
            "pages": text_parts,
            "full_text": "\n".join([p["text"] for p in text_parts])
        }
    
    except Exception as e:
        raise Exception(f"PDF解析失败: {str(e)}")