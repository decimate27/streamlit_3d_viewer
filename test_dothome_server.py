#!/usr/bin/env python3
"""
올바른 서버 경로 테스트
"""

import requests
import json
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def test_correct_server():
    """올바른 서버 경로 테스트"""
    # FTP 경로를 기반으로 한 웹 경로들
    urls_to_test = [
        "https://decimate27.dothome.co.kr/streamlit_data/upload.php",
        "http://decimate27.dothome.co.kr/streamlit_data/upload.php",
        "https://www.decimate27.dothome.co.kr/streamlit_data/upload.php",
        "http://www.decimate27.dothome.co.kr/streamlit_data/upload.php",
    ]
    
    print("🔍 올바른 서버 경로 테스트")
    print("=" * 60)
    
    for url in urls_to_test:
        try:
            print(f"\n📡 테스트: {url}")
            
            # GET 요청 테스트
            response = requests.get(url, timeout=10, verify=False)
            print(f"   GET 응답: {response.status_code}")
            
            if response.status_code == 200:
                print(f"   ✅ GET 성공!")
                print(f"   내용: {response.text[:100]}...")
                
                # POST 요청 테스트
                print(f"   📤 POST 테스트 중...")
                post_response = requests.post(url, data={}, timeout=10, verify=False)
                print(f"   POST 응답: {post_response.status_code}")
                print(f"   POST 내용: {post_response.text[:200]}...")
                
                if post_response.status_code == 200:
                    try:
                        result = post_response.json()
                        print(f"   ✅ JSON 파싱 성공: {result}")
                        return url  # 성공한 URL 반환
                    except json.JSONDecodeError:
                        print(f"   ⚠️ JSON 파싱 실패하지만 서버 응답은 정상")
                        return url
                        
            elif response.status_code == 405:  # Method Not Allowed
                print(f"   ⚠️ GET은 허용 안됨, POST 테스트...")
                post_response = requests.post(url, data={}, timeout=10, verify=False)
                print(f"   POST 응답: {post_response.status_code}")
                if post_response.status_code == 200:
                    return url
                    
        except Exception as e:
            print(f"   ❌ 오류: {str(e)}")
    
    return None

def test_file_upload(server_url):
    """실제 파일 업로드 테스트"""
    print(f"\n🚀 파일 업로드 테스트: {server_url}")
    print("=" * 60)
    
    try:
        # 테스트 파일 생성
        test_content = "# Test OBJ file\nv 0.0 0.0 0.0\nv 1.0 0.0 0.0\nv 0.0 1.0 0.0\nf 1 2 3"
        from datetime import datetime
        model_id = f"test{datetime.now().strftime('%Y%m%d%H%M%S')}"  # 언더스코어 제거
        
        files = {
            'file': ('test.obj', test_content.encode('utf-8')),
            'model_id': (None, model_id),
            'action': (None, 'upload')
        }
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        print(f"📤 업로드 시작: {model_id}")
        
        response = requests.post(
            server_url, 
            files=files, 
            headers=headers,
            timeout=30, 
            verify=False
        )
        
        print(f"📡 응답 상태: {response.status_code}")
        print(f"📄 응답 내용: {response.text}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                if result.get('status') == 'success':
                    print(f"✅ 업로드 성공: {result.get('file_path')}")
                    return True
                else:
                    print(f"❌ 업로드 실패: {result.get('message')}")
                    return False
            except json.JSONDecodeError:
                print(f"❌ JSON 파싱 실패: {response.text}")
                return False
        else:
            print(f"❌ HTTP 오류: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 업로드 오류: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 서버 연결 확인")
    print("=" * 80)
    
    # 1. 서버 경로 찾기
    working_url = test_correct_server()
    
    if working_url:
        print(f"\n✅ 작동하는 서버 발견: {working_url}")
        
        # 2. 파일 업로드 테스트
        upload_success = test_file_upload(working_url)
        
        if upload_success:
            print(f"\n🎉 모든 테스트 성공!")
            print(f"✅ 사용할 서버 URL: {working_url}")
        else:
            print(f"\n⚠️ 서버는 있지만 업로드 실패")
    else:
        print(f"\n❌ 작동하는 서버를 찾을 수 없음")
