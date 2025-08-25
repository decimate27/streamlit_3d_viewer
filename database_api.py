"""
웹서버 PHP API 전용 데이터베이스 클래스
모든 DB 작업을 웹서버 API를 통해 처리
로컬 SQLite 의존성 완전 제거
"""

import json
import uuid
import requests
import streamlit as st
from datetime import datetime
from web_storage import WebServerStorage, LocalBackupStorage

class ModelDatabase:
    """웹서버 API 기반 데이터베이스 클래스"""
    
    def __init__(self):
        """초기화 - 로컬 DB 없음, API만 사용"""
        self.api_base_url = "http://decimate27.dothome.co.kr/streamlit_data"
        self.web_storage = WebServerStorage()
        self.local_backup = LocalBackupStorage()  # 백업용으로만 사용
        
        # API 엔드포인트
        self.endpoints = {
            'get_all': f"{self.api_base_url}/api_get_models.php",
            'get_one': f"{self.api_base_url}/api_get_model.php",
            'save': f"{self.api_base_url}/api_save_model.php",  # 새로운 API 사용
            'delete': f"{self.api_base_url}/api_delete_model.php",
            'scan': f"{self.api_base_url}/scan_and_rebuild_db.php",
            'update_height': f"{self.api_base_url}/api_update_height.php",
            'annotations': f"{self.api_base_url}/api_annotations.php"
        }
        
        # 세션 캐시 (API 호출 최소화)
        if 'models_cache' not in st.session_state:
            st.session_state.models_cache = None
            st.session_state.cache_time = None
    
    def _make_request(self, endpoint, method='GET', data=None, params=None):
        """API 요청 헬퍼 함수"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            if method == 'GET':
                response = requests.get(endpoint, params=params, headers=headers, timeout=30, verify=False)
            elif method == 'POST':
                if data:
                    headers['Content-Type'] = 'application/json'
                    response = requests.post(endpoint, json=data, headers=headers, timeout=30, verify=False)
                else:
                    response = requests.post(endpoint, headers=headers, timeout=30, verify=False)
            elif method == 'PUT':
                if data:
                    headers['Content-Type'] = 'application/json'
                    response = requests.put(endpoint, json=data, headers=headers, timeout=30, verify=False)
                else:
                    response = requests.put(endpoint, headers=headers, timeout=30, verify=False)
            elif method == 'DELETE':
                response = requests.delete(endpoint, params=params, headers=headers, timeout=30, verify=False)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            if response.status_code == 200:
                return response.json()
            else:
                st.error(f"API 오류: {response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            st.error(f"네트워크 오류: {str(e)}")
            return None
        except json.JSONDecodeError as e:
            st.error(f"응답 파싱 오류: {str(e)}")
            return None
    
    def save_model(self, name, author, description, obj_content, mtl_content, texture_data, real_height=1.0):
        """모델 저장 - 웹서버에만 저장"""
        model_id = str(uuid.uuid4()).replace('-', '')
        share_token = str(uuid.uuid4())
        
        st.write(f"🚀 모델 저장 시작: {model_id}")
        
        # 1. 파일을 웹서버에 업로드
        st.write("🌐 웹서버에 파일 업로드 중...")
        file_paths = self.web_storage.save_model_to_server(
            model_id, obj_content, mtl_content, texture_data,
            name, author, description, share_token, real_height
        )
        
        if not file_paths:
            st.error("❌ 파일 업로드 실패")
            return None, None
        
        st.success("✅ 파일 업로드 성공!")
        
        # 2. DB에 메타데이터 저장 (PHP API 호출) - 파일 내용은 보내지 않음
        st.write("💾 데이터베이스에 정보 저장 중...")
        
        # 메타데이터만 전송 (파일은 이미 업로드됨)
        save_data = {
            'model_id': model_id,
            'name': name,
            'author': author,
            'description': description,
            'share_token': share_token
        }
        
        result = self._make_request(self.endpoints['save'], method='POST', data=save_data)
        
        if result and result.get('status') == 'success':
            st.success("✅ 데이터베이스 저장 성공!")
            
            # 캐시 무효화
            st.session_state.models_cache = None
            
            # 로컬 백업 (선택사항)
            try:
                backup_paths = self.local_backup.save_model_backup(
                    model_id, obj_content, mtl_content, texture_data
                )
                if backup_paths:
                    st.write("💾 로컬 백업 완료")
            except:
                pass  # 백업 실패는 무시
            
            return model_id, share_token
        else:
            st.warning("⚠️ 데이터베이스 저장 실패 (파일은 업로드됨)")
            # 데이터베이스 저장 실패해도 model_id와 share_token은 반환
            # 파일은 이미 업로드되었으므로 접근 가능
            return model_id, share_token
    
    def get_all_models(self):
        """모든 모델 목록 조회 - 웹서버 API 사용"""
        # 캐시 확인 (5초 유효)
        if st.session_state.models_cache and st.session_state.cache_time:
            from datetime import timedelta
            if datetime.now() - st.session_state.cache_time < timedelta(seconds=5):
                return st.session_state.models_cache
        
        # API 호출
        result = self._make_request(self.endpoints['get_all'])
        
        if result and result.get('status') == 'success':
            models = result.get('models', [])
            
            # file_paths JSON 파싱
            for model in models:
                if isinstance(model.get('file_paths'), str):
                    try:
                        model['file_paths'] = json.loads(model['file_paths'])
                    except:
                        model['file_paths'] = {}
            
            # 캐시 저장
            st.session_state.models_cache = models
            st.session_state.cache_time = datetime.now()
            
            return models
        else:
            return []
    
    def get_model_by_token(self, share_token):
        """공유 토큰으로 모델 조회"""
        result = self._make_request(
            self.endpoints['get_one'], 
            params={'token': share_token}
        )
        
        if result and result.get('status') == 'success':
            model = result.get('model')
            
            # file_paths JSON 파싱
            if model and isinstance(model.get('file_paths'), str):
                try:
                    model['file_paths'] = json.loads(model['file_paths'])
                except:
                    model['file_paths'] = {}
            
            return model
        else:
            return None
    
    def delete_model(self, model_id):
        """모델 삭제"""
        st.write(f"🗑️ 모델 삭제 중: {model_id}")
        
        # API 호출
        result = self._make_request(
            self.endpoints['delete'],
            method='POST',
            data={'model_id': model_id}
        )
        
        if result and result.get('status') == 'success':
            st.success("✅ 모델이 삭제되었습니다.")
            
            # 캐시 무효화
            st.session_state.models_cache = None
            
            # 로컬 백업도 삭제 (있는 경우)
            try:
                self.local_backup.delete_model_backup(model_id)
            except:
                pass
            
            return True
        else:
            st.error("❌ 모델 삭제 실패")
            return False
    
    def get_model_count(self):
        """저장된 모델 수 조회"""
        models = self.get_all_models()
        return len(models)
    
    def scan_and_rebuild(self, rebuild=False, show_progress=True):
        """웹서버 files 폴더 스캔하여 DB 재구축"""
        
        params = {}
        if rebuild:
            params['rebuild'] = 'true'
            if show_progress:
                st.warning("⚠️ 기존 DB를 완전히 재구축합니다.")
        
        if show_progress:
            st.info("🔍 웹서버 파일 시스템 스캔 중...")
        
        result = self._make_request(
            self.endpoints['scan'],
            params=params
        )
        
        if result and result.get('status') == 'success':
            summary = result.get('summary', {})
            
            if show_progress:
                st.success(f"""
                ✅ 스캔 완료!
                - 스캔된 디렉토리: {summary.get('directories_scanned', 0)}개
                - 발견된 모델: {summary.get('models_found', 0)}개
                - 새로 추가: {summary.get('inserted', 0)}개
                - 업데이트: {summary.get('updated', 0)}개
                - 오류: {summary.get('errors', 0)}개
                """)
            
            # 캐시 무효화
            st.session_state.models_cache = None
            
            return True
        else:
            if show_progress:
                st.error("❌ 스캔 실패")
            return False
    
    # 호환성을 위한 메서드들 (더미 구현)
    def init_db(self):
        """더미 메서드 - API 사용으로 불필요"""
        pass
    
    def sync_with_web_db(self, show_progress=True):
        """더미 메서드 - 이미 웹서버 DB 사용"""
        if show_progress:
            st.info("ℹ️ 이미 웹서버 DB를 직접 사용 중입니다.")
        return True
    
    def auto_sync_with_web(self):
        """더미 메서드 - 이미 웹서버 DB 사용"""
        return True
    
    def get_sync_status(self):
        """동기화 상태 - 항상 동기화됨"""
        return {
            'local_count': self.get_model_count(),
            'synced': True
        }
    
    def update_model_height(self, model_id, height):
        """모델 높이 업데이트"""
        data = {
            'model_id': model_id,
            'height': float(height)
        }
        
        result = self._make_request(
            self.endpoints['update_height'],
            method='POST',
            data=data
        )
        
        if result and result.get('status') == 'success':
            # 캐시 무효화
            st.session_state.models_cache = None
            return True
        else:
            if result:
                st.error(f"높이 업데이트 실패: {result.get('message', 'Unknown error')}")
            else:
                st.error("높이 업데이트 중 오류가 발생했습니다.")
            return False
    
    # Annotation 관련 메서드들
    def get_annotations(self, share_token):
        """수정점 조회"""
        params = {'action': 'list', 'model_token': share_token}
        result = self._make_request(
            self.endpoints['annotations'],
            method='GET',
            params=params
        )
        
        if result and result.get('status') == 'success':
            return result.get('annotations', [])
        return []
    
    def add_annotation(self, share_token, position, text):
        """수정점 추가"""
        data = {
            'model_token': share_token,
            'position': position,
            'text': text
        }
        
        result = self._make_request(
            self.endpoints['annotations'] + '?action=save',
            method='POST',
            data=data
        )
        
        if result and result.get('status') == 'success':
            return result.get('annotation_id')
        return None
    
    def save_annotations_batch(self, model_token, annotations, changes):
        """여러 수정점 일괄 저장"""
        data = {
            'model_token': model_token,
            'annotations': annotations,
            'changes': changes
        }
        
        result = self._make_request(
            self.endpoints['annotations'] + '?action=save_batch',
            method='POST',
            data=data
        )
        
        if result and result.get('status') == 'success':
            return True
        return False
    
    def update_annotation_status(self, annotation_id, completed):
        """수정점 상태 업데이트"""
        data = {
            'id': annotation_id,
            'completed': completed
        }
        
        result = self._make_request(
            self.endpoints['annotations'] + '?action=update_status',
            method='PUT',
            data=data
        )
        
        if result and result.get('status') == 'success':
            return True
        return False
    
    def delete_annotation(self, annotation_id):
        """수정점 삭제"""
        params = {'id': annotation_id}
        result = self._make_request(
            self.endpoints['annotations'],
            method='DELETE',
            params=params
        )
        
        if result and result.get('status') == 'success':
            return True
        return False

# 기존 코드와의 호환성을 위한 함수들
def load_model_files(model_data):
    """저장된 모델 파일들 로드 - 웹서버에서 직접"""
    web_storage = WebServerStorage()
    
    # 웹서버에서 로드
    result = web_storage.load_model_from_server(model_data['file_paths'])
    
    if result:
        return result
    else:
        # 로컬 백업 시도 (있는 경우)
        local_backup = LocalBackupStorage()
        backup_result = local_backup.load_model_backup(model_data.get('backup_paths'))
        if backup_result:
            st.warning("⚠️ 로컬 백업에서 로드됨")
            return backup_result
        else:
            st.error("모델 파일 로드 실패")
            return None

def generate_share_url(share_token):
    """공유 URL 생성"""
    import os
    # Streamlit Cloud URL 사용 (환경변수로 설정 가능)
    base_url = os.getenv('BASE_URL', 'https://airbible-3d-viewer.streamlit.app')
    return f"{base_url}/viewer?token={share_token}"

def reset_database(db_path=None):
    """데이터베이스 리셋 - 웹서버 DB 재구축"""
    st.warning("⚠️ 웹서버 DB를 재구축합니다.")
    db = ModelDatabase()
    return db.scan_and_rebuild(rebuild=True)