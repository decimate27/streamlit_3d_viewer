#!/usr/bin/env python3
"""
서버 삭제 기능 테스트
"""

import requests
import json
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def test_server_list():
    """서버 모델 목록 조회 테스트"""
    delete_url = "http://decimate27.dothome.co.kr/streamlit_data/delete.php"
    
    print("📋 서버 모델 목록 조회 테스트")
    print("=" * 50)
    
    try:
        data = {'action': 'list'}
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.post(delete_url, data=data, headers=headers, timeout=10, verify=False)
        
        print(f"📡 응답 상태: {response.status_code}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                if result.get('status') == 'success':
                    models = result.get('models', [])
                    print(f"✅ 서버에 {len(models)}개 모델 발견")
                    
                    for model in models:
                        print(f"   🎮 모델 ID: {model['model_id']}")
                        print(f"      파일 수: {len(model['files'])}")
                        for file_info in model['files']:
                            print(f"      - {file_info['name']} ({file_info['size']} bytes)")
                        print()
                    
                    return models
                else:
                    print(f"❌ 목록 조회 실패: {result.get('message')}")
                    return []
            except json.JSONDecodeError:
                print(f"❌ JSON 파싱 실패: {response.text}")
                return []
        else:
            print(f"❌ HTTP 오류: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"❌ 오류: {str(e)}")
        return []

def test_server_delete(model_id):
    """서버 모델 삭제 테스트"""
    delete_url = "http://decimate27.dothome.co.kr/streamlit_data/delete.php"
    
    print(f"🗑️ 모델 삭제 테스트: {model_id}")
    print("=" * 50)
    
    try:
        data = {
            'model_id': model_id,
            'action': 'delete'
        }
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.post(delete_url, data=data, headers=headers, timeout=10, verify=False)
        
        print(f"📡 응답 상태: {response.status_code}")
        print(f"📄 응답 내용: {response.text}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                if result.get('status') == 'success':
                    print(f"✅ 삭제 성공: {result.get('message')}")
                    return True
                else:
                    print(f"❌ 삭제 실패: {result.get('message')}")
                    return False
            except json.JSONDecodeError:
                print(f"❌ JSON 파싱 실패: {response.text}")
                return False
        else:
            print(f"❌ HTTP 오류: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 오류: {str(e)}")
        return False

def main():
    print("🚀 서버 삭제 기능 테스트")
    print("=" * 80)
    
    # 1. 서버 모델 목록 조회
    models = test_server_list()
    
    if not models:
        print("\n❌ 서버에 모델이 없거나 목록 조회 실패")
        return
    
    # 2. 첫 번째 모델 삭제 테스트 (주의: 실제로 삭제됨!)
    first_model = models[0]
    model_id = first_model['model_id']
    
    print(f"\n⚠️ 주의: '{model_id}' 모델을 삭제하려고 합니다!")
    confirm = input("정말 삭제하시겠습니까? (yes/no): ")
    
    if confirm.lower() == 'yes':
        success = test_server_delete(model_id)
        
        if success:
            print(f"\n🎉 '{model_id}' 모델 삭제 완료!")
            
            # 삭제 후 목록 다시 확인
            print(f"\n📋 삭제 후 서버 상태:")
            test_server_list()
        else:
            print(f"\n❌ '{model_id}' 모델 삭제 실패")
    else:
        print("\n🚫 삭제가 취소되었습니다.")

if __name__ == "__main__":
    main()
