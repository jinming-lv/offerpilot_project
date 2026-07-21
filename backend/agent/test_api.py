import requests
import json

BASE_URL = "http://localhost:8000/api"

def test_parse_jd():
    """测试JD解析接口"""
    url = f"{BASE_URL}/parse_jd"
    
    test_jd = """
    岗位名称：Python后端开发工程师
    经验要求：3-5年
    学历要求：本科及以上
    
    岗位职责：
    1. 负责公司核心业务系统的后端开发与维护
    
    任职要求：
    1. 3年以上Python开发经验
    2. 熟练掌握Django/Flask
    3. 熟悉MySQL、Redis
    """
    
    response = requests.post(url, json={"job_text": test_jd})
    print("=" * 50)
    print("测试 /api/parse_jd")
    print("=" * 50)
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"岗位: {data.get('data', {}).get('job_title', 'N/A')}")
        print(f"必须技能: {data.get('data', {}).get('required_skills', [])}")
    else:
        print(f"错误: {response.text}")

def test_match():
    """测试匹配接口"""
    url = f"{BASE_URL}/match"
    
    payload = {
        "resume_id": "resume_001",
        "job_text": """
        岗位名称：Python后端开发工程师
        任职要求：
        1. 3年以上Python开发经验
        2. 熟练掌握Django/Flask
        3. 熟悉MySQL、Redis
        """
    }
    
    print("\n" + "=" * 50)
    print("测试 /api/match")
    print("=" * 50)
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"完整返回: {json.dumps(data, ensure_ascii=False, indent=2)}")
        else:
            print(f"错误: {response.text}")
    except requests.exceptions.ConnectionError:
        print("❌ 服务未启动，请先运行 python app.py")
    except requests.exceptions.Timeout:
        print("❌ 请求超时")

if __name__ == "__main__":
    test_parse_jd()
    test_match()