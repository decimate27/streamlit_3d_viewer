#!/usr/bin/env python3
"""
다양한 경로로 서버 테스트
"""

import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def test_multiple_paths():
    """여러 경로 테스트"""
    paths_to_test = [
        "https://airbible.kr/streamlit_data/upload.php",
        "https://airbible.kr/upload.php", 
        "https://airbible.kr/streamlit/upload.php",
        "https://airbible.kr/data/upload.php",
        "https://airbible.kr/3d/upload.php",
        "https://www.airbible.kr/streamlit_data/upload.php",
    ]
    
    print("🔍 다양한 경로 테스트")
    print("=" * 60)
    
    for url in paths_to_test:
        try:
            print(f"\n📡 테스트: {url}")
            response = requests.get(url, timeout=5, verify=False)
            print(f"   응답: {response.status_code}")
            
            if response.status_code == 200:
                print(f"   ✅ 성공! 내용: {response.text[:100]}...")
                return url
            elif response.status_code != 404:
                print(f"   ⚠️ 특이 응답: {response.text[:100]}...")
                
        except Exception as e:
            print(f"   ❌ 오류: {str(e)}")
    
    return None

if __name__ == "__main__":
    result = test_multiple_paths()
    if result:
        print(f"\n✅ 작동하는 경로 발견: {result}")
    else:
        print(f"\n❌ 모든 경로에서 실패")
