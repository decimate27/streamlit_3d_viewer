import requests
import json
import base64
import streamlit as st
from datetime import datetime
import uuid

class WebServerDatabase:
    """웹서버의 SQLite 데이터베이스와 연동하는 클래스"""
    
    def __init__(self):
        self.base_url = "http://decimate27.dothome.co.kr/streamlit_data"
        self.init_db_url = f"{self.base_url}/init_database.php"
        self.save_model_url = f"{self.base_url}/save_model.php"
        self.load_model_url = f"{self.base_url}/load_model.php"
        self.feedback_api_url = f"{self.base_url}/feedback_api.php"
        self.model_api_url = f"{self.base_url}/model_api.php"
        
    def initialize_database(self):
        """웹서버에 데이터베이스 초기화"""
        try:
            response = requests.get(self.init_db_url, timeout=30, verify=False)
            if response.status_code == 200:
                result = response.json()
                if result.get('status') == 'success':
                    st.success("✅ 웹서버 데이터베이스 초기화 완료!")
                    return True
                else:
                    st.error(f"데이터베이스 초기화 실패: {result.get('message')}")
                    return False
            else:
                st.error(f"서버 오류: {response.status_code}")
                return False
        except Exception as e:
            st.error(f"데이터베이스 초기화 중 오류: {str(e)}")
            return False
    
    def save_model(self, model_name, author_name, description, obj_content, mtl_content, texture_data):
        """모델을 웹서버 DB에 저장"""
        try:
            model_id = str(uuid.uuid4())
            share_token = str(uuid.uuid4())
            
            # 텍스처 데이터를 base64로 인코딩
            texture_base64 = {}
            for name, data in texture_data.items():
                texture_base64[name] = base64.b64encode(data).decode('utf-8')
            
            # 서버로 전송할 데이터
            payload = {
                'model_id': model_id,
                'name': model_name,
                'author': author_name,
                'description': description,
                'share_token': share_token,
                'obj_content': obj_content,
                'mtl_content': mtl_content,
                'texture_data': texture_base64
            }
            
            st.write(f"📡 웹서버에 모델 저장 중... (ID: {model_id[:8]}...)")
            
            response = requests.post(
                self.save_model_url,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=60,
                verify=False
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('status') == 'success':
                    st.success("✅ 웹서버에 모델 저장 완료!")
                    return model_id, share_token
                else:
                    st.error(f"모델 저장 실패: {result.get('message')}")
                    return None, None
            else:
                st.error(f"서버 오류: {response.status_code}")
                return None, None
                
        except Exception as e:
            st.error(f"모델 저장 중 오류: {str(e)}")
            return None, None
    
    def load_model(self, share_token):
        """웹서버 DB에서 모델 로드"""
        try:
            params = {'token': share_token}
            response = requests.get(self.load_model_url, params=params, timeout=30, verify=False)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('status') == 'success':
                    files = result.get('files', {})
                    
                    # base64 텍스처 데이터를 바이너리로 변환
                    texture_data = {}
                    for name, base64_data in files.get('texture_data', {}).items():
                        texture_data[name] = base64.b64decode(base64_data)
                    
                    return (
                        files.get('obj_content', ''),
                        files.get('mtl_content', ''),
                        texture_data,
                        result.get('model', {}),
                        result.get('feedbacks', [])
                    )
                else:
                    return None, None, None, None, None
            else:
                return None, None, None, None, None
                
        except Exception as e:
            st.error(f"모델 로드 중 오류: {str(e)}")
            return None, None, None, None, None
    
    def save_feedback(self, model_id, x, y, z, screen_x, screen_y, comment, feedback_type='point'):
        """피드백을 웹서버 DB에 저장"""
        try:
            payload = {
                'model_id': model_id,
                'x': float(x),
                'y': float(y),
                'z': float(z),
                'screen_x': float(screen_x),
                'screen_y': float(screen_y),
                'comment': comment,
                'feedback_type': feedback_type
            }
            
            response = requests.post(
                f"{self.feedback_api_url}?action=save",
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=30,
                verify=False
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    return result.get('feedback_id')
                else:
                    st.error(f"피드백 저장 실패: {result.get('error')}")
                    return None
            else:
                st.error(f"서버 오류: {response.status_code}")
                return None
                
        except Exception as e:
            st.error(f"피드백 저장 중 오류: {str(e)}")
            return None
    
    def get_feedbacks(self, model_id):
        """특정 모델의 피드백 목록 조회"""
        try:
            params = {'action': 'list', 'model_id': model_id}
            response = requests.get(self.feedback_api_url, params=params, timeout=30, verify=False)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    return result.get('feedbacks', [])
                else:
                    st.error(f"피드백 조회 실패: {result.get('error')}")
                    return []
            else:
                return []
                
        except Exception as e:
            st.error(f"피드백 조회 중 오류: {str(e)}")
            return []
    
    def update_feedback_status(self, feedback_id, status):
        """피드백 상태 업데이트"""
        try:
            payload = {'id': feedback_id, 'status': status}
            response = requests.put(
                f"{self.feedback_api_url}?action=update_status",
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=30,
                verify=False
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('success', False)
            else:
                return False
                
        except Exception as e:
            st.error(f"피드백 상태 업데이트 중 오류: {str(e)}")
            return False
    
    def delete_feedback(self, feedback_id):
        """피드백 삭제"""
        try:
            params = {'id': feedback_id}
            response = requests.delete(self.feedback_api_url, params=params, timeout=30, verify=False)
            
            if response.status_code == 200:
                result = response.json()
                return result.get('success', False)
            else:
                return False
                
        except Exception as e:
            st.error(f"피드백 삭제 중 오류: {str(e)}")
            return False
    
    def get_all_models(self):
        """모든 모델 목록 조회"""
        try:
            params = {'action': 'list'}
            response = requests.get(self.model_api_url, params=params, timeout=30, verify=False)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('status') == 'success':
                    return result.get('models', [])
            
            return []
        except Exception as e:
            # 에러는 콘솔에만 출력하고 빈 리스트 반환
            print(f"모델 목록 조회 중 오류: {str(e)}")
            return []
    
    def get_model_count(self):
        """저장된 모델 수 조회"""
        try:
            params = {'action': 'count'}
            response = requests.get(self.model_api_url, params=params, timeout=10, verify=False)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('status') == 'success':
                    return result.get('count', 0)
            
            return 0
        except Exception as e:
            # 에러는 콘솔에만 출력하고 0 반환
            print(f"모델 수 조회 중 오류: {str(e)}")
            return 0
    
    def delete_model(self, model_id):
        """모델 삭제"""
        try:
            params = {'action': 'delete', 'model_id': model_id}
            response = requests.get(self.model_api_url, params=params, timeout=30, verify=False)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('status') == 'success':
                    st.success("✅ 웹서버에서 모델 삭제 완료!")
                    return True
                else:
                    st.error(f"❌ 모델 삭제 실패: {result.get('message')}")
                    return False
            
            return False
        except Exception as e:
            st.error(f"모델 삭제 중 오류: {str(e)}")
            return False
    
    def add_feedback(self, model_id, x, y, z, screen_x, screen_y, comment, feedback_type='point'):
        """피드백 추가 (save_feedback와 동일)"""
        return self.save_feedback(model_id, x, y, z, screen_x, screen_y, comment, feedback_type)

# 호환성을 위한 별칭
ModelDatabase = WebServerDatabase
