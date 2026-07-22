import docx2txt
import os

def extract_text_from_docx(file_path: str) -> str:
    """
    从DOCX文件中提取文本（使用 docx2txt）
    
    Args:
        file_path: DOCX文件路径
    
    Returns:
        提取的文本内容
    """
    if not os.path.exists(file_path):
        raise ValueError(f"文件不存在: {file_path}")
    
    # 检查文件大小
    file_size = os.path.getsize(file_path)
    if file_size == 0:
        raise ValueError(f"文件为空: {file_path}")
    
    try:
        # docx2txt 能更好地处理各种 DOCX 格式
        text = docx2txt.process(file_path)
        
        if not text or not text.strip():
            raise ValueError("DOCX中未提取到任何文本内容")
        
        return text.strip()
    
    except ImportError:
        # 如果 docx2txt 未安装，回退到 python-docx
        from docx import Document
        doc = Document(file_path)
        text_parts = []
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                text_parts.append(paragraph.text)
        
        full_text = "\n".join(text_parts)
        if not full_text.strip():
            raise ValueError("DOCX中未提取到任何文本内容")
        return full_text
    
    except Exception as e:
        raise Exception(f"DOCX解析失败: {str(e)}")