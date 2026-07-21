#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
简历解析测试脚本
用于测试Resume Agent的功能
"""

import os
import sys
import json
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent.resume_agent import ResumeAgent
from utils.logger import get_logger

logger = get_logger(__name__)

def test_with_pdf(pdf_path: str):
    """使用PDF文件测试"""
    if not os.path.exists(pdf_path):
        logger.error(f"文件不存在: {pdf_path}")
        return False
    
    logger.info(f"开始测试PDF解析: {pdf_path}")
    
    try:
        agent = ResumeAgent(save_to_file=True)
        result = agent.parse_resume(pdf_path)
        
        logger.info(f"解析成功! Resume ID: {result['resume_id']}")
        
        # 打印关键信息
        data = result['data']
        basic = data.get('basic_info', {})
        skills = data.get('skills', [])
        
        print("\n" + "="*50)
        print("解析结果摘要:")
        print("="*50)
        print(f"姓名: {basic.get('name', 'N/A')}")
        print(f"学历: {basic.get('education', 'N/A')}")
        print(f"专业: {basic.get('major', 'N/A')}")
        print(f"技能: {', '.join(skills[:5])}")
        print(f"项目数: {len(data.get('projects', []))}")
        print(f"经历数: {len(data.get('experience', []))}")
        print("="*50)
        
        # 保存完整结果
        output_dir = Path("dataset/resumes")
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / f"{result['resume_id']}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"完整结果已保存到: {output_file}")
        return True
        
    except Exception as e:
        logger.error(f"解析失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("\n" + "="*50)
    print("Resume Agent 测试")
    print("="*50)
    
    # 检查是否有测试PDF
    test_pdf = "test_resume.pdf"
    if os.path.exists(test_pdf):
        success = test_with_pdf(test_pdf)
        print(f"\n测试结果: {'✅ 成功' if success else '❌ 失败'}")
    else:
        print(f"\n⚠️ 未找到测试PDF文件: {test_pdf}")
        print("请将简历PDF文件命名为 test_resume.pdf 放在项目根目录")
        print("或者修改 test_pdf 变量指向你的PDF文件路径")
        
        # 列出可用的PDF文件
        pdf_files = list(Path(".").glob("*.pdf")) + list(Path("backend").glob("*.pdf"))
        if pdf_files:
            print(f"\n找到以下PDF文件:")
            for f in pdf_files:
                print(f"  - {f}")
            print("\n你可以用以下方式测试:")
            print(f"  python test_resume.py [PDF文件路径]")

if __name__ == "__main__":
    # 支持命令行参数
    if len(sys.argv) > 1:
        test_with_pdf(sys.argv[1])
    else:
        main()