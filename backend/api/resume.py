from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import os
import tempfile
from typing import Optional

from agent.resume_agent import ResumeAgent

router = APIRouter()
resume_agent = ResumeAgent()

@router.post("/resume/upload")
async def upload_resume(file: UploadFile = File(...)):
    """
    上传简历文件（PDF/DOCX）并提取结构化信息
    """
    # 验证文件类型
    allowed_extensions = {'.pdf', '.docx'}
    file_extension = os.path.splitext(file.filename)[1].lower()
    
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件格式。仅支持: {', '.join(allowed_extensions)}"
        )
    
    # 保存临时文件
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
        
        # 调用 ResumeAgent 处理
        result = resume_agent.parse_resume(tmp_file_path, file.filename)
        
        # 清理临时文件
        os.unlink(tmp_file_path)
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "resume_id": result.get("resume_id"),
                "data": result.get("data")
            }
        )
    
    except Exception as e:
        # 清理临时文件
        if 'tmp_file_path' in locals() and os.path.exists(tmp_file_path):
            os.unlink(tmp_file_path)
        
        raise HTTPException(
            status_code=500,
            detail=f"简历处理失败: {str(e)}"
        )