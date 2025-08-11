import requests
import json
import urllib3

# SSL 경고 비활성화 (테스트용)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def test_upload():
    """웹서버 업로드 테스트"""
    url = "https://airbible.kr/streamlit_data/upload.php"
    
    # 테스트 파일 생성
    test_content = "# Test OBJ file\nv 0.0 0.0 0.0\nv 1.0 0.0 0.0\nv 0.0 1.0 0.0\nf 1 2 3"
    
    files = {
        'file': ('test.obj', test_content.encode('utf-8')),
        'model_id': (None, 'test-model-123'),
        'action': (None, 'upload')
    }
    
    try:
        response = requests.post(url, files=files, timeout=30, verify=False)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Result: {result}")
            return result.get('status') == 'success'
        else:
            print(f"HTTP Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

def test_download():
    """웹서버 다운로드 테스트"""
    url = "https://airbible.kr/streamlit_data/files/test-model-123/test.obj"
    
    try:
        response = requests.get(url, timeout=30, verify=False)
        print(f"Download Status: {response.status_code}")
        if response.status_code == 200:
            print(f"Content: {response.text[:100]}...")
            return True
        return False
    except Exception as e:
        print(f"Download Error: {str(e)}")
        return False

if __name__ == "__main__":
    print("=== 웹서버 업로드 테스트 ===")
    if test_upload():
        print("✅ 업로드 성공!")
        
        print("\n=== 웹서버 다운로드 테스트 ===")
        if test_download():
            print("✅ 다운로드 성공!")
        else:
            print("❌ 다운로드 실패")
    else:
        print("❌ 업로드 실패")
