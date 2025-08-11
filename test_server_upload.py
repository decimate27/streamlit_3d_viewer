#!/usr/bin/env python3
"""
웹서버 업로드 테스트 스크립트
서버 연결 상태와 업로드 기능 확인
"""

import requests
import json
import tempfile
import os
from datetime import datetime

def test_server_connection():
    """서버 연결 테스트"""
    base_url = "https://airbible.kr/streamlit_data"
    upload_url = f"{base_url}/upload.php"
    
    print("🔍 서버 연결 테스트")
    print("=" * 50)
    print(f"📡 테스트 URL: {upload_url}")
    
    try:
        # 1. 기본 경로 확인
        print("\n1️⃣ 기본 경로 확인...")
        response = requests.get(base_url, timeout=10, verify=False)
        print(f"   기본 경로 응답: {response.status_code}")
        
        # 2. upload.php 직접 접근 (GET)
        print("\n2️⃣ upload.php GET 요청...")
        response = requests.get(upload_url, timeout=10, verify=False)
        print(f"   GET 응답: {response.status_code}")
        print(f"   GET 내용: {response.text[:200]}...")
        
        # 3. upload.php POST 요청 (빈 데이터)
        print("\n3️⃣ upload.php POST 요청...")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.post(
            upload_url, 
            data={}, 
            headers=headers,
            timeout=10, 
            verify=False
        )
        
        print(f"   POST 응답: {response.status_code}")
        print(f"   POST 내용: {response.text[:300]}...")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"   ✅ JSON 파싱 성공: {result}")
                return True, result
            except json.JSONDecodeError as e:
                print(f"   ❌ JSON 파싱 실패: {e}")
                print(f"   원본 응답 (전체): {response.text}")
                return False, None
        else:
            print(f"   ❌ HTTP 오류: {response.status_code}")
            return False, None
            
    except requests.exceptions.Timeout:
        print(f"❌ 타임아웃 오류: 서버 응답이 너무 느림")
        return False, None
    except requests.exceptions.ConnectionError as e:
        print(f"❌ 연결 오류: {str(e)}")
        return False, None
    except Exception as e:
        print(f"❌ 기타 오류: {str(e)}")
        return False, None

def test_file_upload():
    """실제 파일 업로드 테스트"""
    upload_url = "https://airbible.kr/streamlit_data/upload.php"
    
    print("\n🔍 파일 업로드 테스트")
    print("=" * 50)
    
    try:
        # 테스트 파일 생성
        test_content = "# Test OBJ file\nv 0.0 0.0 0.0\nv 1.0 0.0 0.0\nv 0.0 1.0 0.0\nf 1 2 3"
        model_id = f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
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
            upload_url, 
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
                    return True, result
                else:
                    print(f"❌ 업로드 실패: {result.get('message')}")
                    return False, result
            except json.JSONDecodeError:
                print(f"❌ JSON 파싱 실패: {response.text}")
                return False, None
        else:
            print(f"❌ HTTP 오류: {response.status_code}")
            return False, None
            
    except Exception as e:
        print(f"❌ 업로드 오류: {str(e)}")
        return False, None

def main():
    print("🚀 웹서버 업로드 기능 테스트")
    print("=" * 60)
    
    # 1. 서버 연결 테스트
    conn_success, conn_result = test_server_connection()
    
    if not conn_success:
        print("\n❌ 서버 연결 실패 - 업로드 테스트 중단")
        return
    
    # 2. 파일 업로드 테스트
    upload_success, upload_result = test_file_upload()
    
    print("\n" + "=" * 60)
    print("📋 테스트 결과 요약:")
    print(f"   서버 연결: {'✅ 성공' if conn_success else '❌ 실패'}")
    print(f"   파일 업로드: {'✅ 성공' if upload_success else '❌ 실패'}")
    
    if not upload_success:
        print("\n🔧 문제 해결 제안:")
        print("1. 서버 PHP 스크립트 확인")
        print("2. 파일 권한 확인 (웹서버 쓰기 권한)")
        print("3. 업로드 디렉토리 존재 여부 확인")
        print("4. 서버 로그 확인")

if __name__ == "__main__":
    main()
